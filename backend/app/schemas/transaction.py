from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class TransactionBase(BaseModel):
    type: str
    amount: Decimal
    status: Optional[str] = 'pending'
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: int
    match_id: Optional[int] = None
    mpesa_reference: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    user_id: int
    match_id: Optional[int] = None

    class Config:
        from_attributes = True
