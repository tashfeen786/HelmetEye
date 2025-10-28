import os
from db_config import DB_PATH

print("Checking if database exists at:", DB_PATH)
print("Exists?", os.path.exists(DB_PATH))

print("DB_PATH used by FastAPI:", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "events.db")))
print("Current working directory:", os.getcwd())