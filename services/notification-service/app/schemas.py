from pydantic import BaseModel, EmailStr
from typing import Optional

class NotificationRequest(BaseModel):
    user_id: int
    email: Optional[str] = None
    subject: str
    message: str
    notification_type: str = "info"  # info, warning, alert

class BudgetAlertRequest(BaseModel):
    user_id: int
    email: str
    budget_name: str
    category: str
    usage_percentage: float
    limit_amount: float
    spent_amount: float
