from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, DECIMAL
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class MatchmakingQueue(Base):
    __tablename__ = "matchmaking_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    game_type = Column(String, nullable=False, index=True, default='default')
    wager_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String, default='waiting', nullable=False, index=True)  # e.g., 'waiting', 'matched'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="matchmaking_entry")
