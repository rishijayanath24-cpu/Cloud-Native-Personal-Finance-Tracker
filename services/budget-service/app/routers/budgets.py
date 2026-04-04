from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db
from jose import jwt, JWTError
from app.config import settings

router = APIRouter()

def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/", response_model=schemas.BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(budget: schemas.BudgetCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return crud.create_budget(db, budget, user_id)

@router.get("/", response_model=List[schemas.BudgetResponse])
def list_budgets(skip: int = 0, limit: int = 100, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    budgets = crud.get_budgets(db, user_id, skip, limit)
    result = []
    for b in budgets:
        b_dict = {c.name: getattr(b, c.name) for c in b.__table__.columns}
        b_dict['usage_percentage'] = (b.spent_amount / b.limit_amount * 100) if b.limit_amount > 0 else 0
        result.append(schemas.BudgetResponse(**b_dict))
    return result

@router.get("/{budget_id}", response_model=schemas.BudgetResponse)
def get_budget(budget_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    budget = crud.get_budget(db, budget_id, user_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    b_dict = {c.name: getattr(budget, c.name) for c in budget.__table__.columns}
    b_dict['usage_percentage'] = (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
    return schemas.BudgetResponse(**b_dict)

@router.put("/{budget_id}", response_model=schemas.BudgetResponse)
def update_budget(budget_id: int, budget_update: schemas.BudgetUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    budget = crud.update_budget(db, budget_id, user_id, budget_update)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    b_dict = {c.name: getattr(budget, c.name) for c in budget.__table__.columns}
    b_dict['usage_percentage'] = (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
    return schemas.BudgetResponse(**b_dict)

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not crud.delete_budget(db, budget_id, user_id):
        raise HTTPException(status_code=404, detail="Budget not found")

@router.post("/{budget_id}/spend")
def record_spend(budget_id: int, amount: float, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    budget = crud.update_spent_amount(db, budget_id, user_id, amount)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    usage = (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
    alert = usage >= budget.alert_threshold
    return {"budget_id": budget_id, "spent_amount": budget.spent_amount, "usage_percentage": usage, "alert_triggered": alert}
