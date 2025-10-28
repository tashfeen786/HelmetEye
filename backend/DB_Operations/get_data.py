import sqlite3
import os

# Always use the same DB path for backend and scripts
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "events.db")  # Absolute path to project root

def get_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events ORDER BY date DESC, time DESC")
    rows = cursor.fetchall()

    response = []
    for row in rows:
        response.append({
            "id": row["id"],
            "date": row["date"],
            "time": row["time"],
            "location": row["location"],
            "numberPlate": row["number_plate"],
            "hasHelmet": bool(row["has_helmet"]),
            "imageUrl": row["image_url"]
        })

    conn.close()
    return response

if __name__ == "__main__":
    print("USING DATABASE ->", DB_PATH)
    data = get_data()
    print(data)
