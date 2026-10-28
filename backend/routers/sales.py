from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import MonthlyRevenue, CategorySales, TopProduct, PaymentBreakdown
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/sales", tags=["Sales & Revenue"])

@router.get("/monthly", response_model=List[MonthlyRevenue], summary="Monthly revenue trajectory")
def get_monthly_revenue(db: Session = Depends(get_db)):
    return AnalyticsService.get_monthly_revenue(db)

@router.get("/categories", response_model=List[CategorySales], summary="Top performing product categories")
def get_top_categories(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_top_categories(db, limit=limit)

@router.get("/top-products", response_model=List[TopProduct], summary="Top revenue generating products with stock status")
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_top_products(db, limit=limit)

@router.get("/payments", response_model=List[PaymentBreakdown], summary="Payment methods distribution")
def get_payment_breakdown(db: Session = Depends(get_db)):
    return AnalyticsService.get_payment_breakdown(db)
