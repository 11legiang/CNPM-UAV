import sys
from pathlib import Path

# <--- 1. CẬP NHẬT IMPORT: Bỏ cv2, thêm Slot và VideoWorker --->
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from video_worker import VideoWorker
# ---------------------------------------------------------------


class MonitoringWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.video_path = None

        # <--- 2. CẬP NHẬT KHỞI TẠO: Thay video/timer bằng worker --->
        self.worker = None
        self.close_pending = False
        # ------------------------------------------------------------

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
        self.preview_label.clear()
        self.preview_label.setText("Nhấn Bắt đầu để phát video")
        self.video_label.setText(f"Video: {Path(path).name}")
        self.status_label.setText("Trạng thái: Đã chọn video")
        self.start_button.setEnabled(True)

    # <--- 3. CẬP NHẬT: Khởi chạy và gửi yêu cầu dừng tới VideoWorker --->
    def start_monitoring(self):
        if not self.video_path or self.worker is not None:
            return

        self.select_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Trạng thái: Đang mở video")

        self.worker = VideoWorker(self.video_path, self)
        self.worker.frame_ready.connect(self.display_frame)
        self.worker.status_changed.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def stop_monitoring(self):
        if self.worker is not None:
            self.stop_button.setEnabled(False)
            self.status_label.setText("Trạng thái: Đang dừng")
            self.worker.requestInterruption()
    # --------------------------------------------------------------------

    # <--- 4. CẬP NHẬT: Nhận ảnh từ worker và xử lý dọn dẹp khi xong --->
    @Slot(QImage)
    def display_frame(self, image):
        pixmap = QPixmap.fromImage(image)
        self.preview_label.setPixmap(
            pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    @Slot()
    def on_worker_finished(self):
        self.worker.deleteLater()
        self.worker = None

        self.select_button.setEnabled(True)
        self.start_button.setEnabled(self.video_path is not None)
        self.stop_button.setEnabled(False)

        if self.close_pending:
            self.close()
    # --------------------------------------------------------------------

    # <--- 5. CẬP NHẬT: Đợi worker dừng an toàn trước khi đóng cửa sổ --->
    def closeEvent(self, event):
        if self.worker is not None:
            self.close_pending = True
            self.stop_monitoring()
            event.ignore()
        else:
            event.accept()
    # --------------------------------------------------------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitoringWindow()
    window.show()
    sys.exit(app.exec())
