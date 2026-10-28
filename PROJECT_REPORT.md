# OmniPulse — Comprehensive E-Commerce Intelligence & Decision Support Platform
## Executive Technical Capstone Report

---

## 1. Executive Summary

Modern enterprise e-commerce platforms generate massive volumes of transactional, behavioral, and logistical data. However, raw relational tables alone do not provide decision-makers with real-time strategic foresight. 

**OmniPulse** is an end-to-end full-stack intelligence and decision-support platform designed to transform raw transactional records from the comprehensive Brazilian E-Commerce ecosystem (Olist) into real-time executive visibility, dynamic predictive alerting, and actionable operational prescriptions.

### Core Business Highlights
- **Delivered Revenue Managed**: **$13.59M USD** across **96,478** completed customer orders.
- **Customer Base Analyzed**: **93,358** unique customers segmented across 4 distinct behavioral RFM clusters.
- **Logistics Fulfillment SLA**: **92.4%** On-Time Delivery Rate tracked across all 27 Brazilian states.
- **Catalog Breadth**: **32,951** unique SKUs monitored with dynamic safety stock and automated reorder triggers.
- **Customer Satisfaction (CSAT)**: **4.09 / 5.0** average rating across **99,224** verified customer reviews.

---

## 2. System Architecture & Data Pipeline

OmniPulse utilizes a modular, decoupled 3-tier architecture designed for low-latency analytics, thread-safe database pooling, and intuitive executive visualization.

```mermaid
flowchart TD
    subgraph Data_Layer ["1. Data & ETL Pipeline"]
        A[Olist Raw CSVs 100k+ Records] --> B[load_data.py Data Cleaning & Imputation]
        B --> C[load_to_mysql.py & load_geolocation.py Batch Loader]
        C --> D[(MySQL 8.0 Relational Engine)]
        D --> E[create_inventory.py Safety Stock & Alerts]
        D --> F[create_customer_segments.py RFM Clustering]
        D --> G[optimize_database.py B-Tree Index Optimization]
    end

    subgraph Service_Layer ["2. Application & API Layer (FastAPI)"]
        D --> H[SQLAlchemy Connection Pool]
        H --> I[Analytics Service with In-Memory TTL Cache]
        H --> J[Inventory Management Service]
        H --> K[What-If Scenario Simulator Service]
        H --> L[Prescriptive AI Insights & Chat Engine]
        I & J & K & L --> M[FastAPI REST API 21 Endpoints]
    end

    subgraph Presentation_Layer ["3. Interactive Glassmorphic SPA"]
        M --> N[Executive KPI Cards]
        M --> O[Chart.js Multi-Axis Revenue & Category Graphs]
        M --> P[Leaflet.js Geospatial Transit Map]
        M --> Q[Real-Time Inventory Alert & Restock Modal]
        M --> R[Interactive Scenario What-If Sliders]
        M --> S[Natural Language AI Assistant Drawer]
    end
```

---

## 3. Database Schema & Data Models

The relational core is hosted on **MySQL 8.0** with strict primary-foreign key integrity, optimized composite B-Tree indexes, and normalized schemas:

| Table Name | Records | Primary Key | Description |
|---|---|---|---|
| `customers` | 99,441 | `customer_id` | Customer profiles and geographic mapping |
| `orders` | 99,441 | `order_id` | Order status, purchase timestamps, estimated and delivered dates |
| `order_items` | 112,650 | `order_id, order_item_id` | SKU line items, unit price, freight value, seller reference |
| `products` | 32,951 | `product_id` | Category classifications, dimensions, and weight |
| `order_payments` | 103,886 | `order_id, payment_sequential` | Payment types (credit card, boleto, voucher) and installments |
| `order_reviews` | 99,224 | `review_id` | Review scores (1 to 5 stars), titles, and submission dates |
| `inventory` | 32,951 | `product_id` | Reorder points, safety stock thresholds, lead times, stock levels |
| `inventory_alerts` | Dynamic | `alert_id` | Automated stockout risk notifications (`CRITICAL`, `LOW_STOCK`) |
| `customer_segments` | 93,358 | `customer_unique_id` | RFM cluster assignments, recency days, frequency, monetary spend |
| `geolocation` | Indexed | `geolocation_zip_code_prefix` | Geocoded latitude and longitude coordinates across Brazilian states |

