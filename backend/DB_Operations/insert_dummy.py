import sqlite3

# Connect to SQLite database (creates file if it doesn’t exist)
conn = sqlite3.connect("events.db")
cursor = conn.cursor()

# Insert the provided values
sample_data = [
    # ("evt-007", "2024-07-28", "14:32", "Rawalpindi 6th Road", "B-123-XYZ", 1, "https://your-image-url.com/image1.png"),
   # ("evt-005", "2024-07-26", "14:31", "Main St & 1st Ave", "C-456-ABC", 0, "https://your-image-url.com/image2.png"),
    # ("evt-006", "2024-07-27", "09:17", "Oak Rd & Pine Ln", "D-101-LMN", 0, "https://your-image-url.com/image3.png"),
    # ("evt-008", "2025-09-07", "14:32", "Rawalpindi 6th Road", "B-125-XYZ", 1, "https://your-image-url.com/image1.png"),
    ("evt-009", "2025-09-07", "18:32", "Double Road", "ISB 123", 0, "https://your-image-url.com/image1.png"),

]


cursor.executemany(
    """
    INSERT OR REPLACE INTO events (id, date, time, location, number_plate, has_helmet, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    sample_data
)

# Commit and close
conn.commit()
conn.close()
