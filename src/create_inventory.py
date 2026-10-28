from pathlib import Path
import os
import math

import numpy as np
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


print("\nTesting MySQL connection...")

with engine.connect() as connection:
    database = connection.execute(
        text("SELECT DATABASE()")
    ).scalar()

print("Connected to:", database)


# ==========================================================
# 3. CHECK IF INVENTORY ALREADY EXISTS
# ==========================================================

with engine.connect() as connection:

    inventory_count = connection.execute(
        text("SELECT COUNT(*) FROM inventory")
    ).scalar()

if inventory_count > 0:

    print(
        f"\nInventory already contains "
        f"{inventory_count:,} rows."
    )

    print("Skipping inventory generation.")

    raise SystemExit


# ==========================================================
# 4. GET ALL PRODUCTS
# ==========================================================

products = pd.read_sql(
    """
    SELECT product_id
    FROM products
    """,
    engine
)

print(
    "\nProducts found:",
    f"{len(products):,}"
)


# ==========================================================
# 5. GET HISTORICAL DELIVERED SALES
# ==========================================================

sales = pd.read_sql(
    """
    SELECT
        oi.product_id,
        o.order_purchase_timestamp
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    """,
    engine
)

sales["order_purchase_timestamp"] = pd.to_datetime(
    sales["order_purchase_timestamp"]
)


# ==========================================================
# 6. DETERMINE SALES PERIOD
# ==========================================================

start_date = sales[
    "order_purchase_timestamp"
].min()

end_date = sales[
    "order_purchase_timestamp"
].max()

sales_period_days = (
    end_date - start_date
).days + 1

print(
    "Historical sales period:",
    sales_period_days,
    "days"
)


# ==========================================================
# 7. CALCULATE PRODUCT SALES
# ==========================================================

product_sales = (
    sales
    .groupby("product_id")
    .size()
    .reset_index(
        name="units_sold"
    )
)


# ==========================================================
# 8. MERGE ALL PRODUCTS
# ==========================================================

inventory = products.merge(
    product_sales,
    on="product_id",
    how="left"
)

inventory["units_sold"] = (
    inventory["units_sold"]
    .fillna(0)
)


# ==========================================================
# 9. AVERAGE DAILY SALES
# ==========================================================

inventory[
    "average_daily_sales"
] = (
    inventory["units_sold"]
    / sales_period_days
)


# ==========================================================
# 10. SUPPLIER LEAD TIME
# ==========================================================

# Simulated supplier lead time.
# Reproducible random values are used.

rng = np.random.default_rng(42)

inventory[
    "supplier_lead_time_days"
] = rng.integers(
    3,
    11,
    size=len(inventory)
)


# ==========================================================
# 11. SAFETY STOCK
# ==========================================================

inventory["safety_stock"] = (
    inventory[
        "average_daily_sales"
    ] * 7
).apply(
    lambda value:
    max(5, math.ceil(value))
)


# ==========================================================
# 12. REORDER LEVEL
# ==========================================================

# Formula:
#
# Reorder Point =
# Average Daily Demand × Lead Time
# + Safety Stock

inventory["reorder_level"] = (
    (
        inventory[
            "average_daily_sales"
        ]
        *
        inventory[
            "supplier_lead_time_days"
        ]
    )
    +
    inventory[
        "safety_stock"
    ]
).apply(
    math.ceil
)


# ==========================================================
# 13. SIMULATE CURRENT STOCK
# ==========================================================

# Different factors deliberately create:
#
# critical stock
# low stock
# healthy stock

stock_factors = rng.choice(
    [
        0.25,
        0.50,
        0.80,
        1.00,
        1.50,
        2.00
    ],
    size=len(inventory)
)

inventory["current_stock"] = (
    inventory["reorder_level"]
    * stock_factors
).round().astype(int)


# ==========================================================
# 14. PREPARE MYSQL INVENTORY COLUMNS
# ==========================================================

inventory_mysql = inventory[
    [
        "product_id",
        "current_stock",
        "reorder_level",
        "safety_stock",
        "average_daily_sales",
        "supplier_lead_time_days"
    ]
].copy()

inventory_mysql[
    "average_daily_sales"
] = inventory_mysql[
    "average_daily_sales"
].round(2)


# ==========================================================
# 15. LOAD INVENTORY INTO MYSQL
# ==========================================================

print("\nLoading inventory into MySQL...")

inventory_mysql.to_sql(
    name="inventory",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print(
    "Inventory rows inserted:",
    f"{len(inventory_mysql):,}"
)


# ==========================================================
# 16. CREATE INVENTORY ALERTS
# ==========================================================

alerts = []

for _, row in inventory.iterrows():

    current_stock = int(
        row["current_stock"]
    )

    safety_stock = int(
        row["safety_stock"]
    )

    reorder_level = int(
        row["reorder_level"]
    )

    product_id = row[
        "product_id"
    ]


    # ------------------------------------------
    # CRITICAL
    # ------------------------------------------

    if current_stock <= safety_stock:

        alert_type = "CRITICAL"

        target_stock = (
            reorder_level * 2
        )

        reorder_quantity = max(
            0,
            target_stock
            - current_stock
        )

        message = (
            f"Critical stock. "
            f"Current stock: {current_stock}. "
            f"Reorder level: {reorder_level}."
        )


    # ------------------------------------------
    # LOW STOCK
    # ------------------------------------------

    elif current_stock <= reorder_level:

        alert_type = "LOW_STOCK"

        target_stock = (
            reorder_level * 2
        )

        reorder_quantity = max(
            0,
            target_stock
            - current_stock
        )

        message = (
            f"Low stock. "
            f"Current stock: {current_stock}. "
            f"Reorder level: {reorder_level}."
        )


    else:
        continue


    alerts.append(
        {
            "product_id":
                product_id,

            "alert_type":
                alert_type,

            "current_stock":
                current_stock,

            "reorder_level":
                reorder_level,

            "recommended_reorder_quantity":
                reorder_quantity,

            "alert_message":
                message,

            "alert_status":
                "OPEN"
        }
    )


alerts_df = pd.DataFrame(
    alerts
)


# ==========================================================
# 17. LOAD ALERTS INTO MYSQL
# ==========================================================

if not alerts_df.empty:

    print(
        "\nLoading inventory alerts..."
    )

    alerts_df.to_sql(
        name="inventory_alerts",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )

    print(
        "Alerts inserted:",
        f"{len(alerts_df):,}"
    )


# ==========================================================
# 18. FINAL VERIFICATION
# ==========================================================

with engine.connect() as connection:

    total_inventory = connection.execute(
        text(
            "SELECT COUNT(*) "
            "FROM inventory"
        )
    ).scalar()

    total_alerts = connection.execute(
        text(
            "SELECT COUNT(*) "
            "FROM inventory_alerts"
        )
    ).scalar()

    critical_alerts = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM inventory_alerts
            WHERE alert_type = 'CRITICAL'
            """
        )
    ).scalar()

    low_stock_alerts = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM inventory_alerts
            WHERE alert_type = 'LOW_STOCK'
            """
        )
    ).scalar()


print("\n" + "=" * 60)
print("INVENTORY SYSTEM CREATED")
print("=" * 60)

print(
    "Inventory Products:",
    f"{total_inventory:,}"
)

print(
    "Total Alerts:",
    f"{total_alerts:,}"
)

print(
    "Critical Alerts:",
    f"{critical_alerts:,}"
)

print(
    "Low Stock Alerts:",
    f"{low_stock_alerts:,}"
)

print("\nInventory generation completed successfully.")