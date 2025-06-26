from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.match import Match
from app.models.user import User
from app.schemas.transaction import TransactionCreate
from app.services import (
    cod_api as cod_api_service,
    notification as notification_service,
    tournament as tournament_service,
    transaction as transaction_service,
)
from app.core.celery_app import celery_app


def get_match(db: Session, match_id: int) -> Match | None:
    """Fetches a single match by its ID."""
    return db.query(Match).filter(Match.id == match_id).first()


def get_matches_for_user(db: Session, user_id: int) -> list[Match]:
    """Fetches all matches for a specific user."""
    return db.query(Match).filter((Match.player1_id == user_id) | (Match.player2_id == user_id)).all()


def confirm_ready(db: Session, match: Match, user: User) -> Match:
    """Marks a player as ready for a match. Starts the match if both are ready."""
    if match.status != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Match is not pending readiness.")

    if match.player1_id == user.id:
        match.player1_ready = True
    elif match.player2_id == user.id:
        match.player2_ready = True
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not a player in this match.")

    if match.player1_ready and match.player2_ready:
        match.status = "active"
        # Schedule the first check in 15 minutes
        check_time = datetime.utcnow() + timedelta(minutes=15)
        celery_app.send_task("app.worker.verify_match_result", args=[match.id], eta=check_time)

    db.commit()
    db.refresh(match)
    return match


def _finalize_match(db: Session, *, match: Match, winner_id: int):
    """Finalizes a match, transfers wagers, creates notifications, and advances tournaments."""
    if match.status != "active":
        return  # Avoid double processing

    loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id
    winner = db.query(User).filter(User.id == winner_id).first()
    loser = db.query(User).filter(User.id == loser_id).first()

    if not winner or not loser:
        return # Should not happen

    match.winner_id = winner_id
    match.status = "completed"
    match.ended_at = datetime.utcnow()

    # Handle wager transfer
    if match.wager_amount > 0:
        winner.wallet_balance += match.wager_amount * 2  # Winner gets the full pot
        transaction_service.create_transaction(
            db,
            TransactionCreate(
                user_id=winner_id,
                amount=match.wager_amount * 2,
                type="wager_win",
                description=f"Won wager against {loser.username}",
            ),
        )

    # Create notifications
    notification_service.create_notification(
        db, user_id=winner_id, message=f"You won your match against {loser.username}!"
    )
    notification_service.create_notification(
        db, user_id=loser_id, message=f"You lost your match against {winner.username}."
    )

    # Advance tournament if applicable
    if match.tournament_id:
        tournament_service.advance_tournament_round(db=db, completed_match=match)

    db.commit()


async def automated_match_verification(match_id: int):
    """The core automated task to verify a match result via the CoD API."""
    db = SessionLocal()
    try:
        match = get_match(db, match_id=match_id)
        if not match or match.status != "active":
            return

        p1 = match.player1
        p2 = match.player2

        # Fetch recent matches for both players
        p1_history = await cod_api_service.get_match_history(p1.platform, p1.gamertag)
        p2_history = await cod_api_service.get_match_history(p2.platform, p2.gamertag)

        if not p1_history or not p2_history:
            print(f"Could not fetch match history for match {match_id}")
            # Optionally, reschedule check
            return

        # Find the most recent match they played together
        p1_match_ids = {m["matchID"] for m in p1_history["matches"]}
        shared_match_id = None
        for p2_match in p2_history["matches"]:
            if p2_match["matchID"] in p1_match_ids:
                shared_match_id = p2_match["matchID"]
                break

        if not shared_match_id:
            print(f"No shared match found yet for match {match_id}")
            # Optionally, reschedule check
            return

        # Get details of the shared match
        match_details = await cod_api_service.get_match_details(p1.platform, shared_match_id)
        if not match_details or not match_details.get("allPlayers"):
            return

        # Determine winner based on team placement (lower is better)
        winner_username = None
        p1_placement = -1
        p2_placement = -1

        for player_data in match_details["allPlayers"]:
            if player_data.get("player", {}).get("username").lower() == p1.gamertag.lower():
                p1_placement = player_data.get("playerStats", {}).get("teamPlacement", -1)
            if player_data.get("player", {}).get("username").lower() == p2.gamertag.lower():
                p2_placement = player_data.get("playerStats", {}).get("teamPlacement", -1)
        
        if p1_placement != -1 and p2_placement != -1:
            if p1_placement < p2_placement:
                winner_username = p1.username
            elif p2_placement < p1_placement:
                winner_username = p2.username
            # If placement is the same, other logic (e.g. kills) could be used.
            # For now, we'll leave it as a draw if placements are equal.

        if winner_username:
            winner = db.query(User).filter(User.username == winner_username).first()
            if winner:
                _finalize_match(db=db, match=match, winner_id=winner.id)

    finally:
        db.close()

