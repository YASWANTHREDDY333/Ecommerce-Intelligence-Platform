from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OverviewKPIs(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    average_order_value: float
    on_time_rate: float
    early_rate: float
    late_rate: float
    avg_delivery_days: float
    avg_review_score: float
    critical_alerts_count: int
    low_stock_alerts_count: int
    total_products: int
    total_sellers: int

class MonthlyRevenue(BaseModel):
    month: str
    revenue: float
    orders: int
    avg_order_value: float

class CategorySales(BaseModel):
    category: str
    revenue: float
    items_sold: int
    avg_price: float

class TopProduct(BaseModel):
    product_id: str
    category: str
    revenue: float
    items_sold: int
    current_stock: int
    stock_status: str

class PaymentBreakdown(BaseModel):
    payment_type: str
    count: int
    total_value: float
    percentage: float

class CustomerSegmentSummary(BaseModel):
    segment_name: str
    customer_count: int
    percentage: float
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    total_revenue: float

class StateMetric(BaseModel):
    state: str
    customer_count: int
    orders_count: int
    total_revenue: float
    avg_delivery_days: float
    late_rate: float

class InventorySummary(BaseModel):
    total_skus: int
    critical_count: int
    low_stock_count: int
    healthy_count: int
    open_alerts_count: int

class InventoryAlertResponse(BaseModel):
    alert_id: int
    product_id: str
    category: Optional[str] = "Unknown"
    alert_type: str
    current_stock: int
    reorder_level: int
    recommended_reorder_quantity: int
    alert_message: str
    alert_status: str

class InventoryItemResponse(BaseModel):
    product_id: str
    category: Optional[str] = "Unknown"
    current_stock: int
    reorder_level: int
    safety_stock: int
    average_daily_sales: float
    supplier_lead_time_days: int
    stock_status: str

class AlertStatusUpdate(BaseModel):
    alert_status: str = Field(..., description="'OPEN', 'ACKNOWLEDGED', or 'RESOLVED'")

class RestockAction(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, description="Quantity of units to add to inventory")

class LogisticsSummary(BaseModel):
    total_delivered: int
    early_deliveries: int
    on_time_deliveries: int
    late_deliveries: int
    early_percentage: float
    on_time_percentage: float
    late_percentage: float
    on_or_before_percentage: float
    avg_delivery_days: float
    avg_delay_days: float

class ReviewAnalyticsResponse(BaseModel):
    average_score: float
    total_reviews: int
    score_distribution: Dict[str, int]
    score_percentages: Dict[str, float]
    delivery_delay_vs_rating: List[Dict[str, Any]]

class AIInsight(BaseModel):
    id: str
    category: str
    title: str
    description: str
    impact_level: str
    metric: str
    recommended_action: str

class AIChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language user query")

class AIChatResponse(BaseModel):
    answer: str
    data_points: List[str] = []
    suggested_tab: Optional[str] = "tab-overview"
    action_chips: List[str] = []

class SimulationRequest(BaseModel):
    delivery_delay_reduction_days: float = Field(0.0, ge=0, le=10, description="Reduction in transit days")
    churn_winback_rate: float = Field(0.0, ge=0, le=100, description="Percentage of at-risk customers recovered")
    stockout_prevention_rate: float = Field(0.0, ge=0, le=100, description="Percentage of critical stockout orders protected")
    freight_subsidy_pct: float = Field(0.0, ge=0, le=50, description="Freight discount percentage")

class SimulationResponse(BaseModel):
    projected_revenue_growth_usd: float
    projected_revenue_growth_pct: float
    recovered_churn_revenue: float
    protected_stockout_revenue: float
    projected_csat: float
    csat_delta: float
    net_financial_benefit: float

class GeoMapState(BaseModel):
    state: str
    lat: float
    lng: float
    customer_count: int
    orders_count: int
    total_revenue: float
    avg_delivery_days: float
    late_rate: float
    sla_status: str
