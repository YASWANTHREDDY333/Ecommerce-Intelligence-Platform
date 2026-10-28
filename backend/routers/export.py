import csv
import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.inventory_service import InventoryService
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/export", tags=["Data Export Hub"])

@router.get("/inventory-alerts", summary="Download active inventory alerts as CSV")
def export_inventory_alerts(db: Session = Depends(get_db)):
    alerts, _ = InventoryService.get_alerts(db, limit=5000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Alert ID", "Product ID", "Category", "Alert Type", "Current Stock", "Reorder Level", "Recommended Reorder Qty", "Alert Status", "Message"])
    for a in alerts:
        writer.writerow([a.alert_id, a.product_id, a.category, a.alert_type, a.current_stock, a.reorder_level, a.recommended_reorder_quantity, a.alert_status, a.alert_message])

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=omnipulse_inventory_alerts.csv"}
    )

@router.get("/customer-segments", summary="Download customer segments summary as CSV")
def export_customer_segments(db: Session = Depends(get_db)):
    segments = AnalyticsService.get_customer_segments(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Segment Name", "Customer Count", "Percentage", "Avg Recency Days", "Avg Frequency", "Avg Monetary Spend", "Total Revenue"])
    for s in segments:
        writer.writerow([s.segment_name, s.customer_count, f"{s.percentage}%", s.avg_recency, s.avg_frequency, s.avg_monetary, s.total_revenue])

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=omnipulse_customer_segments.csv"}
    )

@router.get("/state-logistics", summary="Download state delivery and SLA report as CSV")
def export_state_logistics(db: Session = Depends(get_db)):
    states = AnalyticsService.get_state_metrics(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["State", "Delivered Orders", "Unique Customers", "Total Revenue", "Avg Transit Days", "Late Delivery Rate (%)"])
    for s in states:
        writer.writerow([s.state, s.orders_count, s.customer_count, s.total_revenue, s.avg_delivery_days, f"{s.late_rate:.2f}%"])

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=omnipulse_state_logistics.csv"}
    )
