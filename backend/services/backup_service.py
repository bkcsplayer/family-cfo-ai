"""
Backup Service - Full database export/import with encryption support
"""
import json
import base64
import hashlib
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from decimal import Decimal
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy.orm import Session
from sqlalchemy import inspect

import models


class BackupService:
    """
    Database backup and restore service with encryption support.
    Exports all tables to JSON format and supports importing with merge capability.
    """
    
    # Tables to export (in order for proper foreign key handling)
    EXPORT_TABLES = [
        ("users", models.User),
        ("transactions", models.Transaction),
        ("assets", models.Asset),
        ("assets_v3", models.AssetV3),
        ("subscriptions", models.Subscription),
        ("canadian_accounts", models.CanadianAccount),
        ("insurance_policies", models.InsurancePolicy),
        ("budgets", models.Budget),
        ("categories", models.Category),
        ("liabilities", models.Liability),
        ("government_benefits", models.GovBenefit),
        ("documents", models.Document),
        ("pending_reviews", models.PendingReview),
    ]
    
    def __init__(self):
        self.version = "3.0"
    
    def _serialize_value(self, value: Any) -> Any:
        """Convert Python objects to JSON-serializable format"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, 'value'):  # Enum
            return value.value
        return value
    
    def _model_to_dict(self, obj) -> Dict:
        """Convert SQLAlchemy model instance to dictionary"""
        mapper = inspect(obj.__class__)
        result = {}
        for column in mapper.columns:
            value = getattr(obj, column.key)
            result[column.key] = self._serialize_value(value)
        return result
    
    def _generate_encryption_key(self, password: str, salt: bytes = None) -> tuple:
        """Generate Fernet encryption key from password"""
        if salt is None:
            salt = hashlib.sha256(b"familycfo_backup_salt").digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key), salt
    
    def export_all_data(self, db: Session, password: Optional[str] = None) -> Dict:
        """
        Export all database tables to a dictionary.
        
        Args:
            db: Database session
            password: Optional password for encryption
            
        Returns:
            Dictionary containing all table data (optionally encrypted)
        """
        export_data = {
            "version": self.version,
            "exported_at": datetime.utcnow().isoformat(),
            "encrypted": password is not None,
            "database_info": {
                "tables": [],
                "total_records": 0
            },
            "data": {}
        }
        
        total_records = 0
        
        for table_name, model_class in self.EXPORT_TABLES:
            try:
                records = db.query(model_class).all()
                table_data = [self._model_to_dict(record) for record in records]
                export_data["data"][table_name] = table_data
                export_data["database_info"]["tables"].append({
                    "name": table_name,
                    "count": len(table_data)
                })
                total_records += len(table_data)
            except Exception as e:
                # Table might not exist, skip it
                print(f"Warning: Could not export {table_name}: {e}")
                export_data["data"][table_name] = []
        
        export_data["database_info"]["total_records"] = total_records
        
        # Encrypt if password provided
        if password:
            fernet, salt = self._generate_encryption_key(password)
            data_json = json.dumps(export_data["data"])
            encrypted_data = fernet.encrypt(data_json.encode())
            export_data["data"] = base64.b64encode(encrypted_data).decode()
            export_data["salt"] = base64.b64encode(salt).decode()
        
        return export_data
    
    def decrypt_data(self, encrypted_data: str, password: str, salt: str) -> Dict:
        """Decrypt exported data using password"""
        try:
            salt_bytes = base64.b64decode(salt.encode())
            fernet, _ = self._generate_encryption_key(password, salt_bytes)
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Decryption failed: Invalid password or corrupted data - {e}")
    
    def validate_import_data(self, data: Dict) -> Dict:
        """
        Validate import data structure and compatibility.
        
        Returns:
            Validation result with status and any warnings
        """
        result = {
            "valid": True,
            "version": data.get("version", "unknown"),
            "encrypted": data.get("encrypted", False),
            "tables_found": [],
            "missing_tables": [],
            "warnings": []
        }
        
        if "data" not in data:
            result["valid"] = False
            result["warnings"].append("Missing 'data' field in import file")
            return result
        
        expected_tables = [t[0] for t in self.EXPORT_TABLES]
        
        if isinstance(data["data"], str):
            # Encrypted data - need password to validate further
            result["warnings"].append("Data is encrypted - provide password to import")
            return result
        
        for table_name in expected_tables:
            if table_name in data["data"]:
                result["tables_found"].append(table_name)
            else:
                result["missing_tables"].append(table_name)
        
        if result["missing_tables"]:
            result["warnings"].append(f"Missing tables: {', '.join(result['missing_tables'])}")
        
        return result
    
    def import_all_data(
        self, 
        db: Session, 
        data: Dict, 
        password: Optional[str] = None,
        merge: bool = True,
        skip_users: bool = True
    ) -> Dict:
        """
        Import data from backup.
        
        Args:
            db: Database session
            data: Import data dictionary
            password: Password for encrypted backups
            merge: If True, merge with existing data; if False, replace
            skip_users: Skip importing users (security)
            
        Returns:
            Import result summary
        """
        result = {
            "success": True,
            "imported_tables": [],
            "skipped_tables": [],
            "errors": [],
            "total_imported": 0
        }
        
        # Handle encrypted data
        import_data = data["data"]
        if data.get("encrypted") and password:
            try:
                import_data = self.decrypt_data(
                    data["data"], 
                    password, 
                    data.get("salt", "")
                )
            except ValueError as e:
                result["success"] = False
                result["errors"].append(str(e))
                return result
        elif data.get("encrypted") and not password:
            result["success"] = False
            result["errors"].append("Data is encrypted but no password provided")
            return result
        
        # Import each table
        for table_name, model_class in self.EXPORT_TABLES:
            if table_name == "users" and skip_users:
                result["skipped_tables"].append("users (security)")
                continue
                
            if table_name not in import_data:
                result["skipped_tables"].append(f"{table_name} (not in backup)")
                continue
            
            try:
                records = import_data[table_name]
                imported_count = 0
                
                for record_data in records:
                    # Check if record exists (by id)
                    existing = None
                    if "id" in record_data:
                        existing = db.query(model_class).filter(
                            model_class.id == record_data["id"]
                        ).first()
                    
                    if existing and merge:
                        # Update existing record
                        for key, value in record_data.items():
                            if key != "id" and hasattr(existing, key):
                                setattr(existing, key, value)
                    elif not existing:
                        # Create new record (without id to let DB assign)
                        new_record_data = {k: v for k, v in record_data.items() if k != "id"}
                        new_record = model_class(**new_record_data)
                        db.add(new_record)
                    
                    imported_count += 1
                
                db.commit()
                result["imported_tables"].append({
                    "name": table_name,
                    "count": imported_count
                })
                result["total_imported"] += imported_count
                
            except Exception as e:
                db.rollback()
                result["errors"].append(f"{table_name}: {str(e)}")
        
        if result["errors"]:
            result["success"] = False
        
        return result
    
    def get_database_status(self, db: Session) -> Dict:
        """Get current database status and table counts"""
        status = {
            "status": "healthy",
            "version": self.version,
            "timestamp": datetime.utcnow().isoformat(),
            "tables": []
        }
        
        for table_name, model_class in self.EXPORT_TABLES:
            try:
                count = db.query(model_class).count()
                status["tables"].append({
                    "name": table_name,
                    "count": count
                })
            except Exception as e:
                status["tables"].append({
                    "name": table_name,
                    "count": 0,
                    "error": str(e)
                })
        
        return status


# Global instance
backup_service = BackupService()
