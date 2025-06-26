import random
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.phone_verification import PhoneVerification
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.auth import get_user_by_email, get_user_by_username


def get_user(db: Session, user_id: int) -> User | None:
    """Fetches a single user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Fetches multiple users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, *, db_user: User, user_in: UserUpdate) -> User:
    """Updates a user's profile information."""
    user_data = user_in.model_dump(exclude_unset=True)

    if "email" in user_data and user_data["email"] != db_user.email:
        if get_user_by_email(db, email=user_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user.",
            )

    if "username" in user_data and user_data["username"] != db_user.username:
        if get_user_by_username(db, username=user_data["username"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken by another user.",
            )

    if "password" in user_data:
        hashed_password = get_password_hash(user_data["password"])
        db_user.hashed_password = hashed_password
        del user_data["password"]

    for field, value in user_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_phone_verification(db: Session, phone_number: str) -> PhoneVerification:
    """Generates and stores a new phone verification code."""
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # In a real app, you would use an SMS gateway to send the code
    print(f"[SIMULATED SMS] Verification code for {phone_number} is: {code}")

    verification_entry = db.query(PhoneVerification).filter_by(phone_number=phone_number).first()
    if verification_entry:
        verification_entry.code = code
        verification_entry.expires_at = expires_at
    else:
        verification_entry = PhoneVerification(
            phone_number=phone_number, code=code, expires_at=expires_at
        )
    db.add(verification_entry)
    db.commit()
    db.refresh(verification_entry)
    return verification_entry


def verify_phone_code(db: Session, phone_number: str, code: str) -> bool:
    """Verifies a phone number using the provided code."""
    verification_entry = (
        db.query(PhoneVerification)
        .filter_by(phone_number=phone_number, code=code)
        .first()
    )

    if not verification_entry or verification_entry.expires_at < datetime.utcnow():
        return False

    user = db.query(User).filter_by(phone=phone_number).first()
    if user:
        user.is_phone_verified = True
        db.add(user)
        # Can delete the verification entry after successful verification
        db.delete(verification_entry)
        db.commit()
        return True

    return False

