from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class MatchmakingQueueBase(BaseModel):
    game_type: str
    wager_amount: Decimal

class MatchmakingQueueCreate(MatchmakingQueueBase):
    pass

class MatchmakingQueue(MatchmakingQueueBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
