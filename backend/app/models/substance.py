from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Substance(Base):
    __tablename__ = "substances"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_inn: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_uz: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_ru: Mapped[str | None] = mapped_column(String(255), nullable=True)
