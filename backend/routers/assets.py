from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Assets & Accounts"])

# ==================== ASSETS ====================
@router.get("/assets", response_model=List[schemas.AssetResponse])
def list_assets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all assets (Real Estate, Vehicles, Stocks)"""
    assets = db.query(models.Asset).all()
    return assets

@router.post("/assets", response_model=schemas.AssetResponse)
def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new asset"""
    db_asset = models.Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.put("/assets/{asset_id}", response_model=schemas.AssetResponse)
def update_asset(
    asset_id: int,
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing asset"""
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for key, value in asset.dict(exclude_unset=True).items():
        setattr(db_asset, key, value)

    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an asset"""
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(db_asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

# ==================== CANADIAN ACCOUNTS ====================
@router.get("/accounts", response_model=List[schemas.CanadianAccountResponse])
def list_canadian_accounts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all Canadian registered accounts (TFSA, RRSP, RESP, FHSA)"""
    accounts = db.query(models.CanadianAccount).all()
    return accounts

@router.post("/accounts", response_model=schemas.CanadianAccountResponse)
def create_account(
    account: schemas.CanadianAccountCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new Canadian registered account"""
    db_account = models.CanadianAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/accounts/{account_id}", response_model=schemas.CanadianAccountResponse)
def update_account(
    account_id: int,
    account: schemas.CanadianAccountUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing account"""
    db_account = db.query(models.CanadianAccount).filter(models.CanadianAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in account.dict(exclude_unset=True).items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an account"""
    db_account = db.query(models.CanadianAccount).filter(models.CanadianAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(db_account)
    db.commit()
    return {"message": "Account deleted successfully"}

# ==================== SUBSCRIPTIONS ====================
@router.get("/subscriptions", response_model=List[schemas.SubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all active subscriptions"""
    subscriptions = db.query(models.Subscription).filter(
        models.Subscription.status == "Active"
    ).all()
    return subscriptions
