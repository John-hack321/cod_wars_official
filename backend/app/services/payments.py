from sqlalchemy.orm import Session
from app.models.user import User
from app.models.transaction import Transaction
from app.services import mpesa as mpesa_service

def initiate_deposit(db: Session, user: User, amount: int) -> Transaction:
    transaction = Transaction(
        user_id=user.id,
        amount=amount,
        type='deposit',
        status='pending'
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    mpesa_service.initiate_stk_push(user.phone_number, amount, transaction.id)

    return transaction

def process_mpesa_callback(data: dict):
    # Logic to process the callback from M-Pesa
    # Find the transaction, update its status, and update user wallet
    pass
