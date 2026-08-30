from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.drug import Drug
from app.routers.drugs import to_search_result
from app.schemas.prescription import (
    DetectedDrugItem,
    MatchCandidate,
    PrescriptionConfirmRequest,
    PrescriptionConfirmResponse,
    PrescriptionScanResponse,
)
from app.schemas.drug import DrugPricesResponse
from app.services.gemini_vision import scan_prescription_image
from app.services.normalization import normalize_and_match
from app.services.pricing import get_drug_prices

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


@router.post("/scan", response_model=PrescriptionScanResponse)
async def scan_prescription(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp", "image/heic"}:
        raise HTTPException(status_code=400, detail="Faqat rasm fayli qabul qilinadi")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Rasm hajmi juda katta (max 10MB)")

    raw_names = scan_prescription_image(image_bytes, mime_type=file.content_type)

    items: list[DetectedDrugItem] = []
    for raw_name in raw_names:
        match = normalize_and_match(raw_name, db)[0]
        items.append(
            DetectedDrugItem(
                raw_text=match.raw_text,
                matched_drug_id=match.drug_id,
                matched_trade_name=match.trade_name,
                confidence=match.confidence,
                status=match.status,
                candidates=[
                    MatchCandidate(drug_id=c.drug_id, trade_name=c.trade_name, score=c.score)
                    for c in match.candidates
                ],
            )
        )

    return PrescriptionScanResponse(items=items)


@router.post("/confirm", response_model=PrescriptionConfirmResponse)
def confirm_prescription(payload: PrescriptionConfirmRequest, db: Session = Depends(get_db)):
    results: list[DrugPricesResponse] = []
    for item in payload.items:
        drug = db.get(Drug, item.drug_id)
        if drug is None:
            raise HTTPException(status_code=404, detail=f"drug_id={item.drug_id} topilmadi")

        prices = get_drug_prices(db, drug, lat=payload.lat, lng=payload.lng, radius_km=payload.radius_km)
        results.append(DrugPricesResponse(drug=_to_search_result(drug), prices=prices))

    return PrescriptionConfirmResponse(results=results)
