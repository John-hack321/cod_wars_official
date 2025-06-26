from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String) # e.g., 'deposit', 'withdrawal', 'wager', 'win'
    status = Column(String, default='pending') # e.g., 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=func.now())
    description = Column(String)

    user = relationship("User", back_populates="transactions")
