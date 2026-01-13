# Family CFO - Data Structure & Relationships

> **Version**: 2.0
> **Database**: PostgreSQL 15
> **ORM**: SQLAlchemy

---

## 📊 Complete Data Model Overview

This document provides a comprehensive view of all data structures, their relationships, and the business logic that connects them.

---

## 🗃️ Entity Relationship Diagram (ERD)

```
                          ┌─────────────────────────────────┐
                          │          USERS TABLE            │
                          │─────────────────────────────────│
                          │ PK: id                          │
                          │ UK: username                    │
                          │     email                       │
                          │     hashed_password             │
                          │     display_name                │
                          │     role (admin/user)           │
                          │     is_active                   │
                          │     created_at                  │
                          │     updated_at                  │
                          └───────────┬─────────────────────┘
                                      │
                                      │ (Future: FK to all tables)
                                      │ (Currently: No explicit FK)
                                      │
                ┌─────────────────────┼─────────────────────┬───────────────────┐
                │                     │                     │                   │
                ▼                     ▼                     ▼                   ▼
    ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐ ┌─────────────────┐
    │   TRANSACTIONS    │ │     ACCOUNTS      │ │    INSURANCES     │ │  SUBSCRIPTIONS  │
    │───────────────────│ │───────────────────│ │───────────────────│ │─────────────────│
    │ PK: id            │ │ PK: id            │ │ PK: id            │ │ PK: id          │
    │ merchant          │ │ type (ENUM)       │ │ provider          │ │ name            │
    │ amount (DECIMAL)  │ │ balance (DECIMAL) │ │ type (VARCHAR)    │ │ amount (DECIMAL)│
    │ date (DATE)       │ │ institution       │ │ policy_number     │ │ frequency       │
    │ category          │ │ account_number    │ │ coverage_amount   │ │ next_due (DATE) │
    │ type (ENUM)       │ │ interest_rate     │ │ premium (DECIMAL) │ │ status          │
    │   - expense       │ │ maturity_date     │ │ premium_frequency │ │ category        │
    │   - income        │ │ created_at        │ │ renewal_date      │ │ created_at      │
    │   - debt_payment  │ │ updated_at        │ │ beneficiary       │ │ updated_at      │
    │ status (ENUM)     │ └───────────────────┘ │ created_at        │ └─────────────────┘
    │   - Pending       │                       │ updated_at        │
    │   - Posted        │                       └───────────────────┘
    │   - Draft         │
    │ notes (TEXT)      │
    │ created_at        │
    │ updated_at        │
    └───────────────────┘

Legend:
─────────────────────
PK = Primary Key
UK = Unique Key
FK = Foreign Key
ENUM = Enumerated Type
DECIMAL = Decimal/Numeric
VARCHAR = Variable Character
TEXT = Long Text
DATE = Date Only
```

---

## 🔗 Table Relationships

### Current State (v2.0)
Currently, all tables are **independent** with no explicit foreign key relationships. This design provides:
- ✅ Flexibility in data management
- ✅ Simplified CRUD operations
- ✅ Easy data migration
- ⚠️ Less referential integrity enforcement

### Future Enhancement (v2.1+)
Planned foreign key relationships:

```sql
-- Future schema enhancements
ALTER TABLE transactions ADD COLUMN user_id INTEGER;
ALTER TABLE transactions ADD CONSTRAINT fk_transaction_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE accounts ADD COLUMN user_id INTEGER;
ALTER TABLE accounts ADD CONSTRAINT fk_account_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE insurances ADD COLUMN user_id INTEGER;
ALTER TABLE insurances ADD CONSTRAINT fk_insurance_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE subscriptions ADD COLUMN user_id INTEGER;
ALTER TABLE subscriptions ADD CONSTRAINT fk_subscription_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

---

## 📋 Detailed Table Structures

### 1. Users Table

**Purpose**: Stores user accounts for authentication and authorization

```python
# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    role = Column(String(50), default="user", nullable=False)  # 'admin' or 'user'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Key Concepts**:
- `hashed_password`: Bcrypt hashed, never store plaintext
- `role`: Role-based access control (RBAC)
- `is_active`: Soft delete mechanism

**Indexes**:
- Primary: `id`
- Unique: `username`, `email`
- Regular: `role`

---

