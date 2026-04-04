from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import crud, schemas
from app.database import get_db
from app.models import TransactionType
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

@router.post("/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: schemas.TransactionCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction, user_id)

@router.get("/", response_model=List[schemas.TransactionResponse])
def list_transactions(
    skip: int = 0, limit: int = 100,
    transaction_type: Optional[TransactionType] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return crud.get_transactions(db, user_id, skip, limit, transaction_type, category, start_date, end_date)

@router.get("/summary", response_model=schemas.TransactionSummary)
def get_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return crud.get_summary(db, user_id, start_date, end_date)

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(transaction_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id, user_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(transaction_id: int, transaction_update: schemas.TransactionUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    transaction = crud.update_transaction(db, transaction_id, user_id, transaction_update)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not crud.delete_transaction(db, transaction_id, user_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
