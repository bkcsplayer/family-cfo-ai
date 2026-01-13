"""
AI Router - Endpoints for AI-powered features
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from routers.auth import get_current_user
from services.ai_service import ai_service, get_all_categories

router = APIRouter(prefix="/api/ai", tags=["AI"])


# Request/Response Models
class TransactionCategorizationRequest(BaseModel):
    merchant: str
    amount: float
    date: Optional[str] = None
    description: Optional[str] = None


class BatchCategorizationRequest(BaseModel):
    transactions: List[dict]


class CategorizationResponse(BaseModel):
    category: str
    confidence: int
    reasoning: str
    is_income: bool


# Endpoints
@router.post("/categorize-transaction", response_model=CategorizationResponse)
async def categorize_transaction(
    request: TransactionCategorizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Categorize a single transaction using AI
    
    Example:
    ```json
    {
        "merchant": "Costco",
        "amount": -234.56,
        "date": "2025-12-27",
        "description": "Grocery shopping"
    }
    ```
    """
    if not ai_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Please set up OpenRouter or OpenAI API keys in .env file."
        )
    
    try:
        result = await ai_service.categorize_transaction(
            merchant=request.merchant,
            amount=request.amount,
            date=request.date,
            description=request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categorize-batch")
async def categorize_batch(
    request: BatchCategorizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Categorize multiple transactions in batch
    
    Example:
    ```json
    {
        "transactions": [
            {"id": 1, "merchant": "Costco", "amount": -234.56},
            {"id": 2, "merchant": "Shell", "amount": -78.90}
        ]
    }
    ```
    """
    if not ai_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured. Please set up OpenRouter or OpenAI API keys in .env file."
        )
    
    try:
        results = await ai_service.categorize_batch(request.transactions)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
    """
    Get list of all available categories
    """
    return {
        "categories": get_all_categories(),
        "count": len(get_all_categories())
    }
