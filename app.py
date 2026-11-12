import sys
from pathlib import Path

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

        self.setWindowTitle("Giám sát cháy từ camera UAV")
        self.resize(800, 500)

        self.video_label = QLabel("Chưa chọn video")
        self.status_label = QLabel("Trạng thái: Chưa chọn video")

        self.select_button = QPushButton("Chọn video")
        self.select_button.clicked.connect(self.select_video)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
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
        self.video_label.setText(f"Video: {Path(path).name}")
        self.status_label.setText("Trạng thái: Đã chọn video")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitoringWindow()
    window.show()
    sys.exit(app.exec())