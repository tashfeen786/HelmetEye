import sqlite3
import os
from DB_Operations.db_config import DB_PATH  # ✅ Import shared DB path


def create_events_table():
    """Create the 'events' table if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database file not found at {DB_PATH}. A new one will be created automatically.")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    location TEXT NOT NULL,
                    number_plate TEXT NOT NULL,
                    has_helmet INTEGER NOT NULL CHECK (has_helmet IN (0, 1)),
                    image_url TEXT
                )
            """)

            conn.commit()
            print("✅ 'events' table is ready in the database.")

    except sqlite3.Error as e:
        print(f"❌ SQLite error creating table: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    print("📂 Database schema path ->", DB_PATH)
    create_events_table()
