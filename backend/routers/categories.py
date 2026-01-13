from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas
from routers.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories (v3.0)"])

# ==================== HELPER FUNCTIONS ====================
def build_category_tree(categories: List[models.Category], parent_id: Optional[int] = None) -> List[schemas.CategoryTree]:
    """
    Recursively build a category tree structure.
    """
    tree = []
    for category in categories:
        if category.parent_id == parent_id:
            category_dict = schemas.CategoryTree.from_orm(category).dict()
            category_dict['subcategories'] = build_category_tree(categories, category.id)
            tree.append(schemas.CategoryTree(**category_dict))
    return tree

# ==================== CRUD ENDPOINTS ====================
@router.get("/", response_model=List[schemas.CategoryResponse])
def list_categories(
    type: Optional[schemas.CategoryType] = Query(None, description="Filter by category type"),
    is_system: Optional[bool] = Query(None, description="Filter system vs user categories"),
    is_active: bool = Query(True, description="Show only active categories"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List all categories with optional filtering.
    Returns both system and user-defined categories.
    """
    query = db.query(models.Category)

    # Filter by type
    if type:
        query = query.filter(models.Category.type == type)

    # Filter by system/user
    if is_system is not None:
        query = query.filter(models.Category.is_system == is_system)

    # Filter by active status
    query = query.filter(models.Category.is_active == is_active)

    # Filter by user (show user's categories + system categories)
    query = query.filter(
        (models.Category.user_id == current_user.id) |
        (models.Category.is_system == True)
    )

    categories = query.order_by(models.Category.name).all()
    return categories

@router.get("/tree", response_model=List[schemas.CategoryTree])
def get_category_tree(
    type: Optional[schemas.CategoryType] = Query(None, description="Filter by category type"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get hierarchical category tree structure.
    Returns nested categories with parent-child relationships.
    """
    query = db.query(models.Category).filter(models.Category.is_active == True)

    # Filter by type
    if type:
        query = query.filter(models.Category.type == type)

    # Filter by user (show user's categories + system categories)
    query = query.filter(
        (models.Category.user_id == current_user.id) |
        (models.Category.is_system == True)
    )

    categories = query.all()
    return build_category_tree(categories)

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific category by ID."""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check access: must be system category or belong to current user
    if not category.is_system and category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this category")

    return category

@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new user-defined category.
    System categories cannot be created via API.
    """
    # Validate parent exists if specified
    if category.parent_id:
        parent = db.query(models.Category).filter(models.Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")

        # Ensure parent belongs to user or is system category
        if not parent.is_system and parent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot use another user's category as parent")

    # Create category
    category_data = category.dict(exclude={'user_id'})
    db_category = models.Category(
        **category_data,
        user_id=current_user.id,
        is_system=False  # User-created categories are never system categories
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing category.
    System categories cannot be modified.
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Cannot modify system categories
    if db_category.is_system:
        raise HTTPException(status_code=403, detail="Cannot modify system categories")

    # Check ownership
    if db_category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this category")

    # Validate parent if being changed
    if category.parent_id is not None:
        # Prevent setting self as parent
        if category.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")

        # Validate parent exists
        parent = db.query(models.Category).filter(models.Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")

        # Ensure parent belongs to user or is system category
        if not parent.is_system and parent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot use another user's category as parent")

    # Update fields
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a category (soft delete by setting is_active=False).
    System categories cannot be deleted.
    Categories with subcategories or linked assets/liabilities cannot be deleted.
    """
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Cannot delete system categories
    if db_category.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system categories")

    # Check ownership
    if db_category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this category")

    # Check for subcategories
    subcategories = db.query(models.Category).filter(
        models.Category.parent_id == category_id,
        models.Category.is_active == True
    ).count()
    if subcategories > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {subcategories} active subcategories. Delete or reassign subcategories first."
        )

    # Check for linked assets
    linked_assets = db.query(models.AssetV3).filter(
        models.AssetV3.category_id == category_id,
        models.AssetV3.is_active == True
    ).count()
    if linked_assets > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {linked_assets} linked assets. Reassign or delete assets first."
        )

    # Check for linked liabilities
    linked_liabilities = db.query(models.Liability).filter(
        models.Liability.category_id == category_id,
        models.Liability.is_active == True
    ).count()
    if linked_liabilities > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {linked_liabilities} linked liabilities. Reassign or delete liabilities first."
        )

    # Soft delete
    db_category.is_active = False
    db.commit()

    return {"message": "Category deleted successfully"}

# ==================== UTILITY ENDPOINTS ====================
@router.get("/{category_id}/subcategories", response_model=List[schemas.CategoryResponse])
def get_subcategories(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all direct subcategories of a category."""
    # Verify parent exists and user has access
    parent = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent category not found")

    if not parent.is_system and parent.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this category")

    # Get subcategories
    subcategories = db.query(models.Category).filter(
        models.Category.parent_id == category_id,
        models.Category.is_active == True
    ).order_by(models.Category.name).all()

    return subcategories
