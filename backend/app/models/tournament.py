from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default="upcoming")  # upcoming, active, completed
    start_date = Column(DateTime)
    entry_fee = Column(Numeric(10, 2), default=0.00)
    max_participants = Column(Integer)
    current_participants = Column(Integer, default=0)

    participants = relationship("TournamentParticipant", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User", back_populates="tournaments")
