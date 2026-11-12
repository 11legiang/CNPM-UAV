import sys
from pathlib import Path

import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MonitoringWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.video_path = None
        self.video = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.setWindowTitle("Giám sát cháy từ camera UAV")
        self.resize(800, 600)

        self.video_label = QLabel("Chưa chọn video")
        self.status_label = QLabel("Trạng thái: Chưa chọn video")

        self.preview_label = QLabel("Video sẽ hiển thị tại đây")
        self.preview_label.setFixedSize(640, 360)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(
            "background-color: #202020; color: white;"
        )

        self.select_button = QPushButton("Chọn video")
        self.select_button.clicked.connect(self.select_video)

        self.start_button = QPushButton("Bắt đầu")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_monitoring)

        self.stop_button = QPushButton("Dừng")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_monitoring)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.preview_label)
        layout.addStretch()

        self.setLayout(layout)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn video để giám sát",
            "",
            "Video (*.mp4 *.avi *.mov *.mkv)",
        )

        if not path:
            return

        self.video_path = path

        # <--- MỚI THÊM: Xóa khung hình cũ và nhắc người dùng bấm Bắt đầu --->
        self.preview_label.clear()
        self.preview_label.setText("Nhấn Bắt đầu để phát video")
        # -------------------------------------------------------------------

        self.video_label.setText(f"Video: {Path(path).name}")
        self.status_label.setText("Trạng thái: Đã chọn video")
        self.start_button.setEnabled(True)

    def start_monitoring(self):
        if not self.video_path:
            return

        self.video = cv2.VideoCapture(self.video_path)
        if not self.video.isOpened():
            self.video.release()
            self.video = None
            self.status_label.setText("Lỗi: Không mở được video")
            return

        self.select_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Trạng thái: Đang phát video")
        self.timer.start(33)

    def stop_monitoring(self):
        self.timer.stop()
        if self.video is not None:
            self.video.release()
            self.video = None

        self.select_button.setEnabled(True)
        self.start_button.setEnabled(self.video_path is not None)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Trạng thái: Đã dừng")

    def update_frame(self):
        if self.video is None:
            return

        success, frame = self.video.read()
        if not success:
            self.stop_monitoring()
            self.status_label.setText(
                "Trạng thái: Hết video hoặc không đọc được khung tiếp theo"
            )
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape
        image = QImage(
            rgb_frame.data,
            width,
            height,
            rgb_frame.strides[0],
            QImage.Format.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(image)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def closeEvent(self, event):
        self.stop_monitoring()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitoringWindow()
    window.show()
    sys.exit(app.exec())
