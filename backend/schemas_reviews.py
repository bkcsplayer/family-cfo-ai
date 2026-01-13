"""
Pydantic schemas for pending reviews and document scanning workflow.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class DocumentUploadResponse(BaseModel):
    """Response after uploading a document for scanning"""
    document_id: int
    review_id: int
    status: str = "pending_review"
    ai_confidence: Optional[Decimal] = None
    parsed_preview: Optional[Dict[str, Any]] = None

class PendingReviewBase(BaseModel):
    """Base schema for pending review"""
    entity_type: str = Field(..., description="Type of entity: insurance, transaction, asset, etc.")
    parsed_data: Dict[str, Any] = Field(..., description="AI-extracted structured data")
    ai_confidence: Optional[Decimal] = Field(None, ge=0, le=1, description="AI confidence score 0-1")
    reviewer_notes: Optional[str] = None

class PendingReviewCreate(PendingReviewBase):
    """Schema for creating a pending review"""
    original_file_id: int
    user_id: int

class PendingReviewUpdate(BaseModel):
    """Schema for updating parsed data during review"""
    parsed_data: Optional[Dict[str, Any]] = None
    reviewer_notes: Optional[str] = None

class PendingReviewApprove(BaseModel):
    """Schema for approving a review with final data"""
    final_data: Dict[str, Any] = Field(..., description="Final approved data after human review")
    reviewer_notes: Optional[str] = None

class PendingReviewReject(BaseModel):
    """Schema for rejecting a review"""
    reviewer_notes: str = Field(..., description="Reason for rejection")

class PendingReviewResponse(PendingReviewBase):
    """Response schema for pending review"""
    id: int
    status: str
    reviewer_id: Optional[int] = None
    linked_entity_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Include document info
    document: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class InsuranceParsedData(BaseModel):
    """Example schema for parsed insurance data"""
    provider: str
    type: str  # Auto, Home, Life, Health, Disability
    policy_number: Optional[str] = None
    coverage_amount: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    frequency: Optional[str] = "Monthly"
    renewal_date: Optional[str] = None
    insured_item: Optional[str] = None
    reimbursement_details: Optional[Dict[str, Any]] = None  # e.g., {"dental": 0.8, "vision": 0.5}
    notes: Optional[str] = None
