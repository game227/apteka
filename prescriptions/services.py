"""Gemini-yordamida: (1) retsept rasmidan dori nomlarini o'qish,
(2) hech narsa topilmaganda substance/INN nomini taxmin qilish.
Ikkalasi ham best-effort — xato bo'lsa jim tarzda bo'sh natija qaytaradi."""

import json
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiUnavailableError(Exception):
    """Gemini chaqiruvi muvaffaqiyatsiz tugadi (tarmoq, kvota, kalit va h.k.) —
    'hech qanday dori topilmadi' bilan chalkashmasligi uchun alohida turdagi xato."""

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
    if not settings.GEMINI_API_KEY:
        return None, None
    from google import genai

    return genai.Client(api_key=settings.GEMINI_API_KEY), settings.GEMINI_MODEL


def scan_prescription_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> list[str]:
    client, model = _get_client()
    if client is None:
        logger.warning("GEMINI_API_KEY sozlanmagan, retsept skaneri ishlamaydi")
        raise GeminiUnavailableError("GEMINI_API_KEY sozlanmagan")
    try:
        from google.genai import types

        response = client.models.generate_content(
            model=model,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), _SCAN_PROMPT],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(response.text or "{}")
        return [d.strip() for d in data.get("drugs", []) if isinstance(d, str) and d.strip()]
    except Exception as exc:
        logger.exception("Gemini retsept skanerlashda xatolik")
        raise GeminiUnavailableError(str(exc)) from exc


def guess_substance_name(raw_text: str) -> str | None:
    client, model = _get_client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(model=model, contents=_GUESS_PROMPT.format(raw_text=raw_text))
        guess = re.sub(r"^[\"'\-\s]+|[\"'\-\s]+$", "", (response.text or "").strip())
        if not guess or "NOMA" in guess.upper():
            return None
        return guess.splitlines()[0].strip()
    except Exception:
        logger.exception("Gemini nom taxminida xatolik")
        return None
