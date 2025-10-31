import sqlite3
import os

# Get absolute path to project root (one level above current folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "events.db")

def delete_test_records():
    """Delete specific test records from the events table"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # List of test record IDs to delete based on user's list
            test_ids = ['test-123', 'test-456', 'test-789', 'test-101', 'test-202', 'test-303', 'test-404']

            # Delete records with these IDs
            cursor.executemany("DELETE FROM events WHERE id = ?", [(id,) for id in test_ids])

            deleted_count = cursor.rowcount
            print(f"✅ Deleted {deleted_count} test records successfully!")

    except Exception as e:
        print(f"❌ Error deleting test records: {e}")
        raise

if __name__ == "__main__":
    delete_test_records()
