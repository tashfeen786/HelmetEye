import os
import sys

# Ensure parent directory (project root) is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DB_Operations.db_config import DB_PATH  # ✅ Import shared DB path


def test_database_path():
    """Check if database path is correctly resolved and accessible."""
    print("\n🔍 Checking database configuration...\n")

    print(f"📂 DB_PATH from db_config.py: {DB_PATH}")
    print(f"📍 Absolute DB_PATH: {os.path.abspath(DB_PATH)}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"✅ Database exists: {os.path.exists(DB_PATH)}")

    # For reference, what FastAPI (or main app) might use
    fastapi_db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "events.db")
    )
    print(f"⚙️  DB_PATH as resolved by FastAPI: {fastapi_db_path}")

    if DB_PATH != fastapi_db_path:
        print("⚠️  Note: DB_PATH differs from FastAPI's expected path — check imports or relative paths.")
    else:
        print("✅  DB_PATH matches FastAPI's expected location.")


if __name__ == "__main__":
    test_database_path()
