from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Drug(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    trade_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    substance_id: Mapped[int] = mapped_column(ForeignKey("substances.id", ondelete="RESTRICT"), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dosage_strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reference_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    substance: Mapped["Substance"] = relationship("Substance")  # noqa: F821
    aliases: Mapped[list["DrugAlias"]] = relationship(  # noqa: F821
        "DrugAlias", back_populates="drug", cascade="all, delete-orphan"
    )
