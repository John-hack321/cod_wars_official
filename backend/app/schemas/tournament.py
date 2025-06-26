from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

# Tournament Schemas
class TournamentBase(BaseModel):
    name: str
    entry_fee: Decimal
    max_participants: int
    status: Optional[str] = 'upcoming'
    start_date: datetime

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class Tournament(TournamentBase):
    id: int
    current_participants: int

    class Config:
        from_attributes = True

# TournamentParticipant Schemas
class TournamentParticipantBase(BaseModel):
    eliminated: Optional[bool] = False

class TournamentParticipantCreate(TournamentParticipantBase):
    tournament_id: int
    user_id: int

class TournamentParticipant(TournamentParticipantBase):
    id: int
    tournament_id: int
    user_id: int

    class Config:
        from_attributes = True
