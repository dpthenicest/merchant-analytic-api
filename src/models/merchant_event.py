import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Numeric, text, UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.database.database import Base

class MerchantEvent(Base):
    # Using underscore instead of hyphen for standard SQL compatibility
    __tablename__ = "merchant_events"

    # Explicitly using UUID type for PostgreSQL native support
    # as_uuid=True ensures SQLAlchemy gives you a Python uuid.UUID object
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()") 
    )
    
    merchant_id: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    
    # DateTime with timezone=True is best practice for audit logs - nullable
    event_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        default=None,
    )

    product: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    event_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Decimal is the standard for financial data (precision 15, scale 2) - defaults to 0
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))

    # Status, Channel, and Tier as strings (can be further optimized with Enums) - nullable
    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    merchant_tier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Event {self.event_id} | Merchant {self.merchant_id} | {self.amount} NGN>"