### 2. Transactions Table

**Purpose**: Core financial transaction records

```python
# Transaction Types
class TransactionType(str, Enum):
    expense = "expense"
    income = "income"
    debt_payment = "debt_payment"

# Transaction Status
class TransactionStatus(str, Enum):
    pending = "Pending"    # Awaiting review
    posted = "Posted"      # Confirmed/processed
    draft = "Draft"        # Incomplete entry

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    merchant = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)  # Positive=income, Negative=expense
    date = Column(Date, default=date.today, nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    type = Column(Enum(TransactionType), default=TransactionType.expense, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Business Rules**:
- `amount > 0`: Income
- `amount < 0`: Expense or debt payment
- `amount == 0`: Invalid (database constraint)

**Indexes**:
- Primary: `id`
- Regular: `date`, `category`, `status`, `type`

**Common Categories**:
```
Expenses:
- Groceries, Dining, Transportation
- Utilities, Shopping, Healthcare
- Entertainment, Insurance

Income:
- Salary, Freelance, Investment
- Rental, Side Business

Debt Payment:
- Credit Card, Mortgage, Loan
```

---

### 3. Accounts Table

**Purpose**: Financial account tracking (bank accounts, investments)

```python
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    balance = Column(Numeric(15, 2), default=0.0, nullable=False)
    institution = Column(String(100), nullable=True, index=True)
    account_number = Column(String(100), nullable=True)  # Should be encrypted
    interest_rate = Column(Numeric(5, 2), nullable=True)
    maturity_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Account Types**:
```
Canadian Registered:
- TFSA (Tax-Free Savings Account)
- RRSP (Registered Retirement Savings Plan)
- FHSA (First Home Savings Account)
- RESP (Registered Education Savings Plan)

Standard Accounts:
- Checking
- Savings
- Investment
- GIC (Guaranteed Investment Certificate)
```

**Security Note**: `account_number` should be encrypted at rest in production.

---

### 4. Insurances Table

**Purpose**: Insurance policy management

