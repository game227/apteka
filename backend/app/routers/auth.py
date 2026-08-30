from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.telegram_auth import verify_telegram_payload
from app.deps import get_current_user, get_db
from app.models.pharmacy_invite import PharmacyInvite
from app.models.user import User, UserRole
from app.schemas.auth import MeResponse, TelegramAuthPayload, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/telegram", response_model=TokenResponse)
def telegram_login(payload: TelegramAuthPayload, db: Session = Depends(get_db)) -> TokenResponse:
    telegram_fields = payload.model_dump(exclude_none=True, exclude={"invite_token"})
    verified = verify_telegram_payload(telegram_fields)

    telegram_id = verified["id"]
    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()

    full_name = " ".join(filter(None, [verified.get("first_name"), verified.get("last_name")])) or "Foydalanuvchi"
    username = verified.get("username")

    if user is None:
        user = User(telegram_id=telegram_id, full_name=full_name, telegram_username=username)
        db.add(user)
        db.flush()
    else:
        user.full_name = full_name
        user.telegram_username = username

    if payload.invite_token:
        invite = db.query(PharmacyInvite).filter(PharmacyInvite.token == payload.invite_token).one_or_none()
        if invite is None:
            raise HTTPException(status_code=400, detail="Taklif havolasi yaroqsiz")
        if invite.used_by_user_id is not None:
            raise HTTPException(status_code=400, detail="Taklif havolasi allaqachon ishlatilgan")
        if invite.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Taklif havolasi muddati o'tgan")

        invite.used_by_user_id = user.id
        user.role = UserRole.pharmacy_staff
        user.pharmacy_id = invite.pharmacy_id

    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user
