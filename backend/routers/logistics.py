from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import LogisticsSummary, StateMetric
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/logistics", tags=["Logistics & Fulfillment"])

@router.get("/summary", response_model=LogisticsSummary, summary="Logistics delivery SLA and on-time delivery summary")
def get_logistics_summary(db: Session = Depends(get_db)):
    return AnalyticsService.get_logistics_summary(db)

@router.get("/by-state", response_model=List[StateMetric], summary="Delivery performance by destination state")
def get_logistics_by_state(db: Session = Depends(get_db)):
    return AnalyticsService.get_state_metrics(db)
