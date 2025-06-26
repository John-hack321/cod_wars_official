from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as user_model
from app.schemas import mpesa as mpesa_schema
from app.services import mpesa as mpesa_service, user as user_service

router = APIRouter()


@router.post("/stk-push", response_model=mpesa_schema.MpesaSTKPushResponse)
async def stk_push(
    *, 
    db: Session = Depends(deps.get_db), 
    stk_push_in: mpesa_schema.STKPush, 
    current_user: user_model.User = Depends(deps.get_current_active_user)
):
    """Initiate an M-Pesa STK Push to the user's phone number."""
    if not current_user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User does not have a registered phone number."
        )
    
    response = await mpesa_service.initiate_stk_push(
        amount=stk_push_in.amount,
        phone_number=current_user.phone_number,
        description=f"Deposit for {current_user.username}"
    )
    
    if response.get("ResponseCode") != "0":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.get("ResponseDescription", "Failed to initiate STK push.")
        )
    
    return response


@router.post("/callback")
async def mpesa_callback(request: Request, db: Session = Depends(deps.get_db)):
    """Callback endpoint for M-Pesa to send transaction status."""
    data = await request.json()
    print("M-Pesa Callback Received:", data)

    # Extract the relevant data from the callback
    stk_callback = data.get('Body', {}).get('stkCallback', {})
    result_code = stk_callback.get('ResultCode')

    if result_code == 0:
        # Payment was successful
        metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
        amount = next((item['Value'] for item in metadata if item['Name'] == 'Amount'), None)
        phone_number = next((item['Value'] for item in metadata if item['Name'] == 'PhoneNumber'), None)

        if amount and phone_number:
            # M-Pesa returns phone number in 254... format
            formatted_phone = f"0{str(phone_number)[3:]}"
            user_to_update = user_service.get_user_by_phone(db, phone_number=formatted_phone)
            if user_to_update:
                user_service.update_wallet_balance(db, user=user_to_update, amount=float(amount))
                print(f"Successfully updated wallet for {user_to_update.username}")

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
