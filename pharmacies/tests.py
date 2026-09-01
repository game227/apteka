import pytest
from django.urls import reverse

from accounts.models import User, UserRole
from catalog.models import Drug, Favorite, PriceDropAlert, Substance
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


@pytest.mark.django_db
def test_price_drop_creates_alert_for_favoriting_users_only():
    substance = Substance.objects.create(name_inn="Test Substance")
    drug = Drug.objects.create(trade_name="Test Drug", substance=substance)
    pharmacy = Pharmacy.objects.create(name="Test Pharmacy", address="Test", lat=41.3, lng=69.25)
    staff = User.objects.create_user(username="staff1", password="demo12345", role=UserRole.PHARMACY_STAFF, pharmacy=pharmacy)
    fan = User.objects.create_user(username="fan1", password="demo12345")
    other = User.objects.create_user(username="other1", password="demo12345")
    Favorite.objects.create(user=fan, drug=drug)

    upsert_price(pharmacy=pharmacy, drug=drug, price=10000, in_stock=True, user=staff)
    assert PriceDropAlert.objects.count() == 0  # birinchi narx — pasayish emas

    upsert_price(pharmacy=pharmacy, drug=drug, price=8000, in_stock=True, user=staff)
    alerts = PriceDropAlert.objects.all()
    assert alerts.count() == 1
    alert = alerts.first()
    assert alert.user_id == fan.id
    assert alert.old_price == 10000
    assert alert.new_price == 8000
    assert alert.discount_pct == 20
    assert not PriceDropAlert.objects.filter(user=other).exists()
    assert not PriceDropAlert.objects.filter(user=staff).exists()

    # Narx oshsa — bildirishnoma yaratilmaydi
    upsert_price(pharmacy=pharmacy, drug=drug, price=9000, in_stock=True, user=staff)
    assert PriceDropAlert.objects.count() == 1


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


def test_staff_can_update_own_pharmacy_contact_info(client, staff_user, pharmacy):
    client.force_login(staff_user)
    response = client.post(
        reverse("pharmacies:staff_contact_info_update"),
        {"phone": "+998901234567", "telegram": "@apteka_bot", "work_hours": "08:00-22:00"},
    )
    assert response.status_code == 302
    pharmacy.refresh_from_db()
    assert pharmacy.phone == "+998901234567"
    assert pharmacy.telegram == "@apteka_bot"
    assert pharmacy.telegram_url == "https://t.me/apteka_bot"
    assert pharmacy.work_hours == "08:00-22:00"


def test_staff_contact_info_update_requires_login(client, pharmacy):
    response = client.post(reverse("pharmacies:staff_contact_info_update"), {"phone": "123"})
    assert response.status_code == 302
    pharmacy.refresh_from_db()
    assert pharmacy.phone == ""


def test_pharmacy_qr_code_returns_png(client, user, pharmacy):
    client.force_login(user)
    response = client.get(reverse("pharmacies:qr", args=[pharmacy.slug]))
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_pharmacy_maps_url_uses_coordinates(pharmacy):
    assert str(pharmacy.lat) in pharmacy.maps_url
    assert str(pharmacy.lng) in pharmacy.maps_url


def test_pharmacy_list_accessible_without_login(client, pharmacy):
    response = client.get(reverse("pharmacies:list"))
    assert response.status_code == 200


def test_pharmacy_detail_accessible_without_login(client, pharmacy):
    response = client.get(pharmacy.get_absolute_url())
    assert response.status_code == 200
    assert response.context["review_form"] is None


def test_pharmacy_qr_accessible_without_login(client, pharmacy):
    response = client.get(reverse("pharmacies:qr", args=[pharmacy.slug]))
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"


def test_pharmacy_list_search_and_sort(client, user, pharmacy):
    far_pharmacy = Pharmacy.objects.create(name="Uzoq Apteka", address="Samarqand", lat=39.65, lng=66.97)
    client.force_login(user)

    response = client.get(reverse("pharmacies:list"))
    assert response.status_code == 200
    assert list(response.context["pharmacies"]) == [pharmacy, far_pharmacy]  # nomi bo'yicha (Meta.ordering)

    response = client.get(reverse("pharmacies:list"), {"q": "Shifo"})
    assert list(response.context["pharmacies"]) == [pharmacy]

    response = client.get(reverse("pharmacies:list"), {"lat": 41.3, "lng": 69.25, "sort": "distance"})
    results = list(response.context["pharmacies"])
    assert results[0] == pharmacy  # yaqinroq birinchi
    assert results[0].distance_km < results[1].distance_km


def test_admin_dashboard_shows_top_drugs_and_active_pharmacies(client, staff_user, pharmacy):
    admin = User.objects.create_superuser(username="bossadmin", email="a@a.com", password="demo12345")
    substance = Substance.objects.create(name_inn="Test Substance")
    popular = Drug.objects.create(trade_name="Popular Drug", substance=substance, search_hits=42)
    Drug.objects.create(trade_name="Unsearched Drug", substance=substance, search_hits=0)
    upsert_price(pharmacy=pharmacy, drug=popular, price=10000, in_stock=True, user=staff_user)
    upsert_price(pharmacy=pharmacy, drug=popular, price=9000, in_stock=True, user=staff_user)

    client.force_login(admin)
    response = client.get(reverse("pharmacies:admin_dashboard"))
    assert response.status_code == 200
    assert list(response.context["top_drugs"]) == [popular]
    assert list(response.context["active_pharmacies"]) == [pharmacy]
    assert response.context["active_pharmacies"][0].price_update_count == 2


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
