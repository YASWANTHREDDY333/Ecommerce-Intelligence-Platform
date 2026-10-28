from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ==========================================================
# 1. PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ==========================================================
# 2. LOAD DATABASE SETTINGS
# ==========================================================

load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# ==========================================================
# 3. CREATE MYSQL CONNECTION
# ==========================================================

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True
)


# ==========================================================
# 4. TEST CONNECTION
# ==========================================================

print("\nTesting MySQL connection...")

with engine.connect() as connection:
    database = connection.execute(
        text("SELECT DATABASE()")
    ).scalar()

print("Connected to:", database)


# ==========================================================
# 5. CHECK EXISTING ROWS
# ==========================================================

with engine.connect() as connection:
    existing_rows = connection.execute(
        text("SELECT COUNT(*) FROM geolocation")
    ).scalar()

if existing_rows > 0:
    print(
        f"\ngeolocation already contains "
        f"{existing_rows:,} rows."
    )
    print("Skipping loading.")
    raise SystemExit


# ==========================================================
# 6. LOAD GEOLOCATION CSV
# ==========================================================

print("\nLoading geolocation CSV...")

geolocation = pd.read_csv(
    RAW_DATA_DIR / "olist_geolocation_dataset.csv"
)

print(
    "Rows found:",
    f"{len(geolocation):,}"
)


# ==========================================================
# 7. CLEAN DATA
# ==========================================================

geolocation["geolocation_city"] = (
    geolocation["geolocation_city"]
    .astype(str)
    .str.strip()
)

geolocation["geolocation_state"] = (
    geolocation["geolocation_state"]
    .astype(str)
    .str.strip()
)

geolocation = geolocation[
    [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]
]


# ==========================================================
# 8. INSERT INTO MYSQL
# ==========================================================

print("\nLoading geolocation into MySQL...")
print("This may take some time because there are over 1 million rows.")

geolocation.to_sql(
    name="geolocation",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000
)


# ==========================================================
# 9. VERIFY
# ==========================================================

with engine.connect() as connection:
    final_count = connection.execute(
        text("SELECT COUNT(*) FROM geolocation")
    ).scalar()


print("\n" + "=" * 60)
print("GEOLOCATION LOADING COMPLETED")
print("=" * 60)

print(
    "Rows in MySQL:",
    f"{final_count:,}"
)