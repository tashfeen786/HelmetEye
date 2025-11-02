import sys, os
import sqlite3

# Add parent directory to Python's import path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from DB_Operations.db_config import DB_PATH  # ✅ Import the database path

def print_ids_with_live_feed():
    """Print IDs where the location field contains a live camera feed."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Adjust this query based on your data
            cursor.execute("""
                SELECT id, number_plate FROM events
                WHERE number_plate LIKE '%UNKNOWN%'
            """)
            rows = cursor.fetchall()

            if rows:
                print("✅ Event IDs with live camera feeds:")
                for row in rows:
                    print(f"{row[0]} → {row[1]}")
                print(f"\nTotal: {len(rows)} records found.")
            else:
                print("⚠️ No records found with live camera feed info.")

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    print_ids_with_live_feed()
