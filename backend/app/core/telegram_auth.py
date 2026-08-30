"""Verification of Telegram Login Widget payloads.

Reference: https://core.telegram.org/widgets/login#checking-authorization
"""

import hashlib
import hmac
import time

from fastapi import HTTPException, status

from app.config import get_settings

MAX_AUTH_AGE_SECONDS = 24 * 60 * 60


def verify_telegram_payload(data: dict) -> dict:
    """Validate the HMAC signature and freshness of a Telegram Login payload.

    `data` is the raw dict sent by the Telegram Login Widget (contains at least
    id, auth_date, hash, and optionally first_name/last_name/username/photo_url).
    Returns the same dict on success, raises HTTPException(401) otherwise.
    """
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TELEGRAM_BOT_TOKEN sozlanmagan",
        )

    data = dict(data)
    received_hash = data.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="hash yo'q")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()) if v is not None)
    secret_key = hashlib.sha256(settings.telegram_bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Telegram imzosi noto'g'ri")

    auth_date = int(data.get("auth_date", 0))
    if time.time() - auth_date > MAX_AUTH_AGE_SECONDS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login muddati o'tgan")

    data["hash"] = received_hash
    return data
