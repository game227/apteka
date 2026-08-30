"""Drug-name normalization & matching.

Layered strategy (tried in order, first confident hit wins):
  1. Exact match against `drug_aliases` / `drugs.trade_name`.
  2. Same exact match after Cyrillic->Latin transliteration + cleanup.
  3. Fuzzy matching (rapidfuzz) against all known trade names/aliases.
  4. Gemini-assisted guess (substance name), still surfaced as "needs_confirmation".

Used by both the prescription scanner (app.services.gemini_vision) and the
manual drug search endpoint, so it lives here as one independently testable
unit. Matching requires the drug catalog, so `db` is a required argument
(a Session, real or test-fixture) — everything else about the function is
pure and deterministic given that data.
"""

import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz, process
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.drug import Drug
from app.models.drug_alias import DrugAlias

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
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


@dataclass
class MatchCandidate:
    drug_id: int
    trade_name: str
    score: float


@dataclass
class MatchResult:
    raw_text: str
    drug_id: int | None
    trade_name: str | None
    substance_id: int | None
    confidence: float  # 0..1
    method: str  # exact_alias | exact_trade_name | fuzzy | gemini_suggested | not_found
    status: str  # matched | needs_confirmation | not_found
    candidates: list[MatchCandidate] = field(default_factory=list)


class _Catalog:
    """Loads (drug_id, substance_id, searchable_text) rows once per call."""

    def __init__(self, db: Session):
        rows: list[tuple[int, int, str, str]] = []  # drug_id, substance_id, trade_name, normalized

        for drug_id, substance_id, trade_name in db.execute(
            select(Drug.id, Drug.substance_id, Drug.trade_name)
        ).all():
            rows.append((drug_id, substance_id, trade_name, normalize_text(trade_name)))

        for drug_id, substance_id, alias_text in db.execute(
            select(DrugAlias.drug_id, Drug.substance_id, DrugAlias.alias_text).join(
                Drug, Drug.id == DrugAlias.drug_id
            )
        ).all():
            rows.append((drug_id, substance_id, alias_text, normalize_text(alias_text)))

        self.rows = rows
        self.by_normalized: dict[str, tuple[int, int, str]] = {}
        for drug_id, substance_id, trade_name, norm in rows:
            self.by_normalized.setdefault(norm, (drug_id, substance_id, trade_name))

    def exact(self, normalized: str) -> tuple[int, int, str] | None:
        return self.by_normalized.get(normalized)

    def fuzzy(self, normalized: str, limit: int = 5) -> list[tuple[str, float, int]]:
        if not self.rows:
            return []
        choices = {i: r[3] for i, r in enumerate(self.rows)}
        matches = process.extract(normalized, choices, scorer=fuzz.WRatio, limit=limit)
        return matches  # list of (normalized_text, score, index)


def normalize_and_match(
    raw_text: str,
    db: Session,
    use_gemini_fallback: bool = True,
) -> list[MatchResult]:
    """Resolve a single raw drug-name string (as read off a prescription or
    typed by a user) to one or more candidate `drugs` rows.

    Returns a list because a single line of text can plausibly refer to more
    than one product (ambiguous fuzzy matches) — the caller decides whether
    to auto-pick the top one or ask the user to confirm, based on `.status`.
    """
    settings = get_settings()
    raw_text = raw_text.strip()
    if not raw_text:
        return [
            MatchResult(
                raw_text=raw_text, drug_id=None, trade_name=None, substance_id=None,
                confidence=0.0, method="not_found", status="not_found",
            )
        ]

    catalog = _Catalog(db)

    # 1 & 2: exact match, with and without dosage suffix stripped.
    for strip_dosage in (False, True):
        norm = normalize_text(raw_text, strip_dosage=strip_dosage)
        hit = catalog.exact(norm)
        if hit:
            drug_id, substance_id, trade_name = hit
            method = "exact_alias" if strip_dosage else "exact_trade_name"
            return [
                MatchResult(
                    raw_text=raw_text, drug_id=drug_id, trade_name=trade_name,
                    substance_id=substance_id, confidence=1.0, method=method, status="matched",
                )
            ]

    # 3: fuzzy matching.
    norm = normalize_text(raw_text, strip_dosage=True)
    fuzzy_matches = catalog.fuzzy(norm, limit=5)
    if fuzzy_matches:
        candidates: list[MatchCandidate] = []
        seen_drug_ids: set[int] = set()
        for _text, score, idx in fuzzy_matches:
            drug_id, _substance_id, trade_name, _norm = catalog.rows[idx]
            if drug_id in seen_drug_ids:
                continue
            seen_drug_ids.add(drug_id)
            candidates.append(MatchCandidate(drug_id=drug_id, trade_name=trade_name, score=score))

        if candidates:
            top = candidates[0]
            confidence = top.score / 100.0
            if top.score >= settings.fuzzy_match_threshold:
                drug_id, substance_id, trade_name, _ = next(
                    r for r in catalog.rows if r[0] == top.drug_id
                )
                return [
                    MatchResult(
                        raw_text=raw_text, drug_id=drug_id, trade_name=trade_name,
                        substance_id=substance_id, confidence=confidence, method="fuzzy",
                        status="matched", candidates=candidates,
                    )
                ]
            if top.score >= settings.fuzzy_match_confirm_threshold:
                return [
                    MatchResult(
                        raw_text=raw_text, drug_id=None, trade_name=top.trade_name,
                        substance_id=None, confidence=confidence, method="fuzzy",
                        status="needs_confirmation", candidates=candidates,
                    )
                ]

    # 4: Gemini-assisted guess — always surfaced as needs_confirmation.
    if use_gemini_fallback and settings.gemini_api_key:
        from app.services.gemini_vision import guess_substance_name

        guessed = guess_substance_name(raw_text)
        if guessed:
            return [
                MatchResult(
                    raw_text=raw_text, drug_id=None, trade_name=guessed,
                    substance_id=None, confidence=0.3, method="gemini_suggested",
                    status="needs_confirmation",
                )
            ]

    return [
        MatchResult(
            raw_text=raw_text, drug_id=None, trade_name=None, substance_id=None,
            confidence=0.0, method="not_found", status="not_found",
        )
    ]
