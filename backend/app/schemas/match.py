from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MatchBase(BaseModel):
    player1_id: int
    player2_id: int
    wager_amount: float
    tournament_id: Optional[int] = None
    round_number: Optional[int] = None

class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    winner_id: Optional[int] = None
    status: Optional[str] = None

class Match(MatchBase):
    id: int
    winner_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
