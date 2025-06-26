from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.models.tournament import Tournament
from app.schemas import tournament as tournament_schema
from app.services import tournament as tournament_service

router = APIRouter()


@router.post("/", response_model=tournament_schema.Tournament)
def create_tournament(
    *, 
    db: Session = Depends(deps.get_db), 
    tournament_in: tournament_schema.TournamentCreate, 
    current_user: user_model.User = Depends(deps.get_current_active_superuser)
):
    """Create a new tournament (Superuser only)."""
    tournament = tournament_service.create_tournament(db, tournament_in=tournament_in)
    return tournament


@router.get("/", response_model=List[tournament_schema.Tournament])
def get_all_tournaments(db: Session = Depends(deps.get_db)):
    """Get all tournaments."""
    return tournament_service.get_all_tournaments(db)


@router.get("/{tournament_id}", response_model=tournament_schema.Tournament)
def get_tournament(
    tournament_id: int, db: Session = Depends(deps.get_db)
):
    """Get a specific tournament by id."""
    tournament = tournament_service.get_tournament_by_id(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("/{tournament_id}/join", response_model=tournament_schema.TournamentParticipant)
def join_tournament(
    tournament_id: int, 
    db: Session = Depends(deps.get_db), 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    """Join a tournament."""
    tournament = tournament_service.get_tournament_by_id(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    return tournament_service.join_tournament(db, tournament=tournament, user=current_user)


@router.post("/{tournament_id}/start")
def start_tournament(
    tournament_id: int, 
    db: Session = Depends(deps.get_db), 
    current_user: user_model.User = Depends(deps.get_current_active_superuser)
):
    """Start a tournament (Superuser only)."""
    tournament = tournament_service.get_tournament_by_id(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    matches = tournament_service.start_tournament(db, tournament=tournament)
    return {"message": "Tournament started successfully", "first_round_matches": matches}
