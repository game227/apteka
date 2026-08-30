import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db, require_role
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_invite import PharmacyInvite
from app.models.user import User, UserRole
from app.schemas.pharmacy import PharmacyCreate, PharmacyInviteOut, PharmacyOut
from app.services.geo import point

router = APIRouter(prefix="/admin", tags=["admin"])

_admin_only = require_role(UserRole.admin)
INVITE_TTL_DAYS = 7


@router.post("/pharmacies", response_model=PharmacyOut)
def create_pharmacy(
    payload: PharmacyCreate, admin: User = Depends(_admin_only), db: Session = Depends(get_db)
):
    pharmacy = Pharmacy(
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        phone=payload.phone,
        created_by_admin_id=admin.id,
        geom=point(payload.lat, payload.lng),
    )
    db.add(pharmacy)
    db.commit()
    db.refresh(pharmacy)
    return pharmacy


@router.get("/pharmacies", response_model=list[PharmacyOut])
def list_pharmacies(admin: User = Depends(_admin_only), db: Session = Depends(get_db)):
    return list(db.execute(select(Pharmacy)).scalars().all())


@router.post("/pharmacies/{pharmacy_id}/invite", response_model=PharmacyInviteOut)
def create_invite(pharmacy_id: int, admin: User = Depends(_admin_only), db: Session = Depends(get_db)):
    pharmacy = db.get(Pharmacy, pharmacy_id)
    if pharmacy is None:
        raise HTTPException(status_code=404, detail="Dorixona topilmadi")

    invite = PharmacyInvite(
        pharmacy_id=pharmacy_id,
        token=secrets.token_urlsafe(24),
        expires_at=datetime.now(timezone.utc) + timedelta(days=INVITE_TTL_DAYS),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return PharmacyInviteOut(token=invite.token, pharmacy_id=pharmacy_id, expires_at=invite.expires_at)
