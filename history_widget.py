import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from event_store import EventStore


class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.store = EventStore()
        self.events = []

        self.refresh_button = QPushButton("Làm mới lịch sử")
        self.refresh_button.clicked.connect(self.refresh_events)

        self.info_label = QLabel()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Giờ xử lý", "Video", "Vị trí (giây)", "Xác nhận"
        ])
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.itemSelectionChanged.connect(self.show_event)

        self.detail_label = QLabel("Chọn một sự kiện để xem bằng chứng.")
        self.detail_label.setWordWrap(True)

        self.image_label = QLabel("Chưa chọn sự kiện")
        self.image_label.setFixedSize(360, 240)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "background-color: #202020; color: white;"
        )

        self.confirm_button = QPushButton("Xác nhận có cháy")
        self.false_alarm_button = QPushButton("Báo nhầm")

        self.confirm_button.clicked.connect(
            lambda: self.review_event("confirmed")
        )
        self.false_alarm_button.clicked.connect(
            lambda: self.review_event("false_alarm")
        )

        details = QVBoxLayout()
        details.addWidget(self.detail_label)
        details.addWidget(self.image_label)
        details.addWidget(self.confirm_button)
        details.addWidget(self.false_alarm_button)
        details.addStretch()

        content = QHBoxLayout()
        content.addWidget(self.table, 1)
        content.addLayout(details)

        layout = QVBoxLayout(self)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.info_label)
        layout.addLayout(content)

        self.refresh_events()

    def selected_event(self):
        rows = self.table.selectionModel().selectedRows()

        if not rows:
            return None

        row = rows[0].row()
        if 0 <= row < len(self.events):
            return self.events[row]

        return None

    def refresh_events(self):
        try:
            events = self.store.get_events()
        except sqlite3.Error as error:
            self.info_label.setText(f"Không đọc được lịch sử: {error}")
            return

        status_labels = {
            "pending": "Chưa xác nhận",
            "confirmed": "Xác nhận có cháy",
            "false_alarm": "Báo nhầm",
        }

        # Không xử lý chọn dòng khi bảng đang được nạp lại.
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
            self.table.clearContents()
            self.events = events
            self.table.setRowCount(len(events))

            for row_index, event in enumerate(events):
                seconds = event["video_time_seconds"]
                time_text = (
                    f"{seconds:.3f}" if seconds is not None else "Không có"
                )

                values = [
                    str(event["id"]),
                    event["created_at"],
                    Path(event["video_path"]).name,
                    time_text,
                    status_labels.get(
                        event["review_status"], event["review_status"]
                    ),
                ]

                for column_index, value in enumerate(values):
                    self.table.setItem(
                        row_index,
                        column_index,
                        QTableWidgetItem(value),
                    )

            self.table.resizeColumnsToContents()
        finally:
            self.table.blockSignals(False)

        self.show_event()
        self.info_label.setText(
            f"Hiển thị {len(events)} sự kiện mới nhất, tối đa 200."
        )

    def show_event(self):
        event = self.selected_event()
        self.confirm_button.setEnabled(event is not None)
        self.false_alarm_button.setEnabled(event is not None)
        self.image_label.clear()

        if event is None:
            self.detail_label.setText(
                "Chọn một sự kiện để xem bằng chứng."
            )
            self.image_label.setText("Chưa chọn sự kiện")
            return

        self.detail_label.setText(
            f"Sự kiện #{event['id']}\n"
            f"Video: {Path(event['video_path']).name}\n"
            f"Giờ xử lý: {event['created_at']}"
        )

        image_path = event["image_path"]
        if not image_path:
            self.image_label.setText("Sự kiện không có ảnh minh chứng")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText("Ảnh bị thiếu hoặc không đọc được")
            return

        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def review_event(self, status):
        event = self.selected_event()
        if event is None:
            return

        event_id = event["id"]

        try:
            self.store.update_review_status(event_id, status)
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.warning(
                self,
                "Không lưu được xác nhận",
                str(error),
            )
            return

        self.refresh_events()
        self.info_label.setText(
            f"Đã lưu kết quả xác nhận cho sự kiện #{event_id}."
        )