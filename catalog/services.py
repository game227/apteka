"""Dori nomini normalizatsiya qilish va bazadagi Drug'ga moslashtirish.

Qatlamlar (birinchi ishonchli natija qaytariladi):
  1. Aniq moslik (trade_name yoki alias, translit+tozalashdan keyin)
  2. Fuzzy matching (rapidfuzz)
  3. Gemini-yordamida taxmin (past ishonch bilan, doim "tasdiqlang" holatida)

Retsept skaneri (prescriptions) va qo'lda qidiruv (catalog qidiruvi)
ikkalasi ham shu funksiyadan foydalanadi.
"""

import re
from dataclasses import dataclass, field

from django.conf import settings
from rapidfuzz import fuzz, process

from catalog.models import Drug, DrugAlias

_CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ц": "s", "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "",
    "ы": "i", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h",
}
_DOSAGE_SUFFIX_RE = re.compile(r"\s*\d+([.,]\d+)?\s*(mg|ml|g|mcg|мг|мл|г|таб|tab)?\.?\s*$", re.IGNORECASE)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9' ]+")
_WHITESPACE_RE = re.compile(r"\s+")


def transliterate(text: str) -> str:
    return "".join(_CYRILLIC_TO_LATIN.get(ch, ch) for ch in text.lower())


def normalize_text(text: str, strip_dosage: bool = False) -> str:
    text = transliterate(text.strip().lower())
    if strip_dosage:
        text = _DOSAGE_SUFFIX_RE.sub("", text)
    text = _NON_ALNUM_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


@dataclass
class MatchCandidate:
    drug_id: int
    trade_name: str
    score: float


@dataclass
class MatchResult:
    raw_text: str
    drug: Drug | None
    confidence: float
    method: str
    status: str  # matched | needs_confirmation | not_found
    candidates: list[MatchCandidate] = field(default_factory=list)


class _Catalog:
    def __init__(self):
        rows: list[tuple[int, str, str]] = []
        for drug_id, trade_name in Drug.objects.values_list("id", "trade_name"):
            rows.append((drug_id, trade_name, normalize_text(trade_name)))
        for drug_id, alias_text in DrugAlias.objects.values_list("drug_id", "alias_text"):
            rows.append((drug_id, alias_text, normalize_text(alias_text)))

        self.rows = rows
        self.by_normalized: dict[str, tuple[int, str]] = {}
        for drug_id, trade_name, norm in rows:
            self.by_normalized.setdefault(norm, (drug_id, trade_name))

    def exact(self, normalized: str):
        return self.by_normalized.get(normalized)

    def fuzzy(self, normalized: str, limit: int = 5):
        if not self.rows:
            return []
        choices = {i: r[2] for i, r in enumerate(self.rows)}
        return process.extract(normalized, choices, scorer=fuzz.WRatio, limit=limit)


def normalize_and_match(raw_text: str, use_gemini_fallback: bool = True) -> MatchResult:
    raw_text = raw_text.strip()
    if not raw_text:
        return MatchResult(raw_text=raw_text, drug=None, confidence=0.0, method="not_found", status="not_found")

    catalog = _Catalog()

    for strip_dosage in (False, True):
        norm = normalize_text(raw_text, strip_dosage=strip_dosage)
        hit = catalog.exact(norm)
        if hit:
            drug_id, _ = hit
            drug = Drug.objects.select_related("substance").get(id=drug_id)
            method = "exact_alias" if strip_dosage else "exact_trade_name"
            return MatchResult(raw_text=raw_text, drug=drug, confidence=1.0, method=method, status="matched")

    norm = normalize_text(raw_text, strip_dosage=True)
    fuzzy_matches = catalog.fuzzy(norm, limit=5)
    if fuzzy_matches:
        candidates: list[MatchCandidate] = []
        seen: set[int] = set()
        for _text, score, idx in fuzzy_matches:
            drug_id, trade_name, _norm = catalog.rows[idx]
            if drug_id in seen:
                continue
            seen.add(drug_id)
            candidates.append(MatchCandidate(drug_id=drug_id, trade_name=trade_name, score=score))

        if candidates:
            top = candidates[0]
            confidence = top.score / 100.0
            if top.score >= settings.FUZZY_MATCH_THRESHOLD:
                drug = Drug.objects.select_related("substance").get(id=top.drug_id)
                return MatchResult(
                    raw_text=raw_text, drug=drug, confidence=confidence, method="fuzzy",
                    status="matched", candidates=candidates,
                )
            if top.score >= settings.FUZZY_MATCH_CONFIRM_THRESHOLD:
                return MatchResult(
                    raw_text=raw_text, drug=None, confidence=confidence, method="fuzzy",
                    status="needs_confirmation", candidates=candidates,
                )

    if use_gemini_fallback and settings.GEMINI_API_KEY:
        from prescriptions.services import guess_substance_name

        guessed = guess_substance_name(raw_text)
        if guessed:
            return MatchResult(
                raw_text=f"{raw_text} (taxmin: {guessed})", drug=None, confidence=0.3,
                method="gemini_suggested", status="needs_confirmation",
            )

    return MatchResult(raw_text=raw_text, drug=None, confidence=0.0, method="not_found", status="not_found")
