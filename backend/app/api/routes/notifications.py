from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import notification as notification_schema
from app.services import notification as notification_service

router = APIRouter()

@router.get("/", response_model=List[notification_schema.Notification])
def read_notifications(
    *, 
    db: Session = Depends(deps.get_db), 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    notifications = notification_service.get_notifications_by_user(db=db, user_id=current_user.id)
    return notifications

@router.post("/{notification_id}/read", response_model=notification_schema.Notification)
def mark_notification_as_read(
    *, 
    db: Session = Depends(deps.get_db), 
    notification_id: int, 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    notification = notification_service.get_notification(db, notification_id=notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification_service.mark_as_read(db=db, db_notification=notification)
