import africastalking
from app.core.config import settings

# Initialize Africa's Talking
username = settings.AFRICASTALKING_USERNAME
api_key = settings.AFRICASTALKING_API_KEY

africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_sms(phone_number: str, message: str):
    """Sends an SMS to a given phone number."""
    try:
        response = sms.send(message, [phone_number])
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
