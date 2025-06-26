from sqlalchemy.orm import Session
from app.models.notification import Notification

def get_notification(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications_by_user(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def create_notification(db: Session, user_id: int, message: str) -> Notification:
    db_notification = Notification(user_id=user_id, message=message)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_as_read(db: Session, db_notification: Notification) -> Notification:
    db_notification.is_read = True
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification
