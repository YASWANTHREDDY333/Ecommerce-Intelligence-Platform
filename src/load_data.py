from pathlib import Path
import pandas as pd


# ==========================================================
# 1. PROJECT PATHS
# ==========================================================

# Main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw dataset directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

# Cleaned dataset directory
CLEAN_DATA_DIR = BASE_DIR / "data" / "cleaned"

# Processed dataset directory
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Create folders automatically if they do not exist
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. FUNCTION TO LOAD CSV FILE
# ==========================================================

def load_csv(filename):
    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return pd.read_csv(file_path)


# ==========================================================
# 3. LOAD ALL OLIST DATASETS
# ==========================================================

print("\nLoading datasets...")

customers = load_csv(
    "olist_customers_dataset.csv"
)

geolocation = load_csv(
    "olist_geolocation_dataset.csv"
)

order_items = load_csv(
    "olist_order_items_dataset.csv"
)

payments = load_csv(
    "olist_order_payments_dataset.csv"
)

reviews = load_csv(
    "olist_order_reviews_dataset.csv"
)

orders = load_csv(
    "olist_orders_dataset.csv"
)

products = load_csv(
    "olist_products_dataset.csv"
)

sellers = load_csv(
    "olist_sellers_dataset.csv"
)

category_translation = load_csv(
    "product_category_name_translation.csv"
)

print("All datasets loaded successfully.")


# ==========================================================
# 4. STORE DATASETS IN DICTIONARY
# ==========================================================

datasets = {
    "Customers": customers,
    "Geolocation": geolocation,
    "Order Items": order_items,
    "Payments": payments,
    "Reviews": reviews,
    "Orders": orders,
    "Products": products,
    "Sellers": sellers,
    "Category Translation": category_translation,
}


# ==========================================================
# 5. BASIC DATASET OVERVIEW
# ==========================================================

print("\n" + "=" * 70)
print("DATASET OVERVIEW")
print("=" * 70)

for name, dataframe in datasets.items():

    print(
        f"{name:<25}"
        f"Rows: {dataframe.shape[0]:<10}"
        f"Columns: {dataframe.shape[1]}"
    )


# ==========================================================
# 6. BASIC STRING CLEANING
# ==========================================================

# Remove unnecessary spaces from string columns

for dataframe in datasets.values():

    string_columns = dataframe.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in string_columns:
        dataframe[column] = dataframe[column].str.strip()


# ==========================================================
# 7. CUSTOMER DATA QUALITY
# ==========================================================

print("\n" + "=" * 70)
print("CUSTOMERS DATASET")
print("=" * 70)

print("Shape:")
print(customers.shape)

print("\nColumns:")
print(customers.columns.tolist())

print("\nMissing Values:")
print(customers.isnull().sum())

print("\nDuplicate Rows:")
print(customers.duplicated().sum())

print("\nUnique Customer IDs:")
print(customers["customer_id"].nunique())

print("\nUnique Real Customers:")
print(customers["customer_unique_id"].nunique())


# ==========================================================
# 8. ORDERS DATA QUALITY
# ==========================================================

print("\n" + "=" * 70)
print("ORDERS DATASET")
print("=" * 70)

print("Shape:")
print(orders.shape)

print("\nMissing Values:")
print(orders.isnull().sum())

print("\nDuplicate Rows:")
print(orders.duplicated().sum())

print("\nOrder Status Counts:")
print(
    orders["order_status"]
    .value_counts()
)


# ==========================================================
# 9. CONVERT ORDER DATE COLUMNS
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


# ==========================================================
# 10. CONVERT ORDER ITEMS DATE
# ==========================================================

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)


# ==========================================================
# 11. CONVERT REVIEW DATES
# ==========================================================

reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)


# ==========================================================
# 12. CREATE ORDER TIME FEATURES
# ==========================================================

orders["order_year"] = (
    orders["order_purchase_timestamp"].dt.year
)

orders["order_month"] = (
    orders["order_purchase_timestamp"].dt.month
)

orders["order_day"] = (
    orders["order_purchase_timestamp"].dt.day
)

