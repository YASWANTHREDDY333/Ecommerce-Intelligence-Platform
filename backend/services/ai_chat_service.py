import re
from typing import List
from sqlalchemy.orm import Session
from backend.schemas import AIChatResponse
from backend.services.analytics_service import AnalyticsService
from backend.services.inventory_service import InventoryService
from backend.services.ai_insights_service import AIInsightsService

class AIChatService:

    @staticmethod
    def answer_query(db: Session, query_text: str) -> AIChatResponse:
        q = query_text.lower().strip()

        # 1. Revenue & Sales Velocity Intent
        if any(w in q for w in ["revenue", "sales", "earnings", "gross", "income", "money", "aov", "order value"]):
            kpis = AnalyticsService.get_overview_kpis(db)
            monthly = AnalyticsService.get_monthly_revenue(db)
            latest = monthly[-1] if monthly else None
            latest_str = f"{latest.month} recorded ${latest.revenue:,.2f} across {latest.orders:,} orders." if latest else ""

            return AIChatResponse(
                answer=f"Total delivered revenue stands at **${kpis.total_revenue:,.2f}** across **{kpis.total_orders:,}** delivered orders, with an Average Order Value (AOV) of **${kpis.average_order_value:.2f}**. {latest_str}",
                data_points=[
                    f"Total Revenue: ${kpis.total_revenue:,.2f}",
                    f"Delivered Orders: {kpis.total_orders:,}",
                    f"Average Order Value: ${kpis.average_order_value:.2f}"
                ],
                suggested_tab="tab-sales",
                action_chips=[
                    "What are the top 5 product categories?",
                    "What is our customer churn risk?",
                    "How are credit card sales performing?"
                ]
            )

        # 2. Inventory, Stockout, & Restock Intent
        elif any(w in q for w in ["inventory", "stock", "stockout", "reorder", "alert", "sku", "warehouse", "supply"]):
            inv = InventoryService.get_summary(db)
            alerts, _ = InventoryService.get_alerts(db, limit=3, alert_type="CRITICAL")
            top_skus = ", ".join([f"SKU {a.product_id[:8]} ({a.category})" for a in alerts[:3]]) if alerts else "None"

            return AIChatResponse(
                answer=f"OmniPulse is monitoring **{inv.total_skus:,} active SKUs**. Currently, there are **{inv.critical_count:,} CRITICAL stockout alerts** (stock &le; safety threshold) and **{inv.low_stock_count:,} low stock alerts**. Top priority critical items include: {top_skus}.",
                data_points=[
                    f"Monitored SKUs: {inv.total_skus:,}",
                    f"Critical Alerts: {inv.critical_count:,}",
                    f"Low Stock Alerts: {inv.low_stock_count:,}",
                    f"Healthy Stock SKUs: {inv.healthy_count:,}"
                ],
                suggested_tab="tab-inventory",
                action_chips=[
                    "Show critical stock alerts",
                    "How many products need restock?",
                    "What is our revenue?"
                ]
            )

        # 3. Customer RFM & Churn Intent
        elif any(w in q for w in ["customer", "churn", "rfm", "segment", "loyal", "at risk", "retention", "vip"]):
            segments = AnalyticsService.get_customer_segments(db)
            seg_dict = {s.segment_name: s for s in segments}
            at_risk = seg_dict.get("At Risk")
            loyal = seg_dict.get("Loyal")
            high_val = seg_dict.get("High Value")

            ans_parts = ["Our customer base of **93,358 unique buyers** is categorized into 4 RFM clusters:"]
            if loyal:
                ans_parts.append(f"• **Loyal**: {loyal.customer_count:,} customers ({loyal.percentage}%) generating ${loyal.total_revenue:,.2f}.")
            if at_risk:
                ans_parts.append(f"• **At Risk**: {at_risk.customer_count:,} dormant customers representing **${at_risk.total_revenue:,.2f}** in historical spend at risk of churn.")
            if high_val:
                ans_parts.append(f"• **High Value VIPs**: {high_val.customer_count:,} top spenders with avg spend of ${high_val.avg_monetary:.2f}.")

            return AIChatResponse(
                answer="\n\n".join(ans_parts),
                data_points=[
                    f"Loyal Customers: {loyal.customer_count if loyal else 0:,}",
                    f"At-Risk Value: ${at_risk.total_revenue if at_risk else 0:,.2f}",
                    f"High-Value VIPs: {high_val.customer_count if high_val else 0:,}"
                ],
                suggested_tab="tab-customers",
                action_chips=[
                    "What is the recommended churn win-back strategy?",
                    "Show sales by Brazilian state",
                    "What are the delivery SLA metrics?"
                ]
            )

        # 4. Logistics, Delivery, & SLA Intent
        elif any(w in q for w in ["delivery", "logistics", "shipping", "transit", "delay", "sla", "late", "carrier"]):
            logistics = AnalyticsService.get_logistics_summary(db)
            states = AnalyticsService.get_state_metrics(db)
            slowest = sorted(states, key=lambda s: s.late_rate, reverse=True)[:3]
            slow_names = ", ".join([f"{s.state} ({s.late_rate:.1f}% late)" for s in slowest])

            return AIChatResponse(
                answer=f"Overall delivery fulfillment achieves a **{logistics.on_or_before_percentage:.1f}% on-or-before estimate rate** ({logistics.early_percentage:.1f}% early, {logistics.on_time_percentage:.1f}% on-time). Late shipments account for **{logistics.late_percentage:.1f}%**. Average transit duration is **{logistics.avg_delivery_days:.1f} days**. The highest delay rates are in: **{slow_names}**.",
                data_points=[
                    f"On-Time / Early Rate: {logistics.on_or_before_percentage:.1f}%",
                    f"Late Delivery Rate: {logistics.late_percentage:.1f}%",
                    f"Average Transit Time: {logistics.avg_delivery_days:.1f} days",
                    f"Average Delivery Delay: {logistics.avg_delay_days:.1f} days"
                ],
                suggested_tab="tab-logistics",
                action_chips=[
                    "Which states have the longest transit time?",
                    "How does delivery delay hurt review ratings?",
                    "What are top selling categories?"
                ]
            )

        # 5. Reviews & CSAT Intent
        elif any(w in q for w in ["review", "csat", "rating", "star", "satisfaction", "sentiment", "feedback"]):
            reviews = AnalyticsService.get_reviews_analytics(db)
            fives = reviews.score_percentages.get("5", 0.0)
            ones = reviews.score_percentages.get("1", 0.0)

            return AIChatResponse(
                answer=f"Customer satisfaction averages **{reviews.average_score:.2f} out of 5.0** across {reviews.total_reviews:,} verified reviews. **{fives:.1f}%** of customers rate their experience 5 stars, while **{ones:.1f}%** leave 1 star. Data shows on-time deliveries score 4.2+ stars, but late shipments plunge ratings to 2.3 stars.",
                data_points=[
                    f"Average CSAT: {reviews.average_score:.2f} / 5.0",
                    f"Total Reviews: {reviews.total_reviews:,}",
                    f"5-Star Share: {fives:.1f}%",
                    f"1-Star Share: {ones:.1f}%"
                ],
                suggested_tab="tab-reviews",
                action_chips=[
                    "What causes 1-star reviews?",
                    "How fast do we deliver orders?",
                    "Show executive summary"
                ]
            )

        # 6. Categories & Products Intent
        elif any(w in q for w in ["category", "product", "item", "best selling", "top sold", "merchandise"]):
            cats = AnalyticsService.get_top_categories(db, limit=5)
            cat_list = ", ".join([f"{c.category} (${c.revenue:,.0f})" for c in cats])

            return AIChatResponse(
                answer=f"The top 5 product categories by delivered revenue are: **{cat_list}**. The leading category is **{cats[0].category}** driving over **${cats[0].revenue:,.2f}** with {cats[0].items_sold:,} items sold.",
                data_points=[f"{c.category}: ${c.revenue:,.2f}" for c in cats[:4]],
                suggested_tab="tab-sales",
                action_chips=[
                    "Show top individual products",
                    "What is our revenue?",
                    "What are critical inventory alerts?"
                ]
            )

        # 7. AI Recommendations & Strategic Advice Intent
        elif any(w in q for w in ["recommend", "insight", "strategy", "action", "advice", "what should we do", "improve"]):
            insights = AIInsightsService.generate_insights(db)
            top_actions = "\n".join([f"• **{ins.title}** ({ins.impact_level}): {ins.recommended_action}" for ins in insights[:3]])

            return AIChatResponse(
                answer=f"Here are the top prescriptive strategic recommendations generated by OmniPulse AI:\n\n{top_actions}",
                data_points=[f"{ins.category}: {ins.metric}" for ins in insights[:3]],
                suggested_tab="tab-ai",
                action_chips=[
                    "How can we win back at-risk customers?",
                    "Simulate revenue growth scenario",
                    "Show inventory stockout alerts"
                ]
            )

        # Default Fallback Synthesizer
        else:
            kpis = AnalyticsService.get_overview_kpis(db)
            return AIChatResponse(
                answer=f"OmniPulse is managing **${kpis.total_revenue:,.2f}** in gross sales across **{kpis.total_orders:,}** orders and **{kpis.total_customers:,}** customers. Our on-time delivery rate is **{kpis.on_time_rate}%** with an average CSAT of **{kpis.avg_review_score}/5.0**. How can I help you explore this data?",
                data_points=[
                    f"Revenue: ${kpis.total_revenue:,.2f}",
                    f"Orders: {kpis.total_orders:,}",
                    f"On-Time: {kpis.on_time_rate}%",
                    f"CSAT: {kpis.avg_review_score}/5.0"
                ],
                suggested_tab="tab-overview",
                action_chips=[
                    "What are our top revenue categories?",
                    "How many SKUs are in critical stock?",
                    "What is our customer churn risk?"
                ]
            )
