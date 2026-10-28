from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import (
    InventorySummary, AlertStatusUpdate, RestockAction
)
from backend.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventory Intelligence"])

@router.get("/summary", response_model=InventorySummary, summary="Inventory health metrics and SKU status summary")
def get_inventory_summary(db: Session = Depends(get_db)):
    return InventoryService.get_summary(db)

@router.get("/alerts", summary="List stock alerts with filters and pagination")
def get_inventory_alerts(
    alert_type: Optional[str] = Query(None, description="'CRITICAL' or 'LOW_STOCK'"),
    alert_status: Optional[str] = Query(None, description="'OPEN', 'ACKNOWLEDGED', 'RESOLVED'"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    alerts, total = InventoryService.get_alerts(
        db, limit=limit, offset=offset, alert_type=alert_type, alert_status=alert_status
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "alerts": alerts
    }

@router.get("/items", summary="List inventory items with search and stock status filter")
def get_inventory_items(
    search: Optional[str] = Query(None, description="Search product ID or category"),
    stock_status: Optional[str] = Query(None, description="'CRITICAL', 'LOW', or 'HEALTHY'"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    items, total = InventoryService.get_items(
        db, search=search, stock_status=stock_status, limit=limit, offset=offset
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }

@router.patch("/alerts/{alert_id}/status", summary="Update alert status (e.g. ACKNOWLEDGED, RESOLVED)")
def update_alert_status(
    alert_id: int,
    body: AlertStatusUpdate,
    db: Session = Depends(get_db)
):
    success = InventoryService.update_alert_status(db, alert_id=alert_id, new_status=body.alert_status)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert_id": alert_id, "new_status": body.alert_status}

@router.post("/restock", summary="Restock product inventory and update alert status")
def restock_product(
    body: RestockAction,
    db: Session = Depends(get_db)
):
    success = InventoryService.restock_product(db, product_id=body.product_id, quantity=body.quantity)
    return {"status": "success", "product_id": body.product_id, "quantity_added": body.quantity}
