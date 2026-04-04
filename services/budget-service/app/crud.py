from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Budget
from app.schemas import BudgetCreate, BudgetUpdate

def get_budget(db: Session, budget_id: int, user_id: int) -> Optional[Budget]:
    return db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()

def get_budgets(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Budget]:
    return db.query(Budget).filter(Budget.user_id == user_id).offset(skip).limit(limit).all()

def create_budget(db: Session, budget: BudgetCreate, user_id: int) -> Budget:
    db_budget = Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, user_id: int, budget_update: BudgetUpdate) -> Optional[Budget]:
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return None
    update_data = budget_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_spent_amount(db: Session, budget_id: int, user_id: int, amount: float) -> Optional[Budget]:
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return None
    db_budget.spent_amount += amount
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int) -> bool:
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return False
    db.delete(db_budget)
    db.commit()
    return True
