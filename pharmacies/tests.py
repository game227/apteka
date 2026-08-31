import pytest
from django.urls import reverse

from accounts.models import User, UserRole
from catalog.models import Drug, Substance
from pharmacies.models import ContactMessage, Pharmacy, PharmacyDrugPrice
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


@pytest.fixture
def pharmacy(db):
    return Pharmacy.objects.create(name="Shifo Apteka", address="Toshkent", lat=41.3, lng=69.25)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="aziz", password="demo12345")


def test_pharmacy_contact_creates_message_addressed_to_pharmacy(client, user, pharmacy):
    client.force_login(user)
    response = client.post(
        reverse("pharmacies:contact", args=[pharmacy.slug]),
        {"subject": "Ish vaqti", "message": "Bugun ochiqmisiz?"},
        follow=True,
    )
    assert response.status_code == 200
    msg = ContactMessage.objects.get()
    assert msg.pharmacy_id == pharmacy.id
    assert msg.sender_id == user.id
    assert msg.subject == "Ish vaqti"


def test_pharmacy_contact_requires_login(client, pharmacy):
    response = client.post(reverse("pharmacies:contact", args=[pharmacy.slug]), {"subject": "x", "message": "y"})
    assert response.status_code == 302
    assert not ContactMessage.objects.exists()


def test_pharmacy_contact_blocks_rapid_repeat_messages(client, user, pharmacy):
    client.force_login(user)
    client.post(reverse("pharmacies:contact", args=[pharmacy.slug]), {"subject": "1", "message": "birinchi"})
    client.post(reverse("pharmacies:contact", args=[pharmacy.slug]), {"subject": "2", "message": "ikkinchi"})
    assert ContactMessage.objects.count() == 1


@pytest.fixture
def staff_user(db, pharmacy):
    return User.objects.create_user(username="dilnoza", password="demo12345", role=UserRole.PHARMACY_STAFF, pharmacy=pharmacy)


def test_staff_can_delete_own_pharmacy_price(client, staff_user, pharmacy):
    substance = Substance.objects.create(name_inn="Test Substance")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance)
    price = upsert_price(pharmacy=pharmacy, drug=drug, price=10000, in_stock=True, user=staff_user)

    client.force_login(staff_user)
    response = client.post(reverse("pharmacies:staff_price_delete", args=[price.id]))
    assert response.status_code == 302
    assert not PharmacyDrugPrice.objects.filter(id=price.id).exists()


def test_staff_csv_export_contains_prices(client, staff_user, pharmacy):
    substance = Substance.objects.create(name_inn="Test")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance)
    upsert_price(pharmacy=pharmacy, drug=drug, price=12000, in_stock=True, user=staff_user)

    client.force_login(staff_user)
    response = client.get(reverse("pharmacies:staff_csv_export"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    content = response.content.decode()
    assert "Test Drug" in content
    assert "12000" in content


def test_resolve_contact_message_logs_action(client, staff_user, pharmacy):
    from pharmacies.models import AuditLog, ContactMessage

    msg = ContactMessage.objects.create(pharmacy=pharmacy, subject="Sinov", message="m")
    client.force_login(staff_user)
    client.post(reverse("pharmacies:resolve_contact_message", args=[msg.id]))

    log = AuditLog.objects.first()
    assert log is not None
    assert log.actor_id == staff_user.id
    assert "Sinov" in log.action


def test_staff_price_delete_logs_action(client, staff_user, pharmacy):
    from pharmacies.models import AuditLog

    substance = Substance.objects.create(name_inn="Test")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance)
    price = upsert_price(pharmacy=pharmacy, drug=drug, price=10000, in_stock=True, user=staff_user)

    client.force_login(staff_user)
    client.post(reverse("pharmacies:staff_price_delete", args=[price.id]))

    log = AuditLog.objects.first()
    assert log is not None
    assert "Test Drug" in log.action


def test_admin_pharmacy_create_logs_action(client, db):
    from pharmacies.models import AuditLog

    admin = User.objects.create_superuser(username="admin", password="demo12345", email="a@example.com")
    client.force_login(admin)
    client.post(
        reverse("pharmacies:admin_pharmacy_create"),
        {"name": "Yangi Apteka", "address": "Toshkent", "lat": "41.3", "lng": "69.25", "phone": "", "work_hours": "09:00-21:00"},
    )
    log = AuditLog.objects.first()
    assert log is not None
    assert "Yangi Apteka" in log.action


def test_staff_drug_list_paginates(client, staff_user):
    substance = Substance.objects.create(name_inn="Test")
    for i in range(60):
        Drug.objects.create(trade_name=f"Dori {i:02d}", substance=substance)

    client.force_login(staff_user)
    response = client.get(reverse("pharmacies:staff_drug_list"))
    assert len(response.context["drugs"]) == 50
    assert response.context["drugs"].paginator.num_pages == 2


def test_staff_cannot_delete_other_pharmacy_price(client, staff_user):
    other_pharmacy = Pharmacy.objects.create(name="Boshqa", address="X", lat=41.0, lng=69.0)
    substance = Substance.objects.create(name_inn="Test Substance")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance)
    price = upsert_price(pharmacy=other_pharmacy, drug=drug, price=10000, in_stock=True, user=None)

    client.force_login(staff_user)
    response = client.post(reverse("pharmacies:staff_price_delete", args=[price.id]))
    assert response.status_code == 404
    assert PharmacyDrugPrice.objects.filter(id=price.id).exists()
