from sqlalchemy.orm import Session

from app.services.normalization import normalize_and_match, normalize_text, transliterate


def test_transliterate_cyrillic_to_latin():
    assert transliterate("Амоксиклав") == "amoksiklav"


def test_normalize_text_strips_punctuation_and_case():
    assert normalize_text("  Amoksiklav-625  ") == "amoksiklav 625"


def test_exact_trade_name_match(db: Session):
    results = normalize_and_match("Amoksiklav", db, use_gemini_fallback=False)
    assert len(results) == 1
    result = results[0]
    assert result.status == "matched"
    assert result.trade_name == "Amoksiklav"
    assert result.confidence == 1.0


def test_exact_cyrillic_alias_match(db: Session):
    results = normalize_and_match("Амоксиклав", db, use_gemini_fallback=False)
    result = results[0]
    assert result.status == "matched"
    assert result.trade_name == "Amoksiklav"


def test_dosage_suffix_is_stripped_for_matching(db: Session):
    results = normalize_and_match("Amoksiklav 625", db, use_gemini_fallback=False)
    result = results[0]
    assert result.status == "matched"
    assert result.trade_name == "Amoksiklav"


def test_fuzzy_match_typo_needs_or_auto_confirms(db: Session):
    # bitta harf xato — Levenshtein masofasi kichik, baland ball berishi kerak
    results = normalize_and_match("Amoksiklaf", db, use_gemini_fallback=False)
    result = results[0]
    assert result.status in {"matched", "needs_confirmation"}
    assert result.trade_name == "Amoksiklav"
    assert result.drug_id is not None or result.status == "needs_confirmation"


def test_completely_unknown_text_is_not_found(db: Session):
    results = normalize_and_match("Zzxq Notanish Modda 999", db, use_gemini_fallback=False)
    result = results[0]
    assert result.status == "not_found"
    assert result.drug_id is None


def test_empty_text_is_not_found(db: Session):
    results = normalize_and_match("   ", db, use_gemini_fallback=False)
    assert results[0].status == "not_found"


def test_different_drugs_do_not_cross_match(db: Session):
    results = normalize_and_match("Panadol", db, use_gemini_fallback=False)
    result = results[0]
    assert result.status == "matched"
    assert result.trade_name == "Panadol"
