from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import user as user_schema
from app.services import user as user_service

router = APIRouter()


@router.get("/", response_model=List[user_schema.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_model.User = Depends(deps.get_current_active_superuser),
):
    """Retrieve users (Superuser only)."""
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=user_schema.User)
def read_user_by_id(
    user_id: int, db: Session = Depends(deps.get_db)
):
    """Get a specific user by id."""
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *, 
    db: Session = Depends(deps.get_db), 
    user_in: user_schema.UserUpdate, 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    """Update own user."""
    user = user_service.update_user(db, db_obj=current_user, obj_in=user_in)
    return user
