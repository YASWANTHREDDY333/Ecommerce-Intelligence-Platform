import os
import pymysql
from dotenv import load_dotenv

load_dotenv("c:/Users/yaswa/OneDrive/Documents/Ecommerce-Intelligence-Platform/.env")

conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)

cursor = conn.cursor()

indexes_to_create = [
    ("orders", "idx_orders_status", "order_status"),
    ("orders", "idx_orders_purchase_ts", "order_purchase_timestamp"),
    ("orders", "idx_orders_year_month", "order_year_month"),
    ("orders", "idx_orders_delivery_status", "delivery_status"),
    ("inventory_alerts", "idx_alerts_status_type", "alert_status, alert_type"),
    ("customer_segments", "idx_segments_name", "segment_name"),
    ("reviews", "idx_reviews_score", "review_score"),
    ("order_items", "idx_order_items_product_price", "product_id, price")
]

print("Applying performance indexes...")

for table, idx_name, cols in indexes_to_create:
    try:
        cursor.execute(f"CREATE INDEX `{idx_name}` ON `{table}` ({cols})")
        print(f"Created index {idx_name} on {table}")
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1061:  # Duplicate key name
            print(f"Index {idx_name} on {table} already exists.")
        else:
            print(f"Notice for {idx_name}: {e}")

conn.commit()
conn.close()
print("Database indexing optimization completed successfully!")
