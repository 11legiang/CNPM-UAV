import sqlite3
from contextlib import closing
from pathlib import Path


class EventStore:
    def __init__(self):
        self.db_path = (
            Path(__file__).resolve().parent / "outputs" / "events.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.create_table()

    def create_table(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    video_path TEXT NOT NULL,
                    video_time_seconds REAL,
                    image_path TEXT,
                    review_status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (
                            review_status IN (
                                'pending', 'confirmed', 'false_alarm'
                            )
                        )
                )
            """)
            connection.commit()

    def add_event(
        self,
        created_at,
        video_path,
        video_time_seconds,
        image_path=None,
    ):
        with closing(sqlite3.connect(self.db_path)) as connection:
            cursor = connection.execute(
                """
                INSERT INTO events (
                    created_at,
                    video_path,
                    video_time_seconds,
                    image_path
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    created_at,
                    str(video_path),
                    video_time_seconds,
                    str(image_path) if image_path is not None else None,
                ),
            )
            connection.commit()
            return cursor.lastrowid

    def get_events(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("""
                SELECT *
                FROM events
                ORDER BY id DESC
                LIMIT 200
            """).fetchall()
            return [dict(row) for row in rows]
    def update_review_status(self, event_id, status):
        if status not in {"confirmed", "false_alarm"}:
            raise ValueError("Trạng thái xác nhận không hợp lệ.")

        with closing(sqlite3.connect(self.db_path)) as connection:
            cursor = connection.execute(
                """
                UPDATE events
                SET review_status = ?
                WHERE id = ?
                """,
                (status, event_id),
            )

            if cursor.rowcount != 1:
                raise ValueError("Không tìm thấy sự kiện cần cập nhật.")

            connection.commit()