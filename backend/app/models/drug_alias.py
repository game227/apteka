from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class DrugAlias(Base):
    __tablename__ = "drug_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_id: Mapped[int] = mapped_column(ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False)
    alias_text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    drug: Mapped["Drug"] = relationship("Drug", back_populates="aliases")