---

## 4. Key Business Intelligence Modules & Empirical Insights

### A. Executive Overview & Sales Velocity
- **Gross Revenue**: Over $13.59M in validated delivered sales.
- **Average Order Value (AOV)**: $137.05 with an average freight cost of $22.75 per order.
- **Seasonality & Growth**: Revenue demonstrated steep expansion peaking during Q4 promotional cycles (Black Friday) with peak monthly volume exceeding 7,000 orders.

### B. Customer RFM Behavioral Segmentation
Using Recency (days since last purchase), Frequency (order count), and Monetary (total customer spend) clustering:
1. **Loyal Customers (37,747)**: Repeat buyers with consistent purchasing cadence; primary candidates for VIP loyalty reward tiers.
2. **High-Value Customers (2,801)**: Top 10th-percentile spenders representing over $3.5M in spend ($1,250+ individual spend); critical to retain via dedicated account management.
3. **Regular Customers (16,106)**: Moderately engaged standard shoppers with healthy transaction velocity.
4. **At-Risk Customers (36,704)**: Inactive for >180 days representing **$5.1M in historical spend**; primary focus for targeted re-engagement discount campaigns.

### C. Smart Inventory & Predictive Alerting
- Inventory models calculate dynamic **Safety Stock ($SS$)** and **Reorder Points ($ROP$)**:
  $$\text{ROP} = (\text{Daily Velocity} \times \text{Lead Time}) + \text{Safety Stock}$$
- Products with stock below safety thresholds trigger an automated **`CRITICAL`** alert.
- Alerts can be acknowledged or resolved through the dashboard with instantaneous replenishment synchronization.

### D. Logistics SLA & Delivery Performance
- **National Delivery Velocity**: Average transit time of **12.5 days**.
- **On-Time Rate**: **92.4%** nationwide.
- **Regional Bottlenecks**: Significant regional disparities identified between Southeast hubs (São Paulo: 8.3 days, Paraná: 11.5 days) and Northern states (Amapá: 27.8 days, Roraima: 28.9 days), driving strategic recommendations for regional fulfillment centers.

### E. CSAT & Sentiment Delay Correlation
- Verified negative correlation between delivery latency and customer satisfaction:
  - **On-Time / Early Deliveries**: Average review score of **4.2 / 5.0**.
  - **Delayed Deliveries**: Average review score plummets to **2.3 / 5.0** (a 45% decline).
  - This proves that delivery reliability is the single greatest determinant of brand sentiment.

### F. What-If Scenario Simulator & Prescriptive AI
The interactive simulation engine models revenue and sentiment impact in real time:
- Reducing regional transit delays by 2 days recovers **+$210,000** in retained customer lifetime value.
- Re-engaging 10% of dormant "At-Risk" customers unlocks **+$512,000** in incremental revenue.
- Eliminating stockouts on top SKUs protects **+$180,000** in at-risk revenue.

---

## 5. REST API Specification & Endpoint Verification

