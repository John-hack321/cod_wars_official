from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="pending")  # pending, active, completed, disputed
    wager_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=func.now())
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=True)
    round_number = Column(Integer, nullable=True)

    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_player2")
    winner = relationship("User", foreign_keys=[winner_id])
    tournament = relationship("Tournament", back_populates="matches")
