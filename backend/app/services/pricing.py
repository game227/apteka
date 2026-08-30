from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.drug import Drug
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_drug_price import PharmacyDrugPrice
from app.models.price_history import PriceHistory
from app.schemas.drug import DrugPriceEntry
from app.services.geo import distance_km_expr, point


def compute_deviation(
    price: float, reference_price: float | None, threshold: float
) -> tuple[float | None, bool]:
    """(price - reference_price) / reference_price. >threshold => shubhali/qimmat."""
    if not reference_price:
        return None, False
    deviation = (price - reference_price) / reference_price
    return deviation, deviation > threshold


def get_drug_prices(
    db: Session,
    drug: Drug,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = None,
) -> list[DrugPriceEntry]:
    settings = get_settings()
    ref_price = float(drug.reference_price) if drug.reference_price is not None else None

    query = (
        select(PharmacyDrugPrice, Pharmacy)
        .join(Pharmacy, Pharmacy.id == PharmacyDrugPrice.pharmacy_id)
        .where(PharmacyDrugPrice.drug_id == drug.id)
    )

    has_location = lat is not None and lng is not None
    if has_location:
        dist_expr = distance_km_expr(lat, lng)
        query = query.add_columns(dist_expr.label("distance_km"))
        if radius_km:
            query = query.where(func.ST_DWithin(Pharmacy.geom, point(lat, lng), radius_km * 1000))
        query = query.order_by(dist_expr)
    else:
        query = query.order_by(PharmacyDrugPrice.price)

    rows = db.execute(query).all()

    results: list[DrugPriceEntry] = []
    for row in rows:
        if has_location:
            pdp, pharmacy, distance_km = row
        else:
            pdp, pharmacy = row
            distance_km = None

        deviation, overpriced = compute_deviation(
            float(pdp.price), ref_price, settings.price_deviation_threshold
        )
        results.append(
            DrugPriceEntry(
                pharmacy_id=pharmacy.id,
                pharmacy_name=pharmacy.name,
                pharmacy_address=pharmacy.address,
                distance_km=round(distance_km, 2) if distance_km is not None else None,
                price=float(pdp.price),
                in_stock=pdp.in_stock,
                reference_price=ref_price,
                deviation_pct=round(deviation * 100, 1) if deviation is not None else None,
                is_overpriced=overpriced,
                updated_at=pdp.updated_at.isoformat(),
            )
        )
    return results


def upsert_pharmacy_price(
    db: Session,
    pharmacy_id: int,
    drug_id: int,
    price: float,
    in_stock: bool,
    updated_by_user_id: int,
) -> PharmacyDrugPrice:
    """One current row per (pharmacy_id, drug_id); always bump updated_at /
    updated_by_user_id even if price/in_stock are unchanged. Also appends a
    snapshot to price_history.
    """
    existing = db.execute(
        select(PharmacyDrugPrice).where(
            PharmacyDrugPrice.pharmacy_id == pharmacy_id,
            PharmacyDrugPrice.drug_id == drug_id,
        )
    ).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if existing:
        existing.price = price
        existing.in_stock = in_stock
        existing.updated_by_user_id = updated_by_user_id
        existing.updated_at = now
        row = existing
    else:
        row = PharmacyDrugPrice(
            pharmacy_id=pharmacy_id,
            drug_id=drug_id,
            price=price,
            in_stock=in_stock,
            updated_by_user_id=updated_by_user_id,
            updated_at=now,
        )
        db.add(row)

    db.add(
        PriceHistory(
            pharmacy_id=pharmacy_id,
            drug_id=drug_id,
            price=price,
            in_stock=in_stock,
            changed_by_user_id=updated_by_user_id,
            recorded_at=now,
        )
    )
    db.flush()
    return row
