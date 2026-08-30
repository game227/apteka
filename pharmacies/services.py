"""Geo-masofa (Haversine) va narx upsert yordamchilari.

Dorixonalar soni kichik (o'nlab-yuzlab) bo'lgani uchun PostGIS shart emas —
Python'da hisoblangan Haversine masofasi yetarli va qo'shimcha tizim
bog'liqliklarisiz ishlaydi.
"""

import math

from django.db import transaction

from pharmacies.models import Pharmacy, PharmacyDrugPrice, PriceHistory

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def nearby_prices(drug_id: int, lat: float | None, lng: float | None, radius_km: float | None):
    """PharmacyDrugPrice ro'yxati, har biriga `.distance_km` biriktirilgan
    holda (lat/lng berilmasa — None, narx bo'yicha saralangan)."""
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
        rows = [r for r in rows if r.distance_km <= radius_km]
    rows.sort(key=lambda r: r.distance_km)
    return rows


def nearby_pharmacies(lat: float, lng: float, radius_km: float = 15):
    pharmacies = list(Pharmacy.objects.all())
    for p in pharmacies:
        p.distance_km = round(haversine_km(lat, lng, p.lat, p.lng), 2)
    pharmacies = [p for p in pharmacies if p.distance_km <= radius_km]
    pharmacies.sort(key=lambda p: p.distance_km)
    return pharmacies


@transaction.atomic
def upsert_price(*, pharmacy: Pharmacy, drug, price, in_stock: bool, user) -> PharmacyDrugPrice:
    """Bitta (pharmacy, drug) uchun joriy narxni yangilaydi/yaratadi va
    price_history'ga o'zgarish yozuvini qo'shadi."""
    row, _created = PharmacyDrugPrice.objects.update_or_create(
        pharmacy=pharmacy, drug=drug,
        defaults={"price": price, "in_stock": in_stock, "updated_by": user},
    )
    PriceHistory.objects.create(
        pharmacy=pharmacy, drug=drug, price=price, in_stock=in_stock, changed_by=user,
    )
    return row
