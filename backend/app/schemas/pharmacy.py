from datetime import datetime

from pydantic import BaseModel, Field


class PharmacyOut(BaseModel):
    id: int
    name: str
    address: str
    lat: float
    lng: float
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PharmacyCreate(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    phone: str | None = None


class PharmacyInviteOut(BaseModel):
    token: str
    pharmacy_id: int
    expires_at: datetime


class PharmacyPriceIn(BaseModel):
    drug_id: int
    price: float = Field(gt=0)
    in_stock: bool = True


class PharmacyPriceOut(BaseModel):
    drug_id: int
    trade_name: str
    price: float
    in_stock: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class CsvRowError(BaseModel):
    row_number: int
    raw: dict
    error: str


class CsvUploadResult(BaseModel):
    imported: int
    errors: list[CsvRowError]
