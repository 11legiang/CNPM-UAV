import cv2
from ultralytics import YOLO

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

    # Kiểm tra có đối tượng lửa/khói trong khung hình không
    # (Đã thụt lề chuẩn vào bên trong vòng lặp while)
    has_fire_or_smoke = len(results[0].boxes) > 0 # Kiểm tra xem trong khung hình hiện tại AI có khoanh vùng được ít nhất 1 đốm lửa hoặc đám khói nào không.

    if has_fire_or_smoke:
        consecutive_detections += 1

        if consecutive_detections >= required_frames and not alarm_active:
            alarm_active = True
            print("CẢNH BÁO: Phát hiện dấu hiệu cháy!")
    else:
        consecutive_detections = 0
        alarm_active = False

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
