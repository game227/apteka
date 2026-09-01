"""Geo-masofa (Haversine) va narx upsert yordamchilari.

Dorixonalar soni kichik (o'nlab-yuzlab) bo'lgani uchun PostGIS shart emas —
Python'da hisoblangan Haversine masofasi yetarli va qo'shimcha tizim
bog'liqliklarisiz ishlaydi.
"""

import math
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from pharmacies.models import AuditLog, ContactMessage, Pharmacy, PharmacyDrugPrice, PriceHistory

EARTH_RADIUS_KM = 6371.0
CONTACT_MESSAGE_COOLDOWN = timedelta(minutes=2)


def log_action(user, action: str) -> None:
    """Admin panelidagi faoliyat tarixi uchun bitta qatorli yozuv."""
    AuditLog.objects.create(actor=user if getattr(user, "is_authenticated", False) else None, action=action)


def contact_message_cooldown_remaining(user) -> int | None:
    """Foydalanuvchi hozir xabar yubora oladimi — bo'lsa None, aks holda
    qolgan soniyalar soni (spam'dan himoya uchun oddiy cooldown)."""
    last = ContactMessage.objects.filter(sender=user).order_by("-created_at").first()
    if not last:
        return None
    elapsed = timezone.now() - last.created_at
    if elapsed >= CONTACT_MESSAGE_COOLDOWN:
        return None
    return int((CONTACT_MESSAGE_COOLDOWN - elapsed).total_seconds())


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def nearby_prices(drug_id: int, lat: float | None, lng: float | None, radius_km: float | None = None):
    """PharmacyDrugPrice ro'yxati, har biriga `.distance_km` biriktirilgan
    holda (lat/lng berilmasa — None, narx bo'yicha saralangan).

    `radius_km` faqat foydalanuvchi aniq radius so'ragan hollar uchun
    ixtiyoriy qattiq filtr — standart holatda YO'Q, chunki foydalanuvchining
    haqiqiy joylashuvi bazadagi dorixonalardan (masalan boshqa shahar/
    mamlakat) uzoq bo'lishi juda oddiy holat, va "hech narsa topilmadi"
    ko'rsatish o'rniga har doim mavjud narxlarni eng yaqinidan boshlab
    ko'rsatish to'g'riroq (xarita ilovalari qanday ishlaydi)."""
    qs = (
        PharmacyDrugPrice.objects.select_related("pharmacy", "drug", "drug__substance")
        .filter(drug_id=drug_id)
    )
    rows = list(qs)

    if lat is None or lng is None:
        rows.sort(key=lambda r: r.price)
        for r in rows:
            r.distance_km = None
        return rows

    for r in rows:
        r.distance_km = round(haversine_km(lat, lng, r.pharmacy.lat, r.pharmacy.lng), 2)
    if radius_km:
        within = [r for r in rows if r.distance_km <= radius_km]
        if within:
            rows = within
    rows.sort(key=lambda r: r.distance_km)
    return rows


def nearby_pharmacies(lat: float | None, lng: float | None, radius_km: float | None = None):
    """Barcha dorixonalar ro'yxati, har biriga `.distance_km` biriktirilgan
    holda (lat/lng berilmasa — None, nomi bo'yicha saralangan)."""
    pharmacies = list(Pharmacy.objects.all())
    if lat is None or lng is None:
        for p in pharmacies:
            p.distance_km = None
        return pharmacies

    for p in pharmacies:
        p.distance_km = round(haversine_km(lat, lng, p.lat, p.lng), 2)
    if radius_km:
        within = [p for p in pharmacies if p.distance_km <= radius_km]
        if within:
            pharmacies = within
    pharmacies.sort(key=lambda p: p.distance_km)
    return pharmacies


@transaction.atomic
def upsert_price(*, pharmacy: Pharmacy, drug, price, in_stock: bool, user) -> PharmacyDrugPrice:
    """Bitta (pharmacy, drug) uchun joriy narxni yangilaydi/yaratadi va
    price_history'ga o'zgarish yozuvini qo'shadi. Narx pasaysa, shu dorini
    sevimli qilib belgilagan foydalanuvchilarga bildirishnoma yaratiladi."""
    existing = PharmacyDrugPrice.objects.filter(pharmacy=pharmacy, drug=drug).first()
    old_price = existing.price if existing else None

    row, _created = PharmacyDrugPrice.objects.update_or_create(
        pharmacy=pharmacy, drug=drug,
        defaults={"price": price, "in_stock": in_stock, "updated_by": user},
    )
    PriceHistory.objects.create(
        pharmacy=pharmacy, drug=drug, price=price, in_stock=in_stock, changed_by=user,
    )

    if old_price is not None and float(price) < float(old_price):
        from catalog.models import Favorite, PriceDropAlert

        favoriters = Favorite.objects.filter(drug=drug).exclude(user=user).values_list("user_id", flat=True)
        PriceDropAlert.objects.bulk_create(
            [
                PriceDropAlert(user_id=uid, drug=drug, pharmacy=pharmacy, old_price=old_price, new_price=price)
                for uid in favoriters
            ]
        )

    return row
