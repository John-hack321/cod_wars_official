from sqlalchemy.orm import Session
from app.models.user import User
from app.models.matchmaking_queue import MatchmakingQueue
from app.models.match import Match
from app.schemas.matchmaking_queue import MatchmakingQueueCreate

def join_queue(db: Session, user: User, queue_in: MatchmakingQueueCreate) -> MatchmakingQueue:
    # Simplified: check for existing entry
    existing_entry = db.query(MatchmakingQueue).filter(MatchmakingQueue.user_id == user.id).first()
    if existing_entry:
        raise ValueError("User already in queue")
    
    queue_entry = MatchmakingQueue(user_id=user.id, wager_amount=queue_in.wager_amount)
    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)
    # Add logic to check for a match
    return queue_entry

def leave_queue(db: Session, user: User):
    entry = db.query(MatchmakingQueue).filter(MatchmakingQueue.user_id == user.id).first()
    if entry:
        db.delete(entry)
        db.commit()

def get_queue_status(db: Session):
    return db.query(MatchmakingQueue).all()
