from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import OverviewKPIs
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/overview", tags=["Executive Overview"])

@router.get("", response_model=OverviewKPIs, summary="Get high-level executive KPIs")
def get_overview(db: Session = Depends(get_db)):
    return AnalyticsService.get_overview_kpis(db)
