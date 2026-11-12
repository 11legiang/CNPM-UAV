import sqlite3
from contextlib import closing

from event_store import EventStore

store = EventStore()

with closing(sqlite3.connect(store.db_path)) as connection:
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT *
        FROM events
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    for row in rows:
        print(dict(row))