from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas.matchmaking_queue import MatchmakingQueue, MatchmakingQueueCreate
from app.schemas.match import Match
from app.services import matchmaking as matchmaking_service

router = APIRouter()

@router.post("/join", response_model=MatchmakingQueue)
def join_matchmaking_queue(
    *, 
    db: Session = Depends(deps.get_db), 
    queue_in: MatchmakingQueueCreate, 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    try:
        queue_entry = matchmaking_service.join_queue(db=db, user=current_user, queue_in=queue_in)
        return queue_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_matchmaking_queue(
    *, 
    db: Session = Depends(deps.get_db), 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    matchmaking_service.leave_queue(db=db, user=current_user)
    return

@router.get("/status", response_model=List[MatchmakingQueue])
def get_queue_status(db: Session = Depends(deps.get_db)):
    return matchmaking_service.get_queue_status(db=db)
