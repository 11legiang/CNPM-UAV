import cv2
from ultralytics import YOLO

# 1. Khởi tạo model YOLOv8
model = YOLO("models/fire_smoke.pt")

# 2. Mở file video
video = cv2.VideoCapture("fire_test.mp4")

if not video.isOpened():
  raise SystemExit("Không mở được video. Kiểm tra tên và vị trí file.")

while True:
  success, frame = video.read()
  if not success:
    break

  # Dự đoán đối tượng trên từng frame
  results = model.predict(
      source=frame,
      device="cpu",
      conf=0.25,
      verbose=False, # Tắt bớt các dòng thông báo log log ra màn hình console (terminal) để màn hình chạy nhìn sạch sẽ hơn.

  )

  # Vẽ kết quả lên frame
  annotated_frame = results[0].plot()

  # Hiển thị frame đã được vẽ bounding box
  cv2.imshow("Video", annotated_frame)

  # Nhấn phím 'q' để thoát vòng lặp
  if cv2.waitKey(10) & 0xFF == ord("q"):
    break

video.release()
cv2.destroyAllWindows()
