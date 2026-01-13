from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, get_db, Base
from dotenv import load_dotenv
import os

# Import routers
from routers import auth, dashboard, transactions, assets, ai, monitoring, categorization, insurance, upload, email_listener, budgets, export
# v3.0 routers
from routers import categories, assets_v3, gov_benefits, reviews, backup

# Import services
from services.telegram_service import telegram_service
from fastapi.staticfiles import StaticFiles
from services.scheduler_service import start_scheduler, stop_scheduler

load_dotenv()

# Create database tables (auto-migration)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Family Inc. CFO API",
    description="Backend API for Family CFO Dashboard - Canadian Financial Management",
    version="1.0.0"
)

# CORS Configuration - Allow React frontends
origins = [
    "http://localhost:6512",      # Admin Dashboard (v3.0)
    "http://localhost:6513",      # Mobile App (v3.0)
    "http://localhost:6502",      # Admin Dashboard (v2.0)
    "http://localhost:6503",      # Mobile App (v2.0)
    "http://localhost:3000",      # Admin Dashboard (OLD)
    "http://localhost:3001",      # Mobile App (Docker)
    "http://localhost:3006",      # Mobile App (Dev OLD)
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:6512",
    "http://127.0.0.1:6513",
    "http://127.0.0.1:6502",
    "http://127.0.0.1:6503",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:5173",
    # Allow all localhost for development
    "http://localhost",
    "http://127.0.0.1",
]

# Add environment-based origins
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    origins.extend(env_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(transactions.router)
app.include_router(assets.router)
app.include_router(ai.router)  # AI endpoints
app.include_router(insurance.router)
app.include_router(upload.router)

app.include_router(monitoring.router)  # Monitoring endpoints
app.include_router(categorization.router)  # Categorization endpoints
app.include_router(email_listener.router)  # Email listener endpoints
app.include_router(budgets.router)  # Budget management endpoints
app.include_router(export.router)  # Data export endpoints

# v3.0 routers
app.include_router(categories.router)  # Category management (v3.0)
app.include_router(assets_v3.router)  # Assets & Liabilities (v3.0)
app.include_router(gov_benefits.router)  # Government Benefits (v3.0)
app.include_router(reviews.router)  # Document scanning & review workflow (v3.0)
app.include_router(backup.router)  # Database backup & export (v3.0)

# Mount static files for uploaded receipts
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    """
    Root endpoint - API status
    """
    return {
        "status": "online",
        "message": "Family Inc. CFO Backend is Online",
        "data_source": "PostgreSQL",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/api/auth/token",
            "dashboard": "/api/dashboard/stats",
            "transactions": "/api/transactions",
            "assets": "/api/assets"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connectivity
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Legacy endpoint for backward compatibility
@app.get("/api/info")
def api_info():
    """
    API information endpoint - Available endpoints
    """
    return {
        "name": "Family Inc. CFO API",
        "version": "1.0.0",
        "description": "Canadian Financial Management System",
        "authentication": "JWT Bearer Token",
        "endpoints": {
            "auth": {
                "login": "POST /api/auth/token",
                "me": "GET /api/auth/me"
            },
            "dashboard": {
                "stats": "GET /api/dashboard/stats",
                "recent_activity": "GET /api/dashboard/recent-activity"
            },
            "transactions": {
                "list": "GET /api/transactions",
                "create": "POST /api/transactions",
                "approve": "PUT /api/transactions/{id}/approve"
            },
            "assets": {
                "list": "GET /api/assets",
                "accounts": "GET /api/accounts",
                "subscriptions": "GET /api/subscriptions"
            }
        },
        "database": {
            "type": "PostgreSQL",
            "port": "5433 (external), 5432 (internal)"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks
    - Send Telegram notification
    - Start background scheduler
    """
    print("🚀 Starting Family CFO Backend...")
    
    # Send startup notification
    if telegram_service.enabled:
        await telegram_service.send_startup_notification()
    
    # Start scheduler for periodic tasks
    if os.getenv("ENABLE_SCHEDULED_TASKS", "true").lower() == "true":
        start_scheduler()
    
    print("✅ Family CFO Backend started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks
    - Stop scheduler
    - Send shutdown notification (optional)
    """
    print("🛑 Shutting down Family CFO Backend...")
    
    # Stop scheduler
    stop_scheduler()
    
    print("✅ Family CFO Backend stopped")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Catch all unhandled exceptions and send alerts to Telegram
    """
    from fastapi.responses import JSONResponse
    
    # Log error
    print(f"❌ Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    # Send to Telegram if enabled
    if telegram_service.enabled:
        await telegram_service.send_error_alert(
            error_type=type(exc).__name__,
            error_message=str(exc),
            details={
                "path": str(request.url.path),
                "method": request.method
            }
        )
    
    # Return error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6501)
