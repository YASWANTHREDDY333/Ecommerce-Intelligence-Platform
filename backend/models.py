from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(32), primary_key=True)
    customer_unique_id = Column(String(32), index=True)
    customer_zip_code_prefix = Column(Integer)
    customer_city = Column(String(100))
    customer_state = Column(String(2))


class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String(32), primary_key=True)
    customer_id = Column(String(32), index=True)
    order_status = Column(String(30), index=True)
    order_purchase_timestamp = Column(DateTime, index=True)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)
    order_year = Column(Integer)
    order_month = Column(Integer)
    order_day = Column(Integer)
    order_year_month = Column(String(10))
    delivery_days = Column(Integer)
    delay_days = Column(Integer)
    delivery_status = Column(String(20))


class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_id = Column(String(32), primary_key=True)
    order_item_id = Column(Integer, primary_key=True)
    product_id = Column(String(32), index=True)
    seller_id = Column(String(32), index=True)
    shipping_limit_date = Column(DateTime)
    price = Column(Numeric(12, 2))
    freight_value = Column(Numeric(12, 2))


class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String(32), primary_key=True)
    product_category_name = Column(String(100))
    product_category_name_english = Column(String(100), index=True)
    product_name_length = Column(Integer)
    product_description_length = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Numeric(10, 2))
    product_length_cm = Column(Numeric(10, 2))
    product_height_cm = Column(Numeric(10, 2))
    product_width_cm = Column(Numeric(10, 2))


class Seller(Base):
    __tablename__ = "sellers"
    
    seller_id = Column(String(32), primary_key=True)
    seller_zip_code_prefix = Column(Integer)
    seller_city = Column(String(100))
    seller_state = Column(String(2))


class Payment(Base):
    __tablename__ = "payments"
    
    order_id = Column(String(32), primary_key=True)
    payment_sequential = Column(Integer, primary_key=True)
    payment_type = Column(String(30))
    payment_installments = Column(Integer)
    payment_value = Column(Numeric(12, 2))


class Review(Base):
    __tablename__ = "reviews"
    
    review_pk = Column(BigInteger, primary_key=True, autoincrement=True)
    review_id = Column(String(32))
    order_id = Column(String(32), index=True)
    review_score = Column(Integer)
    review_comment_title = Column(Text)
    review_comment_message = Column(Text)
    review_creation_date = Column(DateTime)
    review_answer_timestamp = Column(DateTime)


class Inventory(Base):
    __tablename__ = "inventory"
    
    product_id = Column(String(32), primary_key=True)
    current_stock = Column(Integer)
    reorder_level = Column(Integer)
    safety_stock = Column(Integer)
    average_daily_sales = Column(Numeric(10, 2))
    supplier_lead_time_days = Column(Integer)
    last_updated = Column(DateTime)


class InventoryAlert(Base):
    __tablename__ = "inventory_alerts"
    
    alert_id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(String(32), index=True)
    alert_type = Column(String(30), index=True)
    current_stock = Column(Integer)
    reorder_level = Column(Integer)
    recommended_reorder_quantity = Column(Integer)
    alert_message = Column(String(255))
    alert_status = Column(String(20), default="OPEN")


class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    
    customer_unique_id = Column(String(32), primary_key=True)
    recency_days = Column(Integer)
    frequency = Column(Integer)
    monetary = Column(Numeric(14, 2))
    cluster_id = Column(Integer)
    segment_name = Column(String(30), index=True)
    updated_at = Column(DateTime)


class Geolocation(Base):
    __tablename__ = "geolocation"
    
    geolocation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    geolocation_zip_code_prefix = Column(Integer, index=True)
    geolocation_lat = Column(Numeric(10, 7))
    geolocation_lng = Column(Numeric(10, 7))
    geolocation_city = Column(String(100))
    geolocation_state = Column(String(2))
