import sqlite3
import os

# Shared database path for the entire project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "events.db")

print("DB dummy insert path ->", DB_PATH)

# Connect to SQLite database (creates file if it doesn’t exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Insert sample data
sample_data = [
    ("evt-0011", "2025-10-30", "18:32", "kotli basheer ajk", "ISB 123", 0, "https://your-image-url.com/image1.png"),
]

cursor.executemany(
    """
    INSERT OR REPLACE INTO events (id, date, time, location, number_plate, has_helmet, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    sample_data
)

conn.commit()
conn.close()
print("✅ Dummy data inserted successfully!")
