# Configuration Guide for Family CFO

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual values**

3. **Restart the backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

---

## Required Configuration

### Minimum Setup (Development)

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/familycfo

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3006
```

---

## AI Integration Setup

### Option 1: OpenRouter (Recommended)

**Why OpenRouter?**
- Access to multiple AI models (Claude, GPT-4, etc.)
- Pay-as-you-go pricing
- No monthly subscription

**Setup:**
1. Go to https://openrouter.ai/keys
2. Create an API key
3. Add to `.env`:

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

**Available Models:**
- `anthropic/claude-3.5-sonnet` - Best for complex reasoning
- `openai/gpt-4-turbo` - Good all-rounder
- `google/gemini-pro` - Fast and cheap
- `meta-llama/llama-3.1-70b` - Open source option

### Option 2: OpenAI Direct

**Setup:**
1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Add to `.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## Telegram Bot Setup

**Use Case:** Get instant notifications for transactions, budget alerts, etc.

**Setup Steps:**

1. **Create a Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot`
   - Follow instructions to get your `BOT_TOKEN`

2. **Get Your User ID:**
   - Search for `@userinfobot` on Telegram
   - Send `/start` to get your user ID

3. **Configure:**
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_ADMIN_USER_ID=123456789
   TELEGRAM_NOTIFICATIONS_ENABLED=true
   ```

4. **Test:**
   ```bash
   # Send a test message
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
     -d "chat_id=<YOUR_USER_ID>" \
     -d "text=Hello from Family CFO!"
   ```

**Notification Types:**
- New transactions detected
- Large expenses (> threshold)
- Subscription renewals coming up
- Weekly/monthly summaries

---

## Email (SMTP) Setup

**Use Case:** Send weekly reports, monthly summaries, budget alerts

### Gmail Setup (Recommended for Development)

1. **Enable 2-Factor Authentication** on your Google account

2. **Create App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated password

3. **Configure:**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   EMAIL_FROM_ADDRESS=your-email@gmail.com
   ADMIN_EMAILS=admin@example.com,cfo@example.com
   ```

### Other SMTP Providers

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

**AWS SES:**
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

---

## File Storage Setup

### Local Storage (Default)

```env
STORAGE_PROVIDER=local
LOCAL_STORAGE_PATH=./uploads
```

### AWS S3

```env
STORAGE_PROVIDER=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=familycfo-uploads
AWS_S3_REGION=us-east-1
```

### Azure Blob Storage

```env
STORAGE_PROVIDER=azure
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=familycfo-uploads
```

---

## Security Best Practices

### Generate Strong Secret Key

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Production Settings

```env
# Security
SECRET_KEY=<generated-strong-key>
SESSION_COOKIE_SECURE=true
DEBUG=false

# CORS (only allow your actual domains)
CORS_ORIGINS=https://admin.yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

---

## Feature Flags

Enable/disable features without code changes:

```env
# AI Features
FEATURE_AI_CATEGORIZATION=true      # Auto-categorize transactions

# Notifications
FEATURE_TELEGRAM_BOT=true           # Telegram notifications
FEATURE_EMAIL_REPORTS=true          # Email reports

# Integrations
FEATURE_PLAID_INTEGRATION=false     # Bank account linking
FEATURE_OCR_RECEIPTS=false          # Receipt scanning
FEATURE_MULTI_CURRENCY=false        # Multi-currency support
```

---

## Scheduled Tasks

Configure automated reports and summaries:

```env
ENABLE_SCHEDULED_TASKS=true

# Daily summary at 9 AM
DAILY_SUMMARY_TIME=09:00

# Weekly report on Sunday at 10 AM
WEEKLY_REPORT_DAY=0
WEEKLY_REPORT_TIME=10:00

# Monthly report on 1st at 9 AM
MONTHLY_REPORT_DAY=1
MONTHLY_REPORT_TIME=09:00
```

---

## Monitoring & Logging

### Sentry (Error Tracking)

1. Create account at https://sentry.io
2. Create a new project
3. Copy DSN:

```env
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=production
```

### Logging Levels

```env
LOG_LEVEL=INFO    # DEBUG, INFO, WARNING, ERROR, CRITICAL
SQL_ECHO=false    # Set to true to see all SQL queries
```

---

## Testing Configuration

Create a separate `.env.test` for testing:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/familycfo_test
DEBUG=true
LOG_LEVEL=DEBUG
TELEGRAM_NOTIFICATIONS_ENABLED=false
EMAIL_NOTIFICATIONS_ENABLED=false
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec -it familyltdcfo-db-1 psql -U postgres -d familycfo

# Check if port is available
netstat -an | findstr 5433
```

### SMTP Issues

```bash
# Test SMTP connection (Python)
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
```

### Telegram Bot Issues

```bash
# Check bot info
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

---

## Environment-Specific Configs

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
HOT_RELOAD=true
```

### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
SESSION_COOKIE_SECURE=true
RATE_LIMIT_PER_MINUTE=30
```

---

## Next Steps

1. ✅ Copy `.env.example` to `.env`
2. ✅ Configure database connection
3. ✅ Generate and set SECRET_KEY
4. ✅ Choose AI provider (OpenRouter or OpenAI)
5. ⏭️ Optional: Set up Telegram bot
6. ⏭️ Optional: Configure SMTP for emails
7. ⏭️ Optional: Set up file storage (S3/Azure)
8. ⏭️ Optional: Configure monitoring (Sentry)

**Ready to start!** 🚀
