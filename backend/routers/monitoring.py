"""
Monitoring Router - System health checks and status monitoring
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import os

from database import get_db
from routers.auth import get_current_user
from services.telegram_service import telegram_service
import models

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

# AI Token usage tracking (in-memory for now)
ai_token_stats = {
    "total_requests": 0,
    "total_tokens_used": 0,
    "requests_today": 0,
    "tokens_today": 0,
    "last_reset": datetime.now().date()
}


@router.get("/health")
async def health_check_with_notification(db: Session = Depends(get_db)):
    """
    Comprehensive health check with optional Telegram notification
    
    Checks:
    - Database connectivity
    - API responsiveness
    - Environment configuration
    
    Returns health status and optionally sends to Telegram
    """
    # Check database
    db_healthy = True
    db_error = None
    try:
        db.execute(text("SELECT 1"))
        db.commit()
    except Exception as e:
        db_healthy = False
        db_error = str(e)
    
    # Overall health
    api_healthy = True  # If we got here, API is responding
    overall_healthy = db_healthy and api_healthy
    
    # Build response
    health_status = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": {
                "status": "connected" if db_healthy else "disconnected",
                "error": db_error
            },
            "api": {
                "status": "running"
            }
        },
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }
    
    # Send to Telegram if enabled
    if telegram_service.enabled:
        await telegram_service.send_health_check(
            database_healthy=db_healthy,
            api_healthy=api_healthy,
            additional_info={
                "environment": health_status["environment"],
                "version": health_status["version"]
            }
        )
    
    return health_status


@router.post("/test-telegram")
async def test_telegram_notification(current_user = Depends(get_current_user)):
    """
    Test Telegram notification system
    
    Requires authentication. Sends a test message to verify Telegram integration.
    """
    if not telegram_service.enabled:
        return {
            "success": False,
            "message": "Telegram service is not enabled. Check TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_USER_ID in .env"
        }
    
    message = f"""
🧪 <b>测试消息</b>

这是一条来自 Family CFO 的测试消息！

<b>发送时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>发送用户:</b> {current_user.username}
<b>环境:</b> {os.getenv('ENVIRONMENT', 'development')}

✅ Telegram 集成工作正常！
"""
    
    result = await telegram_service.send_message(message.strip())
    
    return {
        "success": result,
        "message": "Test message sent successfully" if result else "Failed to send test message",
        "telegram_enabled": telegram_service.enabled,
        "admin_user_id": telegram_service.admin_user_id
    }


@router.post("/send-status")
async def send_system_status(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Manually trigger system status report to Telegram
    
    Requires authentication. Sends comprehensive system status.
    """
    if not telegram_service.enabled:
        return {"success": False, "message": "Telegram service not enabled"}
    
    # Gather system stats
    db_healthy = True
    try:
        db.execute(text("SELECT 1"))
    except:
        db_healthy = False
    
    status = {
        "database": "✅ Connected" if db_healthy else "❌ Disconnected",
        "api": "✅ Running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_by": current_user.username
    }
    
    result = await telegram_service.send_system_status(
        status,
        alert_level="success" if db_healthy else "warning"
    )
    
    return {
        "success": result,
        "message": "Status report sent" if result else "Failed to send status"
    }


@router.get("/system-status")
async def get_system_status(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get comprehensive system status including:
    - Database health
    - Email service status
    - AI service status
    - AI Token usage
    - Transaction sources breakdown
    - Processing queue status
    """
    # Reset daily stats if new day
    today = datetime.now().date()
    if ai_token_stats["last_reset"] != today:
        ai_token_stats["requests_today"] = 0
        ai_token_stats["tokens_today"] = 0
        ai_token_stats["last_reset"] = today

    # Database check
    db_healthy = True
    try:
        db.execute(text("SELECT 1"))
        db.commit()
    except:
        db_healthy = False

    # Email service check
    email_enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
    imap_enabled = os.getenv("IMAP_LISTENER_ENABLED", "false").lower() == "true"
    email_configured = bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USERNAME"))

    # AI service check
    ai_enabled = bool(os.getenv("OPENROUTER_API_KEY"))
    ai_provider = os.getenv("AI_PROVIDER", "openrouter")
    ai_model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

    # Transaction sources (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    try:
        total_transactions = db.query(models.Transaction).filter(
            models.Transaction.created_at >= yesterday
        ).count()

        # Count by source (we'll add a source field later, for now estimate)
        # Transactions with notes containing "OCR" are from mobile
        mobile_transactions = db.query(models.Transaction).filter(
            models.Transaction.created_at >= yesterday,
            models.Transaction.notes.like('%OCR%')
        ).count()

        # Email transactions would have specific markers
        email_transactions = 0  # Placeholder

        manual_transactions = total_transactions - mobile_transactions - email_transactions
    except:
        total_transactions = 0
        mobile_transactions = 0
        email_transactions = 0
        manual_transactions = 0

    # Processing queue
    try:
        pending_count = db.query(models.Transaction).filter(
            models.Transaction.status == "Pending"
        ).count()

        draft_count = db.query(models.Transaction).filter(
            models.Transaction.status == "draft"
        ).count()
    except:
        pending_count = 0
        draft_count = 0

    return {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": {
                "status": "online" if db_healthy else "offline",
                "healthy": db_healthy
            },
            "email": {
                "status": "online" if (email_enabled and email_configured) else "offline",
                "enabled": email_enabled,
                "configured": email_configured,
                "imap_listener": imap_enabled
            },
            "ai": {
                "status": "online" if ai_enabled else "offline",
                "enabled": ai_enabled,
                "provider": ai_provider,
                "model": ai_model
            }
        },
        "ai_usage": {
            "total_requests": ai_token_stats["total_requests"],
            "total_tokens": ai_token_stats["total_tokens_used"],
            "today_requests": ai_token_stats["requests_today"],
            "today_tokens": ai_token_stats["tokens_today"]
        },
        "transaction_sources_24h": {
            "total": total_transactions,
            "mobile": mobile_transactions,
            "email": email_transactions,
            "manual": manual_transactions
        },
        "processing_queue": {
            "pending": pending_count,
            "draft": draft_count,
            "total_waiting": pending_count + draft_count
        }
    }


def track_ai_usage(tokens_used: int):
    """
    Helper function to track AI token usage
    Call this from AI service after each request
    """
    ai_token_stats["total_requests"] += 1
    ai_token_stats["total_tokens_used"] += tokens_used
    ai_token_stats["requests_today"] += 1
    ai_token_stats["tokens_today"] += tokens_used
