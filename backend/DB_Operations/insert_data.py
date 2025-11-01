import sqlite3
from DB_Operations.db_config import DB_PATH
import os

def insert_event(event):
    """Insert or update a single detection event in the database."""
    try:
        # Ensure the directory for DB exists (important if running in different environments)
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        # Connect will automatically create DB if it doesn't exist — no early return
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    date TEXT,
                    time TEXT,
                    location TEXT,
                    number_plate TEXT,
                    has_helmet INTEGER,
                    image_url TEXT
                )
            """)

            # Insert or update event record
            cursor.execute("""
                INSERT OR REPLACE INTO events 
                (id, date, time, location, number_plate, has_helmet, image_url)
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
            print(f"✅ Event '{event['id']}' inserted successfully!")

    except sqlite3.Error as e:
        print(f"❌ SQLite error inserting event '{event.get('id', 'unknown')}': {e}")
    except Exception as e:
        print(f"❌ Unexpected error inserting event '{event.get('id', 'unknown')}': {e}")
        raise


if __name__ == "__main__":
    # Test event
    test_event = {
        "id": "evt001",
        "date": "2025-10-31",
        "time": "14:00",
        "location": "Test Location",
        "number_plate": "ABC123",
        "has_helmet": True,
        "image_url": "http://example.com/image.jpg"
    }
    insert_event(test_event)