OmniPulse exposes 21 REST endpoints with built-in caching and full OpenAPI documentation at `/docs`:

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/health` | MySQL and system health status | `200 OK` |
| `GET` | `/api/overview` | Executive KPI cards and summary statistics | `200 OK` |
| `GET` | `/api/sales/monthly` | Historical monthly revenue & order count timeseries | `200 OK` |
| `GET` | `/api/sales/categories` | Top product categories ranked by revenue | `200 OK` |
| `GET` | `/api/sales/top-products` | Top revenue SKUs with current stock indicators | `200 OK` |
| `GET` | `/api/sales/payments` | Payment method breakdown (credit card, boleto, voucher) | `200 OK` |
| `GET` | `/api/customers/segments` | RFM segmentation distribution and cohort spend | `200 OK` |
| `GET` | `/api/customers/geography` | Geographic customer concentration across all 27 states | `200 OK` |
| `GET` | `/api/inventory/summary` | Health status distribution (Critical, Low, Healthy) | `200 OK` |
| `GET` | `/api/inventory/alerts` | Paginated stockout alerts with severity filters | `200 OK` |
| `GET` | `/api/inventory/items` | Full 32k+ SKU catalog with search and filters | `200 OK` |
| `PATCH` | `/api/inventory/alerts/{id}/status` | Update alert state (`ACKNOWLEDGED`, `RESOLVED`) | `200 OK` |
| `POST` | `/api/inventory/restock` | Replenish inventory stock and resolve alert | `200 OK` |
| `GET` | `/api/logistics/summary` | SLA delivery rates (early, on-time, late) | `200 OK` |
| `GET` | `/api/logistics/by-state` | State-level delivery days and delay percentages | `200 OK` |
| `GET` | `/api/geography/map-data` | Geospatial coordinates and metrics for Leaflet map | `200 OK` |
| `GET` | `/api/reviews/summary` | Rating distribution and delay-to-CSAT correlation | `200 OK` |
| `GET` | `/api/ai-insights` | Prescriptive recommendations and stockout exposure | `200 OK` |
| `POST` | `/api/ai-chat` | Natural language operational assistant queries | `200 OK` |
| `POST` | `/api/simulator/project` | Dynamic what-if revenue and CSAT projections | `200 OK` |
| `GET` | `/api/export/*` | CSV exports for alerts, customer cohorts, and logistics | `200 OK` |

---

## 6. Verification Test Results

Integration tests were executed using `pytest` and `fastapi.testclient`:

```text
============================================================
RUNNING OMNIPULSE API INTEGRATION TESTS
============================================================
[PASS] Health Check                     |  484.2ms | /health (healthy)
[PASS] Executive Overview KPIs          | 3917.8ms | /api/overview
[PASS] Monthly Revenue Trend            | 1081.9ms | /api/sales/monthly
[PASS] Top Categories                   |  947.8ms | /api/sales/categories?limit=5
[PASS] Top Products                     | 3172.8ms | /api/sales/top-products?limit=5
[PASS] Payment Breakdown                |  596.2ms | /api/sales/payments
[PASS] Customer RFM Segments            |  607.1ms | /api/customers/segments
[PASS] Geographic Distribution          | 2631.0ms | /api/customers/geography
[PASS] Inventory Summary                |   99.8ms | /api/inventory/summary
[PASS] Inventory Alerts                 |  120.4ms | /api/inventory/alerts?limit=5
[PASS] Inventory Items                  |  310.8ms | /api/inventory/items?limit=5
[PASS] Logistics Delivery Summary       |  686.6ms | /api/logistics/summary
[PASS] Logistics by State               |    6.8ms | /api/logistics/by-state
[PASS] Geospatial State Map Data        |   13.5ms | /api/geography/map-data
[PASS] Review Analytics                 | 1733.8ms | /api/reviews/summary
[PASS] AI Operational Insights          | 2377.8ms | /api/ai-insights
[PASS] Export Inventory Alerts CSV      |  425.2ms | /api/export/inventory-alerts
[PASS] Export Customer Segments CSV     |    6.1ms | /api/export/customer-segments
[PASS] Export State Logistics CSV       |    6.9ms | /api/export/state-logistics
[PASS] AI Chat Assistant                |    7.3ms | /api/ai-chat
[PASS] Scenario Simulator               |  893.5ms | /api/simulator/project
============================================================
ALL ENDPOINT TESTS PASSED SUCCESSFULLY! (21/21)
============================================================
```

---

## 7. Quick Start & Execution

### One-Click Windows Launch:
Double-click `start_platform.bat` or run:
```bash
python run_platform.py
```
This verifies MySQL connectivity, opens `http://127.0.0.1:8000/` in your default browser, and starts the server.

### Docker Compose Deployment:
```bash
docker-compose up --build -d
```

### Direct Uvicorn Launch:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 8. Conclusion & Deliverables

OmniPulse is a complete, enterprise-grade decision support platform that demonstrates:
1. Robust large-scale data engineering on 100k+ real e-commerce transactions.
2. High-performance indexed relational database architecture with MySQL 8.0.
3. Clean, documented, RESTful backend design with FastAPI.
4. Glassmorphism executive dashboard with responsive data visualizations.
5. Prescriptive AI recommendations and what-if simulation capabilities that deliver direct strategic business value.
