from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import match as match_schema
from app.services import match as match_service

router = APIRouter()


@router.get("/me", response_model=List[match_schema.Match])
def get_my_matches(
    db: Session = Depends(deps.get_db),
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    """Get all matches for the current user."""
    return match_service.get_matches_for_user(db, user_id=current_user.id)


@router.get("/{match_id}", response_model=match_schema.Match)
def get_match(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    """Get a specific match by id."""
    match = match_service.get_match(db, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.player1_id != current_user.id and match.player2_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not part of this match")
    return match


@router.post("/{match_id}/ready", response_model=match_schema.Match)
def confirm_ready(
    match_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    """Confirm that the user is ready for the match."""
    match = match_service.get_match(db, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    updated_match = match_service.confirm_ready(db, match=match, user=current_user)
    return updated_match
