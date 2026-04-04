from pydantic import BaseModel
from typing import List, Optional

class SummaryResponse(BaseModel):
    user_id: int
    period: str
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int

class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float

class BudgetStatusItem(BaseModel):
    category: str
    limit: float
    spent: float
    remaining: float
    utilization_pct: float
    exceeded: bool

class MonthlyTrendItem(BaseModel):
    month: str
    income: float
    expenses: float
    net: float

class CategoryBreakdownResponse(BaseModel):
    user_id: int
    period: str
    breakdown: List[CategoryBreakdown]

class BudgetStatusResponse(BaseModel):
    user_id: int
    period: str
    items: List[BudgetStatusItem]

class MonthlyTrendResponse(BaseModel):
    user_id: int
    trend: List[MonthlyTrendItem]
