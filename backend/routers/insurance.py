from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from datetime import date
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/insurance",
    tags=["insurance"]
)

# --- SCHEMAS (Should be in schemas.py ideally, but defining here for quick fix if missing) ---
# Check if schemas.py has these. If not, I will add them there. 
# Let's assume I should double check schemas.py first, 
# but I'll write this file assuming I'll update schemas.py next.

@router.get("/", response_model=List[schemas.InsurancePolicyResponse])
def get_policies(db: Session = Depends(get_db)):
    return db.query(models.InsurancePolicy).all()

@router.post("/", response_model=schemas.InsurancePolicyResponse)
def create_policy(policy: schemas.InsurancePolicyCreate, db: Session = Depends(get_db)):
    db_policy = models.InsurancePolicy(
        provider=policy.provider,
        type=policy.type,
        policy_number=policy.policy_number,
        renewal_date=policy.renewal_date,
        premium=policy.premium,
        frequency=policy.frequency,
        insured_item=policy.insured_item
    )
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.put("/{policy_id}", response_model=schemas.InsurancePolicyResponse)
def update_policy(
    policy_id: int,
    policy: schemas.InsurancePolicyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing insurance policy"""
    db_policy = db.query(models.InsurancePolicy).filter(models.InsurancePolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    for key, value in policy.dict(exclude_unset=True).items():
        setattr(db_policy, key, value)
    
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an insurance policy"""
    db_policy = db.query(models.InsurancePolicy).filter(models.InsurancePolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(db_policy)
    db.commit()
    return {"message": "Policy deleted successfully"}
