import pytest

from catalog.models import Drug, Substance
from pharmacies.models import Pharmacy
from pharmacies.services import haversine_km, upsert_price


def test_haversine_same_point_is_zero():
    assert haversine_km(41.31, 69.27, 41.31, 69.27) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance():
    # Toshkent markazi -> Chilonzor markazi, taxminan ~7 km
    d = haversine_km(41.3111, 69.2797, 41.2856, 69.2034)
    assert 5 < d < 10


@pytest.mark.django_db
def test_upsert_price_updates_deviation_and_history():
    substance = Substance.objects.create(name_inn="Test Substance")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance, reference_price=10000)
    pharmacy = Pharmacy.objects.create(name="Test Pharmacy", address="Test", lat=41.3, lng=69.25)

    row = upsert_price(pharmacy=pharmacy, drug=drug, price=13000, in_stock=True, user=None)
    assert row.deviation_pct == pytest.approx(30.0)
    assert row.is_overpriced is True
    assert pharmacy.price_history.count() == 1

    # Qayta yozilganda faqat bitta "joriy" yozuv qoladi, lekin tarixga yana bittasi qo'shiladi
    row2 = upsert_price(pharmacy=pharmacy, drug=drug, price=9000, in_stock=False, user=None)
    assert row.pk == row2.pk
    assert row2.is_overpriced is False
    assert pharmacy.prices.count() == 1
    assert pharmacy.price_history.count() == 2
