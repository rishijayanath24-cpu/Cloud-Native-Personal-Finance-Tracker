from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from app.models import TransactionType

class TransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    category: str
    description: Optional[str] = None
    tags: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransactionCreate(TransactionBase):
    date: Optional[datetime] = None

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    categories: dict
