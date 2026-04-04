from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from app.models import BudgetPeriod

class BudgetBase(BaseModel):
    name: str
    category: str
    limit_amount: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    alert_threshold: float = 80.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator('limit_amount')
    @classmethod
    def limit_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Limit amount must be positive')
        return v

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    limit_amount: Optional[float] = None
    alert_threshold: Optional[float] = None
    is_active: Optional[bool] = None

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent_amount: float
    is_active: bool
    created_at: datetime
    usage_percentage: float = 0.0

    class Config:
        from_attributes = True

    @property
    def usage_percentage(self) -> float:
        if self.limit_amount == 0:
            return 0.0
        return (self.spent_amount / self.limit_amount) * 100
