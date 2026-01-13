from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from database import get_db
import models
import schemas
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v3", tags=["Assets & Liabilities (v3.0)"])

# ==================== ASSETS V3 ====================
@router.get("/assets", response_model=List[schemas.AssetV3Response])
def list_assets_v3(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    refresh_source: Optional[schemas.RefreshSource] = Query(None, description="Filter by refresh source"),
    is_active: bool = Query(True, description="Show only active assets"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all user's assets with optional filtering.
    """
    query = db.query(models.AssetV3).filter(models.AssetV3.user_id == current_user.id)

    if category_id:
        query = query.filter(models.AssetV3.category_id == category_id)

    if refresh_source:
        query = query.filter(models.AssetV3.refresh_source == refresh_source)

    query = query.filter(models.AssetV3.is_active == is_active)

    assets = query.order_by(models.AssetV3.created_at.desc()).all()
    return assets

@router.get("/assets/summary")
def get_assets_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get summary of all assets grouped by category.
    """
    from sqlalchemy import func

    # Get total value per category
    category_summary = db.query(
        models.Category.name,
        models.Category.type,
        func.sum(models.AssetV3.current_value).label('total_value'),
        func.count(models.AssetV3.id).label('count')
    ).join(
        models.AssetV3, models.AssetV3.category_id == models.Category.id
    ).filter(
        models.AssetV3.user_id == current_user.id,
        models.AssetV3.is_active == True
    ).group_by(
        models.Category.id, models.Category.name, models.Category.type
    ).all()

    # Calculate totals
    total_assets = db.query(func.sum(models.AssetV3.current_value)).filter(
        models.AssetV3.user_id == current_user.id,
        models.AssetV3.is_active == True
    ).scalar() or Decimal(0)

    return {
        "total_value": total_assets,
        "category_breakdown": [
            {
                "category_name": cat.name,
                "category_type": cat.type,
                "total_value": cat.total_value,
                "count": cat.count
            }
            for cat in category_summary
        ],
        "last_updated": datetime.utcnow()
    }

@router.get("/assets/{asset_id}", response_model=schemas.AssetV3Response)
def get_asset_v3(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific asset by ID."""
    asset = db.query(models.AssetV3).filter(
        models.AssetV3.id == asset_id,
        models.AssetV3.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset

@router.post("/assets", response_model=schemas.AssetV3Response, status_code=201)
def create_asset_v3(
    asset: schemas.AssetV3Create,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new asset."""
    # Validate category exists and is an asset category
    category = db.query(models.Category).filter(models.Category.id == asset.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.type != schemas.CategoryType.ASSET:
        raise HTTPException(status_code=400, detail="Category must be of type 'asset'")

    # Ensure category belongs to user or is system category
    if not category.is_system and category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot use another user's category")

    # Create asset
    asset_data = asset.dict(exclude={'user_id'})
    db_asset = models.AssetV3(**asset_data, user_id=current_user.id)

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.put("/assets/{asset_id}", response_model=schemas.AssetV3Response)
def update_asset_v3(
    asset_id: int,
    asset: schemas.AssetV3Update,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing asset."""
    db_asset = db.query(models.AssetV3).filter(
        models.AssetV3.id == asset_id,
        models.AssetV3.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Validate category if being changed
    if asset.category_id is not None:
        category = db.query(models.Category).filter(models.Category.id == asset.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category.type != schemas.CategoryType.ASSET:
            raise HTTPException(status_code=400, detail="Category must be of type 'asset'")

        if not category.is_system and category.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot use another user's category")

    # Update fields
    for key, value in asset.dict(exclude_unset=True).items():
        setattr(db_asset, key, value)

    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.delete("/assets/{asset_id}")
def delete_asset_v3(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an asset (soft delete)."""
    db_asset = db.query(models.AssetV3).filter(
        models.AssetV3.id == asset_id,
        models.AssetV3.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Soft delete
    db_asset.is_active = False
    db.commit()

    return {"message": "Asset deleted successfully"}

# ==================== LIABILITIES ====================
@router.get("/liabilities", response_model=List[schemas.LiabilityResponse])
def list_liabilities(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    is_active: bool = Query(True, description="Show only active liabilities"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all user's liabilities with optional filtering.
    """
    query = db.query(models.Liability).filter(models.Liability.user_id == current_user.id)

    if category_id:
        query = query.filter(models.Liability.category_id == category_id)

    query = query.filter(models.Liability.is_active == is_active)

    liabilities = query.order_by(models.Liability.created_at.desc()).all()
    return liabilities

@router.get("/liabilities/summary")
def get_liabilities_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get summary of all liabilities grouped by category.
    """
    from sqlalchemy import func

    # Get total balance per category
    category_summary = db.query(
        models.Category.name,
        models.Category.type,
        func.sum(models.Liability.principal_balance).label('total_balance'),
        func.count(models.Liability.id).label('count')
    ).join(
        models.Liability, models.Liability.category_id == models.Category.id
    ).filter(
        models.Liability.user_id == current_user.id,
        models.Liability.is_active == True
    ).group_by(
        models.Category.id, models.Category.name, models.Category.type
    ).all()

    # Calculate totals
    total_liabilities = db.query(func.sum(models.Liability.principal_balance)).filter(
        models.Liability.user_id == current_user.id,
        models.Liability.is_active == True
    ).scalar() or Decimal(0)

    return {
        "total_balance": total_liabilities,
        "category_breakdown": [
            {
                "category_name": cat.name,
                "category_type": cat.type,
                "total_balance": cat.total_balance,
                "count": cat.count
            }
            for cat in category_summary
        ],
        "last_updated": datetime.utcnow()
    }

@router.get("/liabilities/{liability_id}", response_model=schemas.LiabilityResponse)
def get_liability(
    liability_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific liability by ID."""
    liability = db.query(models.Liability).filter(
        models.Liability.id == liability_id,
        models.Liability.user_id == current_user.id
    ).first()

    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")

    return liability

@router.post("/liabilities", response_model=schemas.LiabilityResponse, status_code=201)
def create_liability(
    liability: schemas.LiabilityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new liability."""
    # Validate category exists and is a liability category
    category = db.query(models.Category).filter(models.Category.id == liability.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.type != schemas.CategoryType.LIABILITY:
        raise HTTPException(status_code=400, detail="Category must be of type 'liability'")

    # Ensure category belongs to user or is system category
    if not category.is_system and category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot use another user's category")

    # Create liability
    liability_data = liability.dict(exclude={'user_id'})
    db_liability = models.Liability(**liability_data, user_id=current_user.id)

    db.add(db_liability)
    db.commit()
    db.refresh(db_liability)
    return db_liability

@router.put("/liabilities/{liability_id}", response_model=schemas.LiabilityResponse)
def update_liability(
    liability_id: int,
    liability: schemas.LiabilityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing liability."""
    db_liability = db.query(models.Liability).filter(
        models.Liability.id == liability_id,
        models.Liability.user_id == current_user.id
    ).first()

    if not db_liability:
        raise HTTPException(status_code=404, detail="Liability not found")

    # Validate category if being changed
    if liability.category_id is not None:
        category = db.query(models.Category).filter(models.Category.id == liability.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category.type != schemas.CategoryType.LIABILITY:
            raise HTTPException(status_code=400, detail="Category must be of type 'liability'")

        if not category.is_system and category.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot use another user's category")

    # Update fields
    for key, value in liability.dict(exclude_unset=True).items():
        setattr(db_liability, key, value)

    db.commit()
    db.refresh(db_liability)
    return db_liability

@router.delete("/liabilities/{liability_id}")
def delete_liability(
    liability_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a liability (soft delete)."""
    db_liability = db.query(models.Liability).filter(
        models.Liability.id == liability_id,
        models.Liability.user_id == current_user.id
    ).first()

    if not db_liability:
        raise HTTPException(status_code=404, detail="Liability not found")

    # Soft delete
    db_liability.is_active = False
    db.commit()

    return {"message": "Liability deleted successfully"}

# ==================== NET WORTH CALCULATION ====================
@router.get("/net-worth", response_model=schemas.NetWorthSummary)
def calculate_net_worth(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Calculate comprehensive net worth.
    Net Worth = Total Assets - Total Liabilities
    """
    from sqlalchemy import func

    # Calculate total assets
    total_assets = db.query(func.sum(models.AssetV3.current_value)).filter(
        models.AssetV3.user_id == current_user.id,
        models.AssetV3.is_active == True
    ).scalar() or Decimal(0)

    # Calculate total liabilities
    total_liabilities = db.query(func.sum(models.Liability.principal_balance)).filter(
        models.Liability.user_id == current_user.id,
        models.Liability.is_active == True
    ).scalar() or Decimal(0)

    # Asset breakdown by category
    asset_breakdown = {}
    asset_categories = db.query(
        models.Category.name,
        func.sum(models.AssetV3.current_value).label('total')
    ).join(
        models.AssetV3, models.AssetV3.category_id == models.Category.id
    ).filter(
        models.AssetV3.user_id == current_user.id,
        models.AssetV3.is_active == True
    ).group_by(models.Category.name).all()

    for cat in asset_categories:
        asset_breakdown[cat.name] = cat.total

    # Liability breakdown by category
    liability_breakdown = {}
    liability_categories = db.query(
        models.Category.name,
        func.sum(models.Liability.principal_balance).label('total')
    ).join(
        models.Liability, models.Liability.category_id == models.Category.id
    ).filter(
        models.Liability.user_id == current_user.id,
        models.Liability.is_active == True
    ).group_by(models.Category.name).all()

    for cat in liability_categories:
        liability_breakdown[cat.name] = cat.total

    return schemas.NetWorthSummary(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        asset_breakdown=asset_breakdown,
        liability_breakdown=liability_breakdown,
        last_updated=datetime.utcnow()
    )
