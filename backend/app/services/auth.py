from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import (
    get_password_hash, verify_password, create_access_token
)
from app.models.user import User
from app.models.phone_verification import PhoneVerification
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetches a user from the database by their email address."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetches a user from the database by their username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_phone(db: Session, phone_number: str) -> User | None:
    """Fetches a user from the database by their phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user in the database after validating input."""
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        phone_number=user.phone_number,
        gamertag=user.cod_username,
        platform=user.platform
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticates a user by username and password."""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_phone_code(db: Session, *, phone_number: str, code: str) -> bool:
    """Verifies a phone number using the provided code."""
    verification_entry = (
        db.query(PhoneVerification)
        .filter(PhoneVerification.phone_number == phone_number)
        .first()
    )

    if not verification_entry or verification_entry.code != code:
        return False

    user = get_user_by_phone(db, phone_number=phone_number)
    if not user:
        return False

    user.is_phone_verified = True
    db.add(user)
    db.delete(verification_entry)
    db.commit()

    return True

