from typing import Literal

from pydantic import BaseModel

from app.schemas.drug import DrugPricesResponse


class MatchCandidate(BaseModel):
    drug_id: int
    trade_name: str
    score: float


class DetectedDrugItem(BaseModel):
    raw_text: str
    matched_drug_id: int | None
    matched_trade_name: str | None
    confidence: float
    status: Literal["matched", "needs_confirmation", "not_found"]
    candidates: list[MatchCandidate] = []


class PrescriptionScanResponse(BaseModel):
    items: list[DetectedDrugItem]


class ConfirmedDrugItem(BaseModel):
    drug_id: int
    raw_text: str | None = None


class PrescriptionConfirmRequest(BaseModel):
    items: list[ConfirmedDrugItem]
    lat: float | None = None
    lng: float | None = None
    radius_km: float = 10


class PrescriptionConfirmResponse(BaseModel):
    results: list[DrugPricesResponse]
