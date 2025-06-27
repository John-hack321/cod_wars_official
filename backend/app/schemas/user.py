from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    cod_username: str
    platform: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    wallet_balance: float
    created_at: datetime
    cod_username: str = Field(alias="gamertag")
    platform: str
    profile_picture: Optional[str] = None

    class ConfigDict:
        from_attributes = True
        populate_by_name = True

    class Config:
        from_attributes = True

class PhoneVerification(BaseModel):
    phone_number: str
    code: str
