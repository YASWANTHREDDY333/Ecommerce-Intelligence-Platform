from typing import List
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.schemas import AIInsight
from backend.services.analytics_service import AnalyticsService

class AIInsightsService:

    @staticmethod
    def generate_insights(db: Session) -> List[AIInsight]:
        insights: List[AIInsight] = []

        # 1. Inventory Stockout Risk Insight
        crit_count = db.execute(text("SELECT COUNT(*) FROM inventory_alerts WHERE alert_type = 'CRITICAL' AND alert_status = 'OPEN'")).scalar() or 0
        if crit_count > 0:
            insights.append(AIInsight(
                id="INS-01",
                category="Inventory Intelligence",
                title="Critical Stockout Risk Exposure",
                description=f"There are currently {crit_count:,} products operating below safety stock levels. Fast stockout mitigation is urgently needed to prevent order fulfillment backlogs and customer dissatisfaction.",
                impact_level="CRITICAL",
                metric=f"{crit_count:,} Critical SKUs",
                recommended_action="Execute automated restock orders for top-velocity SKUs flagged with lead time > 7 days."
            ))

        # 2. Customer Retention / Churn Risk Insight
        at_risk_row = db.execute(text("""
            SELECT COUNT(*), SUM(monetary), AVG(recency_days)
            FROM customer_segments
            WHERE segment_name = 'At Risk'
        """)).fetchone()
        if at_risk_row and at_risk_row[0]:
            count = int(at_risk_row[0])
            monetary = float(at_risk_row[1]) if at_risk_row[1] else 0.0
            avg_rec = round(float(at_risk_row[2])) if at_risk_row[2] else 0
            insights.append(AIInsight(
                id="INS-02",
                category="Customer Retention",
                title="At-Risk Customer Churn Intervention",
                description=f"{count:,} customers holding ${monetary:,.0f} in historical transaction value have not purchased in over {avg_rec} days. Reactivating this cohort presents an immediate revenue recovery opportunity.",
                impact_level="HIGH",
                metric=f"${monetary:,.0f} At-Risk LTV",
                recommended_action="Launch targeted win-back campaigns offering dynamic discounts on previously browsed categories."
            ))

        # 3. High-Value Customer Protection
        high_val_row = db.execute(text("""
            SELECT COUNT(*), SUM(monetary), AVG(monetary)
            FROM customer_segments
            WHERE segment_name = 'High Value'
        """)).fetchone()
        if high_val_row and high_val_row[0]:
            hv_count = int(high_val_row[0])
            hv_monetary = float(high_val_row[1]) if high_val_row[1] else 0.0
            insights.append(AIInsight(
                id="INS-03",
                category="Revenue Growth",
                title="High-Value VIP Loyalty Maximization",
                description=f"The top {hv_count:,} VIP customers contribute ${hv_monetary:,.0f} in revenue. Maintaining high SLA fulfillment for this segment will protect key margins.",
                impact_level="POSITIVE",
                metric=f"${hv_monetary:,.0f} VIP Revenue",
                recommended_action="Provide dedicated priority customer support and exclusive early-access promotional catalog items."
            ))

        # 4. Logistics SLA Bottleneck Insight
        slow_states = db.execute(text("""
            SELECT c.customer_state, AVG(o.delivery_days) as avg_days,
                   SUM(CASE WHEN o.delivery_status = 'Late' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as late_rate
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered' AND o.delivery_days IS NOT NULL
            GROUP BY c.customer_state
            HAVING late_rate > 10
            ORDER BY late_rate DESC
            LIMIT 3
        """)).fetchall()
        if slow_states:
            state_names = ", ".join([f"{r[0]} ({float(r[2]):.1f}% late)" for r in slow_states])
            insights.append(AIInsight(
                id="INS-04",
                category="Logistics Optimization",
                title="Regional Shipping Delays Bottleneck",
                description=f"Significant delivery delays detected in states: {state_names}. Regional fulfillment centers or 3PL renegotiation is suggested.",
                impact_level="HIGH",
                metric="> 10% Late Deliveries",
                recommended_action="Audit regional carrier route handoffs and adjust customer-facing estimated delivery dates (EDD) for these regions."
            ))

        # 5. Customer Review & Delivery Delay Correlation
        rev_impact = db.execute(text("""
            SELECT o.delivery_status, AVG(r.review_score)
            FROM reviews r
            JOIN orders o ON r.order_id = o.order_id
            WHERE o.delivery_status IN ('Early', 'Late')
            GROUP BY o.delivery_status
        """)).fetchall()
        rev_dict = {r[0]: float(r[1]) for r in rev_impact}
        if "Early" in rev_dict and "Late" in rev_dict:
            gap = round(rev_dict["Early"] - rev_dict["Late"], 2)
            insights.append(AIInsight(
                id="INS-05",
                category="Customer Satisfaction",
                title="Late Deliveries Impact on Customer CSAT",
                description=f"Late deliveries cause customer review ratings to plunge from {rev_dict['Early']:.2f} stars down to {rev_dict['Late']:.2f} stars (a drop of {gap} stars). Logistics speed directly dictates brand reputation.",
                impact_level="MEDIUM",
                metric=f"-{gap} Star Rating Penalty",
                recommended_action="Implement proactive delay notifications with compensation vouchers before delivery occurs."
            ))

        return insights
