"""Demo/test ma'lumotlarini DB'ga kiritish.

Har ishga tushirishda demo jadvallarni (narxlar tarixi, narxlar, takliflar,
alias'lar, dorilar, faol moddalar, dorixonalar, demo foydalanuvchilar) tozalab,
`scripts/seed_data.py` dagi to'liq to'plamdan qayta yozadi — faqat dev/test
muhiti uchun, productionda ishlatilmaydi.

Ishga tushirish:
    cd backend && .venv/bin/python -m scripts.seed
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db import SessionLocal
from app.models.drug import Drug
from app.models.drug_alias import DrugAlias
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_drug_price import PharmacyDrugPrice
from app.models.pharmacy_invite import PharmacyInvite
from app.models.price_history import PriceHistory
from app.models.substance import Substance
from app.models.user import User, UserRole
from app.services.geo import point
from app.services.pricing import upsert_pharmacy_price
from scripts.seed_data import DRUGS, PHARMACIES, SUBSTANCES

random.seed(42)

DEMO_USERS = [
    (111, "Aziz Karimov", "aziz_karimov", UserRole.user, None),
    (222, "Dilnoza Yusupova", "dilnoza_y", UserRole.pharmacy_staff, 0),  # pharmacy index 0
    (333, "Admin Boshqaruvchi", "admin_boshqaruvchi", UserRole.admin, None),
]

MIN_DRUGS_PER_PHARMACY = 40
MAX_DRUGS_PER_PHARMACY_RATIO = 0.75  # jami dorilarning shu ulushigacha
FORCED_OVERPRICED_PER_PHARMACY = 3  # har dorixonada kamida shuncha >20% qimmat narx


def round_to_500(value: float) -> float:
    return round(value / 500) * 500


def wipe_demo_data(db) -> None:
    for model in (PriceHistory, PharmacyDrugPrice, PharmacyInvite, DrugAlias, Drug, Substance, User, Pharmacy):
        db.execute(delete(model))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        wipe_demo_data(db)

        substances_by_inn = {}
        for name_inn, name_uz, name_ru in SUBSTANCES:
            substance = Substance(name_inn=name_inn, name_uz=name_uz, name_ru=name_ru)
            db.add(substance)
            substances_by_inn[name_inn] = substance
        db.flush()

        drugs: list[Drug] = []
        for name_inn, entries in DRUGS.items():
            substance = substances_by_inn[name_inn]
            for trade_name, manufacturer, dosage_form, dosage_strength, ref_price, aliases in entries:
                drug = Drug(
                    trade_name=trade_name,
                    substance_id=substance.id,
                    manufacturer=manufacturer,
                    dosage_form=dosage_form,
                    dosage_strength=dosage_strength,
                    reference_price=ref_price,
                )
                db.add(drug)
                db.flush()
                for alias_text in aliases:
                    db.add(DrugAlias(drug_id=drug.id, alias_text=alias_text))
                drugs.append(drug)

        pharmacies: list[Pharmacy] = []
        for name, address, lat, lng, phone in PHARMACIES:
            pharmacy = Pharmacy(name=name, address=address, lat=lat, lng=lng, phone=phone, geom=point(lat, lng))
            db.add(pharmacy)
            pharmacies.append(pharmacy)
        db.flush()

        users: list[User] = []
        for telegram_id, full_name, username, role, pharmacy_idx in DEMO_USERS:
            users.append(
                User(
                    telegram_id=telegram_id,
                    full_name=full_name,
                    telegram_username=username,
                    role=role,
                    pharmacy_id=pharmacies[pharmacy_idx].id if pharmacy_idx is not None else None,
                )
            )
        db.add_all(users)
        db.flush()
        seeder_user_id = next(u.id for u in users if u.role == UserRole.admin)

        max_per_pharmacy = max(MIN_DRUGS_PER_PHARMACY, int(len(drugs) * MAX_DRUGS_PER_PHARMACY_RATIO))
        price_rows = 0
        for pharmacy in pharmacies:
            k = random.randint(MIN_DRUGS_PER_PHARMACY, min(max_per_pharmacy, len(drugs)))
            offered_drugs = random.sample(drugs, k=k)
            forced_overpriced = set(random.sample(offered_drugs, k=min(FORCED_OVERPRICED_PER_PHARMACY, len(offered_drugs))))
            for drug in offered_drugs:
                factor = random.uniform(1.22, 1.5) if drug in forced_overpriced else random.uniform(0.85, 1.18)
                price = round_to_500(float(drug.reference_price) * factor)
                upsert_pharmacy_price(
                    db,
                    pharmacy_id=pharmacy.id,
                    drug_id=drug.id,
                    price=price,
                    in_stock=random.random() > 0.12,
                    updated_by_user_id=seeder_user_id,
                )
                price_rows += 1

        # Admin panelda "taklif havolasi" oqimini sinash uchun bitta ishlatilmagan taklif
        db.add(
            PharmacyInvite(
                pharmacy_id=pharmacies[1].id,
                token="demo-invite-token-0001",
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
        )

        db.commit()
        print(
            f"Seed tayyor: {len(substances_by_inn)} ta faol modda, {len(drugs)} ta dori, "
            f"{len(pharmacies)} ta dorixona, {len(users)} ta demo foydalanuvchi "
            f"(telegram_id 111/222/333), {price_rows} ta narx yozuvi."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
