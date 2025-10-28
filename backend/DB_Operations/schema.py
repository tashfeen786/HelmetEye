import sqlite3
import os

# Shared DB path for all backend scripts
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "events.db")

print("DB schema path ->", DB_PATH)

def create_events_table():
    """Create the 'events' table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        location TEXT NOT NULL,
        number_plate TEXT NOT NULL,
        has_helmet INTEGER NOT NULL CHECK (has_helmet IN (0,1)),
        image_url TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 'events' table ensured in database.")

if __name__ == "__main__":
    create_events_table()
