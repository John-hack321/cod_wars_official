from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import user as user_schema
from app.services import user as user_service, phone_verification as pv_service
from app.schemas.phone_verification import PhoneVerificationVerify

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
def read_users_me(current_user: user_model.User = Depends(deps.get_current_active_user)):
    return current_user

@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserUpdate,
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    user = user_service.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

@router.post("/me/send-verification-code")
def send_verification_code(
    db: Session = Depends(deps.get_db),
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    if not current_user.phone_number:
        raise HTTPException(status_code=400, detail="Phone number not set")
    pv_service.create_verification_code(db, user=current_user)
    return {"message": "Verification code sent"}

@router.post("/me/verify-phone", response_model=user_schema.User)
def verify_phone(
    *,
    db: Session = Depends(deps.get_db),
    verification_in: PhoneVerificationVerify,
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    user = pv_service.verify_code(db, user=current_user, code=verification_in.code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return user