orders["order_year_month"] = (
    orders["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


# ==========================================================
# 13. CALCULATE DELIVERY DAYS
# ==========================================================

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.days


# ==========================================================
# 14. CALCULATE DELIVERY DELAY
# ==========================================================

orders["delay_days"] = (
    orders["order_delivered_customer_date"].dt.normalize()
    - orders["order_estimated_delivery_date"].dt.normalize()
).dt.days


# ==========================================================
# 15. CREATE DELIVERY STATUS
# ==========================================================

orders["delivery_status"] = "Not Delivered"

orders.loc[
    orders["delay_days"] < 0,
    "delivery_status"
] = "Early"

orders.loc[
    orders["delay_days"] == 0,
    "delivery_status"
] = "On Time"

orders.loc[
    orders["delay_days"] > 0,
    "delivery_status"
] = "Late"


print("\nDelivery Status Counts:")

print(
    orders["delivery_status"]
    .value_counts()
)


# ==========================================================
# 16. DELIVERY KPIs
# ==========================================================

delivered_with_date = orders[
    orders["order_delivered_customer_date"].notna()
].copy()

total_delivered_with_date = len(
    delivered_with_date
)

early_deliveries = (
    delivered_with_date["delivery_status"]
    == "Early"
).sum()

on_time_deliveries = (
    delivered_with_date["delivery_status"]
    == "On Time"
).sum()

late_deliveries = (
    delivered_with_date["delivery_status"]
    == "Late"
).sum()


early_percentage = (
    early_deliveries
    / total_delivered_with_date
) * 100

on_time_percentage = (
    on_time_deliveries
    / total_delivered_with_date
) * 100

late_percentage = (
    late_deliveries
    / total_delivered_with_date
) * 100

on_or_before_percentage = (
    (
        early_deliveries
        + on_time_deliveries
    )
    / total_delivered_with_date
) * 100


print("\n" + "=" * 70)
print("DELIVERY KPIs")
print("=" * 70)

print(
    "Orders with Delivery Date:",
    total_delivered_with_date
)

print(
    "Average Delivery Days:",
    round(
        delivered_with_date[
            "delivery_days"
        ].mean(),
        2
    )
)

print(
    "Early Delivery Percentage:",
    round(early_percentage, 2),
    "%"
)

print(
    "On-Time Delivery Percentage:",
    round(on_time_percentage, 2),
    "%"
)

print(
    "Late Delivery Percentage:",
    round(late_percentage, 2),
    "%"
)

print(
    "Delivered On/Before Estimate:",
    round(on_or_before_percentage, 2),
    "%"
)


# ==========================================================
# 17. ORDER ITEMS DATA QUALITY
# ==========================================================

print("\n" + "=" * 70)
print("ORDER ITEMS DATASET")
print("=" * 70)

print("Shape:")
print(order_items.shape)

print("\nMissing Values:")
print(order_items.isnull().sum())

print("\nDuplicate Rows:")
print(order_items.duplicated().sum())

print(
    "\nUnique Orders:",
    order_items["order_id"].nunique()
)

print(
    "Unique Products:",
    order_items["product_id"].nunique()
)

print(
    "Unique Sellers:",
    order_items["seller_id"].nunique()
)


# ==========================================================
# 18. BASIC ORDER ITEM KPIs
# ==========================================================

gross_item_value = (
    order_items["price"].sum()
)

total_freight_value = (
    order_items["freight_value"].sum()
)

average_item_price = (
    order_items["price"].mean()
)

total_item_rows = len(
    order_items
)


print("\n" + "=" * 70)
print("ORDER ITEM KPIs")
print("=" * 70)

print(
    "Gross Item Value (all order items):",
    round(gross_item_value, 2)
)

print(
    "Total Freight Value:",
    round(total_freight_value, 2)
)

print(
    "Average Item Price:",
    round(average_item_price, 2)
)

print(
    "Total Order Item Rows:",
    total_item_rows
)


# ==========================================================
# 19. CLEAN PRODUCT CATEGORY NAMES
# ==========================================================

products["product_category_name"] = (
    products["product_category_name"]
    .fillna("unknown")
)

products = products.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

products[
    "product_category_name_english"
] = (
    products[
        "product_category_name_english"
    ]
    .fillna("unknown")
)


# ==========================================================
# 20. PRODUCT DATA QUALITY
# ==========================================================

print("\n" + "=" * 70)
print("PRODUCTS DATASET")
print("=" * 70)

print("Shape:")
print(products.shape)

print("\nMissing Values:")
print(products.isnull().sum())

print(
    "\nUnique Products:",
    products["product_id"].nunique()
)


# ==========================================================
# 21. MERGE ORDER ITEMS WITH ORDERS
# ==========================================================

sales_data = order_items.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_year",
            "order_month",
            "order_year_month",
            "delivery_status",
        ]
    ],
    on="order_id",
    how="left"
)


# ==========================================================
# 22. MERGE SALES WITH PRODUCTS
# ==========================================================

sales_data = sales_data.merge(
    products[
        [
            "product_id",
            "product_category_name",
            "product_category_name_english",
        ]
    ],
    on="product_id",
    how="left"
)


# ==========================================================
# 23. CREATE ITEM TOTAL
# ==========================================================

sales_data["item_total_with_freight"] = (
    sales_data["price"]
    + sales_data["freight_value"]
)


