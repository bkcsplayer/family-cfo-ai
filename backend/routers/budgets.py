"""
Budget Management API - CRUD operations and budget tracking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, date
from calendar import monthrange

from database import get_db
from models import Budget, Transaction, User
import schemas
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/budgets",
    tags=["budgets"]
)


@router.get("/", response_model=List[schemas.Budget])
async def get_budgets(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all budgets for the current user

    Query Parameters:
    - active_only: Only return active budgets (default: true)
    """
    query = db.query(Budget)

    # Filter by user_id if not None, otherwise show all
    if current_user.id:
        query = query.filter((Budget.user_id == current_user.id) | (Budget.user_id == None))

    if active_only:
        query = query.filter(Budget.is_active == True)

    budgets = query.all()

    # Update current_spent for each budget
    for budget in budgets:
        await update_budget_spent(budget, db)

    return budgets


@router.post("/", response_model=schemas.Budget)
async def create_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new budget

    Body:
    {
        "category": "Food - Restaurants",
        "monthly_limit": 500.00,
        "alert_threshold": 90.0,
        "user_id": 1
    }
    """
    # Check if budget already exists for this category
    existing = db.query(Budget).filter(
        Budget.category == budget.category,
        Budget.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Active budget already exists for category: {budget.category}"
        )

    # Set user_id to current user if not provided
    if budget.user_id is None:
        budget.user_id = current_user.id

    db_budget = Budget(**budget.dict())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)

    # Calculate initial current_spent
    await update_budget_spent(db_budget, db)

    print(f"✅ Budget created: {budget.category} - ${budget.monthly_limit}/month")

    return db_budget


@router.get("/status", response_model=List[schemas.BudgetStatus])
async def get_budget_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get budget usage status for all active budgets

    Returns:
    [
        {
            "id": 1,
            "category": "Food - Restaurants",
            "monthly_limit": 500.00,
            "current_spent": 325.50,
            "remaining": 174.50,
            "percentage_used": 65.1,
            "alert_threshold": 90.0,
            "is_over_budget": false,
            "is_near_limit": false
        }
    ]
    """
    budgets = db.query(Budget).filter(Budget.is_active == True).all()

    status_list = []
    for budget in budgets:
        # Update current_spent
        current_spent = await update_budget_spent(budget, db)

        remaining = budget.monthly_limit - current_spent
        percentage_used = (current_spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        status = schemas.BudgetStatus(
            id=budget.id,
            category=budget.category,
            monthly_limit=budget.monthly_limit,
            current_spent=current_spent,
            remaining=remaining,
            percentage_used=round(percentage_used, 1),
            alert_threshold=budget.alert_threshold,
            is_over_budget=current_spent > budget.monthly_limit,
            is_near_limit=percentage_used >= budget.alert_threshold
        )
        status_list.append(status)

    return status_list


@router.put("/{budget_id}", response_model=schemas.Budget)
async def update_budget(
    budget_id: int,
    budget_update: schemas.BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing budget
    """
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Update fields
    for field, value in budget_update.dict(exclude_unset=True).items():
        setattr(db_budget, field, value)

    db.commit()
    db.refresh(db_budget)

    print(f"✅ Budget updated: {db_budget.category}")

    return db_budget


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a budget (or mark as inactive)
    """
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Soft delete: mark as inactive instead of hard delete
    db_budget.is_active = False
    db.commit()

    print(f"✅ Budget deactivated: {db_budget.category}")

    return {"success": True, "message": f"Budget '{db_budget.category}' deactivated"}


async def update_budget_spent(budget: Budget, db: Session) -> float:
    """
    Update the current_spent field for a budget based on this month's transactions

    Returns the calculated current_spent value
    """
    # Get current month date range
    today = date.today()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    # Calculate total spent for this category this month
    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.category == budget.category,
        Transaction.date >= first_day,
        Transaction.date <= last_day,
        Transaction.amount < 0  # Only expenses (negative amounts)
    ).scalar()

    # Convert to positive value
    current_spent = abs(total_spent) if total_spent else 0.0

    # Update budget
    budget.current_spent = current_spent
    db.commit()

    return current_spent


@router.get("/check-alerts")
async def check_budget_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check all budgets for threshold violations and return alerts

    This endpoint can be called manually or by a scheduled task
    """
    budgets = db.query(Budget).filter(Budget.is_active == True).all()

    alerts = []

    for budget in budgets:
        current_spent = await update_budget_spent(budget, db)
        percentage_used = (current_spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        if percentage_used >= budget.alert_threshold:
            alert = {
                "budget_id": budget.id,
                "category": budget.category,
                "monthly_limit": budget.monthly_limit,
                "current_spent": current_spent,
                "percentage_used": round(percentage_used, 1),
                "alert_type": "over_budget" if percentage_used > 100 else "near_limit",
                "message": f"⚠️ Budget Alert: {budget.category} is at {round(percentage_used, 1)}% (${current_spent:.2f}/${budget.monthly_limit:.2f})"
            }
            alerts.append(alert)

            # Optional: Send Telegram notification
            try:
                from services.telegram_service import telegram_service
                if telegram_service.enabled:
                    await telegram_service.send_message(alert["message"])
            except Exception as e:
                print(f"⚠️ Telegram notification failed: {e}")

    return {
        "total_budgets": len(budgets),
        "alerts": alerts,
        "alert_count": len(alerts)
    }
