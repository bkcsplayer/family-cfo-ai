"""
Scheduler Service - Background tasks and scheduled jobs
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from sqlalchemy import text
import os

from services.telegram_service import telegram_service
from services.email_service import email_service
from database import SessionLocal

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def scheduled_health_check():
    """
    Periodic health check - runs every hour
    Checks database connectivity and sends status to Telegram
    """
    print(f"⏰ Running scheduled health check at {datetime.now()}")
    
    db = SessionLocal()
    db_healthy = True
    
    try:
        db.execute(text("SELECT 1"))
        db.commit()
    except Exception as e:
        db_healthy = False
        print(f"❌ Database health check failed: {str(e)}")
    finally:
        db.close()
    
    # Send to Telegram
    if telegram_service.enabled:
        await telegram_service.send_health_check(
            database_healthy=db_healthy,
            api_healthy=True,
            additional_info={
                "check_type": "scheduled",
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        )
    
    print(f"✅ Health check completed - DB: {'healthy' if db_healthy else 'unhealthy'}")


async def send_daily_summary():
    """
    Daily system summary - runs at 9:00 AM
    Sends comprehensive daily report to Telegram
    """
    print(f"📊 Sending daily summary at {datetime.now()}")
    
    db = SessionLocal()
    
    try:
        # Get transaction count for today
        from models import Transaction
        from datetime import date
        
        today = date.today()
        transaction_count = db.query(Transaction).filter(
            Transaction.date == today
        ).count()
        
        # Build summary
        summary = {
            "report_type": "Daily Summary",
            "date": today.strftime("%Y-%m-%d"),
            "transactions_today": transaction_count,
            "database": "✅ Connected",
            "api": "✅ Running"
        }
        
        if telegram_service.enabled:
            await telegram_service.send_system_status(
                summary,
                alert_level="info"
            )
        
        print(f"✅ Daily summary sent - {transaction_count} transactions today")
        
    except Exception as e:
        print(f"❌ Failed to send daily summary: {str(e)}")
        
        if telegram_service.enabled:
            await telegram_service.send_error_alert(
                error_type="DailySummaryError",
                error_message=str(e)
            )
    finally:
        db.close()


async def send_weekly_report():
    """
    Weekly financial report - runs every Sunday at 10:00 AM
    Sends comprehensive weekly report via Email
    """
    print(f"📧 Sending weekly report at {datetime.now()}")
    
    if not email_service.enabled:
        print("⚠️  Email service disabled, skipping weekly report")
        return
    
    db = SessionLocal()
    
    try:
        from models import Transaction
        from datetime import date, timedelta
        from sqlalchemy import func
        
        # Calculate week range
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)  # Sunday
        
        # Get transactions for the week
        transactions = db.query(Transaction).filter(
            Transaction.date >= week_start,
            Transaction.date <= week_end
        ).all()
        
        # Calculate totals
        total_expenses = sum(abs(tx.amount) for tx in transactions if tx.amount < 0)
        total_income = sum(tx.amount for tx in transactions if tx.amount > 0)
        net_savings = total_income - total_expenses
        
        # Get top categories
        category_totals = {}
        for tx in transactions:
            if tx.amount < 0 and tx.category:
                category_totals[tx.category] = category_totals.get(tx.category, 0) + abs(tx.amount)
        
        top_categories = [
            {"name": cat, "amount": amt}
            for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Get large expenses (over $100)
        large_expenses = [
            {"merchant": tx.merchant, "amount": tx.amount, "date": str(tx.date)}
            for tx in transactions if tx.amount < -100
        ]
        
        # Build report data
        report_data = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_expenses": total_expenses,
            "total_income": total_income,
            "net_savings": net_savings,
            "top_categories": top_categories,
            "large_expenses": large_expenses
        }
        
        # Send email
        admin_email = os.getenv("ADMIN_EMAILS", "admin@example.com").split(",")[0]
        success = email_service.send_weekly_report(admin_email, report_data)
        
        if success:
            print(f"✅ Weekly report sent to {admin_email}")
        else:
            print(f"❌ Failed to send weekly report")
        
    except Exception as e:
        print(f"❌ Failed to generate weekly report: {str(e)}")
    finally:
        db.close()


async def send_monthly_report():
    """
    Monthly financial report - runs on 1st of each month at 9:00 AM
    Sends comprehensive monthly report via Email
    """
    print(f"📧 Sending monthly report at {datetime.now()}")
    
    if not email_service.enabled:
        print("⚠️  Email service disabled, skipping monthly report")
        return
    
    db = SessionLocal()
    
    try:
        from models import Transaction
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Calculate month range (previous month)
        today = date.today()
        month_start = (today.replace(day=1) - relativedelta(months=1))
        month_end = today.replace(day=1) - timedelta(days=1)
        
        # Get transactions for the month
        transactions = db.query(Transaction).filter(
            Transaction.date >= month_start,
            Transaction.date <= month_end
        ).all()
        
        # Calculate totals
        total_expenses = sum(abs(tx.amount) for tx in transactions if tx.amount < 0)
        total_income = sum(tx.amount for tx in transactions if tx.amount > 0)
        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        
        # Get category breakdown
        category_totals = {}
        for tx in transactions:
            if tx.amount < 0 and tx.category:
                category_totals[tx.category] = category_totals.get(tx.category, 0) + abs(tx.amount)
        
        categories = [
            {"name": cat, "amount": amt}
            for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Build report data
        report_data = {
            "month": month_start.strftime("%B %Y"),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate": savings_rate,
            "categories": categories
        }
        
        # Send email
        admin_email = os.getenv("ADMIN_EMAILS", "admin@example.com").split(",")[0]
        success = email_service.send_monthly_report(admin_email, report_data)
        
        if success:
            print(f"✅ Monthly report sent to {admin_email}")
        else:
            print(f"❌ Failed to send monthly report")
        
    except Exception as e:
        print(f"❌ Failed to generate monthly report: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler with all scheduled jobs
    """
    # Job 1: Hourly health check
    scheduler.add_job(
        scheduled_health_check,
        trigger=IntervalTrigger(hours=1),
        id='hourly_health_check',
        name='Hourly Health Check',
        replace_existing=True
    )
    
    # Job 2: Daily summary at 9:00 AM
    daily_summary_time = os.getenv("DAILY_SUMMARY_TIME", "09:00")
    hour, minute = daily_summary_time.split(":")
    
    scheduler.add_job(
        send_daily_summary,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id='daily_summary',
        name='Daily Summary Report',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    print("✅ Scheduler started successfully")
    print(f"   - Hourly health checks enabled")
    print(f"   - Daily summary at {daily_summary_time}")
    
    # Job 3: Weekly report (Sunday at 10:00 AM)
    if os.getenv("EMAIL_NOTIFY_WEEKLY_SUMMARY", "false").lower() == "true":
        weekly_time = os.getenv("WEEKLY_REPORT_TIME", "10:00")
        weekly_day = int(os.getenv("WEEKLY_REPORT_DAY", "0"))  # 0 = Sunday
        hour, minute = weekly_time.split(":")
        
        scheduler.add_job(
            send_weekly_report,
            trigger=CronTrigger(day_of_week=weekly_day, hour=int(hour), minute=int(minute)),
            id='weekly_report',
            name='Weekly Email Report',
            replace_existing=True
        )
        print(f"   - Weekly email report enabled (Day {weekly_day} at {weekly_time})")
    
    # Job 3.5: IMAP Email Listener (every 5 minutes)
    if os.getenv("IMAP_LISTENER_ENABLED", "false").lower() == "true":
        check_interval = int(os.getenv("IMAP_CHECK_INTERVAL", "300"))  # 5 minutes default
        
        async def check_email_inbox():
            """Check email inbox for new receipts"""
            from services.email_listener_service import email_listener
            try:
                await email_listener.check_inbox_once()
            except Exception as e:
                print(f"❌ Email inbox check failed: {e}")
        
        scheduler.add_job(
            check_email_inbox,
            trigger=IntervalTrigger(seconds=check_interval),
            id='email_inbox_check',
            name='IMAP Email Listener',
            replace_existing=True
        )
        print(f"   - IMAP email listener enabled (every {check_interval}s)")
    
    # Job 4: Monthly report (1st of month at 9:00 AM)
    if os.getenv("EMAIL_NOTIFY_MONTHLY_REPORT", "false").lower() == "true":
        monthly_day = int(os.getenv("MONTHLY_REPORT_DAY", "1"))
        monthly_time = os.getenv("MONTHLY_REPORT_TIME", "09:00")
        hour, minute = monthly_time.split(":")
        
        scheduler.add_job(
            send_monthly_report,
            trigger=CronTrigger(day=monthly_day, hour=int(hour), minute=int(minute)),
            id='monthly_report',
            name='Monthly Email Report',
            replace_existing=True
        )
        print(f"   - Monthly email report enabled (Day {monthly_day} at {monthly_time})")


def stop_scheduler():
    """
    Stop the scheduler gracefully
    """
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")
