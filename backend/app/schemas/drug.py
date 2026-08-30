from pydantic import BaseModel

MEDICAL_ADVICE_WARNING = "Bu ma'lumot tibbiy maslahat emas. Shifokor yoki farmatsevt bilan maslahatlashing."


class DrugSearchResult(BaseModel):
    id: int
    trade_name: str
    manufacturer: str | None
    dosage_form: str | None
    dosage_strength: str | None
    substance_id: int
    substance_name_inn: str
    reference_price: float | None

    model_config = {"from_attributes": True}


class DrugPriceEntry(BaseModel):
    pharmacy_id: int
    pharmacy_name: str
    pharmacy_address: str
    distance_km: float | None
    price: float
    in_stock: bool
    reference_price: float | None
    deviation_pct: float | None
    is_overpriced: bool
    updated_at: str


class DrugPricesResponse(BaseModel):
    drug: DrugSearchResult
    prices: list[DrugPriceEntry]


class DrugAlternative(BaseModel):
    id: int
    trade_name: str
    manufacturer: str | None
    dosage_form: str | None
    dosage_strength: str | None
    reference_price: float | None

    model_config = {"from_attributes": True}


class DrugAlternativesResponse(BaseModel):
    substance_id: int
    substance_name_inn: str
    alternatives: list[DrugAlternative]
    warning: str = MEDICAL_ADVICE_WARNING
