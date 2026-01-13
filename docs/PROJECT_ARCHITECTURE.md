# Family CFO - Project Architecture

> **Version**: 2.0
> **Last Updated**: 2026-01-01
> **Tech Stack**: React + TypeScript + FastAPI + PostgreSQL

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Data Flow](#data-flow)
6. [API Design](#api-design)
7. [Authentication & Security](#authentication--security)

---

## System Overview

**Family CFO** 是一个全栈家庭财务管理系统，采用前后端分离架构。

### Core Features
- 📊 **Dashboard**: CFO 级别的数据可视化大屏
- 💰 **Transaction Management**: 收入/支出/债务追踪
- 🏦 **Account Management**: 多账户管理（TFSA, RRSP, 投资账户等）
- 🛡️ **Insurance Tracking**: 保险保单管理
- 📱 **Mobile App**: 移动端 OCR 小票扫描
- 🤖 **AI Categorization**: 自动分类交易
- 📧 **Email Integration**: 邮件解析交易信息
- 📈 **Reports & Analytics**: 财务报表和趋势分析

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │   Admin Panel    │              │   Mobile App     │         │
│  │   (Port 6502)    │              │   (Port 6503)    │         │
│  │                  │              │                  │         │
│  │  - Dashboard     │              │  - OCR Upload    │         │
│  │  - Reports       │              │  - Quick Entry   │         │
│  │  - Settings      │              │  - Wallet View   │         │
│  └────────┬─────────┘              └────────┬─────────┘         │
│           │                                 │                   │
└───────────┼─────────────────────────────────┼───────────────────┘
            │                                 │
            │        HTTPS (REST API)         │
            └─────────────┬───────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Layer                               │
│                      (Port 6501)                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Server                         │  │
│  │                                                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │   Auth      │  │Transactions │  │  Dashboard  │      │  │
│  │  │   Router    │  │   Router    │  │   Router    │      │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │  │
│  │         │                │                │              │  │
│  │         └────────────────┼────────────────┘              │  │
│  │                          ▼                                │  │
│  │              ┌──────────────────────┐                    │  │
│  │              │   Business Logic     │                    │  │
│  │              │   - Services         │                    │  │
│  │              │   - Validators       │                    │  │
│  │              └──────────┬───────────┘                    │  │
│  │                         │                                │  │
│  └─────────────────────────┼────────────────────────────────┘  │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SQLAlchemy ORM                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database Layer                               │
│                     (Port 6500)                                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                PostgreSQL 15                              │  │
│  │                                                            │  │
│  │  Tables:                                                  │  │
│  │  - users                                                  │  │
│  │  - transactions                                           │  │
│  │  - accounts                                               │  │
│  │  - insurances                                             │  │
│  │  - subscriptions                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

External Services:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   OpenRouter │    │   Telegram   │    │    Email     │
│   (AI API)   │    │  (Notify)    │    │  (SMTP/POP3) │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Technology Stack

### Frontend

#### Admin Panel (Port 6502)
```
React 18 + TypeScript
├── Vite - Build tool
├── TailwindCSS - Styling
├── Framer Motion - Animations
├── Recharts - Data visualization
├── Lucide React - Icons
├── Axios - HTTP client
└── date-fns - Date utilities
```

#### Mobile App (Port 6503)
```
React 18 + TypeScript
├── Vite - Build tool
├── TailwindCSS - Styling
├── Framer Motion - Animations
├── Axios - HTTP client
└── Camera API - OCR upload
```

### Backend (Port 6501)
```
Python 3.11
├── FastAPI - Web framework
├── SQLAlchemy - ORM
├── Alembic - Database migrations
├── Pydantic - Data validation
├── python-jose - JWT authentication
├── passlib[bcrypt] - Password hashing
├── httpx - Async HTTP client
├── APScheduler - Task scheduling
└── OpenAI SDK - AI integration
```

### Database (Port 6500)
```
PostgreSQL 15-alpine
└── psycopg2-binary - Python adapter
```

### DevOps
```
Docker & Docker Compose
├── 4 containers (db, backend, admin, frontend)
├── Health checks
└── Volume persistence
```

---

## Project Structure

```
familyltdcfo/
│
├── backend/                    # FastAPI backend
│   ├── main.py                 # Application entry point
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/                # API routes
│   │   ├── auth.py             # Authentication
│   │   ├── transactions.py     # Transaction CRUD
│   │   ├── dashboard.py        # Dashboard data
│   │   ├── monitoring.py       # System monitoring
│   │   └── upload.py           # File upload (OCR)
│   ├── services/               # Business logic
│   │   ├── categorization_service.py
│   │   ├── email_service.py
│   │   └── telegram_service.py
│   ├── alembic/                # Database migrations
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container
│
├── admin/                      # Admin web app
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # Root component
│   │   ├── views/              # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── TransactionReview.tsx
│   │   │   ├── BenefitsLocker.tsx
│   │   │   └── BudgetManager.tsx
│   │   ├── components/         # Reusable components
│   │   │   ├── ui/
│   │   │   ├── MonthPicker.tsx
│   │   │   └── SystemMonitor.tsx
│   │   ├── context/            # React context
│   │   │   └── ViewNavigationContext.tsx
│   │   ├── services/           # API clients
│   │   │   └── api.ts
│   │   └── styles/             # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf              # Nginx configuration
│   └── Dockerfile
│
├── frontend/                   # Mobile app
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   └── MonthPicker.tsx
│   │   └── services/
│   │       └── api.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf
│   └── Dockerfile
│
├── docs/                       # Documentation
│   ├── DATABASE_SCHEMA.md
│   ├── PROJECT_ARCHITECTURE.md
│   └── API_DOCUMENTATION.md
│
├── scripts/                    # Utility scripts
│   ├── seed_mock_data.py       # Generate test data
│   └── clear_data.py           # Clear database
│
├── docker-compose.yml          # Container orchestration
├── .env                        # Environment variables
└── README.md                   # Project readme
```

---

## Data Flow

### 1. User Authentication Flow
```
User Login Request
    │
    ▼
Frontend (POST /api/auth/token)
    │
    ▼
Backend Auth Router
    │
    ├─ Validate credentials
    ├─ Hash password check
    └─ Generate JWT token
    │
    ▼
Return token to frontend
    │
    ▼
Store in localStorage
    │
    ▼
Include in Authorization header for subsequent requests
```

### 2. Transaction Creation Flow (Mobile OCR)
```
User uploads receipt photo
    │
    ▼
Frontend (POST /api/upload/receipt)
    │
    ▼
Backend Upload Router
    │
    ├─ Validate file
    ├─ Call AI service (OCR/categorization)
    ├─ Parse merchant, amount, date
    └─ Create transaction in DB
    │
    ▼
Trigger notifications (Telegram)
    │
    ▼
Return transaction data
    │
    ▼
Refresh transaction list
```

### 3. Dashboard Data Flow
```
User opens Dashboard
    │
    ▼
Frontend requests:
    ├─ GET /api/dashboard/stats
    ├─ GET /api/transactions/?month=2025-12
    ├─ GET /api/accounts/
    └─ GET /api/monitoring/system-status
    │
    ▼
Backend aggregates data from:
    ├─ transactions table
    ├─ accounts table
    ├─ insurances table
    └─ subscriptions table
    │
    ▼
Calculate:
    ├─ Net worth
    ├─ Monthly cash flow
    ├─ Budget vs actual
    └─ Asset allocation
    │
    ▼
Return JSON response
    │
    ▼
Frontend renders charts and cards
```

---

## API Design

### RESTful Principles
- **Resource-based URLs**: `/api/transactions/`, `/api/accounts/`
- **HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Status Codes**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found)
- **JSON Format**: All requests and responses use JSON

### API Versioning
- Current version: **v1** (implicit in `/api/` prefix)
- Future versions will use `/api/v2/` prefix

### Pagination
```
GET /api/transactions/?skip=0&limit=100&month=2025-12
```

### Filtering
```
GET /api/transactions/?status=Pending&category=Groceries
```

### Error Handling
```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-01T12:00:00Z"
}
```

---

## Authentication & Security

### JWT Token-based Authentication
1. User logs in with username/password
2. Backend validates and returns JWT token
3. Frontend stores token in localStorage
4. Token included in `Authorization: Bearer <token>` header
5. Backend validates token on each request

### Token Structure
```json
{
  "sub": "username",
  "exp": 1767300000,
  "role": "admin"
}
```

### Security Best Practices
- ✅ Passwords hashed with bcrypt
- ✅ HTTPS in production (Nginx)
- ✅ CORS configured for specific origins
- ✅ SQL injection protection (ORM)
- ✅ XSS protection (Content-Security-Policy)
- ✅ Rate limiting (TODO: implement)
- ✅ Environment variables for secrets

---

## Deployment Architecture

### Docker Containers
```
docker-compose.yml defines 4 services:

1. database (postgres:15-alpine)
   - Port: 6500
   - Volume: postgres_data

2. backend (familyltdcfo-backend)
   - Port: 6501
   - Depends on: database
   - Health check: /api/health

3. admin (familyltdcfo-admin)
   - Port: 6502
   - Nginx serves static files
   - Health check: HTTP 200

4. frontend (familyltdcfo-frontend)
   - Port: 6503
   - Nginx serves static files
   - Health check: HTTP 200
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/familycfo

# JWT
SECRET_KEY=<random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service
OPENROUTER_API_KEY=<your-api-key>

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-email>
SMTP_PASSWORD=<app-password>

# Telegram
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<chat-id>
```

---

## Performance Considerations

### Database Optimization
- **Indexes** on frequently queried fields (date, category, status)
- **Connection pooling** via SQLAlchemy
- **Query optimization** using ORM eager loading

### Frontend Optimization
- **Code splitting** with Vite
- **Lazy loading** of routes
- **Image optimization** for receipts
- **Caching** API responses

### Backend Optimization
- **Async/await** for I/O operations
- **Background tasks** for email/notifications
- **Response compression** (gzip)

---

## Future Enhancements (Roadmap)

### v2.1
- [ ] Budget forecasting with ML
- [ ] Multi-currency support
- [ ] Export to Excel/PDF
- [ ] Mobile native apps (React Native)

### v2.2
- [ ] Real-time collaboration (WebSocket)
- [ ] Bank account integration (Plaid API)
- [ ] Investment portfolio tracking
- [ ] Tax report generation

### v3.0
- [ ] Multi-family support
- [ ] Financial advisor dashboard
- [ ] Custom reporting builder
- [ ] API marketplace for integrations

---

**End of Architecture Documentation**
