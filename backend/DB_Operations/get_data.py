import sqlite3
import os

from DB_Operations.db_config import DB_PATH  #Import shared DB path


def get_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    print("USING DATABASE ->", DB_PATH)
    print("Exists:", os.path.exists(DB_PATH))

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
