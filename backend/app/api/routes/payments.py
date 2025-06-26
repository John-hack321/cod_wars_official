from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import Any

from app.api import deps
from app.models import user as user_model
from app.schemas import user as user_schema
from app.services import payments as payments_service, match as match_service

router = APIRouter()

class DepositRequest(BaseModel):
    amount: int

@router.post("/deposit", status_code=202)
def initiate_deposit(
    *, 
    request: DepositRequest, 
    db = Depends(deps.get_db), 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    if not current_user.phone_number:
        raise HTTPException(status_code=400, detail="User must have a phone number to make a deposit.")
    
    transaction = payments_service.initiate_deposit(
        db=db, user=current_user, amount=request.amount
    )
    return {"message": "Deposit initiated. Check your phone to complete the transaction.", "transaction_id": transaction.id}

@router.post("/mpasa/callback", include_in_schema=False)
async def mpesa_callback(request: Request):
    data = await request.json()
    # Process callback data
    payments_service.process_mpesa_callback(data)
    return {"ResultCode": 0, "ResultDesc": "Accepted"}
