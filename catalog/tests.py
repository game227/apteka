import pytest
from django.urls import reverse

from accounts.models import User
from catalog.models import Category, Drug, DrugAlias, Substance
from catalog.services import normalize_and_match, normalize_text, transliterate
from pharmacies.models import ContactMessage


@pytest.fixture
def seeded_drugs(db):
    substance = Substance.objects.create(name_inn="Amoxicillin+Clavulanate", name_uz="Amoksitsillin+Klavulanat")
    paracetamol = Substance.objects.create(name_inn="Paracetamol", name_uz="Paratsetamol")

    amoksiklav = Drug.objects.create(
        trade_name="Amoksiklav", substance=substance, manufacturer="Sandoz",
        dosage_form="tabletka", dosage_strength="625mg", reference_price=42000,
    )
    panadol = Drug.objects.create(
        trade_name="Panadol", substance=paracetamol, manufacturer="GSK",
        dosage_form="tabletka", dosage_strength="500mg", reference_price=12000,
    )
    DrugAlias.objects.create(drug=amoksiklav, alias_text="Амоксиклав")
    DrugAlias.objects.create(drug=amoksiklav, alias_text="amoxiclav")
    DrugAlias.objects.create(drug=panadol, alias_text="панадол")
    return {"amoksiklav": amoksiklav, "panadol": panadol}


def test_transliterate_cyrillic_to_latin():
    assert transliterate("Амоксиклав") == "amoksiklav"


def test_normalize_text_strips_punctuation_and_case():
    assert normalize_text("  Amoksiklav-625  ") == "amoksiklav 625"


def test_exact_trade_name_match(seeded_drugs):
    result = normalize_and_match("Amoksiklav", use_gemini_fallback=False)
    assert result.status == "matched"
    assert result.drug == seeded_drugs["amoksiklav"]
    assert result.confidence == 1.0


def test_exact_cyrillic_alias_match(seeded_drugs):
    result = normalize_and_match("Амоксиклав", use_gemini_fallback=False)
    assert result.status == "matched"
    assert result.drug == seeded_drugs["amoksiklav"]


def test_dosage_suffix_is_stripped_for_matching(seeded_drugs):
    result = normalize_and_match("Amoksiklav 625", use_gemini_fallback=False)
    assert result.status == "matched"
    assert result.drug == seeded_drugs["amoksiklav"]


def test_fuzzy_match_typo(seeded_drugs):
    result = normalize_and_match("Amoksiklaf", use_gemini_fallback=False)
    assert result.status in {"matched", "needs_confirmation"}
    assert result.candidates
    assert result.candidates[0].drug_id == seeded_drugs["amoksiklav"].id


def test_completely_unknown_text_is_not_found(seeded_drugs):
    result = normalize_and_match("Zzxq Notanish Modda 999", use_gemini_fallback=False)
    assert result.status == "not_found"
    assert result.drug is None


def test_empty_text_is_not_found(db):
    result = normalize_and_match("   ", use_gemini_fallback=False)
    assert result.status == "not_found"


def test_different_drugs_do_not_cross_match(seeded_drugs):
    result = normalize_and_match("Panadol", use_gemini_fallback=False)
    assert result.status == "matched"
    assert result.drug == seeded_drugs["panadol"]


def test_contact_view_creates_admin_message(client, db):
    user = User.objects.create_user(username="aziz", password="demo12345")
    client.force_login(user)
    response = client.post(reverse("catalog:contact"), {"subject": "Taklif", "message": "Yaxshi loyiha!"}, follow=True)
    assert response.status_code == 200
    msg = ContactMessage.objects.get()
    assert msg.pharmacy_id is None
    assert msg.sender_id == user.id


def test_terms_view_accessible_without_login(client, db):
    response = client.get(reverse("catalog:terms"))
    assert response.status_code == 200


def test_home_view_accessible_without_login(client, db):
    response = client.get(reverse("catalog:home"))
    assert response.status_code == 200


def test_drug_detail_accessible_without_login(client, seeded_drugs):
    drug = Drug.objects.first()
    response = client.get(drug.get_absolute_url())
    assert response.status_code == 200
    assert response.context["is_favorite"] is False


def test_category_list_and_search_suggest_accessible_without_login(client, db):
    response = client.get(reverse("catalog:category_list"))
    assert response.status_code == 200
    response2 = client.get(reverse("catalog:search_suggest"), {"q": "am"})
    assert response2.status_code == 200


def test_toggle_favorite_still_requires_login(client, seeded_drugs):
    drug = Drug.objects.first()
    response = client.post(reverse("catalog:toggle_favorite", args=[drug.id]))
    assert response.status_code == 302
    assert "/hisob/kirish/" in response.url


def test_compress_image_resizes_and_converts_to_jpeg():
    import io

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    from config.image_utils import compress_image

    buf = io.BytesIO()
    Image.new("RGB", (3000, 2000), color="blue").save(buf, format="PNG")
    upload = SimpleUploadedFile("big.png", buf.getvalue(), content_type="image/png")

    result = compress_image(upload, max_dimension=800)
    assert result.name.endswith(".jpg")

    out = Image.open(result)
    assert max(out.size) <= 800


def test_drug_save_compresses_uploaded_image(db):
    import io

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    substance = Substance.objects.create(name_inn="Test")
    buf = io.BytesIO()
    Image.new("RGB", (2000, 2000), color="red").save(buf, format="PNG")
    upload = SimpleUploadedFile("drug.png", buf.getvalue(), content_type="image/png")

    drug = Drug.objects.create(trade_name="Rasmli dori", substance=substance, image=upload)
    drug.refresh_from_db()
    assert drug.image.name.endswith(".jpg")
    out = Image.open(drug.image)
    assert max(out.size) <= 800
    drug.image.delete(save=False)


def test_uz_timesince_and_is_price_stale():
    from datetime import timedelta

    from django.utils import timezone

    from catalog.templatetags.ui_extras import is_price_stale, uz_timesince

    now = timezone.now()
    assert uz_timesince(now) == "hozirgina"
    assert uz_timesince(now - timedelta(hours=3)) == "3 soat oldin"
    assert uz_timesince(now - timedelta(days=5)) == "5 kun oldin"
    assert uz_timesince(None) == ""

    assert is_price_stale(now - timedelta(days=5)) is False
    assert is_price_stale(now - timedelta(days=31)) is True
    assert is_price_stale(None) is False


def test_category_detail_paginates_drug_list(client, db):
    user = User.objects.create_user(username="aziz", password="demo12345")
    category = Category.objects.create(name_uz="Test turkum")
    substance = Substance.objects.create(name_inn="Test", category=category)
    for i in range(30):
        Drug.objects.create(trade_name=f"Dori {i:02d}", substance=substance)

    client.force_login(user)
    response = client.get(reverse("catalog:category", args=[category.slug]))
    assert response.status_code == 200
    assert len(response.context["drugs"]) == 24
    assert response.context["drugs"].paginator.num_pages == 2

    response2 = client.get(reverse("catalog:category", args=[category.slug]), {"page": 2})
    assert len(response2.context["drugs"]) == 6


def test_contact_view_blocks_rapid_repeat_messages(client, db):
    user = User.objects.create_user(username="aziz", password="demo12345")
    client.force_login(user)
    client.post(reverse("catalog:contact"), {"subject": "1", "message": "birinchi"})
    client.post(reverse("catalog:contact"), {"subject": "2", "message": "ikkinchi"})
    assert ContactMessage.objects.count() == 1
