from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PharmacyDrugPrice(Base):
    """Current price per (pharmacy, drug) pair. Upsert-only — one row per pair.

    Full history (if enabled) lives in PriceHistory, appended on every change.
    """

    __tablename__ = "pharmacy_drug_prices"
    __table_args__ = (UniqueConstraint("pharmacy_id", "drug_id", name="uq_pharmacy_drug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    pharmacy_id: Mapped[int] = mapped_column(ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False)
    drug_id: Mapped[int] = mapped_column(ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    pharmacy: Mapped["Pharmacy"] = relationship("Pharmacy")  # noqa: F821
    drug: Mapped["Drug"] = relationship("Drug")  # noqa: F821
