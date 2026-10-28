from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import AIInsight
from backend.services.ai_insights_service import AIInsightsService

router = APIRouter(prefix="/api/ai-insights", tags=["AI Intelligence Engine"])

@router.get("", response_model=List[AIInsight], summary="Automated real-time AI operational insights and recommendations")
def get_ai_insights(db: Session = Depends(get_db)):
    return AIInsightsService.generate_insights(db)
