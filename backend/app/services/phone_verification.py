import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.phone_verification import PhoneVerification
from app.services.sms import send_sms

def create_verification_code(db: Session, user: User) -> str:
    """Generate and save a 6-digit verification code."""
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes

    verification_entry = db.query(PhoneVerification).filter_by(user_id=user.id).first()
    if verification_entry:
        verification_entry.code = code
        verification_entry.expires_at = expires_at
    else:
        verification_entry = PhoneVerification(user_id=user.id, code=code, expires_at=expires_at)
        db.add(verification_entry)
    
    db.commit()
    return code

def send_verification_sms(phone_number: str, code: str):
    """Send the verification code via SMS."""
    message = f"Your verification code is {code}"
    send_sms(phone_number, message)

def verify_code(db: Session, user: User, code: str) -> bool:
    """Verify the provided code."""
    verification_entry = db.query(PhoneVerification).filter_by(user_id=user.id).first()

    if not verification_entry or verification_entry.code != code:
        return False

    if datetime.utcnow() > verification_entry.expires_at:
        return False  # Code has expired

    user.phone_verified = True
    db.delete(verification_entry)  # Code is single-use
    db.commit()
    return True
