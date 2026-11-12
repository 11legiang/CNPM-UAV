import cv2
from ultralytics import YOLO

# 1. Khởi tạo model YOLOv8
model = YOLO("yolov8n.pt")

# 2. Mở file video
video = cv2.VideoCapture("testA94.mp4")

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
      conf=0.5,
      verbose=False,
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
