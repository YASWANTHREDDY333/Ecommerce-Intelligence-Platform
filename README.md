# OmniPulse — E-Commerce Intelligence & Decision Support Platform

![Platform Architecture](https://img.shields.io/badge/Architecture-Fullstack_Intelligence-6366f1?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/Database-MySQL_8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Chart.js](https://img.shields.io/badge/Frontend-Chart.js_Glassmorphism-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)

OmniPulse is an enterprise-grade **E-Commerce Intelligence Platform** built on the comprehensive Brazilian E-Commerce dataset (Olist). It bridges the gap between raw transactional data and strategic decision-making, providing real-time executive visibility into sales velocity, inventory stockout risks, RFM customer segmentation, logistics SLAs, customer CSAT, and prescriptive AI recommendations.

---

## 🌟 Key Features & Modules

### 1. 📊 Executive Overview Dashboard
- **Top-Tier KPIs**: Delivered Revenue ($13.59M), Delivered Orders (96,478), Unique Customers (93,358), and On-Time Delivery Rate (92.4%).
- **Operational Metrics**: Average Order Value ($137.05), Average Shipping Days (12.5 days), Review CSAT (4.09/5), and Active Stock Alerts.
- **Sales Velocity Timeline**: Multi-axis interactive visualization comparing monthly delivered sales revenue ($) against order volumes.
- **Delivery SLA Breakdown**: Real-time early, on-time, and delayed order distribution.

### 2. 💰 Sales & Category Intelligence
- **Category Benchmarking**: Top 10 product categories ranked by revenue, items sold, and average price.
- **Payment Method Distribution**: Credit card, boleto, voucher, and debit card volume share.
- **Top SKU Rankings**: Top revenue-generating products with integrated live stock status badges.

### 3. 👥 Customer RFM Segmentation & Behavior
- **Data-Driven Clustering**: Recency, Frequency, and Monetary (RFM) clustering across 93,358 unique customers.
- **Segment Profiles**:
  - **Loyal (37,747 customers)**: Repeat buyers or recent spenders driving consistent recurring volume.
  - **High Value (2,801 customers)**: Top 10th-percentile monetary spenders ($3.5M+ total spend).
  - **Regular (16,106 customers)**: Active standard-spend customers.
  - **At Risk (36,704 customers)**: Dormant customers holding $5.1M in historical transaction value.
- **Geographic Revenue Distribution**: State-level sales and customer concentration across all 27 Brazilian states.

### 4. 📦 Smart Inventory & Stock Alert Center
- **Automated Reorder Point Calculation**: Based on historical sales velocity, supplier lead time, and dynamic safety stock formulas.
- **Real-Time Stock Alerts**: Categorized into `CRITICAL` (current stock &le; safety stock) and `LOW_STOCK` (current stock &le; reorder point).
- **Interactive Restock & Alert Action**:
  - One-click alert acknowledgment.
  - Instant SKU replenishment with automatic alert resolution and database synchronization.
- **Catalog SKU Explorer**: Real-time search and stock status filtering across 32,951 tracked SKUs.

### 5. 🚚 Logistics & Fulfillment SLA Analytics
- **Delivery Performance**: Tracking early (88.5%), on-time (3.9%), and late (7.6%) shipments.
- **State Transit Duration Matrix**: Average transit days and late delivery rates by destination state, flagging regional bottlenecks (e.g. AP, RR, AM vs SP, PR).

### 6. ⭐ Reviews & Customer CSAT Analysis
- **Rating Distribution**: 1-Star to 5-Star score breakdown across 99,224 verified customer reviews.
- **Delay-to-Rating Correlation**: Quantifiable evidence showing ratings drop from 4.2 stars for on-time delivery down to 2.3 stars for late deliveries.

### 7. 🤖 AI Intelligence & Prescriptive Engine
- **Stockout Exposure Warnings**: Quantifies revenue at risk due to critical stock shortages.
- **Churn Win-Back Opportunities**: Identifies dormant customer cohorts and calculates recoverable lifetime value.
- **Actionable Strategic Steps**: Clear operational recommendations with direct action deployment triggers.

---

## 🏗️ Architecture & Project Structure

```
Ecommerce-Intelligence-Platform/
├── backend/
│   ├── routers/
│   │   ├── ai_insights.py       # AI prescriptive recommendations API
│   │   ├── customers.py         # Customer RFM segmentation API
│   │   ├── inventory.py         # Inventory items, alerts, and restock API
│   │   ├── logistics.py         # Delivery SLA and shipping analytics API
│   │   ├── overview.py          # Executive KPIs and high-level summaries API
│   │   ├── reviews.py           # Customer review CSAT and delay correlation API
│   │   └── sales.py             # Sales trends, top categories, and payments API
│   ├── services/
│   │   ├── ai_insights_service.py # Dynamic intelligence logic
│   │   ├── analytics_service.py   # Aggregated analytics with TTL caching
│   │   └── inventory_service.py   # Inventory management logic
│   ├── static/
│   │   ├── css/style.css        # Premium dark glassmorphism stylesheet
│   │   ├── js/app.js            # Frontend controller and Chart.js integration
│   │   └── index.html           # Single-page intelligence dashboard
│   ├── config.py                # Environment configuration & URL generation
│   ├── database.py              # SQLAlchemy connection pool and session factory
│   ├── main.py                  # FastAPI application entry point
│   ├── models.py                # SQLAlchemy ORM database models
│   └── schemas.py               # Pydantic data schemas
├── data/
│   ├── raw/                     # Original Olist CSV datasets
│   ├── cleaned/                 # Cleaned and normalized CSV datasets
│   └── processed/               # Enriched sales and transaction tables
├── src/
│   ├── create_customer_segments.py # RFM segmentation generation pipeline
│   ├── create_inventory.py         # Inventory safety stock & alert generator
│   ├── load_data.py                # Raw dataset ingestion and data cleaning
│   ├── load_geolocation.py         # Geolocation dataset ingestion
│   ├── load_to_mysql.py            # MySQL database table loader
│   └── optimize_database.py        # Database index optimization script
├── tests/
│   └── test_api.py              # Automated test suite for all endpoints
├── .env                         # Database credentials and configuration
├── requirements.txt             # Project Python dependencies
└── run_platform.py              # One-click startup runner
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: 3.10 or higher
- **MySQL Server**: 8.0 or higher
- Standard web browser (Chrome, Edge, Firefox, Safari)

### 2. Environment Configuration
Verify or update the database credentials in `.env`:
```env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_intelligence
```

### 3. Install Dependencies
Activate your virtual environment and install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Index Optimization
If running from scratch, execute the ingestion pipeline:
```bash
# 1. Clean raw data
python src/load_data.py

# 2. Ingest into MySQL
python src/load_to_mysql.py
python src/load_geolocation.py

# 3. Generate Inventory & Stock Alerts
python src/create_inventory.py

# 4. Generate RFM Customer Segments
python src/create_customer_segments.py

# 5. Apply Performance Indexes
python src/optimize_database.py
```

### 5. Launch the Platform
Start the OmniPulse platform with the one-click runner:
```bash
python run_platform.py
```
This automatically verifies database connectivity, starts the FastAPI server at `http://127.0.0.1:8000`, and launches the interactive dashboard in your default browser.

Or run directly via Uvicorn:
```bash
uvicorn backend.main:app --reload
```

---

## 📡 REST API Documentation

The platform includes full interactive OpenAPI / Swagger documentation accessible at:
👉 **`http://127.0.0.1:8000/docs`**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System and MySQL database connectivity status |
| `GET` | `/api/overview` | Executive overview KPIs and delivery summary |
| `GET` | `/api/sales/monthly` | Historical monthly delivered revenue and order counts |
| `GET` | `/api/sales/categories` | Top product categories ranked by revenue |
| `GET` | `/api/sales/top-products` | Top revenue-generating SKUs with stock status |
| `GET` | `/api/sales/payments` | Payment methods distribution and total values |
| `GET` | `/api/customers/segments` | RFM customer segmentation counts, metrics, and spend |
| `GET` | `/api/customers/geography` | Customer and revenue breakdown by Brazilian state |
| `GET` | `/api/inventory/summary` | Inventory health counts (Critical, Low, Healthy) |
| `GET` | `/api/inventory/alerts` | Filterable list of stock alerts with pagination |
| `GET` | `/api/inventory/items` | Full SKU inventory catalog with search and filters |
| `PATCH` | `/api/inventory/alerts/{id}/status` | Update alert status (`ACKNOWLEDGED`, `RESOLVED`) |
| `POST` | `/api/inventory/restock` | Replenish inventory stock and resolve related alert |
| `GET` | `/api/logistics/summary` | Overall logistics delivery SLA and delay metrics |
| `GET` | `/api/logistics/by-state` | Destination state transit duration and delay analysis |
| `GET` | `/api/reviews/summary` | Review score ratings distribution and delay correlation |
| `GET` | `/api/ai-insights` | Autonomous prescriptive business recommendations |

---

## 🧪 Testing & Verification

Run the automated integration test suite to verify all endpoints and query latency:
```bash
python tests/test_api.py
```

Expected output:
```text
============================================================
RUNNING OMNIPULSE API INTEGRATION TESTS
============================================================
[PASS] Health Check                   |  106.0ms | /health (keys=3)
[PASS] Executive Overview KPIs        |  3460.0ms| /api/overview (keys=13)
[PASS] Monthly Revenue Trend          |  1663.1ms| /api/sales/monthly (items=20)
[PASS] Top Categories                 |  1612.7ms| /api/sales/categories?limit=5 (items=5)
[PASS] Top Products                   |  4894.1ms| /api/sales/top-products?limit=5 (items=5)
[PASS] Payment Breakdown              |   630.7ms| /api/sales/payments (items=5)
[PASS] Customer RFM Segments          |  1037.6ms| /api/customers/segments (items=4)
[PASS] Geographic Distribution        |  4088.9ms| /api/customers/geography (items=27)
[PASS] Inventory Summary              |    57.8ms| /api/inventory/summary (keys=5)
[PASS] Inventory Alerts               |   171.7ms| /api/inventory/alerts?limit=5 (keys=4)
[PASS] Inventory Items                |   156.8ms| /api/inventory/items?limit=5 (keys=4)
[PASS] Logistics Delivery Summary     |  1075.4ms| /api/logistics/summary (keys=10)
[PASS] Logistics by State             |     6.0ms| /api/logistics/by-state (items=27)
[PASS] Review Analytics               |  2324.2ms| /api/reviews/summary (keys=5)
[PASS] AI Operational Insights        |  3534.6ms| /api/ai-insights (items=5)
============================================================
ALL ENDPOINT TESTS PASSED SUCCESSFULLY!
============================================================
```

---

## 📄 License
This project is licensed under the MIT License.
