import sqlite3
import os

# Shared DB path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "events.db")


def insert_event(event):
    """Insert a single detection event into the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO events (id, date, time, location, number_plate, has_helmet, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event["id"],
        event["date"],
        event["time"],
        event["location"],
        event["number_plate"],
        int(event["has_helmet"]),
        event["image_url"]
    ))
    
    conn.commit()
    conn.close()
