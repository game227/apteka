import pytest

from catalog.models import Drug, DrugAlias, Substance
from catalog.services import normalize_and_match, normalize_text, transliterate


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