# ==========================================================
# 24. FILTER DELIVERED SALES
# ==========================================================

delivered_sales = sales_data[
    sales_data["order_status"] == "delivered"
].copy()


# ==========================================================
# 25. SALES KPIs
# ==========================================================

delivered_product_revenue = (
    delivered_sales["price"].sum()
)

delivered_freight = (
    delivered_sales[
        "freight_value"
    ].sum()
)

delivered_total_value = (
    delivered_sales[
        "item_total_with_freight"
    ].sum()
)

average_delivered_item_price = (
    delivered_sales["price"].mean()
)


print("\n" + "=" * 70)
print("DELIVERED SALES KPIs")
print("=" * 70)

print(
    "Delivered Product Revenue:",
    round(
        delivered_product_revenue,
        2
    )
)

print(
    "Delivered Freight Value:",
    round(
        delivered_freight,
        2
    )
)

print(
    "Delivered Total Value Including Freight:",
    round(
        delivered_total_value,
        2
    )
)

print(
    "Average Delivered Item Price:",
    round(
        average_delivered_item_price,
        2
    )
)


# ==========================================================
# 26. TOP 10 PRODUCT CATEGORIES
# ==========================================================

top_categories = (
    delivered_sales
    .groupby(
        "product_category_name_english",
        dropna=False
    )
    .agg(
        revenue=("price", "sum"),
        items_sold=("product_id", "count")
    )
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(10)
)


print("\n" + "=" * 70)
print("TOP 10 PRODUCT CATEGORIES")
print("=" * 70)

print(
    top_categories.round(2)
)


# ==========================================================
# 27. TOP 10 PRODUCTS BY REVENUE
# ==========================================================

top_products = (
    delivered_sales
    .groupby("product_id")
    .agg(
        revenue=("price", "sum"),
        items_sold=("product_id", "count")
    )
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(10)
)


print("\n" + "=" * 70)
print("TOP 10 PRODUCTS BY REVENUE")
print("=" * 70)

print(
    top_products.round(2)
)


# ==========================================================
# 28. CUSTOMER + ORDER MERGE
# ==========================================================

customer_orders = orders.merge(
    customers,
    on="customer_id",
    how="left"
)


# ==========================================================
# 29. ORDERS BY CUSTOMER STATE
# ==========================================================

orders_by_state = (
    customer_orders
    .groupby("customer_state")
    .size()
    .sort_values(
        ascending=False
    )
)


print("\n" + "=" * 70)
print("TOP 10 STATES BY ORDERS")
print("=" * 70)

print(
    orders_by_state.head(10)
)


# ==========================================================
# 30. PAYMENT DATA QUALITY
# ==========================================================

print("\n" + "=" * 70)
print("PAYMENT METHODS")
print("=" * 70)

print(
    payments["payment_type"]
    .value_counts()
)


# ==========================================================
# 31. REVIEW DATA
# ==========================================================

print("\n" + "=" * 70)
print("REVIEW SCORE DISTRIBUTION")
print("=" * 70)

print(
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

print(
    "\nAverage Review Score:",
    round(
        reviews[
            "review_score"
        ].mean(),
        2
    )
)


# ==========================================================
# 32. SAVE CLEANED DATASETS
# ==========================================================

customers.to_csv(
    CLEAN_DATA_DIR
    / "customers_cleaned.csv",
    index=False
)

orders.to_csv(
    CLEAN_DATA_DIR
    / "orders_cleaned.csv",
    index=False
)

order_items.to_csv(
    CLEAN_DATA_DIR
    / "order_items_cleaned.csv",
    index=False
)

products.to_csv(
    CLEAN_DATA_DIR
    / "products_cleaned.csv",
    index=False
)

payments.to_csv(
    CLEAN_DATA_DIR
    / "payments_cleaned.csv",
    index=False
)

reviews.to_csv(
    CLEAN_DATA_DIR
    / "reviews_cleaned.csv",
    index=False
)

sellers.to_csv(
    CLEAN_DATA_DIR
    / "sellers_cleaned.csv",
    index=False
)


# ==========================================================
# 33. SAVE PROCESSED SALES DATA
# ==========================================================

sales_data.to_csv(
    PROCESSED_DATA_DIR
    / "sales_data.csv",
    index=False
)


# ==========================================================
# 34. FINAL MESSAGE
# ==========================================================

print("\n" + "=" * 70)

print(
    "STAGE 1 DATA PREPARATION COMPLETED SUCCESSFULLY"
)

print("=" * 70)

print(
    "\nCleaned files saved to:"
)

print(
    CLEAN_DATA_DIR
)

print(
    "\nProcessed sales data saved to:"
)

print(
    PROCESSED_DATA_DIR
)