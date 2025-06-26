from pydantic import BaseModel, constr

class PhoneVerificationRequest(BaseModel):
    phone_number: str

class PhoneVerificationVerify(BaseModel):
    phone_number: str
    code: constr(min_length=6, max_length=6)
