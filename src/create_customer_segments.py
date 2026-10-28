from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ==========================================================
# 1. PROJECT SETTINGS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# ==========================================================
# 2. MYSQL CONNECTION
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

print("\nTesting MySQL connection for RFM segmentation...")

with engine.connect() as connection:
    database = connection.execute(
        text("SELECT DATABASE()")
    ).scalar()

print("Connected to:", database)


# ==========================================================
# 3. CHECK IF CUSTOMER SEGMENTS ALREADY EXIST
# ==========================================================

with engine.connect() as connection:
    segment_count = connection.execute(
        text("SELECT COUNT(*) FROM customer_segments")
    ).scalar()

if segment_count > 0:
    print(
        f"\ncustomer_segments already contains "
        f"{segment_count:,} rows."
    )
    print("Skipping segmentation generation.")
    raise SystemExit


# ==========================================================
# 4. LOAD DELIVERED ORDERS WITH CUSTOMERS & ITEMS
# ==========================================================

print("\nFetching delivered order transactions...")

query = """
SELECT 
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp,
    oi.price,
    oi.freight_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp IS NOT NULL
"""

df = pd.read_sql(query, engine)
print(f"Transactions loaded: {len(df):,} rows.")

df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["total_value"] = df["price"] + df["freight_value"]

# Reference date for recency calculation (day after latest purchase in dataset)
reference_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
print(f"Analysis Reference Date: {reference_date}")


# ==========================================================
# 5. CALCULATE RFM METRICS PER CUSTOMER
# ==========================================================

print("\nComputing RFM metrics (Recency, Frequency, Monetary)...")

rfm = df.groupby("customer_unique_id").agg(
    last_order_date=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("total_value", "sum")
).reset_index()

rfm["recency_days"] = (reference_date - rfm["last_order_date"]).dt.days
rfm["monetary"] = rfm["monetary"].round(2)


# ==========================================================
# 6. ASSIGN RFM SEGMENTS AND CLUSTERS
# ==========================================================

# Quantile benchmarks
r_median = rfm["recency_days"].median()
m_75th = rfm["monetary"].quantile(0.75)
m_90th = rfm["monetary"].quantile(0.90)

def assign_segment(row):
    if row["monetary"] >= m_90th:
        return 3, "High Value"
    elif row["frequency"] > 1 or (row["recency_days"] <= r_median and row["monetary"] >= m_75th):
        return 0, "Loyal"
    elif row["recency_days"] <= r_median:
        return 2, "Regular"
    else:
        return 1, "At Risk"

results = [assign_segment(row) for _, row in rfm.iterrows()]
rfm["cluster_id"] = [r[0] for r in results]
rfm["segment_name"] = [r[1] for r in results]

segments_mysql = rfm[
    [
        "customer_unique_id",
        "recency_days",
        "frequency",
        "monetary",
        "cluster_id",
        "segment_name"
    ]
].copy()


# ==========================================================
# 7. LOAD SEGMENTS INTO MYSQL
# ==========================================================

print("\nLoading customer segments into MySQL...")

segments_mysql.to_sql(
    name="customer_segments",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000
)

print(f"Customer segments inserted: {len(segments_mysql):,}")


# ==========================================================
# 8. VERIFICATION
# ==========================================================

with engine.connect() as connection:
    total = connection.execute(
        text("SELECT COUNT(*) FROM customer_segments")
    ).scalar()

print("\n" + "=" * 60)
print("CUSTOMER SEGMENTATION COMPLETED")
print("=" * 60)
print(f"Total Segmented Customers in MySQL: {total:,}")