```python
class Insurance(Base):
    __tablename__ = "insurances"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    policy_number = Column(String(100), nullable=True)
    coverage_amount = Column(Numeric(15, 2), nullable=True)
    premium = Column(Numeric(10, 2), nullable=True)
    premium_frequency = Column(String(20), nullable=True)  # 'monthly', 'yearly'
    renewal_date = Column(Date, nullable=True, index=True)
    beneficiary = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Insurance Types**:
- Life Insurance
- Health Insurance
- Home Insurance
- Auto Insurance
- Disability Insurance
- Travel Insurance

**Premium Frequencies**:
- `monthly`: Monthly payments
- `quarterly`: Every 3 months
- `semi-annually`: Every 6 months
- `yearly`: Annual payment

---

### 5. Subscriptions Table

**Purpose**: Recurring subscription service tracking

```python
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    frequency = Column(String(20), default="monthly", nullable=False)
    next_due = Column(Date, nullable=True, index=True)
    status = Column(String(20), default="active", nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Status Values**:
- `active`: Currently subscribed
- `cancelled`: Subscription ended
- `paused`: Temporarily suspended

**Common Categories**:
- Entertainment (Netflix, Spotify)
- Software (Adobe, Microsoft 365)
- News & Media (NYT, WSJ)
- Health & Fitness (Gym, Meal Kit)

---

## 🔄 Data Flow & Interactions

### Transaction Lifecycle

```
1. Creation
   ├─ Manual entry (Admin/Mobile)
   ├─ OCR upload (Mobile app)
   └─ Email parsing (Backend service)
          ↓
2. Draft State
   └─ status = "Draft"
          ↓
3. AI Categorization
   ├─ Merchant → Category mapping
   └─ Confidence score calculation
          ↓
4. Pending Review
   └─ status = "Pending"
          ↓
5. Admin Review
   ├─ Approve → status = "Posted"
   └─ Edit → update fields
          ↓
6. Posted
   └─ Appears in reports and calculations
```

### Account Balance Updates

```
Transaction Created (amount = -$50, category="Groceries")
          ↓
(Optional) Link to Account
          ↓
Update Account Balance
   balance_before = $1000
   balance_after = $1000 - $50 = $950
          ↓
Trigger Notifications
   ├─ Telegram: "New transaction: $50 at Walmart"
   └─ Email: Daily digest
```

### Dashboard Data Aggregation

```
GET /api/dashboard/stats
          ↓
Query Multiple Tables:
   ├─ SUM(transactions.amount WHERE type='income')
   ├─ SUM(transactions.amount WHERE type='expense')
   ├─ SUM(accounts.balance)
   ├─ SUM(insurances.coverage_amount)
   └─ COUNT(subscriptions WHERE status='active')
          ↓
Calculate Derived Metrics:
   ├─ Net Worth = Total Assets - Total Debt
   ├─ Monthly Cash Flow = Income - Expenses
   ├─ Savings Rate = (Income - Expenses) / Income
   └─ Asset Allocation = Group by account type
          ↓
Return JSON Response
```

---

## 📐 Derived Calculations

### Financial Metrics

```python
# Net Worth
net_worth = sum(account.balance for account in accounts) - total_debt

# Monthly Cash Flow
monthly_income = sum(tx.amount for tx in transactions if tx.type == 'income' and tx.date.month == current_month)
monthly_expenses = abs(sum(tx.amount for tx in transactions if tx.type == 'expense' and tx.date.month == current_month))
cash_flow = monthly_income - monthly_expenses

# Savings Rate
savings_rate = (monthly_income - monthly_expenses) / monthly_income * 100 if monthly_income > 0 else 0

# Total Insurance Coverage
total_coverage = sum(insurance.coverage_amount for insurance in insurances if insurance.coverage_amount)

# Monthly Subscription Cost
monthly_subscriptions = sum(sub.amount for sub in subscriptions if sub.frequency == 'monthly' and sub.status == 'active')
yearly_subscriptions = sum(sub.amount / 12 for sub in subscriptions if sub.frequency == 'yearly' and sub.status == 'active')
total_monthly_subs = monthly_subscriptions + yearly_subscriptions
```

---

## 🔍 Common Queries

### Get transactions for a specific month
```sql
SELECT * FROM transactions
WHERE date >= '2025-12-01'
  AND date < '2026-01-01'
ORDER BY date DESC;
```

### Calculate net worth
```sql
SELECT SUM(balance) as total_assets
FROM accounts;

-- Then subtract debts from transactions or separate debt table
```

### Find expiring insurance policies
```sql
SELECT * FROM insurances
WHERE renewal_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY renewal_date ASC;
```

### Get upcoming subscription payments
```sql
SELECT * FROM subscriptions
WHERE status = 'active'
  AND next_due BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY next_due ASC;
```

---

## 🎯 Data Integrity Rules

1. **Transactions**:
   - Amount cannot be zero
   - Date cannot be in the future (optional constraint)
   - Category should match predefined list (soft constraint)

2. **Accounts**:
   - Balance cannot be negative (for most account types)
   - Interest rate must be between 0 and 100%

3. **Insurances**:
   - Renewal date should be in the future
   - Premium must be positive

4. **Subscriptions**:
   - Amount must be positive
   - Frequency must be valid (monthly/yearly)

---

## 🚀 Performance Optimization

### Index Strategy
```sql
-- High-frequency queries
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Join optimization (future)
CREATE INDEX idx_transactions_user_id ON transactions(user_id);

-- Search optimization
CREATE INDEX idx_transactions_merchant ON transactions(merchant);
```

### Query Optimization Tips
- Use `LIMIT` for pagination
- Filter by date range to reduce dataset
- Use `SELECT` specific columns instead of `*`
- Leverage database views for complex aggregations

---

## 📊 Sample Data Snapshot

### Example Transaction
```json
{
  "id": 1,
  "merchant": "Superstore",
  "amount": -127.45,
  "date": "2025-12-15",
  "category": "Groceries",
  "type": "expense",
  "status": "Posted",
  "notes": "Weekly grocery shopping",
  "created_at": "2025-12-15T10:30:00Z",
  "updated_at": "2025-12-15T10:30:00Z"
}
```

### Example Account
```json
{
  "id": 1,
  "type": "TFSA",
  "balance": 45000.00,
  "institution": "TD Bank",
  "account_number": "****1234",
  "interest_rate": 3.5,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2025-12-15T00:00:00Z"
}
```

---

**End of Data Relationships Documentation**
