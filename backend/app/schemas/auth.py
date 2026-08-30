from pydantic import BaseModel

from app.models.user import UserRole


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str
    invite_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    telegram_username: str | None
    role: UserRole
    pharmacy_id: int | None

    model_config = {"from_attributes": True}
