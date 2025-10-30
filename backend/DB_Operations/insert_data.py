import sqlite3
from DB_Operations.db_config import DB_PATH  # Import shared DB path


def insert_event(event):
    """Insert a single detection event into the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ensure table exists (optional but safe)
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

        # Insert or update event
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
        print(f"✅ Event '{event['id']}' inserted successfully!")

    except Exception as e:
        print(f"❌ Error inserting event '{event.get('id', 'unknown')}': {e}")

    finally:
        conn.close()



