import sqlite3
import os

# Database path (points to backend/events.db)
DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")
print("DB dummy insert path ->", DB_PATH)

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
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

# Sample data
sample_data = [
    ("evt-001", "2025-10-30", "18:32", "kotli basheer ajk", "ISB 123", 0, "https://your-image-url.com/image1.png"),
    ("evt-002", "2025-10-30", "18:32", "kotli basheer ajk", "ISB 123", 0, "https://your-image-url.com/image2.png"),
]

# Insert data
cursor.executemany("""
INSERT OR REPLACE INTO events (id, date, time, location, number_plate, has_helmet, image_url)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", sample_data)

conn.commit()
conn.close()
print("✅ Dummy data inserted successfully!")
