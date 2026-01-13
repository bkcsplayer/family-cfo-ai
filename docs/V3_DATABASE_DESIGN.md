# Family CFO v3.0 - Enhanced Database Design

> **Version**: 3.0
> **Date**: 2026-01-01
> **Major Changes**: Categories, Assets, Liabilities, AI Document Parsing, Foreign Keys

---

## 🎯 V3.0 Design Goals

1. **Comprehensive Financial Tracking**
   - Assets (房产、股票、加密货币、TFSA/RRSP等)
   - Liabilities (房贷、车贷、信用卡、学生贷款等)
   - Net Worth Calculation (资产 - 负债)

2. **Flexible Categorization**
   - User-defined categories with hierarchical structure
   - Support for Income, Expense, Asset, Liability types
   - Canadian-specific categories (TFSA, RRSP, FHSA, etc.)

3. **AI-Powered Data Entry**
   - Document upload and parsing
   - Insurance claim extraction
   - Receipt OCR enhancement
   - Confidence scoring

4. **Data Integrity**
   - Foreign key relationships
   - Referential integrity
   - User data isolation
   - Audit trails

---

## 📊 Complete Entity Relationship Diagram (V3.0)

```
                    ┌──────────────────────────────────┐
                    │           USERS TABLE            │
                    │──────────────────────────────────│
                    │ PK: id                           │
                    │ UK: username, email              │
                    │     hashed_password              │
                    │     role (admin/user)            │
                    └────────────┬─────────────────────┘
                                 │ (1:N)
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │    CATEGORIES     │     │    DOCUMENTS      │
        │───────────────────│     │───────────────────│
        │ PK: id            │     │ PK: id            │
        │ type (ENUM)       │     │ file_name         │
        │ parent_id (FK)◄───┼─┐   │ parsed_data(JSON) │
        │ user_id (FK)      │ │   │ linked_entity     │
        └─────┬─────────────┘ │   │ linked_id         │
              │ (1:N)         │   │ user_id (FK)      │
              │               │   └───────────────────┘
    ┌─────────┼───────────────┴───────────┬─────────────────┐
    │         │                           │                 │
    ▼         ▼                           ▼                 ▼
┌─────────┬──────────┐        ┌──────────────────┐  ┌──────────────┐
│TRANSACT.│ ACCOUNTS │        │     ASSETS       │  │ LIABILITIES  │
│─────────│──────────│        │──────────────────│  │──────────────│
│ id (PK) │ id (PK)  │        │ id (PK)          │  │ id (PK)      │
│ cat.(FK)│ cat.(FK) │        │ category_id (FK) │  │ cat_id (FK)  │
│ acc.(FK)│ user(FK) │        │ current_value    │  │ balance      │
│ user(FK)│ type     │        │ refresh_source   │  │ interest_rate│
│ source  │ balance  │        │ user_id (FK)     │  │ user_id (FK) │
└─────────┴──────────┘        └──────────────────┘  └──────────────┘
     │
     ▼
┌──────────────┐              ┌──────────────────┐
│ INSURANCES   │              │  SUBSCRIPTIONS   │
│──────────────│              │──────────────────│
│ id (PK)      │              │ id (PK)          │
│ category(FK) │              │ category_id (FK) │
│ reimb.(JSON) │              │ user_id (FK)     │
│ user_id (FK) │              │ status           │
└──────────────┘              └──────────────────┘

Legend:
─────────
PK = Primary Key
FK = Foreign Key
(1:N) = One to Many
(JSON) = JSONB Field
```

---

## 🆕 New Tables

