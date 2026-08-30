from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.drug import Drug
from app.models.drug_alias import DrugAlias
from app.models.substance import Substance
from app.schemas.drug import (
    DrugAlternative,
    DrugAlternativesResponse,
    DrugPricesResponse,
    DrugSearchResult,
)
from app.services.normalization import normalize_and_match
from app.services.pricing import get_drug_prices

router = APIRouter(prefix="/drugs", tags=["drugs"])


def to_search_result(drug: Drug) -> DrugSearchResult:
    return DrugSearchResult(
        id=drug.id,
        trade_name=drug.trade_name,
        manufacturer=drug.manufacturer,
        dosage_form=drug.dosage_form,
        dosage_strength=drug.dosage_strength,
        substance_id=drug.substance_id,
        substance_name_inn=drug.substance.name_inn,
        reference_price=float(drug.reference_price) if drug.reference_price is not None else None,
    )


@router.get("/search", response_model=list[DrugSearchResult])
def search_drugs(q: str = Query(..., min_length=1), limit: int = 20, db: Session = Depends(get_db)):
    like = f"%{q.strip()}%"
    stmt = (
        select(Drug)
        .join(Substance, Substance.id == Drug.substance_id)
        .outerjoin(DrugAlias, DrugAlias.drug_id == Drug.id)
        .where((Drug.trade_name.ilike(like)) | (DrugAlias.alias_text.ilike(like)))
        .distinct()
        .limit(limit)
    )
    drugs = list(db.execute(stmt).scalars().all())
    if drugs:
        return [to_search_result(d) for d in drugs]

    # To'g'ridan-to'g'ri moslik topilmasa — fuzzy fallback (Gemini'siz, tez javob uchun).
    match = normalize_and_match(q, db, use_gemini_fallback=False)[0]
    if not match.candidates:
        return []
    candidate_ids = [c.drug_id for c in match.candidates]
    rows = {d.id: d for d in db.execute(select(Drug).where(Drug.id.in_(candidate_ids))).scalars().all()}
    ordered = [rows[cid] for cid in candidate_ids if cid in rows]
    return [to_search_result(d) for d in ordered]


@router.get("/{drug_id}/prices", response_model=DrugPricesResponse)
def drug_prices(
    drug_id: int,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
    db: Session = Depends(get_db),
):
    drug = db.get(Drug, drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail="Dori topilmadi")

    prices = get_drug_prices(db, drug, lat=lat, lng=lng, radius_km=radius_km)
    return DrugPricesResponse(drug=to_search_result(drug), prices=prices)


@router.get("/{drug_id}/alternatives", response_model=DrugAlternativesResponse)
def drug_alternatives(drug_id: int, db: Session = Depends(get_db)):
    drug = db.get(Drug, drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail="Dori topilmadi")

    others = db.execute(
        select(Drug).where(Drug.substance_id == drug.substance_id, Drug.id != drug.id)
    ).scalars().all()

    return DrugAlternativesResponse(
        substance_id=drug.substance_id,
        substance_name_inn=drug.substance.name_inn,
        alternatives=[
            DrugAlternative(
                id=d.id,
                trade_name=d.trade_name,
                manufacturer=d.manufacturer,
                dosage_form=d.dosage_form,
                dosage_strength=d.dosage_strength,
                reference_price=float(d.reference_price) if d.reference_price is not None else None,
            )
            for d in others
        ],
    )
