import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.database import check_db_connection

def open_browser():
    time.sleep(1.5)
    url = f"http://127.0.0.1:8000"
    print(f"\nOpening browser to OmniPulse Platform: {url}")
    webbrowser.open(url)

def main():
    print("=" * 70)
    print("  OMNIPULSE | E-COMMERCE INTELLIGENCE & DECISION SUPPORT PLATFORM")
    print("=" * 70)

    print("\n[1/3] Verifying Database Connection...")
    db_ok, msg = check_db_connection()
    if not db_ok:
        print(f"[ERROR] Could not connect to MySQL database '{settings.DB_NAME}': {msg}")
        print("Please check your .env configuration.")
        sys.exit(1)
    print(f"[OK] Connected to MySQL Server at {settings.DB_HOST}:{settings.DB_PORT}")

    print("\n[2/3] Initializing Application...")
    print(f"API Documentation available at: http://127.0.0.1:8000/docs")
    print(f"Interactive Dashboard at:     http://127.0.0.1:8000/")

    print("\n[3/3] Launching OmniPulse Server...")
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
