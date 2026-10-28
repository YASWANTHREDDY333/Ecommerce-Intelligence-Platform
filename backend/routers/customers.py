from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import CustomerSegmentSummary, StateMetric
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/customers", tags=["Customer Intelligence"])

@router.get("/segments", response_model=List[CustomerSegmentSummary], summary="RFM Customer segmentation distribution")
def get_customer_segments(db: Session = Depends(get_db)):
    return AnalyticsService.get_customer_segments(db)

@router.get("/geography", response_model=List[StateMetric], summary="Customer and sales geographic distribution by state")
def get_customer_geography(db: Session = Depends(get_db)):
    return AnalyticsService.get_state_metrics(db)
