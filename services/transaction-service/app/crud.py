from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from app.models import Transaction, TransactionType
from app.schemas import TransactionCreate, TransactionUpdate, TransactionSummary

def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()

def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100,
                     transaction_type: Optional[TransactionType] = None,
                     category: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: TransactionCreate, user_id: int) -> Transaction:
    db_transaction = Transaction(**transaction.model_dump(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, user_id: int, transaction_update: TransactionUpdate) -> Optional[Transaction]:
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return None
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return False
    db.delete(db_transaction)
    db.commit()
    return True

def get_summary(db: Session, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> TransactionSummary:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()
    total_income = sum(t.amount for t in transactions if t.transaction_type == TransactionType.INCOME)
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == TransactionType.EXPENSE)

    categories = {}
    for t in transactions:
        if t.category not in categories:
            categories[t.category] = 0
        categories[t.category] += t.amount

    return TransactionSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        transaction_count=len(transactions),
        categories=categories
    )
