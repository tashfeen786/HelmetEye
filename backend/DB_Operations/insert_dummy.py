import sqlite3
import os
from DB_Operations.db_config import DB_PATH  # ✅ Use shared DB path


def insert_dummy_data():
    """Insert sample dummy data into the events table."""
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database file not found at {DB_PATH}")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Ensure the table exists (safe to include)
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

            # ✅ Sample data (you can uncomment or expand this)
            sample_data = [
               # ("evt-001", "2025-10-30", "18:32", "Kotli Basheer, AJK", "ISB-123", 0, "https://your-image-url.com/image1.png"),
                #("evt-002", "2025-10-30", "19:10", "Kotli Basheer, AJK", "ISB-456", 1, "https://your-image-url.com/image2.png"),
                #("evt-003", "2025-10-30", "21:30", "Kotli MS Hostel, AJK", "ISB-789", 0, "https://your-image-url.com/image3.png"),
                ("evt-004", "2025-11-01", "21:30", "Kotli MS Hostel, AJK", "ISB-789", 0, "https://your-image-url.com/image3.png"),
                ("evt-005", "2025-11-01", "21:30", "Kotli college road, AJK", "ajk-759", 0, "https://your-image-url.com/image3.png"),
            ]

            cursor.executemany("""
                INSERT OR REPLACE INTO events 
                (id, date, time, location, number_plate, has_helmet, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_data)

            conn.commit()
            print(f"✅ {len(sample_data)} dummy records inserted successfully!")

    except sqlite3.Error as e:
        print(f"❌ SQLite error inserting dummy data: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    insert_dummy_data()
