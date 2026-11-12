import cv2
from ultralytics import YOLO
import winsound
from pathlib import Path
from datetime import datetime

# 1. Khởi tạo model YOLOv8
model = YOLO("models/fire_smoke.pt")

# 2. Mở file video
video = cv2.VideoCapture("fire_test.mp4")

if not video.isOpened():
    raise SystemExit("Không mở được video. Kiểm tra tên và vị trí file.")

# Biến cho cải tiến với code cũ:
consecutive_detections = 0  # Số khung liên tiếp có lửa/khói
required_frames = 5
alarm_active = False        # Đã bật trạng thái cảnh báo chưa

consecutive_misses = 0
clear_frames = 10

alert_dir = Path("outputs/alerts")
alert_dir.mkdir(parents=True, exist_ok=True)

while True:
    success, frame = video.read()
    if not success:
        break

    # Dự đoán đối tượng trên từng frame
    results = model.predict(
        source=frame,
        device="cpu",
        conf=0.25,
        verbose=False,
    )

    has_fire_or_smoke = len(results[0].boxes) > 0

    if has_fire_or_smoke:
        consecutive_detections += 1
        consecutive_misses = 0

        if consecutive_detections >= required_frames and not alarm_active:
            alarm_active = True
            print("CẢNH BÁO: Phát hiện dấu hiệu cháy!")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            # Lưu ảnh minh chứng khi cảnh báo vừa bật.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = alert_dir / f"alert_{timestamp}.jpg"

            saved = cv2.imwrite(str(image_path), results[0].plot())

            if saved:
                print(f"Đã lưu ảnh: {image_path}")
            else:
                print(f"Không lưu được ảnh: {image_path}")
    else:
        consecutive_detections = 0
        consecutive_misses += 1

        if consecutive_misses >= clear_frames and alarm_active:
            alarm_active = False
            print("KẾT THÚC CẢNH BÁO: Không còn phát hiện kéo dài.")

    """ Minh họa nếu cần
    print(
    f"Có phát hiện: {has_fire_or_smoke} | "
    f"Đếm: {consecutive_detections} | "
    f"Đang cảnh báo: {alarm_active}"
    )
    """


    # Vẽ kết quả lên frame
    annotated_frame = results[0].plot()

    # Hiển thị frame đã được vẽ bounding box
    cv2.imshow("Video", annotated_frame)

    # Nhấn phím 'q' để thoát vòng lặp
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
