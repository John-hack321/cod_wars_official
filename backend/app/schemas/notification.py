from typing import Optional
from pydantic import BaseModel

class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    is_read: Optional[bool] = False

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
