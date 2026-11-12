import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from ultralytics import YOLO


class VideoWorker(QThread):
    frame_ready = Signal(QImage)
    status_changed = Signal(str)

    # <--- 1. MỚI THÊM: Khai báo tín hiệu trạng thái cảnh báo --->
    alarm_changed = Signal(bool)
    # ------------------------------------------------------------

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

            # <--- 2. MỚI THÊM: Khởi tạo các biến đếm chống nhiễu cảnh báo --->
            detections = 0
            misses = 0
            alarm_active = False
            required_frames = 5
            clear_frames = 10
            # ------------------------------------------------------------------

            while not self.isInterruptionRequested():
                success, frame = video.read()

                if not success:
                    self.status_changed.emit(
                        "Trạng thái: Hết video hoặc không đọc được khung tiếp theo"
                    )
                    return

                results = model.predict(
                    source=frame,
                    device="cpu",
                    conf=0.25,
                    verbose=False,
                )

                if self.isInterruptionRequested():
                    self.status_changed.emit("Trạng thái: Đã dừng")
                    return

                # <--- 3. MỚI THÊM: Kiểm tra phát hiện và phát tín hiệu cảnh báo --->
                has_detection = len(results[0].boxes) > 0
                if has_detection:
                    detections += 1
                    misses = 0
                    if detections >= required_frames and not alarm_active:
                        alarm_active = True
                        self.alarm_changed.emit(True)
                else:
                    detections = 0
                    misses += 1
                    if misses >= clear_frames and alarm_active:
                        alarm_active = False
                        self.alarm_changed.emit(False)
                # ------------------------------------------------------------------

                annotated_frame = results[0].plot()
                rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

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