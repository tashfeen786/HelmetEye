import sqlite3
from DB_Operations.db_config import DB_PATH  # ✅ Import centralized DB path
import os


def get_data():
    """Fetch all event records from the database, sorted by date and time."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return []

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()

            print("✅ USING DATABASE ->", DB_PATH)

            cursor.execute("SELECT * FROM events ORDER BY date DESC, time DESC")
            rows = cursor.fetchall()

            response = [
                {
                    "id": row["id"],
                    "date": row["date"],
                    "time": row["time"],
                    "location": row["location"],
                    "numberPlate": row["number_plate"],
                    "hasHelmet": bool(row["has_helmet"]),
                    "imageUrl": row["image_url"],
                }
                for row in rows
            ]

            print(f"✅ Retrieved {len(response)} records.")
            return response

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []


if __name__ == "__main__":
    data = get_data()
    print(data)
