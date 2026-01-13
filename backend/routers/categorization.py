"""
Batch Categorization Endpoint
Categorize multiple pending transactions at once
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from database import get_db
import models
from routers.auth import get_current_user
from services.categorization_service import categorization_service


router = APIRouter(prefix="/api/categorization", tags=["Categorization"])


class BatchCategorizationRequest(BaseModel):
    """Request to categorize multiple transactions"""
    transaction_ids: List[int]


class CategorizationResult(BaseModel):
    """Result of categorizing a single transaction"""
    transaction_id: int
    merchant: str
    old_category: str
    new_category: str
    confidence: int
    method: str
    reasoning: str


class BatchCategorizationResponse(BaseModel):
    """Response from batch categorization"""
    total: int
    updated: int
    results: List[CategorizationResult]


@router.post("/batch", response_model=BatchCategorizationResponse)
async def categorize_batch(
    request: BatchCategorizationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Categorize multiple transactions at once
    
    Useful for:
    - Re-categorizing existing transactions
    - Applying new rules to old data
    - Improving categorization accuracy
    """
    results = []
    updated_count = 0
    
    for tx_id in request.transaction_ids:
        # Get transaction
        transaction = db.query(models.Transaction).filter(
            models.Transaction.id == tx_id
        ).first()
        
        if not transaction:
            continue
        
        old_category = transaction.category or "None"
        
        # Categorize
        cat_result = await categorization_service.categorize(
            merchant=transaction.merchant,
            amount=transaction.amount,
            date=str(transaction.date)
        )
        
        # Update if different
        if cat_result["category"] != old_category:
            transaction.category = cat_result["category"]
            updated_count += 1
        
        results.append(CategorizationResult(
            transaction_id=transaction.id,
            merchant=transaction.merchant,
            old_category=old_category,
            new_category=cat_result["category"],
            confidence=cat_result["confidence"],
            method=cat_result["method"],
            reasoning=cat_result["reasoning"]
        ))
    
    # Commit all changes
    db.commit()
    
    return BatchCategorizationResponse(
        total=len(results),
        updated=updated_count,
        results=results
    )


@router.post("/pending", response_model=BatchCategorizationResponse)
async def categorize_pending(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Categorize all pending transactions without categories
    
    Automatically finds and categorizes:
    - Transactions with status = Pending
    - Transactions with no category or category = "Other - Miscellaneous"
    """
    # Find pending transactions without proper categories
    transactions = db.query(models.Transaction).filter(
        models.Transaction.status == models.TransactionStatus.PENDING,
        models.Transaction.category.in_([None, "", "Other - Miscellaneous"])
    ).all()
    
    results = []
    updated_count = 0
    
    for transaction in transactions:
        old_category = transaction.category or "None"
        
        # Categorize
        cat_result = await categorization_service.categorize(
            merchant=transaction.merchant,
            amount=transaction.amount,
            date=str(transaction.date)
        )
        
        # Update
        transaction.category = cat_result["category"]
        updated_count += 1
        
        results.append(CategorizationResult(
            transaction_id=transaction.id,
            merchant=transaction.merchant,
            old_category=old_category,
            new_category=cat_result["category"],
            confidence=cat_result["confidence"],
            method=cat_result["method"],
            reasoning=cat_result["reasoning"]
        ))
    
    # Commit all changes
    db.commit()
    
    return BatchCategorizationResponse(
        total=len(results),
        updated=updated_count,
        results=results
    )


@router.get("/stats")
async def get_categorization_stats(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get categorization service statistics
    
    Shows:
    - Total categorizations
    - Rule match rate
    - AI usage rate
    - Default fallback rate
    """
    return categorization_service.get_stats()
