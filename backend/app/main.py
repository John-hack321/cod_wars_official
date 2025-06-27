from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base_class import Base # Changed from app.db.base
from app.db.session import engine


# --- TEMPORARY CODE TO RESET THE USERS TABLE ---
# This will delete the existing users table and all its data
# to apply the new schema changes (gamertag, platform).
# This should be removed after the first successful run.
print("--- DROPPING USERS TABLE TO UPDATE SCHEMA ---")
try:
    # Import the User model to ensure its metadata is loaded
    from app.models.user import User
    Base.metadata.drop_all(bind=engine)
    print("--- USERS TABLE DROPPED SUCCESSFULLY ---")
except Exception as e:
    print(f"--- ERROR DROPPING TABLE (might be the first run): {e} ---")
# --- END OF TEMPORARY CODE ---

# Create all tables
print("--- CREATING ALL TABLES ---")
Base.metadata.create_all(bind=engine)
print("--- ALL TABLES CREATED ---")

app = FastAPI(
    title="WageWars API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you would want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the WageWars API"}

