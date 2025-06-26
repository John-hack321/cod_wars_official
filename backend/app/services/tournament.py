import math
import random
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.tournament import Tournament, TournamentParticipant
from app.models.user import User
from app.schemas.tournament import TournamentCreate


def create_tournament(db: Session, tournament_in: TournamentCreate) -> Tournament:
    """Creates a new tournament in the database."""
    db_tournament = Tournament(**tournament_in.model_dump())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament


def get_all_tournaments(db: Session) -> List[Tournament]:
    """Retrieves all tournaments from the database."""
    return db.query(Tournament).all()


def get_tournament_by_id(db: Session, tournament_id: int) -> Tournament | None:
    """Retrieves a single tournament by its ID."""
    return db.query(Tournament).filter(Tournament.id == tournament_id).first()


def join_tournament(
    db: Session, tournament: Tournament, user: User
) -> TournamentParticipant:
    """Allows a user to join an upcoming tournament."""
    if tournament.status != "upcoming":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is not open for registration.",
        )
    if tournament.current_participants >= tournament.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament is full."
        )
    if user.wallet_balance < tournament.entry_fee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds."
        )
    existing_participant = (
        db.query(TournamentParticipant)
        .filter_by(tournament_id=tournament.id, user_id=user.id)
        .first()
    )
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already joined this tournament."
        )

    user.wallet_balance -= tournament.entry_fee
    tournament.current_participants += 1
    participant = TournamentParticipant(tournament_id=tournament.id, user_id=user.id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def start_tournament(db: Session, tournament: Tournament) -> List[Match]:
    """Starts the tournament and generates the first-round matches."""
    if tournament.status != "upcoming":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament has already started or is completed.",
        )

    participants = [p.user for p in tournament.participants]
    if len(participants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough participants to start.",
        )

    tournament.status = "active"
    random.shuffle(participants)

    # --- Single-Elimination Bracket Generation ---
    num_participants = len(participants)
    total_rounds = math.ceil(math.log2(num_participants))
    next_power_of_two = 2**total_rounds
    num_byes = next_power_of_two - num_participants

    round1_matches = []
    bye_recipients = participants[:num_byes]
    players_for_round1 = participants[num_byes:]

    # Create matches for players who are not getting a bye
    for i in range(0, len(players_for_round1), 2):
        match = Match(
            player1_id=players_for_round1[i].id,
            player2_id=players_for_round1[i + 1].id,
            tournament_id=tournament.id,
            round_number=1,
        )
        db.add(match)
        round1_matches.append(match)

    # Advance players with byes to the second round automatically
    for i in range(0, len(bye_recipients), 2):
        player1 = bye_recipients[i]
        player2 = bye_recipients[i + 1] if i + 1 < len(bye_recipients) else None

        match = Match(
            player1_id=player1.id,
            player2_id=player2.id if player2 else None,
            tournament_id=tournament.id,
            round_number=2,
            winner_id=player1.id if not player2 else None,
            status="completed" if not player2 else "pending",
        )
        db.add(match)

    db.commit()
    for match in round1_matches:
        db.refresh(match)

    return round1_matches


def advance_tournament_round(db: Session, completed_match: Match):
    """Advances the winner of a match to the next round of the tournament."""
    tournament = completed_match.tournament
    if not tournament or tournament.status != "active":
        return

    winner_id = completed_match.winner_id
    if not winner_id:
        return

    current_round = completed_match.round_number
    next_round = current_round + 1

    # Check if this was the final match
    num_participants = tournament.current_participants
    total_rounds = math.ceil(math.log2(num_participants))
    if current_round == total_rounds:
        tournament.status = "completed"
        tournament.winner_id = winner_id
        # In a real app, trigger prize distribution here
        db.commit()
        return

    # Find an open match in the next round
    next_match = (
        db.query(Match)
        .filter(
            Match.tournament_id == tournament.id,
            Match.round_number == next_round,
            Match.player2_id == None,
        )
        .first()
    )

    if next_match:
        # Found a match with a waiting player, add the winner as player2
        next_match.player2_id = winner_id
    else:
        # No waiting match found, create a new one for the next round
        new_match = Match(
            player1_id=winner_id, tournament_id=tournament.id, round_number=next_round
        )
        db.add(new_match)

    db.commit()

