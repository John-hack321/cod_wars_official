from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import tournament as tournament_schema, match as match_schema
from app.services import tournament as tournament_service

router = APIRouter()

@router.post("/", response_model=tournament_schema.Tournament)
def create_tournament(
    *,
    db: Session = Depends(deps.get_db),
    tournament_in: tournament_schema.TournamentCreate,
    current_user: user_model.User = Depends(deps.get_current_active_superuser),
):
    tournament = tournament_service.create_tournament(db=db, tournament_in=tournament_in)
    return tournament

@router.get("/", response_model=List[tournament_schema.Tournament])
def read_tournaments(db: Session = Depends(deps.get_db)):
    tournaments = tournament_service.get_all_tournaments(db=db)
    return tournaments

@router.get("/{tournament_id}", response_model=tournament_schema.Tournament)
def read_tournament(*, db: Session = Depends(deps.get_db), tournament_id: int):
    tournament = tournament_service.get_tournament(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament

@router.post("/{tournament_id}/join", response_model=tournament_schema.TournamentParticipant)
def join_tournament(
    *,
    db: Session = Depends(deps.get_db),
    tournament_id: int,
    current_user: user_model.User = Depends(deps.get_current_active_user),
):
    try:
        participant = tournament_service.join_tournament(db=db, tournament_id=tournament_id, user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return participant

@router.post("/{tournament_id}/start", response_model=List[match_schema.Match])
def start_tournament(
    *,
    db: Session = Depends(deps.get_db),
    tournament_id: int,
    current_user: user_model.User = Depends(deps.get_current_active_superuser),
):
    try:
        matches = tournament_service.start_tournament(db=db, tournament_id=tournament_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return matches

@router.get("/{tournament_id}/participants", response_model=List[tournament_schema.TournamentParticipant])
def get_tournament_participants(*, db: Session = Depends(deps.get_db), tournament_id: int):
    tournament = tournament_service.get_tournament(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament.participants

@router.get("/{tournament_id}/matches", response_model=List[match_schema.Match])
def get_tournament_matches(*, db: Session = Depends(deps.get_db), tournament_id: int):
    tournament = tournament_service.get_tournament(db, tournament_id=tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament.matches
