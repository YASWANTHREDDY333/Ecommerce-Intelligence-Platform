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

CLEAN_DATA_DIR = BASE_DIR / "data" / "cleaned"
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
    database=DB_NAME,
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

    mysql_version = connection.execute(
        text("SELECT VERSION()")
    ).scalar()

    database_name = connection.execute(
        text("SELECT DATABASE()")
    ).scalar()


print("Connected successfully.")
print("MySQL Version:", mysql_version)
print("Database:", database_name)


# ==========================================================
# 5. LOAD CLEANED CSV FILES
# ==========================================================

print("\nLoading cleaned CSV files...")

customers = pd.read_csv(
    CLEAN_DATA_DIR / "customers_cleaned.csv"
)

products = pd.read_csv(
    CLEAN_DATA_DIR / "products_cleaned.csv"
)

sellers = pd.read_csv(
    CLEAN_DATA_DIR / "sellers_cleaned.csv"
)

orders = pd.read_csv(
    CLEAN_DATA_DIR / "orders_cleaned.csv"
)

order_items = pd.read_csv(
    CLEAN_DATA_DIR / "order_items_cleaned.csv"
)

payments = pd.read_csv(
    CLEAN_DATA_DIR / "payments_cleaned.csv"
)

reviews = pd.read_csv(
    CLEAN_DATA_DIR / "reviews_cleaned.csv"
)

print("Cleaned CSV files loaded successfully.")


# ==========================================================
# 6. PREPARE PRODUCTS
# ==========================================================

# Olist original file contains spelling mistakes:
# lenght -> length

products = products.rename(
    columns={
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length",
    }
)

products = products[
    [
        "product_id",
        "product_category_name",
        "product_category_name_english",
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
]


# ==========================================================
# 7. PREPARE ORDERS
# ==========================================================

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in order_date_columns:

    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )


orders = orders[
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "order_year",
        "order_month",
        "order_day",
        "order_year_month",
        "delivery_days",
        "delay_days",
        "delivery_status",
    ]
]


# ==========================================================
# 8. PREPARE ORDER ITEMS
# ==========================================================

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)


# ==========================================================
# 9. PREPARE REVIEWS
# ==========================================================

reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)

reviews = reviews[
    [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ]
]


# ==========================================================
# 10. TABLE ROW COUNT FUNCTION
# ==========================================================

def get_table_count(table_name):

    with engine.connect() as connection:

        count = connection.execute(
            text(
                f"SELECT COUNT(*) FROM {table_name}"
            )
        ).scalar()

    return count


# ==========================================================
# 11. SAFE INSERT FUNCTION
# ==========================================================

def insert_dataframe(
    dataframe,
    table_name,
    chunk_size=1000
):

    existing_rows = get_table_count(
        table_name
    )

    if existing_rows > 0:

        print(
            f"\n{table_name} already contains "
            f"{existing_rows:,} rows."
        )

        print(
            f"Skipping {table_name}."
        )

        return

    print(
        f"\nLoading {table_name}..."
    )

    dataframe.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=chunk_size
    )

    final_count = get_table_count(
        table_name
    )

    print(
        f"{table_name}: "
        f"{final_count:,} rows inserted successfully."
    )


# ==========================================================
# 12. INSERT TABLES
# ==========================================================

# IMPORTANT:
# Insert parent tables first because foreign keys exist.

insert_dataframe(
    customers,
    "customers"
)

insert_dataframe(
    products,
    "products"
)

insert_dataframe(
    sellers,
    "sellers"
)

insert_dataframe(
    orders,
    "orders"
)

insert_dataframe(
    order_items,
    "order_items"
)

insert_dataframe(
    payments,
    "payments"
)

insert_dataframe(
    reviews,
    "reviews"
)


# ==========================================================
# 13. VERIFY ROW COUNTS
# ==========================================================

print("\n" + "=" * 60)
print("MYSQL ROW COUNT VERIFICATION")
print("=" * 60)

tables = [
    "customers",
    "products",
    "sellers",
    "orders",
    "order_items",
    "payments",
    "reviews",
]

for table in tables:

    count = get_table_count(
        table
    )

    print(
        f"{table:<20}: {count:,}"
    )


print("\n" + "=" * 60)
print("CORE DATA LOADING COMPLETED")
print("=" * 60)