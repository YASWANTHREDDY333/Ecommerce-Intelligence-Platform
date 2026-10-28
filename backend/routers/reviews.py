from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import ReviewAnalyticsResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/reviews", tags=["Reviews & Satisfaction"])

@router.get("/summary", response_model=ReviewAnalyticsResponse, summary="Review score ratings distribution and delay correlation")
def get_reviews_summary(db: Session = Depends(get_db)):
    return AnalyticsService.get_reviews_analytics(db)
