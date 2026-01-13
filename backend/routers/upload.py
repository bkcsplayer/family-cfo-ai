from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from datetime import datetime, date
from database import get_db
from models import Transaction, TransactionStatus
import json

router = APIRouter(
    prefix="/api/upload",
    tags=["upload"]
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


async def process_receipt_task(file_path: str, file_name: str, user_id: int = 1):
    """
    Background task to process receipt with AI OCR and create transaction
    
    This runs asynchronously after the upload endpoint returns 200 OK
    """
    from services.ocr_service import ocr_service
    from database import SessionLocal
    
    db = SessionLocal()
    
    try:
        print(f"🔍 [Background] Processing receipt: {file_name}")
        
        # Process receipt with OCR + AI categorization
        if not ocr_service.enabled:
            print(f"⚠️  [Background] OCR service disabled, skipping processing")
            return
        
        result = await ocr_service.process_receipt(file_path)
        
        print(f"✅ [Background] OCR Result: {result.get('merchant')} - ${result.get('amount')} - {result.get('category')}")
        print(f"   Confidence: {result.get('confidence')}% | AI Category: {result.get('ai_category')} ({result.get('ai_confidence')}%)")
        
        # Determine if we should auto-create transaction
        confidence = result.get('confidence', 0)
        
        if confidence < 50:
            print(f"⚠️  [Background] Confidence too low ({confidence}%), skipping auto-creation")
            return
        
        # Create transaction in database
        transaction_status = TransactionStatus.PENDING  # Always pending for review
        
        # If confidence > 90%, we could auto-post, but for safety, always require review
        # transaction_status = TransactionStatus.POSTED if confidence > 90 else TransactionStatus.PENDING
        
        # Prepare notes with AI metadata
        ai_metadata = {
            "source": "receipt_upload",
            "file": file_name,
            "ocr_confidence": result.get('confidence'),
            "ocr_category": result.get('category'),
            "ai_category": result.get('ai_category'),
            "ai_confidence": result.get('ai_confidence'),
            "ai_reasoning": result.get('ai_reasoning'),
            "line_items": result.get('line_items', [])
        }
        
        notes = f"AI Extracted (OCR: {result.get('confidence')}%)\n"
        if result.get('ai_category'):
            notes += f"AI Category: {result.get('ai_category')} ({result.get('ai_confidence')}%)\n"
        if result.get('ai_reasoning'):
            notes += f"Reasoning: {result.get('ai_reasoning')}\n"
        notes += f"File: {file_name}\n"
        notes += f"Metadata: {json.dumps(ai_metadata, indent=2)}"
        
        # Parse date
        transaction_date = date.today()
        if result.get('date'):
            try:
                transaction_date = datetime.strptime(result['date'], '%Y-%m-%d').date()
            except:
                print(f"⚠️  [Background] Failed to parse date: {result.get('date')}, using today")
        
        # Use AI category if available and confident, otherwise use OCR category
        final_category = result.get('category', 'Uncategorized')
        if result.get('ai_category') and result.get('ai_confidence', 0) > 80:
            final_category = result.get('ai_category')
        
        # Create transaction
        new_transaction = Transaction(
            date=transaction_date,
            amount=-abs(result.get('amount', 0)),  # Negative for expense
            merchant=result.get('merchant', 'Unknown Merchant'),
            category=final_category,
            status=transaction_status,
            notes=notes
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        print(f"✅ [Background] Transaction created: ID={new_transaction.id}, Status={transaction_status.value}")
        
        # Optional: Send notification via Telegram
        try:
            from services.telegram_service import telegram_service
            if telegram_service.enabled:
                await telegram_service.send_message(
                    f"📄 New Receipt Processed\n\n"
                    f"Merchant: {result.get('merchant')}\n"
                    f"Amount: ${abs(result.get('amount', 0)):.2f}\n"
                    f"Category: {final_category}\n"
                    f"Confidence: {confidence}%\n"
                    f"Status: {transaction_status.value}"
                )
        except Exception as e:
            print(f"⚠️  [Background] Telegram notification failed: {e}")
        
    except Exception as e:
        print(f"❌ [Background] Receipt processing failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@router.post("/receipt")
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload receipt image and trigger async AI OCR processing
    
    Returns immediately with 200 OK while processing happens in background
    
    Returns:
    {
        "success": true,
        "filename": "20251229_235959_abc123.jpg",
        "path": "/uploads/20251229_235959_abc123.jpg",
        "url": "http://localhost:6501/uploads/20251229_235959_abc123.jpg",
        "message": "Receipt uploaded successfully. Processing in background..."
    }
    """
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.heic'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_name = f"{timestamp}_{unique_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Schedule background processing
    background_tasks.add_task(process_receipt_task, file_path, file_name)
    
    # Return immediately
    return {
        "success": True,
        "filename": file_name,
        "path": f"/uploads/{file_name}",
        "url": f"http://localhost:6501/uploads/{file_name}",
        "message": "Receipt uploaded successfully. AI processing in background..."
    }


@router.get("/health")
async def upload_health():
    """Check if upload directory is writable and OCR service is available"""
    from services.ocr_service import ocr_service
    
    return {
        "status": "healthy",
        "upload_dir": UPLOAD_DIR,
        "writable": os.access(UPLOAD_DIR, os.W_OK),
        "ocr_enabled": ocr_service.enabled,
        "ocr_model": "anthropic/claude-3.5-sonnet" if ocr_service.enabled else None
    }
