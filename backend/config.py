"""
Configuration management for Family CFO application.
Loads environment variables and provides typed configuration objects.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(default="postgresql://postgres:postgres@localhost:5433/familycfo", env="DATABASE_URL")
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5433, env="DB_PORT")
    name: str = Field(default="familycfo", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    echo: bool = Field(default=False, env="SQL_ECHO")

    class Config:
        env_file = ".env"


class JWTConfig(BaseSettings):
    """JWT authentication configuration"""
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"


class AIConfig(BaseSettings):
    """AI/LLM configuration"""
    provider: str = Field(default="openrouter", env="AI_PROVIDER")  # openai, openrouter
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # OpenRouter
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(default="anthropic/claude-3.5-sonnet", env="OPENROUTER_MODEL")
    openrouter_site_url: str = Field(default="http://localhost:3000", env="OPENROUTER_SITE_URL")
    openrouter_site_name: str = Field(default="Family CFO", env="OPENROUTER_SITE_NAME")

    class Config:
        env_file = ".env"


class TelegramConfig(BaseSettings):
    """Telegram bot configuration"""
    bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    admin_user_id: Optional[int] = Field(default=None, env="TELEGRAM_ADMIN_USER_ID")
    webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    
    # Notification settings
    notifications_enabled: bool = Field(default=True, env="TELEGRAM_NOTIFICATIONS_ENABLED")
    notify_new_transactions: bool = Field(default=True, env="TELEGRAM_NOTIFY_NEW_TRANSACTIONS")
    notify_large_expenses: bool = Field(default=True, env="TELEGRAM_NOTIFY_LARGE_EXPENSES")
    large_expense_threshold: float = Field(default=500.0, env="TELEGRAM_LARGE_EXPENSE_THRESHOLD")
    notify_subscription_renewals: bool = Field(default=True, env="TELEGRAM_NOTIFY_SUBSCRIPTION_RENEWALS")
    renewal_notice_days: int = Field(default=7, env="TELEGRAM_RENEWAL_NOTICE_DAYS")

    class Config:
        env_file = ".env"


class EmailConfig(BaseSettings):
    """Email/SMTP configuration"""
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_use_ssl: bool = Field(default=False, env="SMTP_USE_SSL")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    from_address: str = Field(default="noreply@familycfo.com", env="EMAIL_FROM_ADDRESS")
    from_name: str = Field(default="Family CFO", env="EMAIL_FROM_NAME")
    
    # Notification settings
    notifications_enabled: bool = Field(default=True, env="EMAIL_NOTIFICATIONS_ENABLED")
    notify_weekly_summary: bool = Field(default=True, env="EMAIL_NOTIFY_WEEKLY_SUMMARY")
    notify_monthly_report: bool = Field(default=True, env="EMAIL_NOTIFY_MONTHLY_REPORT")
    notify_budget_alerts: bool = Field(default=True, env="EMAIL_NOTIFY_BUDGET_ALERTS")
    
    admin_emails: str = Field(default="admin@example.com", env="ADMIN_EMAILS")

    @property
    def admin_email_list(self) -> list[str]:
        """Parse comma-separated admin emails"""
        return [email.strip() for email in self.admin_emails.split(",")]

    class Config:
        env_file = ".env"


class StorageConfig(BaseSettings):
    """File storage configuration"""
    provider: str = Field(default="local", env="STORAGE_PROVIDER")  # local, s3, azure
    local_path: str = Field(default="./uploads", env="LOCAL_STORAGE_PATH")
    
    # AWS S3
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    aws_s3_region: str = Field(default="us-east-1", env="AWS_S3_REGION")
    
    # Azure
    azure_connection_string: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONNECTION_STRING")
    azure_container: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONTAINER")

    class Config:
        env_file = ".env"


class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling features"""
    ai_categorization: bool = Field(default=True, env="FEATURE_AI_CATEGORIZATION")
    telegram_bot: bool = Field(default=True, env="FEATURE_TELEGRAM_BOT")
    email_reports: bool = Field(default=True, env="FEATURE_EMAIL_REPORTS")
    plaid_integration: bool = Field(default=False, env="FEATURE_PLAID_INTEGRATION")
    ocr_receipts: bool = Field(default=False, env="FEATURE_OCR_RECEIPTS")
    multi_currency: bool = Field(default=False, env="FEATURE_MULTI_CURRENCY")

    class Config:
        env_file = ".env"


class AppConfig(BaseSettings):
    """Main application configuration"""
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    
    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:3006", env="CORS_ORIGINS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Documentation
    enable_docs: bool = Field(default=True, env="ENABLE_DOCS")
    enable_redoc: bool = Field(default=True, env="ENABLE_REDOC")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


class Settings:
    """Global settings object"""
    def __init__(self):
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.jwt = JWTConfig()
        self.ai = AIConfig()
        self.telegram = TelegramConfig()
        self.email = EmailConfig()
        self.storage = StorageConfig()
        self.features = FeatureFlags()


# Global settings instance
settings = Settings()
