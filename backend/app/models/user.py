from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True)
    gamertag = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    is_phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    wallet_balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=func.now())

    matches_as_player1 = relationship("Match", foreign_keys="[Match.player1_id]", back_populates="player1")
    matches_as_player2 = relationship("Match", foreign_keys="[Match.player2_id]", back_populates="player2")
    transactions = relationship("Transaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    phone_verifications = relationship("PhoneVerification", back_populates="user")
    tournaments = relationship("TournamentParticipant", back_populates="user")
    matchmaking_entry = relationship("MatchmakingQueue", back_populates="user", uselist=False)
    player_stats = relationship("PlayerStats", back_populates="user", uselist=False)
