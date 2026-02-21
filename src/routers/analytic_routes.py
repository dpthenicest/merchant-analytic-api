from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from src.services.analytics_service import AnalyticsService
from src.database.database import get_session
from fastapi import APIRouter, Depends

analytic_router = APIRouter(
  prefix="/analytics",
  tags=["analytics"]
)

@analytic_router.get("/top-merchant")
def get_top_merchant(session: Session = Depends(get_session)):
  return AnalyticsService.get_top_merchant(session)

@analytic_router.get("/monthly-active-merchants")
def get_monthly_active_merchants(session: Session = Depends(get_session)):
  return AnalyticsService.get_monthly_active_merchants(session)

@analytic_router.get("/product-adoption")
def get_product_adoption(session: Session = Depends(get_session)):
  return AnalyticsService.get_product_adoption(session)

@analytic_router.get("/kyc-funnel")
def get_kyc_funnel(session: Session = Depends(get_session)):
  return AnalyticsService.get_kyc_funnel(session)

@analytic_router.get("/failure-rates")
def get_failure_rates(session: Session = Depends(get_session)):
  return AnalyticsService.get_failure_rates(session)
