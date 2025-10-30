import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DB_Operations.db_config import DB_PATH  #Import shared DB path

print("Checking if database exists at:", DB_PATH)
print("Exists?", os.path.exists(DB_PATH))

print("DB_PATH used by FastAPI:", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "events.db")))
print("Current working directory:", os.getcwd())