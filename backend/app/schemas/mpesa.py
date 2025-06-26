from pydantic import BaseModel
from typing import Optional, List

class STKPush(BaseModel):
    phone_number: str
    amount: int


class MpesaSTKPushResponse(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResponseCode: str
    ResponseDescription: str
    CustomerMessage: str

class STKCallback(BaseModel):
    Body: dict

class MpesaTransaction(BaseModel):
    id: int
    user_id: int
    amount: float
    receipt_number: str

    class Config:
        from_attributes = True
