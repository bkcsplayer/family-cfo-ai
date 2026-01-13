"""
Backup API Router - Full database backup and restore endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
import io
from datetime import datetime

from database import get_db
from models import User
from routers.auth import get_current_user
from services.backup_service import backup_service


router = APIRouter(
    prefix="/api/backup",
    tags=["backup"]
)


class ExportRequest(BaseModel):
    """Request model for data export"""
    password: Optional[str] = None  # Optional encryption password
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "your_password_here"
            }
        }


class ImportRequest(BaseModel):
    """Request model for data import"""
    password: Optional[str] = None  # Password for encrypted backups
    merge: bool = True  # Merge with existing data or replace
    skip_users: bool = True  # Skip importing users for security
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "your_password_here",
                "merge": True,
                "skip_users": True
            }
        }


@router.post("/export")
async def export_all_data(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all database data to JSON.
    
    - **password**: Optional password for encryption (uses login password)
    
    Returns a JSON file containing all database tables.
    If password is provided, the data section will be encrypted.
    """
    try:
        export_data = backup_service.export_all_data(db, password=request.password)
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"familycfo_backup_{timestamp}.json"
        
        # Return as downloadable file
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        return StreamingResponse(
            io.BytesIO(json_str.encode('utf-8')),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/json")
async def export_all_data_json(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export all database data and return as JSON response (not file download).
    Useful for programmatic access.
    """
    try:
        export_data = backup_service.export_all_data(db, password=request.password)
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    password: Optional[str] = None,
    merge: bool = True,
    skip_users: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import data from a backup JSON file.
    
    - **file**: The backup JSON file to import
    - **password**: Password if the backup is encrypted
    - **merge**: If true, merge with existing data; if false, replace
    - **skip_users**: Skip importing users for security (recommended)
    
    Returns import result summary.
    """
    try:
        # Read and parse the uploaded file
        content = await file.read()
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Import the data
        result = backup_service.import_all_data(
            db=db,
            data=data,
            password=password,
            merge=merge,
            skip_users=skip_users
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/validate")
async def validate_import_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate an import file before actually importing.
    
    - **file**: The backup JSON file to validate
    
    Returns validation result with:
    - Version compatibility
    - Tables found/missing
    - Whether data is encrypted
    - Any warnings
    """
    try:
        content = await file.read()
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        result = backup_service.validate_import_data(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/status")
async def get_database_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current database status and table counts.
    
    Returns:
    - Database health status
    - List of all tables with record counts
    - Current version
    """
    try:
        status = backup_service.get_database_status(db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/info")
async def get_backup_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the backup system.
    
    Returns:
    - Available tables for backup
    - Current version
    - Encryption support status
    """
    return {
        "version": backup_service.version,
        "encryption_supported": True,
        "tables": [t[0] for t in backup_service.EXPORT_TABLES],
        "endpoints": {
            "export": "POST /api/backup/export",
            "export_json": "POST /api/backup/export/json",
            "import": "POST /api/backup/import",
            "validate": "POST /api/backup/validate",
            "status": "GET /api/backup/status"
        }
    }
