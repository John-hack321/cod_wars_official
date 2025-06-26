from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.models import user as user_model
from app.schemas import user as user_schema, token as token_schema
from app.services import auth as auth_service, user as user_service

router = APIRouter()


@router.post("/register", response_model=user_schema.User)
def register(
    *, db: Session = Depends(deps.get_db), user_in: user_schema.UserCreate
):
    """Register a new user and send a phone verification code."""
    user = auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    user = auth_service.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this username already exists.",
        )
    if not user_in.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required."
        )

    new_user = auth_service.create_user(db, user_in)
    # In a real app, the code would be sent via SMS
    verification = user_service.create_phone_verification(db, new_user.phone_number)
    # In a real application, you would send this code via SMS.
    # For local development, we'll just print it to the console.
    print(f"--- VERIFICATION CODE for {new_user.phone_number}: {verification.code} ---")
    return new_user


@router.post("/verify-phone")
def verify_phone(
    *, db: Session = Depends(deps.get_db), verification_data: user_schema.PhoneVerification
):
    """Verify a user's phone number with the provided code."""
    success = user_service.verify_phone_code(
        db, phone_number=verification_data.phone_number, code=verification_data.code
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code or expired."
        )
    user = auth_service.get_user_by_phone(db, phone_number=verification_data.phone_number)
    if user:
        user.is_phone_verified = True
        db.commit()
    return {"message": "Phone number verified successfully."}


@router.post("/login/access-token", response_model=token_schema.Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = auth_service.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user.is_phone_verified:
        raise HTTPException(status_code=400, detail="Phone number not verified")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schema.User)
def read_users_me(
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    """Get current user."""
    return current_user
