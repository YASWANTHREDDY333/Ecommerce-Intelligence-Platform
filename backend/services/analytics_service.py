import time
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.schemas import (
    OverviewKPIs, MonthlyRevenue, CategorySales, TopProduct,
    PaymentBreakdown, CustomerSegmentSummary, StateMetric,
    LogisticsSummary, ReviewAnalyticsResponse
)

# In-memory TTL Cache
_cache: Dict[str, Any] = {}
_cache_expiry: Dict[str, float] = {}
CACHE_TTL = 300  # 5 minutes

def get_cached(key: str):
    if key in _cache and time.time() < _cache_expiry.get(key, 0):
        return _cache[key]
    return None

def set_cached(key: str, value: Any, ttl: int = CACHE_TTL):
    _cache[key] = value
    _cache_expiry[key] = time.time() + ttl

def invalidate_cache(prefix: str = None):
    global _cache, _cache_expiry
    if prefix:
        keys_to_del = [k for k in _cache if k.startswith(prefix)]
        for k in keys_to_del:
            _cache.pop(k, None)
            _cache_expiry.pop(k, None)
    else:
        _cache.clear()
        _cache_expiry.clear()


class AnalyticsService:

    @staticmethod
    def get_overview_kpis(db: Session) -> OverviewKPIs:
        cached = get_cached("overview_kpis")
        if cached:
            return cached

        # 1. Total delivered revenue and order counts
        rev_query = text("""
            SELECT 
                COALESCE(SUM(oi.price), 0) AS total_revenue,
                COUNT(DISTINCT o.order_id) AS total_orders,
                COUNT(DISTINCT o.customer_id) AS total_customers
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
        """)
        rev_row = db.execute(rev_query).fetchone()
        total_revenue = float(rev_row[0]) if rev_row else 0.0
        total_orders = int(rev_row[1]) if rev_row else 0
        total_customers = int(rev_row[2]) if rev_row else 0
        aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

        # 2. Logistics & Delivery Performance
        deliv_query = text("""
            SELECT 
                delivery_status,
                COUNT(*) as count,
                AVG(delivery_days) as avg_days
            FROM orders
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date IS NOT NULL
            GROUP BY delivery_status
        """)
        deliv_rows = db.execute(deliv_query).fetchall()
        deliv_dict = {r[0]: r[1] for r in deliv_rows}
        early_cnt = deliv_dict.get("Early", 0)
        ontime_cnt = deliv_dict.get("On Time", 0)
        late_cnt = deliv_dict.get("Late", 0)
        tot_deliv = early_cnt + ontime_cnt + late_cnt

        on_time_rate = round(((early_cnt + ontime_cnt) / tot_deliv * 100), 2) if tot_deliv > 0 else 0.0
        early_rate = round((early_cnt / tot_deliv * 100), 2) if tot_deliv > 0 else 0.0
        late_rate = round((late_cnt / tot_deliv * 100), 2) if tot_deliv > 0 else 0.0

        avg_days_query = text("""
            SELECT AVG(delivery_days) 
            FROM orders 
            WHERE order_status = 'delivered' AND delivery_days IS NOT NULL AND delivery_days >= 0
        """)
        avg_days_row = db.execute(avg_days_query).fetchone()
        avg_delivery_days = round(float(avg_days_row[0]), 1) if avg_days_row and avg_days_row[0] is not None else 0.0

        # 3. Reviews average
        review_query = text("SELECT AVG(review_score) FROM reviews WHERE review_score IS NOT NULL")
        rev_score_row = db.execute(review_query).fetchone()
        avg_review_score = round(float(rev_score_row[0]), 2) if rev_score_row and rev_score_row[0] is not None else 0.0

        # 4. Inventory Alerts counts
        alert_query = text("""
            SELECT alert_type, COUNT(*) 
            FROM inventory_alerts 
            WHERE alert_status = 'OPEN' 
            GROUP BY alert_type
        """)
        alert_rows = db.execute(alert_query).fetchall()
        alert_dict = {r[0]: r[1] for r in alert_rows}
        critical_alerts = alert_dict.get("CRITICAL", 0)
        low_stock_alerts = alert_dict.get("LOW_STOCK", 0)

        # 5. Product & Seller counts
        prod_count = db.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
        seller_count = db.execute(text("SELECT COUNT(*) FROM sellers")).scalar() or 0

        res = OverviewKPIs(
            total_revenue=round(total_revenue, 2),
            total_orders=total_orders,
            total_customers=total_customers,
            average_order_value=aov,
            on_time_rate=on_time_rate,
            early_rate=early_rate,
            late_rate=late_rate,
            avg_delivery_days=avg_delivery_days,
            avg_review_score=avg_review_score,
            critical_alerts_count=critical_alerts,
            low_stock_alerts_count=low_stock_alerts,
            total_products=prod_count,
            total_sellers=seller_count
        )
        set_cached("overview_kpis", res)
        return res

    @staticmethod
    def get_monthly_revenue(db: Session) -> List[MonthlyRevenue]:
        cached = get_cached("monthly_revenue")
        if cached:
            return cached

        query = text("""
            SELECT 
                o.order_year_month as month,
                SUM(oi.price) as revenue,
                COUNT(DISTINCT o.order_id) as orders
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
              AND o.order_year_month IS NOT NULL
              AND o.order_year_month >= '2017-01'
            GROUP BY o.order_year_month
            ORDER BY o.order_year_month ASC
        """)
        rows = db.execute(query).fetchall()
        result = []
        for r in rows:
            rev = float(r[1])
            orders = int(r[2])
            aov = round(rev / orders, 2) if orders > 0 else 0.0
            result.append(MonthlyRevenue(
                month=r[0],
                revenue=round(rev, 2),
                orders=orders,
                avg_order_value=aov
            ))
        set_cached("monthly_revenue", result)
        return result

    @staticmethod
    def get_top_categories(db: Session, limit: int = 10) -> List[CategorySales]:
        cached = get_cached(f"top_categories_{limit}")
        if cached:
            return cached

        query = text(f"""
            SELECT 
                COALESCE(p.product_category_name_english, 'Other') AS category,
                SUM(oi.price) AS revenue,
                COUNT(oi.product_id) AS items_sold,
                AVG(oi.price) AS avg_price
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_status = 'delivered'
            GROUP BY p.product_category_name_english
            ORDER BY revenue DESC
            LIMIT {limit}
        """)
        rows = db.execute(query).fetchall()
        result = [
            CategorySales(
                category=r[0].replace("_", " ").title() if r[0] else "Other",
                revenue=round(float(r[1]), 2),
                items_sold=int(r[2]),
                avg_price=round(float(r[3]), 2)
            ) for r in rows
        ]
        set_cached(f"top_categories_{limit}", result)
        return result

    @staticmethod
    def get_top_products(db: Session, limit: int = 10) -> List[TopProduct]:
        cached = get_cached(f"top_products_{limit}")
        if cached:
            return cached

        query = text(f"""
            SELECT 
                oi.product_id,
                COALESCE(p.product_category_name_english, 'Other') AS category,
                SUM(oi.price) AS revenue,
                COUNT(oi.product_id) AS items_sold,
                COALESCE(inv.current_stock, 0) AS current_stock,
                COALESCE(inv.reorder_level, 0) AS reorder_level
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN inventory inv ON oi.product_id = inv.product_id
            WHERE o.order_status = 'delivered'
            GROUP BY oi.product_id, p.product_category_name_english, inv.current_stock, inv.reorder_level
            ORDER BY revenue DESC
            LIMIT {limit}
        """)
        rows = db.execute(query).fetchall()
        result = []
        for r in rows:
            stock = int(r[4])
            reorder = int(r[5])
            if stock == 0:
                status = "OUT_OF_STOCK"
            elif stock <= reorder * 0.5:
                status = "CRITICAL"
            elif stock <= reorder:
                status = "LOW"
            else:
                status = "HEALTHY"

            result.append(TopProduct(
                product_id=r[0],
                category=r[1].replace("_", " ").title(),
                revenue=round(float(r[2]), 2),
                items_sold=int(r[3]),
                current_stock=stock,
                stock_status=status
            ))
        set_cached(f"top_products_{limit}", result)
        return result

    @staticmethod
    def get_payment_breakdown(db: Session) -> List[PaymentBreakdown]:
        cached = get_cached("payment_breakdown")
        if cached:
            return cached

        query = text("""
            SELECT 
                payment_type,
                COUNT(*) as count,
                SUM(payment_value) as total_val
            FROM payments
            GROUP BY payment_type
            ORDER BY total_val DESC
        """)
        rows = db.execute(query).fetchall()
        total_sum = sum(float(r[2]) for r in rows if r[2] is not None)
        result = []
        for r in rows:
            val = float(r[2]) if r[2] is not None else 0.0
            pct = round((val / total_sum * 100), 2) if total_sum > 0 else 0.0
            p_name = r[0].replace("_", " ").title() if r[0] else "Unknown"
            result.append(PaymentBreakdown(
                payment_type=p_name,
                count=int(r[1]),
                total_value=round(val, 2),
                percentage=pct
            ))
        set_cached("payment_breakdown", result)
        return result

    @staticmethod
    def get_customer_segments(db: Session) -> List[CustomerSegmentSummary]:
        cached = get_cached("customer_segments")
        if cached:
            return cached

        query = text("""
            SELECT 
                segment_name,
                COUNT(*) as customer_count,
                AVG(recency_days) as avg_recency,
                AVG(frequency) as avg_frequency,
                AVG(monetary) as avg_monetary,
                SUM(monetary) as total_revenue
            FROM customer_segments
            GROUP BY segment_name
            ORDER BY total_revenue DESC
        """)
        rows = db.execute(query).fetchall()
        total_customers = sum(int(r[1]) for r in rows)
        result = []
        for r in rows:
            cnt = int(r[1])
            pct = round((cnt / total_customers * 100), 2) if total_customers > 0 else 0.0
            result.append(CustomerSegmentSummary(
                segment_name=r[0],
                customer_count=cnt,
                percentage=pct,
                avg_recency=round(float(r[2]), 1),
                avg_frequency=round(float(r[3]), 2),
                avg_monetary=round(float(r[4]), 2),
                total_revenue=round(float(r[5]), 2)
            ))
        set_cached("customer_segments", result)
        return result

    @staticmethod
    def get_state_metrics(db: Session) -> List[StateMetric]:
        cached = get_cached("state_metrics")
        if cached:
            return cached

        query = text("""
            SELECT 
                c.customer_state as state,
                COUNT(DISTINCT c.customer_unique_id) as customer_count,
                COUNT(DISTINCT o.order_id) as orders_count,
                COALESCE(SUM(oi.price), 0) as total_revenue,
                AVG(o.delivery_days) as avg_delivery_days,
                SUM(CASE WHEN o.delivery_status = 'Late' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(o.order_id), 0) as late_rate
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_state
            ORDER BY total_revenue DESC
        """)
        rows = db.execute(query).fetchall()
        result = [
            StateMetric(
                state=r[0],
                customer_count=int(r[1]),
                orders_count=int(r[2]),
                total_revenue=round(float(r[3]), 2),
                avg_delivery_days=round(float(r[4]), 1) if r[4] is not None else 0.0,
                late_rate=round(float(r[5]), 2) if r[5] is not None else 0.0
            ) for r in rows
        ]
        set_cached("state_metrics", result)
        return result

    @staticmethod
    def get_logistics_summary(db: Session) -> LogisticsSummary:
        cached = get_cached("logistics_summary")
        if cached:
            return cached

        query = text("""
            SELECT 
                delivery_status,
                COUNT(*) as count,
                AVG(delivery_days) as avg_deliv_days,
                AVG(delay_days) as avg_delay_days
            FROM orders
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date IS NOT NULL
            GROUP BY delivery_status
        """)
        rows = db.execute(query).fetchall()
        counts = {r[0]: int(r[1]) for r in rows}
        early_cnt = counts.get("Early", 0)
        ontime_cnt = counts.get("On Time", 0)
        late_cnt = counts.get("Late", 0)
        total_delivered = early_cnt + ontime_cnt + late_cnt

        early_pct = round((early_cnt / total_delivered * 100), 2) if total_delivered > 0 else 0.0
        ontime_pct = round((ontime_cnt / total_delivered * 100), 2) if total_delivered > 0 else 0.0
        late_pct = round((late_cnt / total_delivered * 100), 2) if total_delivered > 0 else 0.0
        on_or_before_pct = round(((early_cnt + ontime_cnt) / total_delivered * 100), 2) if total_delivered > 0 else 0.0

        avg_query = text("""
            SELECT 
                AVG(delivery_days),
                AVG(delay_days)
            FROM orders
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date IS NOT NULL
        """)
        avg_row = db.execute(avg_query).fetchone()
        avg_deliv = round(float(avg_row[0]), 2) if avg_row and avg_row[0] is not None else 0.0
        avg_delay = round(float(avg_row[1]), 2) if avg_row and avg_row[1] is not None else 0.0

        res = LogisticsSummary(
            total_delivered=total_delivered,
            early_deliveries=early_cnt,
            on_time_deliveries=ontime_cnt,
            late_deliveries=late_cnt,
            early_percentage=early_pct,
            on_time_percentage=ontime_pct,
            late_percentage=late_pct,
            on_or_before_percentage=on_or_before_pct,
            avg_delivery_days=avg_deliv,
            avg_delay_days=avg_delay
        )
        set_cached("logistics_summary", res)
        return res

    @staticmethod
    def get_reviews_analytics(db: Session) -> ReviewAnalyticsResponse:
        cached = get_cached("reviews_analytics")
        if cached:
            return cached

        query = text("""
            SELECT 
                review_score,
                COUNT(*) as count
            FROM reviews
            WHERE review_score IS NOT NULL
            GROUP BY review_score
            ORDER BY review_score ASC
        """)
        rows = db.execute(query).fetchall()
        dist = {str(r[0]): int(r[1]) for r in rows}
        total_rev = sum(dist.values())
        avg_score = sum(int(score) * cnt for score, cnt in dist.items()) / total_rev if total_rev > 0 else 0.0
        percentages = {score: round(cnt / total_rev * 100, 2) for score, cnt in dist.items()}

        delay_query = text("""
            SELECT 
                o.delivery_status,
                AVG(r.review_score) as avg_score,
                COUNT(*) as review_count
            FROM reviews r
            JOIN orders o ON r.order_id = o.order_id
            WHERE o.delivery_status IS NOT NULL
            GROUP BY o.delivery_status
        """)
        delay_rows = db.execute(delay_query).fetchall()
        delay_vs_rating = [
            {
                "status": r[0],
                "avg_rating": round(float(r[1]), 2),
                "review_count": int(r[2])
            } for r in delay_rows
        ]

        res = ReviewAnalyticsResponse(
            average_score=round(avg_score, 2),
            total_reviews=total_rev,
            score_distribution=dist,
            score_percentages=percentages,
            delivery_delay_vs_rating=delay_vs_rating
        )
        set_cached("reviews_analytics", res)
        return res
