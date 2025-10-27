import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "events.db"))

def insert_event(event):
    """Insert single detection event into database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("DB insert path:", os.path.abspath(DB_PATH))

    cursor.execute("""
        INSERT INTO events (id, date, time, location, number_plate, has_helmet, image_url)
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
