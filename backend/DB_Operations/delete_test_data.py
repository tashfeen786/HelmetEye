import sqlite3
from DB_Operations.db_config import DB_PATH  # ✅ Import the database path

def delete_test_records():
    """Delete specific test records from the events table."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # List of test record IDs to delete
            test_ids = [
                'evt-41cfd7a5',
'evt-3a65899f',
'evt-c5cd8296', 
                ]

            # Delete records with these IDs
            cursor.executemany("DELETE FROM events WHERE id = ?", [(id,) for id in test_ids])

            conn.commit()  # ✅ Explicit commit (even though 'with' handles it safely)
            deleted_count = cursor.rowcount
            print(f"✅ Deleted {deleted_count} test records successfully!")

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    delete_test_records()
