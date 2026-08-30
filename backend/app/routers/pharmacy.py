import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db, require_pharmacy_staff
from app.models.drug import Drug
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_drug_price import PharmacyDrugPrice
from app.models.user import User
from app.schemas.pharmacy import (
    CsvRowError,
    CsvUploadResult,
    PharmacyOut,
    PharmacyPriceIn,
    PharmacyPriceOut,
)
from app.services.pricing import upsert_pharmacy_price

router = APIRouter(prefix="/pharmacy/my", tags=["pharmacy"])


@router.get("", response_model=PharmacyOut)
def my_pharmacy(user: User = Depends(require_pharmacy_staff), db: Session = Depends(get_db)):
    pharmacy = db.get(Pharmacy, user.pharmacy_id)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Dorixona topilmadi")
    return pharmacy


@router.get("/prices", response_model=list[PharmacyPriceOut])
def my_pharmacy_prices(user: User = Depends(require_pharmacy_staff), db: Session = Depends(get_db)):
    rows = db.execute(
        select(PharmacyDrugPrice, Drug.trade_name)
        .join(Drug, Drug.id == PharmacyDrugPrice.drug_id)
        .where(PharmacyDrugPrice.pharmacy_id == user.pharmacy_id)
    ).all()
    return [
        PharmacyPriceOut(
            drug_id=pdp.drug_id,
            trade_name=trade_name,
            price=float(pdp.price),
            in_stock=pdp.in_stock,
            updated_at=pdp.updated_at,
        )
        for pdp, trade_name in rows
    ]


@router.post("/prices", response_model=PharmacyPriceOut)
def upsert_my_price(
    payload: PharmacyPriceIn,
    user: User = Depends(require_pharmacy_staff),
    db: Session = Depends(get_db),
):
    drug = db.get(Drug, payload.drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail="Dori topilmadi")

    row = upsert_pharmacy_price(
        db,
        pharmacy_id=user.pharmacy_id,
        drug_id=payload.drug_id,
        price=payload.price,
        in_stock=payload.in_stock,
        updated_by_user_id=user.id,
    )
    db.commit()
    return PharmacyPriceOut(
        drug_id=row.drug_id,
        trade_name=drug.trade_name,
        price=float(row.price),
        in_stock=row.in_stock,
        updated_at=row.updated_at,
    )


@router.post("/prices/csv", response_model=CsvUploadResult)
async def upload_prices_csv(
    file: UploadFile = File(...),
    user: User = Depends(require_pharmacy_staff),
    db: Session = Depends(get_db),
):
    raw = (await file.read()).decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))

    errors: list[CsvRowError] = []
    imported = 0

    for row_number, raw_row in enumerate(reader, start=2):  # 1-qator = sarlavha
        try:
            drug_id_field = (raw_row.get("drug_id") or "").strip()
            trade_name_field = (raw_row.get("trade_name") or "").strip()
            price_field = (raw_row.get("price") or "").strip()
            in_stock_field = (raw_row.get("in_stock") or "true").strip().lower()

            if not price_field:
                raise ValueError("price ustuni bo'sh")
            price = float(price_field)
            if price <= 0:
                raise ValueError("price musbat son bo'lishi kerak")

            in_stock = in_stock_field in {"1", "true", "yes", "ha"}

            drug: Drug | None = None
            if drug_id_field:
                drug = db.get(Drug, int(drug_id_field))
            elif trade_name_field:
                drug = db.execute(
                    select(Drug).where(Drug.trade_name.ilike(trade_name_field))
                ).scalars().first()

            if drug is None:
                raise ValueError("dori topilmadi (drug_id yoki trade_name noto'g'ri)")

            upsert_pharmacy_price(
                db,
                pharmacy_id=user.pharmacy_id,
                drug_id=drug.id,
                price=price,
                in_stock=in_stock,
                updated_by_user_id=user.id,
            )
            imported += 1
        except Exception as exc:  # noqa: BLE001 - har bir qatorni alohida xato sifatida yig'amiz
            errors.append(CsvRowError(row_number=row_number, raw=raw_row, error=str(exc)))

    db.commit()
    return CsvUploadResult(imported=imported, errors=errors)
