from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func, Enum
import enum
from app.database import Base

class BudgetPeriod(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    limit_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)
    period = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    is_active = Column(Boolean, default=True)
    alert_threshold = Column(Float, default=80.0)  # percentage
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
