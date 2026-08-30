"""Gemini-backed helpers: (1) reading drug names off a prescription photo,
(2) a last-resort guess of a substance/INN name when normalization's
alias/fuzzy layers find nothing. Both are best-effort — any failure here
must degrade gracefully (empty list / None), never break the request.
"""

import json
import logging
import re

from app.config import get_settings

logger = logging.getLogger(__name__)

_SCAN_PROMPT = """\
Bu — qo'lda yozilgan yoki bosma shifokor retsepti rasmi.
Rasmda ko'rsatilgan barcha dori nomlarini (savdo nomi yoki ta'sir moddasi) aniqlang.
Faqat quyidagi JSON formatda javob bering, boshqa hech narsa yozmang:
{"drugs": ["dori nomi 1", "dori nomi 2"]}
Agar rasmda hech qanday dori nomi topilmasa: {"drugs": []}
"""

_GUESS_PROMPT = """\
Quyidagi matn — dorixona retsepti yoki foydalanuvchi tomonidan yozilgan dori nomi
bo'lishi mumkin, ehtimol xato yoki noaniq yozilgan: "{raw_text}"

Bu qaysi dori yoki ta'sir moddasi (INN) nomiga eng yaqin bo'lishi mumkinligini
taxmin qiling. Faqat nom(lar)ni qisqa qilib yozing, izoh yozmang. Agar hech
narsa taxmin qila olmasangiz, faqat "NOMA'LUM" deb javob bering.
"""


def _get_client():
    settings = get_settings()
    if not settings.gemini_api_key:
        return None, None
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    return client, settings.gemini_model


def scan_prescription_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> list[str]:
    """Returns raw drug-name strings as read off the image (unvalidated —
    caller must run each through normalize_and_match)."""
    client, model = _get_client()
    if client is None:
        logger.warning("GEMINI_API_KEY sozlanmagan, retsept skaneri ishlamaydi")
        return []

    try:
        from google.genai import types

        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                _SCAN_PROMPT,
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text or "{}"
        data = json.loads(text)
        drugs = data.get("drugs", [])
        return [d.strip() for d in drugs if isinstance(d, str) and d.strip()]
    except Exception:
        logger.exception("Gemini retsept skanerlashda xatolik")
        return []


def guess_substance_name(raw_text: str) -> str | None:
    client, model = _get_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=model,
            contents=_GUESS_PROMPT.format(raw_text=raw_text),
        )
        guess = (response.text or "").strip()
        guess = re.sub(r"^[\"'\-\s]+|[\"'\-\s]+$", "", guess)
        if not guess or guess.upper() == "NOMA'LUM" or "NOMA" in guess.upper():
            return None
        return guess.splitlines()[0].strip()
    except Exception:
        logger.exception("Gemini nom taxminida xatolik")
        return None
