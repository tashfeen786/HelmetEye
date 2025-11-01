# DB_Operations/db_config.py
import os

# Always point to the backend root directory (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "events.db")

print(f"✅ USING DATABASE -> {DB_PATH}")