### 1. Categories Table (自定义分类)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense', 'asset', 'liability')),
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- NULL = system-wide
    icon VARCHAR(50),  -- For UI (e.g., 'home', 'car', 'food')
    color VARCHAR(20),  -- For charts (#FF5733)
    is_system BOOLEAN DEFAULT FALSE,  -- Cannot be deleted by user
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
```

**Key Features**:
- **Hierarchical Structure**: `parent_id` allows nesting (e.g., "日常消费" > "超市购物")
- **User-Specific**: Each family can customize their categories
- **System Categories**: Pre-defined Canadian categories (TFSA, RRSP, etc.)

**Example Data**:
```json
// Income Categories
{
  "id": 1,
  "name": "工资收入",
  "type": "income",
  "parent_id": null,
  "is_system": true
}
{
  "id": 2,
  "name": "政府福利",
  "type": "income",
  "parent_id": null,
  "children": [
    {"name": "儿童福利金 (CCB)", "parent_id": 2},
    {"name": "GST/HST退税", "parent_id": 2}
  ]
}

// Expense Categories
{
  "id": 10,
  "name": "房屋运营",
  "type": "expense",
  "parent_id": null,
  "children": [
    {"name": "水电费", "parent_id": 10},
    {"name": "地税", "parent_id": 10},
    {"name": "房屋保险", "parent_id": 10}
  ]
}

// Asset Categories
{
  "id": 50,
  "name": "退休账户",
  "type": "asset",
  "children": [
    {"name": "TFSA", "parent_id": 50},
    {"name": "RRSP", "parent_id": 50},
    {"name": "FHSA", "parent_id": 50}
  ]
}
```

---

### 2. Assets Table (资产追踪)

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    current_value NUMERIC(18,2) NOT NULL,
    purchase_date DATE,
    purchase_value NUMERIC(18,2),
    appreciation_rate NUMERIC(5,2),  -- Annual %
    refresh_source VARCHAR(50),  -- 'manual', 'stock_api', 'crypto_api', 'real_estate_api'
    last_refreshed TIMESTAMP,
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB,  -- Flexible storage for API-specific data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT positive_value CHECK (current_value >= 0)
);

CREATE INDEX idx_assets_user_id ON assets(user_id);
CREATE INDEX idx_assets_category_id ON assets(category_id);
CREATE INDEX idx_assets_last_refreshed ON assets(last_refreshed);
```

**Example Assets**:
```json
// House
{
  "name": "主住宅 - 123 Main St",
  "category_id": 51,  // "房地产"
  "current_value": 850000,
  "purchase_date": "2020-05-15",
  "purchase_value": 650000,
  "appreciation_rate": 5.2,
  "refresh_source": "real_estate_api",
  "metadata": {"sqft": 2000, "bedrooms": 3}
}

// TFSA Account
{
  "name": "TD TFSA - Growth Portfolio",
  "category_id": 52,  // "TFSA"
  "current_value": 45000,
  "purchase_value": 0,  // Started at 0
  "refresh_source": "manual",
  "metadata": {"contribution_room": 6500}
}

// Stocks
{
  "name": "NVDA - 100 shares",
  "category_id": 55,  // "股票"
  "current_value": 48500,
  "refresh_source": "stock_api",
  "metadata": {"ticker": "NVDA", "shares": 100, "avg_cost": 350}
}
```

---

### 3. Liabilities Table (负债追踪)

```sql
CREATE TABLE liabilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    principal_balance NUMERIC(18,2) NOT NULL,  -- 本金余额
    interest_rate NUMERIC(5,2) NOT NULL,  -- APR (%)
    payment_frequency VARCHAR(20) DEFAULT 'monthly',  -- monthly/bi-weekly/weekly
    payment_amount NUMERIC(10,2),  -- Regular payment
    due_date DATE,  -- Next payment due
    origination_date DATE,  -- Loan start
    maturity_date DATE,  -- Loan end
    lender VARCHAR(100),  -- Bank/creditor name
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT positive_balance CHECK (principal_balance >= 0),
    CONSTRAINT valid_interest CHECK (interest_rate >= 0 AND interest_rate <= 100)
);

CREATE INDEX idx_liabilities_user_id ON liabilities(user_id);
CREATE INDEX idx_liabilities_category_id ON liabilities(category_id);
CREATE INDEX idx_liabilities_due_date ON liabilities(due_date);
```

**Example Liabilities**:
```json
// Mortgage
{
  "name": "房贷 - 123 Main St",
  "category_id": 71,  // "抵押贷款"
  "principal_balance": 450000,
  "interest_rate": 3.5,
  "payment_frequency": "monthly",
  "payment_amount": 2245,
  "due_date": "2026-02-01",
  "origination_date": "2020-05-15",
  "maturity_date": "2045-05-15",
  "lender": "TD Bank",
  "metadata": {"term": "25 years", "type": "fixed"}
}

// Credit Card
{
  "name": "TD Visa - ***1234",
  "category_id": 73,  // "信用卡"
  "principal_balance": 2500,
  "interest_rate": 19.99,
  "payment_amount": 50,  // Minimum payment
  "due_date": "2026-01-25",
  "lender": "TD Bank"
}

// Car Loan
{
  "name": "Toyota Tundra 贷款",
  "category_id": 72,  // "车辆贷款"
  "principal_balance": 25000,
  "interest_rate": 4.5,
  "payment_amount": 465,
  "due_date": "2026-02-10",
  "maturity_date": "2028-12-31"
}
```

---

### 4. Documents Table (AI文档解析)

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),  -- Storage path
    file_type VARCHAR(50),  -- 'pdf', 'image', 'csv'
    file_size INTEGER,  -- bytes
    upload_date TIMESTAMP DEFAULT NOW(),
    parsed_data JSONB,  -- AI extracted content
    parsing_status VARCHAR(20) DEFAULT 'pending',  -- pending/processing/completed/failed
    ai_confidence NUMERIC(5,2),  -- 0-100 %
    linked_entity VARCHAR(50),  -- 'transaction', 'insurance', 'asset', etc.
    linked_id INTEGER,  -- ID in the linked table
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_parsing_status ON documents(parsing_status);
CREATE INDEX idx_documents_linked_entity ON documents(linked_entity, linked_id);
```

**Example Parsed Data**:
```json
// Insurance Document
{
  "file_name": "牙医报销_2025_12.pdf",
  "file_type": "pdf",
  "parsed_data": {
    "type": "dental_claim",
    "provider": "Sun Life",
    "claim_items": [
      {
        "procedure": "牙齿清洁",
        "cost": 150,
        "coverage_ratio": 0.8,
        "reimbursement": 120
      },
      {
        "procedure": "X光",
        "cost": 80,
        "coverage_ratio": 0.8,
        "reimbursement": 64
      }
    ],
    "total_reimbursement": 184
  },
  "ai_confidence": 95.5,
  "linked_entity": "insurance",
  "linked_id": 3
}

