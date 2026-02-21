from sqlalchemy import func, case, and_, extract
from sqlalchemy.orm import Session
from src.models.merchant_event import MerchantEvent
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics queries and computations."""
    
    @staticmethod
    def get_top_merchant(db: Session) -> dict:
        """
        Returns the merchant with the highest total successful transaction amount.
        Monetary values formatted to 2 decimal places.
        """
        try:
            result = db.query(
                MerchantEvent.merchant_id,
                func.sum(MerchantEvent.amount).label("total_volume")
            ).filter(
                MerchantEvent.status == "SUCCESS",
                MerchantEvent.merchant_id.isnot(None),
                MerchantEvent.amount.isnot(None)
            ).group_by(
                MerchantEvent.merchant_id
            ).order_by(
                func.sum(MerchantEvent.amount).desc()
            ).first()
            
            if not result:
                return {"merchant_id": None, "total_volume": 0.0}
            
            total_volume = 0.0
            if result.total_volume:
                try:
                    total_volume = round(float(result.total_volume), 2)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert total_volume to float: {result.total_volume}")
                    total_volume = 0.0
            
            return {
                "merchant_id": result.merchant_id,
                "total_volume": total_volume
            }
        except Exception as e:
            logger.error(f"Error in get_top_merchant: {e}")
            return {"merchant_id": None, "total_volume": 0.0}
    
    @staticmethod
    def get_monthly_active_merchants(db: Session) -> dict:
        """
        Returns count of unique merchants with at least one successful event per month.
        """
        try:
            results = db.query(
                func.to_char(MerchantEvent.event_timestamp, 'YYYY-MM').label("month"),
                func.count(func.distinct(MerchantEvent.merchant_id)).label("merchant_count")
            ).filter(
                MerchantEvent.status == "SUCCESS",
                MerchantEvent.merchant_id.isnot(None),
                MerchantEvent.event_timestamp.isnot(None)
            ).group_by(
                func.to_char(MerchantEvent.event_timestamp, 'YYYY-MM')
            ).order_by(
                func.to_char(MerchantEvent.event_timestamp, 'YYYY-MM')
            ).all()
            
            return {row.month: (row.merchant_count or 0) for row in results if row.month}
        except Exception as e:
            logger.error(f"Error in get_monthly_active_merchants: {e}")
            return {}
    
    @staticmethod
    def get_product_adoption(db: Session) -> dict:
        """
        Returns unique merchant count per product, sorted by count descending.
        """
        try:
            results = db.query(
                MerchantEvent.product,
                func.count(func.distinct(MerchantEvent.merchant_id)).label("merchant_count")
            ).filter(
                MerchantEvent.product.isnot(None),
                MerchantEvent.merchant_id.isnot(None)
            ).group_by(
                MerchantEvent.product
            ).order_by(
                func.count(func.distinct(MerchantEvent.merchant_id)).desc()
            ).all()
            
            return {row.product: (row.merchant_count or 0) for row in results if row.product}
        except Exception as e:
            logger.error(f"Error in get_product_adoption: {e}")
            return {}
    
    @staticmethod
    def get_kyc_funnel(db: Session) -> dict:
        """
        Returns KYC conversion funnel (unique merchants at each stage, successful events only).
        """
        try:
            stages = ["STARTER", "VERIFIED", "PREMIUM"]
            result = {}
            
            for stage in stages:
                count = db.query(
                    func.count(func.distinct(MerchantEvent.merchant_id))
                ).filter(
                    MerchantEvent.merchant_tier == stage,
                    MerchantEvent.status == "SUCCESS",
                    MerchantEvent.merchant_id.isnot(None)
                ).scalar()
                
                result[f"tier_{stage.lower()}"] = count or 0
            
            return result
        except Exception as e:
            logger.error(f"Error in get_kyc_funnel: {e}")
            return {"tier_starter": 0, "tier_verified": 0, "tier_premium": 0}
    
    @staticmethod
    def get_failure_rates(db: Session) -> list:
        """
        Returns failure rate per product: (FAILED / (SUCCESS + FAILED)) x 100.
        Excludes PENDING events. Sorted by rate descending.
        Percentages formatted to 1 decimal place.
        """
        try:
            results = db.query(
                MerchantEvent.product,
                func.count(case((MerchantEvent.status == "FAILED", 1))).label("failed_count"),
                func.count(case((MerchantEvent.status == "SUCCESS", 1))).label("success_count")
            ).filter(
                MerchantEvent.product.isnot(None),
                MerchantEvent.status.in_(["SUCCESS", "FAILED"])
            ).group_by(
                MerchantEvent.product
            ).all()
            
            failure_rates = []
            for row in results:
                try:
                    failed_count = int(row.failed_count) if row.failed_count else 0
                    success_count = int(row.success_count) if row.success_count else 0
                    total = failed_count + success_count
                    
                    if total > 0:
                        rate = (failed_count / total) * 100
                        failure_rates.append({
                            "product": row.product or "UNKNOWN",
                            "failure_rate": round(rate, 1)
                        })
                except (ValueError, TypeError, ZeroDivisionError) as e:
                    logger.warning(f"Could not calculate failure rate for product {row.product}: {e}")
                    continue
            
            # Sort by failure_rate descending
            failure_rates.sort(key=lambda x: x["failure_rate"], reverse=True)
            
            return failure_rates
        except Exception as e:
            logger.error(f"Error in get_failure_rates: {e}")
            return []
