from app.services.mpesa_daraja import MpesaDaraja
from app.core.config import settings

mpesa_api = MpesaDaraja(
    consumer_key=settings.MPESA_CONSUMER_KEY,
    consumer_secret=settings.MPESA_CONSUMER_SECRET,
    passkey=settings.MPESA_PASSKEY,
    shortcode=settings.MPESA_SHORTCODE,
    env=settings.MPESA_ENV
)

def stk_push(phone_number: str, amount: int, transaction_desc: str, callback_url: str, reference: str):
    """Initiates an M-Pesa STK push request."""
    try:
        response = mpesa_api.stk_push(
            phone_number=phone_number,
            amount=amount,
            transaction_desc=transaction_desc,
            callback_url=callback_url,
            reference=reference
        )
        return response
    except Exception as e:
        print(f"An error occurred during STK push: {e}")
        return None
