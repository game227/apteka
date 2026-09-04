import random
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User, UserRole
from catalog.demo_data import CATEGORIES, DRUGS, PHARMACIES
from catalog.models import Category, Drug, DrugAlias, Substance
from config.image_utils import compress_image
from pharmacies.models import Pharmacy, PharmacyDrugPrice, PharmacyInvite, PriceHistory
from pharmacies.services import upsert_price

MIN_DRUGS_PER_PHARMACY = 20
FORCED_OVERPRICED_PER_PHARMACY = 3

DEMO_IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "demo_images"

# Savdo nomi -> demo_images/ ichidagi fayl nomi. Haqiqiy qadoq fotolari
# (Wikimedia Commons, ochiq litsenziyali) — demo bazani ko'rgazmali qilish
# uchun; Drug.save() ularni avtomatik siqadi (config.image_utils.compress_image).
DRUG_IMAGE_FILES = {
    "Panadol": "panadol.jpg",
    "Nurofen": "nurofen.jpg",
    "Sumamed": "sumamed.jpg",
    "No-shpa": "no-shpa.jpg",
    "Smecta": "smecta.jpg",
    "Voltaren": "voltaren.jpg",
    "Amoksiklav": "amoksiklav.jpg",
    "Augmentin": "augmentin.jpg",
    "Vitrum": "vitrum.jpg",
    "Omez": "omez.jpg",
}


class Command(BaseCommand):
    help = "Demo ma'lumotlarni bazaga kiritadi (dev/test uchun, har ishga tushirishda qayta yozadi)."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        for model in (PriceHistory, PharmacyDrugPrice, PharmacyInvite, DrugAlias, Drug, Substance, Category, Pharmacy):
            model.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        substances_by_inn = {}
        for icon, cat_name, subs in CATEGORIES:
            category = Category.objects.create(name_uz=cat_name, icon=icon)
            for name_inn, name_uz in subs:
                substances_by_inn[name_inn] = Substance.objects.create(
                    name_inn=name_inn, name_uz=name_uz, category=category
                )

        drugs = []
        for name_inn, entries in DRUGS.items():
            substance = substances_by_inn[name_inn]
            for trade_name, manufacturer, dosage_form, dosage_strength, ref_price, aliases in entries:
                drug = Drug.objects.create(
                    trade_name=trade_name, substance=substance, manufacturer=manufacturer,
                    dosage_form=dosage_form, dosage_strength=dosage_strength, reference_price=ref_price,
                )
                DrugAlias.objects.bulk_create([DrugAlias(drug=drug, alias_text=a) for a in aliases])
                image_file = DRUG_IMAGE_FILES.get(trade_name)
                if image_file:
                    with open(DEMO_IMAGES_DIR / image_file, "rb") as f:
                        compressed = compress_image(File(f, name=image_file), max_dimension=800)
                    drug.image.save(compressed.name, compressed, save=True)
                drugs.append(drug)

        pharmacies = [
            Pharmacy.objects.create(name=name, address=address, lat=lat, lng=lng, phone=phone)
            for name, address, lat, lng, phone in PHARMACIES
        ]

        demo_users = [
            ("aziz", "Aziz", UserRole.USER, None),
            ("dilnoza", "Dilnoza", UserRole.PHARMACY_STAFF, pharmacies[0]),
        ]
        for username, first_name, role, pharmacy in demo_users:
            user = User.objects.create_user(username=username, password="demo12345", first_name=first_name, role=role)
            if pharmacy:
                user.pharmacy = pharmacy
                user.save(update_fields=["pharmacy"])
            seeder_user = user

        price_rows = 0
        for pharmacy in pharmacies:
            k = random.randint(MIN_DRUGS_PER_PHARMACY, len(drugs))
            offered = random.sample(drugs, k=k)
            overpriced = set(random.sample(offered, k=min(FORCED_OVERPRICED_PER_PHARMACY, len(offered))))
            for drug in offered:
                factor = random.uniform(1.22, 1.5) if drug in overpriced else random.uniform(0.85, 1.18)
                price = round(float(drug.reference_price) * factor / 500) * 500
                upsert_price(pharmacy=pharmacy, drug=drug, price=price, in_stock=random.random() > 0.1, user=seeder_user)
                price_rows += 1

        PharmacyInvite.objects.create(pharmacy=pharmacies[1])

        self.stdout.write(self.style.SUCCESS(
            f"Seed tayyor: {len(substances_by_inn)} modda, {len(drugs)} dori, "
            f"{len(pharmacies)} dorixona, {price_rows} narx yozuvi.\n"
            f"Demo hisoblar: aziz/demo12345 (user), dilnoza/demo12345 (pharmacy_staff, {pharmacies[0].name}).\n"
            f"Admin: `createsuperuser` orqali serverdan yaratiladi."
        ))
