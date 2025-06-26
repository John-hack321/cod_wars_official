from fastapi import APIRouter

from app.api.v1.endpoints import auth, user, tournament, match, mpesa

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(tournament.router, prefix="/tournaments", tags=["tournaments"])
api_router.include_router(match.router, prefix="/matches", tags=["matches"])
api_router.include_router(mpesa.router, prefix="/mpesa", tags=["mpesa"])
