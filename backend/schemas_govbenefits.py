"""
Pydantic schemas for Government Benefits API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class GovBenefitBase(BaseModel):
    name: str = Field(..., max_length=200)
    benefit_type: str = Field(..., max_length=50)  # CCB, GST, OAS, CPP, EI
    amount: Decimal
    frequency: str = "MONTHLY"  # WEEKLY, BIWEEKLY, MONTHLY, QUARTERLY, SEMI_ANNUALLY, ANNUALLY
    next_payment_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    government_agency: Optional[str] = Field(None, max_length=100)
    beneficiary: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    extra_data: Optional[dict] = None
    is_active: bool = True

class GovBenefitCreate(GovBenefitBase):
    pass

class GovBenefitUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    benefit_type: Optional[str] = Field(None, max_length=50)
    amount: Optional[Decimal] = None
    frequency: Optional[str] = None
    next_payment_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    government_agency: Optional[str] = Field(None, max_length=100)
    beneficiary: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    extra_data: Optional[dict] = None
    is_active: Optional[bool] = None

class GovBenefitResponse(GovBenefitBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
