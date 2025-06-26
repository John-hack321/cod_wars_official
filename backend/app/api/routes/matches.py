from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import match as match_schema
from app.services import match as match_service

router = APIRouter()

class MatchAction(BaseModel):
    action: str

@router.get("/", response_model=List[match_schema.Match])
def read_matches(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100):
    matches = match_service.get_matches(db, skip=skip, limit=limit)
    return matches

@router.get("/{match_id}", response_model=match_schema.Match)
def read_match(*, db: Session = Depends(deps.get_db), match_id: int):
    match = match_service.get_match(db, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.post("/{match_id}/action", response_model=match_schema.Match)
def match_action(
    *,
    db: Session = Depends(deps.get_db),
    match_id: int,
    payload: MatchAction,
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    match = match_service.get_match(db, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if payload.action == "confirm_ready":
        try:
            match = match_service.confirm_ready(db=db, match=match, user=current_user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return match
