"""
Government Benefits API Router
Handles CRUD operations for Canadian government benefits (CCB, GST, OAS, CPP, EI)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import GovBenefit, User
from schemas_govbenefits import GovBenefitCreate, GovBenefitUpdate, GovBenefitResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v3/gov-benefits", tags=["Government Benefits v3.0"])

@router.get("/", response_model=List[GovBenefitResponse])
def get_government_benefits(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all government benefits for the current user"""
    query = db.query(GovBenefit).filter(GovBenefit.user_id == current_user.id)

    if active_only:
        query = query.filter(GovBenefit.is_active == True)

    benefits = query.order_by(GovBenefit.next_payment_date.desc()).all()
    return benefits

@router.get("/{benefit_id}", response_model=GovBenefitResponse)
def get_government_benefit(
    benefit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific government benefit"""
    benefit = db.query(GovBenefit).filter(
        GovBenefit.id == benefit_id,
        GovBenefit.user_id == current_user.id
    ).first()

    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Government benefit not found"
        )

    return benefit

@router.post("/", response_model=GovBenefitResponse, status_code=status.HTTP_201_CREATED)
def create_government_benefit(
    benefit_data: GovBenefitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new government benefit"""
    new_benefit = GovBenefit(
        **benefit_data.model_dump(),
        user_id=current_user.id
    )

    db.add(new_benefit)
    db.commit()
    db.refresh(new_benefit)

    return new_benefit

@router.put("/{benefit_id}", response_model=GovBenefitResponse)
def update_government_benefit(
    benefit_id: int,
    benefit_data: GovBenefitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing government benefit"""
    benefit = db.query(GovBenefit).filter(
        GovBenefit.id == benefit_id,
        GovBenefit.user_id == current_user.id
    ).first()

    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Government benefit not found"
        )

    # Update only provided fields
    update_data = benefit_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(benefit, field, value)

    db.commit()
    db.refresh(benefit)

    return benefit

@router.delete("/{benefit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_government_benefit(
    benefit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a government benefit"""
    benefit = db.query(GovBenefit).filter(
        GovBenefit.id == benefit_id,
        GovBenefit.user_id == current_user.id
    ).first()

    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Government benefit not found"
        )

    db.delete(benefit)
    db.commit()

    return None

@router.get("/summary/annual", response_model=dict)
def get_annual_benefits_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate annual total of all active government benefits"""
    benefits = db.query(GovBenefit).filter(
        GovBenefit.user_id == current_user.id,
        GovBenefit.is_active == True
    ).all()

    annual_total = 0
    benefit_breakdown = []

    for benefit in benefits:
        # Calculate annual amount based on frequency
        multiplier = {
            "WEEKLY": 52,
            "BIWEEKLY": 26,
            "MONTHLY": 12,
            "QUARTERLY": 4,
            "SEMI_ANNUALLY": 2,
            "ANNUALLY": 1
        }.get(benefit.frequency, 12)

        annual_amount = float(benefit.amount) * multiplier
        annual_total += annual_amount

        benefit_breakdown.append({
            "id": benefit.id,
            "name": benefit.name,
            "benefit_type": benefit.benefit_type,
            "amount": float(benefit.amount),
            "frequency": benefit.frequency,
            "annual_amount": annual_amount
        })

    return {
        "annual_total": annual_total,
        "monthly_average": annual_total / 12,
        "total_benefits": len(benefits),
        "breakdown": benefit_breakdown
    }
