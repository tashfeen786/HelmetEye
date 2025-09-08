import sqlite3

# Connect to SQLite database (creates file if it doesn’t exist)
conn = sqlite3.connect("events.db")
cursor = conn.cursor()

# Create table matching your response model
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        location TEXT NOT NULL,
        number_plate TEXT NOT NULL,
        has_helmet INTEGER NOT NULL CHECK (has_helmet IN (0,1)),
        image_url TEXT
    )
    """
)

# Commit and close
conn.commit()
conn.close()
