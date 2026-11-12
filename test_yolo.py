from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.predict(
    source="https://ultralytics.com/images/bus.jpg",
    device="cpu",
    save=True,
)