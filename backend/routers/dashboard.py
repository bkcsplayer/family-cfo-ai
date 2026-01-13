from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict

from database import get_db
import models
from routers.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Dict:
    """
    Get dashboard statistics: Net Worth, Cash Flow, Burn Rate
    """
    # Calculate Net Worth (Assets + Canadian Accounts)
    total_assets = db.query(func.sum(models.Asset.value)).scalar() or 0
    total_accounts = db.query(func.sum(models.CanadianAccount.current_value)).scalar() or 0
    net_worth = total_assets + total_accounts
    
    # Calculate Cash Flow (Income vs Expenses - simplified for demo)
    # Positive amounts = expenses, negative = income (simplified logic)
    total_expenses = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.status == models.TransactionStatus.POSTED
    ).scalar() or 0
    
    # Burn Rate (average monthly spending)
    # For demo: total expenses / number of months (assuming 1 month of data)
    burn_rate = total_expenses
    
    return {
        "net_worth": round(net_worth, 2),
        "total_assets": round(total_assets, 2),
        "total_accounts": round(total_accounts, 2),
        "cash_flow": {
            "expenses": round(total_expenses, 2),
            "income": 0,  # Not tracked in current schema
            "net": round(-total_expenses, 2)
        },
        "burn_rate": round(burn_rate, 2),
        "currency": "CAD"
    }

@router.get("/recent-activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = 5
):
    """
    Get recent transactions
    """
    transactions = db.query(models.Transaction).order_by(
        models.Transaction.date.desc()
    ).limit(limit).all()
    
    return {
        "transactions": [
            {
                "id": t.id,
                "date": t.date.isoformat(),
                "merchant": t.merchant,
                "amount": t.amount,
                "category": t.category,
                "status": t.status.value
            }
            for t in transactions
        ]
    }
