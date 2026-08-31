import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from accounts.models import User
from catalog.models import Drug, DrugAlias, Substance
from prescriptions.models import PrescriptionScan, PrescriptionScanItem


def _fake_image_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="white").save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="aziz", password="demo12345")


@pytest.fixture
def seeded_drug(db):
    substance = Substance.objects.create(name_inn="Paracetamol", name_uz="Paratsetamol")
    drug = Drug.objects.create(trade_name="Panadol", substance=substance, dosage_strength="500mg", reference_price=12000)
    DrugAlias.objects.create(drug=drug, alias_text="панадол")
    return drug


def test_upload_view_requires_login(client, db):
    response = client.get(reverse("prescriptions:upload"))
    assert response.status_code == 302


def test_upload_view_renders_for_logged_in_user(client, user):
    client.force_login(user)
    response = client.get(reverse("prescriptions:upload"))
    assert response.status_code == 200


def test_scan_view_redirects_without_image(client, user):
    client.force_login(user)
    response = client.post(reverse("prescriptions:scan"))
    assert response.status_code == 302
    assert response.url == reverse("prescriptions:upload")


def test_scan_view_matches_recognized_drug_names(client, user, seeded_drug, monkeypatch, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    monkeypatch.setattr(
        "prescriptions.services.scan_prescription_image",
        lambda image_bytes, mime_type="image/jpeg": ["Panadol", "Notanish Dori Nomi 999"],
    )

    client.force_login(user)
    image = SimpleUploadedFile("retsept.png", _fake_image_bytes(), content_type="image/png")
    response = client.post(reverse("prescriptions:scan"), {"image": image})

    assert response.status_code == 200
    scan = PrescriptionScan.objects.get(user=user)
    items = list(scan.items.all())
    assert len(items) == 2

    matched_item = next(i for i in items if i.raw_text == "Panadol")
    assert matched_item.status == "matched"
    assert matched_item.matched_drug_id == seeded_drug.id

    unmatched_item = next(i for i in items if i.raw_text != "Panadol")
    assert unmatched_item.status == "not_found"
    assert unmatched_item.matched_drug_id is None


def test_scan_view_with_no_recognized_names_creates_empty_scan(client, user, monkeypatch, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    monkeypatch.setattr("prescriptions.services.scan_prescription_image", lambda image_bytes, mime_type="image/jpeg": [])

    client.force_login(user)
    image = SimpleUploadedFile("retsept.png", _fake_image_bytes(), content_type="image/png")
    response = client.post(reverse("prescriptions:scan"), {"image": image})

    assert response.status_code == 200
    scan = PrescriptionScan.objects.get(user=user)
    assert scan.items.count() == 0


def test_scan_view_shows_error_message_when_gemini_unavailable(client, user, monkeypatch, settings, tmp_path):
    from django.contrib.messages import get_messages

    from prescriptions.services import GeminiUnavailableError

    settings.MEDIA_ROOT = tmp_path

    def _raise(image_bytes, mime_type="image/jpeg"):
        raise GeminiUnavailableError("kvota tugadi")

    monkeypatch.setattr("prescriptions.services.scan_prescription_image", _raise)

    client.force_login(user)
    image = SimpleUploadedFile("retsept.png", _fake_image_bytes(), content_type="image/png")
    response = client.post(reverse("prescriptions:scan"), {"image": image})

    assert response.status_code == 200
    scan = PrescriptionScan.objects.get(user=user)
    assert scan.items.count() == 0
    error_messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert any("hozir ishlamayapti" in m for m in error_messages)


def test_confirm_view_sets_confirmed_drug_and_returns_prices(client, user, seeded_drug, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    scan = PrescriptionScan.objects.create(user=user, image=SimpleUploadedFile("r.png", _fake_image_bytes()))
    item = PrescriptionScanItem.objects.create(
        scan=scan, raw_text="Panadol", matched_drug=seeded_drug, confidence=1.0, status="matched",
    )

    client.force_login(user)
    response = client.post(reverse("prescriptions:confirm", args=[scan.id]), {f"drug_{item.id}": seeded_drug.id})

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.confirmed_drug_id == seeded_drug.id
    assert response.context["results"][0]["drug"] == seeded_drug


def test_confirm_view_only_accessible_for_own_scan(client, user, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    other_user = User.objects.create_user(username="dilnoza", password="demo12345")
    scan = PrescriptionScan.objects.create(user=other_user, image=SimpleUploadedFile("r.png", _fake_image_bytes()))

    client.force_login(user)
    response = client.post(reverse("prescriptions:confirm", args=[scan.id]), {})
    assert response.status_code == 404


def test_history_view_lists_only_own_scans(client, user, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    other_user = User.objects.create_user(username="dilnoza", password="demo12345")
    own_scan = PrescriptionScan.objects.create(user=user, image=SimpleUploadedFile("r.png", _fake_image_bytes()))
    PrescriptionScan.objects.create(user=other_user, image=SimpleUploadedFile("r2.png", _fake_image_bytes()))

    client.force_login(user)
    response = client.get(reverse("prescriptions:history"))

    assert response.status_code == 200
    scans = list(response.context["scans"])
    assert scans == [own_scan]
