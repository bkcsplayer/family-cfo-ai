from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    prefix="/api/email",
    tags=["email"]
)


@router.post("/check-inbox")
async def trigger_inbox_check():
    """
    Manually trigger email inbox check
    
    Useful for testing or forcing an immediate check
    """
    from services.email_listener_service import email_listener
    
    if not email_listener.enabled:
        raise HTTPException(
            status_code=503,
            detail="IMAP listener is not enabled. Set IMAP_LISTENER_ENABLED=true in .env"
        )
    
    try:
        await email_listener.check_inbox_once()
        return {
            "success": True,
            "message": "Inbox check completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inbox check failed: {str(e)}"
        )


@router.get("/listener/status")
async def get_listener_status():
    """
    Get IMAP listener configuration and status
    """
    from services.email_listener_service import email_listener
    
    return {
        "enabled": email_listener.enabled,
        "imap_host": email_listener.imap_host if email_listener.enabled else None,
        "imap_username": email_listener.imap_username if email_listener.enabled else None,
        "check_interval": email_listener.check_interval,
        "inbox_folder": email_listener.inbox_folder,
        "allowed_extensions": list(email_listener.allowed_extensions),
        "sender_whitelist": email_listener.sender_whitelist if email_listener.sender_whitelist else "All senders allowed"
    }


@router.get("/listener/health")
async def check_listener_health():
    """
    Test IMAP connection
    """
    from services.email_listener_service import email_listener
    
    if not email_listener.enabled:
        return {
            "status": "disabled",
            "message": "IMAP listener is not enabled"
        }
    
    try:
        mail = email_listener.connect()
        mail.logout()
        
        return {
            "status": "healthy",
            "message": "IMAP connection successful",
            "server": email_listener.imap_host
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"IMAP connection failed: {str(e)}"
        )
