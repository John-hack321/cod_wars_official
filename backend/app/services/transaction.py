from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate

class TransactionService:
    def create_transaction(self, db: Session, *, obj_in: TransactionCreate) -> Transaction:
        """
        Create a new transaction.
        """
        db_obj = Transaction(
            user_id=obj_in.user_id,
            amount=obj_in.amount,
            type=obj_in.type,
            status=obj_in.status,
            description=obj_in.description,
            match_id=obj_in.match_id,
            mpesa_reference=obj_in.mpesa_reference
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

transaction = TransactionService()
