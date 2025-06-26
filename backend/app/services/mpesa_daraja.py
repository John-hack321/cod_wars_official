import requests
import base64
from datetime import datetime, timedelta

class MpesaDaraja:
    def __init__(self, consumer_key, consumer_secret, shortcode, passkey, env="sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.api_url = (
            "https://sandbox.safaricom.co.ke" if env == "sandbox" else "https://api.safaricom.co.ke"
        )
        self.access_token = None
        self.token_expiry = datetime.now()

    def get_access_token(self):
        url = f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(
                url, auth=requests.auth.HTTPBasicAuth(self.consumer_key, self.consumer_secret), timeout=10
            )
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = int(token_data.get("expires_in", 3540))
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"Failed to get M-Pesa access token: {e}")
            raise Exception("Failed to get M-Pesa access token") from e

    def initiate_stk_push(self, phone_number, amount, callback_url, transaction_desc):
        if not self.access_token or datetime.now() >= self.token_expiry:
            self.get_access_token()

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (self.shortcode + self.passkey + timestamp).encode()
        ).decode()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "WageWarsDeposit",
            "TransactionDesc": transaction_desc,
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        url = f"{self.api_url}/mpesa/stkpush/v1/processrequest"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"STK push request failed: {e}")
            return {"error": "STK push request failed", "details": str(e)}
