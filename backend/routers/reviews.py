"""
Pending Reviews API - Document scanning and approval workflow
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pathlib import Path

from database import get_db
from routers.auth import get_current_user
from models import PendingReview, Document, User, InsurancePolicy, ReviewStatus, EntityType, ParsingStatus
from schemas_reviews import (
    PendingReviewResponse,
    PendingReviewUpdate,
    PendingReviewApprove,
    PendingReviewReject,
    DocumentUploadResponse
)
from services.ai_document_parser import ai_parser

router = APIRouter(prefix="/api/v3/reviews", tags=["Document Reviews v3.0"])

# File upload configuration
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload/insurance", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_insurance_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and scan an insurance policy document.
    Creates a pending review for admin approval.
    """
    try:
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Save file
        file_extension = Path(file.filename).suffix
        file_name = f"{datetime.utcnow().timestamp()}_{file.filename}"
        file_path = UPLOAD_DIR / file_name

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create document record
        document = Document(
            file_name=file.filename,
            file_path=str(file_path),
            file_type=file.content_type,
            file_size=file_size,
            parsing_status=ParsingStatus.PROCESSING,
            linked_entity="insurance",
            user_id=current_user.id
        )
        db.add(document)
        db.flush()  # Get document ID

        # Parse document with AI
        parsed_data, confidence = await ai_parser.parse_insurance_document(str(file_path))

        # Update document with parsed data
        document.parsed_data = parsed_data
        document.ai_confidence = confidence
        document.parsing_status = ParsingStatus.COMPLETED

        # Create pending review
        pending_review = PendingReview(
            entity_type="insurance",
            parsed_data=parsed_data,
            ai_confidence=confidence,
            status="pending",
            original_file_id=document.id,
            user_id=current_user.id
        )
        db.add(pending_review)
        db.commit()
        db.refresh(pending_review)

        return DocumentUploadResponse(
            document_id=document.id,
            review_id=pending_review.id,
            status="pending_review",
            ai_confidence=confidence,
            parsed_preview=parsed_data
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
    finally:
        file.file.close()

@router.get("/pending", response_model=List[PendingReviewResponse])
def get_pending_reviews(
    entity_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of pending reviews.
    Admin can see all, regular users see only their own.
    """
    query = db.query(PendingReview).filter(PendingReview.status == "pending")

    # Filter by entity type if specified
    if entity_type:
        query = query.filter(PendingReview.entity_type == entity_type)

    # Non-admin users can only see their own reviews
    if current_user.role.value != "Admin":
        query = query.filter(PendingReview.user_id == current_user.id)

    reviews = query.order_by(PendingReview.created_at.desc()).offset(skip).limit(limit).all()

    # Enrich with document information
    result = []
    for review in reviews:
        review_dict = {
            "id": review.id,
            "entity_type": review.entity_type,
            "parsed_data": review.parsed_data,
            "ai_confidence": review.ai_confidence,
            "status": review.status,
            "reviewer_id": review.reviewer_id,
            "linked_entity_id": review.linked_entity_id,
            "reviewed_at": review.reviewed_at,
            "user_id": review.user_id,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "reviewer_notes": review.reviewer_notes,
            "document": {
                "id": review.document.id,
                "file_name": review.document.file_name,
                "file_path": review.document.file_path,
                "file_type": review.document.file_type,
                "upload_date": review.document.upload_date.isoformat() if review.document.upload_date else None
            } if review.document else None
        }
        result.append(PendingReviewResponse(**review_dict))

    return result

@router.get("/{review_id}", response_model=PendingReviewResponse)
def get_pending_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific pending review"""
    review = db.query(PendingReview).filter(PendingReview.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check permissions
    if current_user.role.value != "Admin" and review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this review")

    return review

@router.put("/{review_id}", response_model=PendingReviewResponse)
def update_pending_review(
    review_id: int,
    update_data: PendingReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update parsed data in a pending review.
    Allows human editing before approval.
    """
    review = db.query(PendingReview).filter(PendingReview.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Only pending reviews can be updated
    if review.status != "pending":
        raise HTTPException(status_code=400, detail="Can only update pending reviews")

    # Update fields
    if update_data.parsed_data is not None:
        review.parsed_data = update_data.parsed_data

    if update_data.reviewer_notes is not None:
        review.reviewer_notes = update_data.reviewer_notes

    review.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(review)

    return review

@router.post("/{review_id}/approve", status_code=status.HTTP_200_OK)
def approve_review(
    review_id: int,
    approval_data: PendingReviewApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a pending review and create the formal entity.
    Only Admin users can approve.
    """
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can approve reviews")

    review = db.query(PendingReview).filter(PendingReview.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status != "pending":
        raise HTTPException(status_code=400, detail="Review already processed")

    try:
        # Create formal entity based on type
        final_data = approval_data.final_data

        if review.entity_type == "insurance":
            # Create insurance policy
            insurance = InsurancePolicy(
                provider=final_data.get("provider", ""),
                type=final_data.get("type", "Health"),
                policy_number=final_data.get("policy_number", "N/A"),
                renewal_date=final_data.get("renewal_date", datetime.utcnow().date()),
                premium=float(final_data.get("premium", 0)),
                frequency=final_data.get("frequency", "Monthly"),
                insured_item=final_data.get("insured_item", "")
            )
            db.add(insurance)
            db.flush()
            linked_id = insurance.id

        else:
            # TODO: Handle other entity types (transaction, asset, etc.)
            raise HTTPException(status_code=400, detail=f"Entity type {review.entity_type} not yet supported")

        # Update review status
        review.status = "approved"
        review.reviewer_id = current_user.id
        review.linked_entity_id = linked_id
        review.reviewed_at = datetime.utcnow()
        if approval_data.reviewer_notes:
            review.reviewer_notes = approval_data.reviewer_notes

        # Update document link
        if review.document:
            review.document.linked_entity = review.entity_type
            review.document.linked_id = linked_id

        db.commit()

        return {
            "status": "approved",
            "entity_type": review.entity_type,
            "entity_id": linked_id,
            "review_id": review.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve review: {str(e)}"
        )

@router.post("/{review_id}/reject", status_code=status.HTTP_200_OK)
def reject_review(
    review_id: int,
    rejection_data: PendingReviewReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a pending review.
    Only Admin users can reject.
    """
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can reject reviews")

    review = db.query(PendingReview).filter(PendingReview.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status != "pending":
        raise HTTPException(status_code=400, detail="Review already processed")

    # Update review status
    review.status = "rejected"
    review.reviewer_id = current_user.id
    review.reviewed_at = datetime.utcnow()
    review.reviewer_notes = rejection_data.reviewer_notes

    db.commit()

    return {
        "status": "rejected",
        "review_id": review.id,
        "reason": rejection_data.reviewer_notes
    }
