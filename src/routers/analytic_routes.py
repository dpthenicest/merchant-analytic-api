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
  top_merchant = AnalyticsService.get_top_merchant(session)
  if not top_merchant:
      raise HTTPException(status_code=404, detail="Top merchant not found")
  return top_merchant

@analytic_router.get("/monthly-active-merchants")
def get_monthly_active_merchants(session: Session = Depends(get_session)):
  monthly_active_merchants = AnalyticsService.get_monthly_active_merchants(session)
  if not monthly_active_merchants:
      raise HTTPException(status_code=404, detail="Monthly active merchants not found")
  return monthly_active_merchants

@analytic_router.get("/product-adoption")
def get_product_adoption(session: Session = Depends(get_session)):
  product_adoption = AnalyticsService.get_product_adoption(session)
  if not product_adoption:
      raise HTTPException(status_code=404, detail="Product adoption data not found")
  return product_adoption

@analytic_router.get("/kyc-funnel")
def get_kyc_funnel(session: Session = Depends(get_session)):
  kyc_funnel = AnalyticsService.get_kyc_funnel(session)
  if not kyc_funnel:
      raise HTTPException(status_code=404, detail="KYC funnel data not found")
  return kyc_funnel

@analytic_router.get("/failure-rates")
def get_failure_rates(session: Session = Depends(get_session)):
  failure_rates = AnalyticsService.get_failure_rates(session)
  if not failure_rates:
      raise HTTPException(status_code=404, detail="Failure rates data not found")
  return failure_rates
