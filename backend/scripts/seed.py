"""Test uchun demo ma'lumotlar kiritish (idempotent — qayta ishga tushirish xavfsiz).

Ishga tushirish:
    cd backend && .venv/bin/python -m scripts.seed
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models.drug import Drug
from app.models.drug_alias import DrugAlias
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_drug_price import PharmacyDrugPrice
from app.models.pharmacy_invite import PharmacyInvite
from app.models.substance import Substance
from app.models.user import User, UserRole
from app.services.geo import point

random.seed(42)

SUBSTANCES = [
    ("Amoxicillin + Clavulanic acid", "Amoksitsillin + Klavulanat kislotasi"),
    ("Paracetamol", "Paratsetamol"),
    ("Ibuprofen", "Ibuprofen"),
    ("Omeprazole", "Omeprazol"),
    ("Loratadine", "Loratadin"),
    ("Metformin", "Metformin"),
    ("Azithromycin", "Azitromitsin"),
]

# (trade_name, substance_index, manufacturer, dosage_form, dosage_strength, reference_price, aliases)
DRUGS = [
    ("Amoxiclav", 0, "Lek (Slovenia)", "tabletka", "500mg/125mg", 45000, ["Амоксиклав", "amoksiklav"]),
    ("Augmentin", 0, "GSK", "tabletka", "500mg/125mg", 68000, ["Аугментин"]),
    ("Panadol", 1, "GSK", "tabletka", "500mg", 12000, ["Панадол"]),
    ("Paracetamol-Farmak", 1, "Farmak", "tabletka", "500mg", 4500, ["Парацетамол", "paracetamol"]),
    ("Nurofen", 2, "Reckitt", "tabletka", "200mg", 18000, ["Нурофен"]),
    ("Ibuprofen-Nika", 2, "Nika Pharm", "tabletka", "400mg", 8000, ["Ибупрофен", "ibuprofen"]),
    ("Omez", 3, "Dr. Reddy's", "kapsula", "20mg", 24000, ["Омез"]),
    ("Ultop", 3, "KRKA", "kapsula", "20mg", 27000, ["Ултоп"]),
    ("Claritin", 4, "Bayer", "tabletka", "10mg", 32000, ["Кларитин"]),
    ("Loratadin-Teva", 4, "Teva", "tabletka", "10mg", 9000, ["Лоратадин", "loratadin"]),
    ("Siofor", 5, "Berlin-Chemie", "tabletka", "500mg", 35000, ["Сиофор"]),
    ("Metformin-SZ", 5, "Severnaya Zvezda", "tabletka", "850mg", 15000, ["Метформин", "metformin"]),
    ("Sumamed", 6, "Teva/Pliva", "tabletka", "500mg", 42000, ["Сумамед"]),
    ("Azithromycin-Lekform", 6, "Lekform", "kapsula", "250mg", 20000, ["Азитромицин", "azithromycin"]),
]

# (name, address, lat, lng, phone)
PHARMACIES = [
    ("Oq Tepa Apteka", "Chilonzor tumani, Bunyodkor shoh ko'chasi 12", 41.2856, 69.2034, "+998901234501"),
    ("Shifo Dorixonasi", "Yunusobod tumani, Amir Temur ko'chasi 45", 41.3417, 69.2880, "+998901234502"),
    ("Salomatlik Apteka", "Mirzo Ulug'bek tumani, Universitet ko'chasi 8", 41.3275, 69.3149, "+998901234503"),
    ("Doristor", "Yakkasaroy tumani, Mustaqillik shoh ko'chasi 21", 41.2937, 69.2565, "+998901234504"),
    ("Farmatsiya Plus", "Sergeli tumani, Qatortol ko'chasi 3", 41.2263, 69.2192, "+998901234505"),
    ("Med Apteka 24", "Mirobod tumani, Nukus ko'chasi 17", 41.3033, 69.2951, "+998901234506"),
]

OVERPRICE_THRESHOLD = 0.20


def round_to_500(value: float) -> float:
    return round(value / 500) * 500


def main() -> None:
    db = SessionLocal()
    try:
        if db.execute(select(Substance.id)).first() is not None:
            print("Ma'lumotlar allaqachon mavjud — seed o'tkazib yuborildi.")
            return

        substances = [Substance(name_inn=inn, name_uz=uz) for inn, uz in SUBSTANCES]
        db.add_all(substances)
        db.flush()

        drugs: list[Drug] = []
        for trade_name, sub_idx, manufacturer, dosage_form, dosage_strength, ref_price, aliases in DRUGS:
            drug = Drug(
                trade_name=trade_name,
                substance_id=substances[sub_idx].id,
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
            pharmacy = Pharmacy(
                name=name, address=address, lat=lat, lng=lng, phone=phone, geom=point(lat, lng)
            )
            db.add(pharmacy)
            pharmacies.append(pharmacy)
        db.flush()

        users = [
            User(telegram_id=111, full_name="Aziz Karimov", telegram_username="aziz_karimov", role=UserRole.user),
            User(
                telegram_id=222,
                full_name="Dilnoza Yusupova",
                telegram_username="dilnoza_y",
                role=UserRole.pharmacy_staff,
                pharmacy_id=pharmacies[0].id,
            ),
            User(
                telegram_id=333,
                full_name="Admin Boshqaruvchi",
                telegram_username="admin_boshqaruvchi",
                role=UserRole.admin,
            ),
        ]
        db.add_all(users)

        for pharmacy in pharmacies:
            offered_drugs = random.sample(drugs, k=random.randint(9, len(drugs)))
            # Har bir dorixonada kamida 2 ta "shubhali qimmat" (>20%) narx bo'lishini kafolatlaymiz
            forced_overpriced = set(random.sample(offered_drugs, k=min(2, len(offered_drugs))))
            for drug in offered_drugs:
                if drug in forced_overpriced:
                    factor = random.uniform(1.22, 1.45)
                else:
                    factor = random.uniform(0.85, 1.18)
                price = round_to_500(float(drug.reference_price) * factor)
                db.add(
                    PharmacyDrugPrice(
                        pharmacy_id=pharmacy.id,
                        drug_id=drug.id,
                        price=price,
                        in_stock=random.random() > 0.12,
                    )
                )

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
            f"Seed tayyor: {len(substances)} ta faol modda, {len(drugs)} ta dori, "
            f"{len(pharmacies)} ta dorixona, {len(users)} ta demo foydalanuvchi (telegram_id 111/222/333)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
