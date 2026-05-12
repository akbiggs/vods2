import sqlite3
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import TypedDict


db_path = Path(__file__).parent.parent / "database.db"


class RecentEvent(TypedDict):
    name: str
    url: str


def get_recent_events(num_events: int = 5) -> list[RecentEvent]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM event
        ORDER BY id DESC
        LIMIT ?
    """, (num_events,))

    rows = cursor.fetchall()

    conn.close()

    events: list[RecentEvent] = []

    for row in rows:
        event_name = row[0]

        events.append({
            "name": event_name,
            "url": urllib.parse.quote_plus(event_name),
        })

    return events

def get_last_updated_date() -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT value
        FROM metadata
        WHERE key = 'last_updated'
    """)

    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return "Unknown"

    # parse YYYY-MM-DD from DB
    dt = datetime.strptime(row[0], "%Y-%m-%d")

    day = dt.day

    # suffix logic
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    return dt.strftime(f"%B {day}{suffix}, %Y")