// Receipt
{
  "file_name": "walmart_receipt.jpg",
  "parsed_data": {
    "merchant": "Walmart",
    "amount": 127.45,
    "date": "2025-12-15",
    "items": [
      {"name": "Milk", "price": 4.99},
      {"name": "Bread", "price": 3.50}
    ],
    "suggested_category": "Groceries"
  },
  "ai_confidence": 88.0,
  "linked_entity": "transaction",
  "linked_id": 1523
}
```

---

## 🔄 Modified Existing Tables

### Transactions Table (Enhanced)

```sql
ALTER TABLE transactions
ADD COLUMN category_id INTEGER REFERENCES categories(id),
ADD COLUMN account_id INTEGER REFERENCES accounts(id),
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN source_type VARCHAR(20) DEFAULT 'manual',  -- manual/ai_scan/email_parse/api
ADD COLUMN ai_confidence NUMERIC(5,2),
ADD COLUMN metadata JSONB;

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
```

### Accounts Table (Enhanced)

```sql
ALTER TABLE accounts
ADD COLUMN category_id INTEGER REFERENCES categories(id),
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN contribution_limit NUMERIC(18,2),  -- TFSA/RRSP annual limit
ADD COLUMN contribution_room NUMERIC(18,2),  -- Available room
ADD COLUMN ytd_contributions NUMERIC(18,2) DEFAULT 0,  -- Year-to-date
ADD COLUMN metadata JSONB;

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_category_id ON accounts(category_id);
```

### Insurances Table (Enhanced)

```sql
ALTER TABLE insurances
ADD COLUMN category_id INTEGER REFERENCES categories(id),
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN reimbursement_details JSONB,  -- Claims/coverage breakdown
ADD COLUMN metadata JSONB;

CREATE INDEX idx_insurances_user_id ON insurances(user_id);
CREATE INDEX idx_insurances_category_id ON insurances(category_id);
```

### Subscriptions Table (Enhanced)

```sql
ALTER TABLE subscriptions
ADD COLUMN category_id INTEGER REFERENCES categories(id),
ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_category_id ON subscriptions(category_id);
```

---

## 📐 Key Financial Calculations

### Net Worth
```sql
-- Assets
SELECT SUM(current_value) as total_assets
FROM assets
WHERE user_id = ?;

-- Account Balances
SELECT SUM(balance) as account_balances
FROM accounts
WHERE user_id = ?;

-- Liabilities
SELECT SUM(principal_balance) as total_liabilities
FROM liabilities
WHERE user_id = ?;

-- Net Worth = (Assets + Accounts) - Liabilities
```

### Debt-to-Income Ratio
```sql
-- Monthly Income
SELECT SUM(amount) as monthly_income
FROM transactions
WHERE user_id = ?
  AND type = 'income'
  AND date >= date_trunc('month', CURRENT_DATE);

-- Monthly Debt Payments
SELECT SUM(payment_amount) as monthly_debt
FROM liabilities
WHERE user_id = ?
  AND payment_frequency = 'monthly';

-- Ratio = monthly_debt / monthly_income
```

### Savings Rate
```sql
-- (Income - Expenses) / Income * 100
SELECT
    (SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) -
     ABS(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END))) /
    NULLIF(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) * 100
    as savings_rate
FROM transactions
WHERE user_id = ?
  AND date >= date_trunc('month', CURRENT_DATE);
```

---

## 🔐 Data Integrity Rules

1. **Foreign Keys**: All `user_id` enforce CASCADE delete
2. **Constraints**:
   - Values >= 0 for assets/accounts
   - Interest rates 0-100%
   - Amounts != 0 for transactions
3. **Triggers** (Future):
   - Auto-update `updated_at` on row change
   - Calculate net worth on asset/liability change
4. **Indexes**: All FK columns + frequently queried dates

---

## 🚀 Migration Strategy (V2 → V3)

1. **Create new tables**: categories, assets, liabilities, documents
2. **Add FKs to existing tables**: Start with NULLable, populate, then NOT NULL
3. **Seed system categories**: Canadian-specific (TFSA, RRSP, etc.)
4. **Migrate existing data**:
   - Map current transaction categories to new `categories` table
   - Populate `user_id` from session context
5. **Update application code**: Use new FK relationships
6. **Test rollback**: Ensure migration can be reversed

---

**End of V3.0 Database Design**
