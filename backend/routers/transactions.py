from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from database import get_db
import models
import schemas
from routers.auth import get_current_user
from services.telegram_service import telegram_service

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.get("/", response_model=List[schemas.TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    month: Optional[str] = None,  # Format: "YYYY-MM"
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all transactions with pagination and optional month filter

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        month: Optional month filter in "YYYY-MM" format (e.g., "2025-01")
    """
    query = db.query(models.Transaction)

    # Apply month filter if provided
    if month:
        try:
            year, month_num = month.split('-')
            year = int(year)
            month_num = int(month_num)

            # Filter by year and month
            query = query.filter(
                models.Transaction.date >= datetime(year, month_num, 1).date()
            )

            # Calculate next month for upper bound
            if month_num == 12:
                next_year = year + 1
                next_month = 1
            else:
                next_year = year
                next_month = month_num + 1

            query = query.filter(
                models.Transaction.date < datetime(next_year, next_month, 1).date()
            )
        except (ValueError, IndexError):
            # Invalid month format, ignore filter
            pass

    transactions = query.offset(skip).limit(limit).all()
    return transactions

@router.post("/", response_model=schemas.TransactionResponse)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new transaction (for receipt upload feature)
    
    Features:
    - Automatic categorization (if category not provided)
    - Telegram notifications (if enabled)
    - Large expense alerts (if enabled)
    """
    # Import categorization service
    from services.categorization_service import categorization_service
    
    # Create transaction dict
    tx_data = transaction.dict()
    
    # Auto-categorize if no category provided
    if not tx_data.get("category"):
        cat_result = await categorization_service.categorize(
            merchant=tx_data["merchant"],
            amount=tx_data["amount"],
            date=str(tx_data["date"])
        )
        tx_data["category"] = cat_result["category"]
        print(f"✨ Auto-categorized '{tx_data['merchant']}' as '{cat_result['category']}' (method: {cat_result['method']})")
    
    db_transaction = models.Transaction(**tx_data)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Send Telegram notifications
    if telegram_service.enabled:
        # Check if new transaction notifications are enabled
        if os.getenv("TELEGRAM_NOTIFY_NEW_TRANSACTIONS", "false").lower() == "true":
            # Determine transaction type
            tx_type = "💰 收入" if db_transaction.amount > 0 else "💸 支出"
            
            message = f"""
{tx_type} <b>新交易</b>

<b>商家:</b> {db_transaction.merchant}
<b>金额:</b> ${abs(db_transaction.amount):.2f}
<b>日期:</b> {db_transaction.date}
<b>分类:</b> {db_transaction.category or '未分类'}
<b>状态:</b> {db_transaction.status.value}
"""
            await telegram_service.send_message(message.strip())
        
        # Check for large expense alert
        if os.getenv("TELEGRAM_NOTIFY_LARGE_EXPENSES", "false").lower() == "true":
            threshold = float(os.getenv("TELEGRAM_LARGE_EXPENSE_THRESHOLD", "500"))
            
            # Only alert for expenses (negative amounts)
            if db_transaction.amount < 0 and abs(db_transaction.amount) > threshold:
                message = f"""
⚠️ <b>大额支出告警</b>

<b>商家:</b> {db_transaction.merchant}
<b>金额:</b> ${abs(db_transaction.amount):.2f}
<b>超过阈值:</b> ${threshold:.2f}
<b>日期:</b> {db_transaction.date}
<b>分类:</b> {db_transaction.category or '未分类'}

请确认此笔交易是否正常。
"""
                await telegram_service.send_message(message.strip())
    
    return db_transaction

@router.put("/{transaction_id}/approve", response_model=schemas.TransactionResponse)
def approve_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Approve a transaction (change status from Pending to Posted)
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = models.TransactionStatus.POSTED
    db.commit()
    db.refresh(transaction)
    return transaction

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a transaction's details
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a transaction
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully", "id": transaction_id}

@router.post("/{transaction_id}/reject", response_model=schemas.TransactionResponse)
def reject_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Reject a transaction (change status to Rejected)
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = models.TransactionStatus.REJECTED
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific transaction by ID
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction
