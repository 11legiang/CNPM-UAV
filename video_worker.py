from datetime import datetime
from pathlib import Path
import sqlite3  # <--- 1. MỚI THÊM

import cv2
from ultralytics import YOLO

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from event_store import EventStore  # <--- 1. MỚI THÊM


class VideoWorker(QThread):
    frame_ready = Signal(QImage)
    status_changed = Signal(str)
    alarm_changed = Signal(bool)

    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path

    def run(self):
        video = None

        try:
            video = cv2.VideoCapture(self.video_path)

            if not video.isOpened():
                self.status_changed.emit("Lỗi: Không mở được video")
                return

            self.status_changed.emit("Trạng thái: Đang tải mô hình")
            model = YOLO("models/fire_smoke.pt")

            if self.isInterruptionRequested():
                self.status_changed.emit("Trạng thái: Đã dừng")
                return

            self.status_changed.emit("Trạng thái: Đang nhận diện")

            # <--- 2. MỚI THÊM: Khởi tạo kho lưu trữ sự kiện SQLite --->
            store = EventStore()
            # -----------------------------------------------------------

            # Bộ đếm được khởi tạo lại ở mỗi lượt giám sát.
            detections = 0
            misses = 0
            alarm_active = False
            required_frames = 5
            clear_frames = 10

            while not self.isInterruptionRequested():
                success, frame = video.read()

                if not success:
                    self.status_changed.emit(
                        "Trạng thái: Hết video hoặc không đọc được khung tiếp theo"
                    )
                    return

                # Nhận diện trên một khung hình.
                results = model.predict(
                    source=frame,
                    device="cpu",
                    conf=0.25,
                    verbose=False,
                )

                if self.isInterruptionRequested():
                    self.status_changed.emit("Trạng thái: Đã dừng")
                    return

                # results là danh sách; lấy kết quả của khung hình đầu tiên.
                result = results[0]
                annotated_frame = result.plot()
                has_detection = len(result.boxes) > 0

                # Chỉ phát tín hiệu khi trạng thái cảnh báo thay đổi.
                if has_detection:
                    detections += 1
                    misses = 0

                    # <--- 4. CẬP NHẬT: Lưu ảnh minh chứng và ghi sự kiện vào SQLite --->
                    if detections >= required_frames and not alarm_active:
                        alarm_active = True
                        self.alarm_changed.emit(True)

                        created_at = datetime.now().astimezone().isoformat(
                            timespec="seconds"
                        )
                        video_time_seconds = (
                            video.get(cv2.CAP_PROP_POS_MSEC) / 1000
                        )
                        image_path = self.save_alert_frame(annotated_frame)

                        try:
                            event_id = store.add_event(
                                created_at=created_at,
                                video_path=self.video_path,
                                video_time_seconds=video_time_seconds,
                                image_path=image_path,
                            )
                            print(f"Đã lưu sự kiện cảnh báo #{event_id}")
                        except sqlite3.Error as error:
                            print(f"Không lưu được sự kiện cảnh báo: {error}")
                    # ------------------------------------------------------------------
                else:
                    detections = 0
                    misses += 1

                    if misses >= clear_frames and alarm_active:
                        alarm_active = False
                        self.alarm_changed.emit(False)

                # Chuyển ảnh BGR sang RGB để hiển thị bằng Qt.
                rgb_frame = cv2.cvtColor(
                    annotated_frame,
                    cv2.COLOR_BGR2RGB,
                )
                height, width, _ = rgb_frame.shape

                image = QImage(
                    rgb_frame.data,
                    width,
                    height,
                    rgb_frame.strides[0],
                    QImage.Format.Format_RGB888,
                ).copy()

                self.frame_ready.emit(image)
                self.msleep(33)

            self.status_changed.emit("Trạng thái: Đã dừng")

        except Exception as error:
            self.status_changed.emit(f"Lỗi xử lý video: {error}")

        finally:
            if video is not None:
                video.release()

    def save_alert_frame(self, frame):
        try:
            alert_dir = (
                Path(__file__).resolve().parent / "outputs" / "alerts"
            )
            alert_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = alert_dir / f"alert_{timestamp}.jpg"

            success, encoded_image = cv2.imencode(".jpg", frame)

            if not success:
                print("Không mã hóa được ảnh minh chứng.")
                return None

            image_path.write_bytes(encoded_image.tobytes())
            print(f"Đã lưu ảnh minh chứng: {image_path}")
            return image_path  # <--- 3. MỚI THÊM: Trả về đường dẫn ảnh

        except (OSError, cv2.error) as error:
            print(f"Không lưu được ảnh minh chứng: {error}")
            return None
