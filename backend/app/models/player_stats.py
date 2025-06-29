from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    
    total_matches = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    total_wagered = Column(DECIMAL(10,2), default=0.00)
    total_winnings = Column(DECIMAL(10,2), default=0.00)
    current_rank = Column(Integer, default=1000)
    
    # Relationships
    user = relationship("User", back_populates="player_stats")