from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.schemas import SimulationRequest, SimulationResponse

class SimulatorService:

    @staticmethod
    def run_simulation(db: Session, req: SimulationRequest) -> SimulationResponse:
        # Base values from database
        base_rev_row = db.execute(text("SELECT COALESCE(SUM(price), 13591643.70) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE o.order_status = 'delivered'")).fetchone()
        base_rev = float(base_rev_row[0]) if base_rev_row else 13591643.70

        at_risk_row = db.execute(text("SELECT COALESCE(SUM(monetary), 5100000.0) FROM customer_segments WHERE segment_name = 'At Risk'")).fetchone()
        at_risk_pool = float(at_risk_row[0]) if at_risk_row and at_risk_row[0] else 5100000.0

        base_csat = 4.09

        # 1. Recovered Churn Revenue from Win-Back Campaign
        recovered_churn = (req.churn_winback_rate / 100.0) * at_risk_pool

        # 2. Protected Stockout Revenue from Timely Restock
        # Estimated stockout revenue exposure is ~6% of catalog value = ~$815,000
        stockout_exposure_pool = base_rev * 0.06
        protected_stockout = (req.stockout_prevention_rate / 100.0) * stockout_exposure_pool

        # 3. Freight Subsidy Elasticity Effect
        # A subsidy costs discount dollars, but generates elasticity volume (1.4x)
        freight_pool = 2251909.54
        subsidy_cost = (req.freight_subsidy_pct / 100.0) * freight_pool
        freight_volume_gain = subsidy_cost * 1.4

        # Net Revenue Growth
        net_additional_revenue = recovered_churn + protected_stockout + (freight_volume_gain - subsidy_cost)
        rev_growth_pct = round((net_additional_revenue / base_rev) * 100, 2)

        # 4. Projected CSAT Impact
        # Delay reduction directly boosts CSAT by ~0.08 stars per day eliminated
        csat_boost = min(0.70, req.delivery_delay_reduction_days * 0.085)
        # Stockout prevention also prevents customer dissatisfaction (+0.05 max)
        csat_boost += (req.stockout_prevention_rate / 100.0) * 0.05
        projected_csat = min(4.90, round(base_csat + csat_boost, 2))
        csat_delta = round(projected_csat - base_csat, 2)

        return SimulationResponse(
            projected_revenue_growth_usd=round(net_additional_revenue, 2),
            projected_revenue_growth_pct=rev_growth_pct,
            recovered_churn_revenue=round(recovered_churn, 2),
            protected_stockout_revenue=round(protected_stockout, 2),
            projected_csat=projected_csat,
            csat_delta=csat_delta,
            net_financial_benefit=round(net_additional_revenue, 2)
        )
