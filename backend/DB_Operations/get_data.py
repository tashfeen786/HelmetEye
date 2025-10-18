import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "events.db"))

def get_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")
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
    return response

if __name__ == "__main__":
    data = get_data()
    print(data)