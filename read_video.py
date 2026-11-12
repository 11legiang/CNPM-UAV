import cv2

video = cv2.VideoCapture("sample.mp4")

if not video.isOpened():
    raise SystemExit("Không mở được video. Kiểm tra tên và vị trí file.")

while True:
    success, frame = video.read()

    if not success:
        break

    cv2.imshow("Video", frame)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()