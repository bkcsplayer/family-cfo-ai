# Family CFO - Database Schema Documentation

> **Version**: 2.0
> **Last Updated**: 2026-01-01
> **Database**: PostgreSQL 15

---

## Table of Contents
1. [Overview](#overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Table Definitions](#table-definitions)
4. [Relationships](#relationships)
5. [Indexes](#indexes)

---

## Overview

Family CFO 使用 PostgreSQL 数据库来管理家庭财务数据。数据库设计遵循以下原则：
- **标准化**: 符合第三范式 (3NF)
- **审计**: 所有表包含 `created_at` 和 `updated_at` 字段
- **类型安全**: 使用 SQLAlchemy ORM 和 Enum 类型
- **可扩展**: 支持未来功能扩展

---

## Entity Relationship Diagram

```
┌─────────────┐
│   Users     │
│─────────────│
│ id (PK)     │
│ username    │
│ email       │
│ role        │
└──────┬──────┘
       │
       │ (1:N) - 创建者
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Transactions │    │  Accounts   │    │ Insurances  │    │Subscriptions│
│─────────────│    │─────────────│    │─────────────│    │─────────────│
│ id (PK)     │    │ id (PK)     │    │ id (PK)     │    │ id (PK)     │
│ merchant    │    │ type        │    │ provider    │    │ name        │
│ amount      │    │ balance     │    │ type        │    │ amount      │
│ date        │    │ institution │    │ coverage    │    │ frequency   │
│ category    │    │ account_num │    │ premium     │    │ next_due    │
│ type        │    │ created_at  │    │ renewal_dt  │    │ status      │
│ status      │    │ updated_at  │    │ created_at  │    │ created_at  │
│ notes       │    └─────────────┘    │ updated_at  │    │ updated_at  │
│ created_at  │                       └─────────────┘    └─────────────┘
│ updated_at  │
└─────────────┘

Legend:
PK = Primary Key
FK = Foreign Key
1:N = One to Many relationship
```

---

## Table Definitions

### 1. **users** - 用户表

存储系统用户信息（管理员、家庭成员等）。

| Column        | Type         | Nullable | Default | Description          |
|---------------|--------------|----------|---------|----------------------|
| id            | INTEGER      | NO       | AUTO    | 主键                 |
| username      | VARCHAR(100) | NO       | -       | 用户名（唯一）       |
| email         | VARCHAR(255) | YES      | NULL    | 邮箱地址             |
| hashed_password| VARCHAR(255)| NO       | -       | 加密后的密码         |
| display_name  | VARCHAR(100) | YES      | NULL    | 显示名称             |
| role          | VARCHAR(50)  | NO       | 'user'  | 角色 (admin/user)    |
| is_active     | BOOLEAN      | NO       | TRUE    | 账户激活状态         |
| created_at    | TIMESTAMP    | NO       | NOW()   | 创建时间             |
| updated_at    | TIMESTAMP    | NO       | NOW()   | 更新时间             |

**Constraints:**
- PRIMARY KEY: `id`
- UNIQUE: `username`
- INDEX: `email`, `role`

---

### 2. **transactions** - 交易表

存储所有金融交易记录（收入、支出、债务偿还等）。

| Column     | Type         | Nullable | Default    | Description                    |
|------------|--------------|----------|------------|--------------------------------|
| id         | INTEGER      | NO       | AUTO       | 主键                           |
| merchant   | VARCHAR(255) | NO       | -          | 商家名称                       |
| amount     | DECIMAL(15,2)| NO       | -          | 金额（正数=收入，负数=支出）   |
| date       | DATE         | NO       | TODAY      | 交易日期                       |
| category   | VARCHAR(100) | YES      | NULL       | 分类（如 Groceries, Dining）   |
| type       | ENUM         | NO       | 'expense'  | 类型：expense/income/debt_payment|
| status     | ENUM         | NO       | 'Pending'  | 状态：Pending/Posted/Draft     |
| notes      | TEXT         | YES      | NULL       | 备注信息                       |
| created_at | TIMESTAMP    | NO       | NOW()      | 创建时间                       |
| updated_at | TIMESTAMP    | NO       | NOW()      | 更新时间                       |

**Constraints:**
- PRIMARY KEY: `id`
- INDEX: `date`, `category`, `status`, `type`
- CHECK: `amount != 0`

**Enums:**
- `TransactionType`: `expense`, `income`, `debt_payment`
- `TransactionStatus`: `Pending`, `Posted`, `Draft`

---

### 3. **accounts** - 账户表

存储各类金融账户（银行账户、投资账户、福利账户等）。

| Column         | Type         | Nullable | Default | Description                    |
|----------------|--------------|----------|---------|--------------------------------|
| id             | INTEGER      | NO       | AUTO    | 主键                           |
| type           | VARCHAR(50)  | NO       | -       | 账户类型 (TFSA/RRSP/Checking)  |
| balance        | DECIMAL(15,2)| NO       | 0.00    | 当前余额                       |
| institution    | VARCHAR(100) | YES      | NULL    | 金融机构名称                   |
| account_number | VARCHAR(100) | YES      | NULL    | 账户号码（加密存储）           |
| interest_rate  | DECIMAL(5,2) | YES      | NULL    | 利率（%）                      |
| maturity_date  | DATE         | YES      | NULL    | 到期日（如GIC）                |
| created_at     | TIMESTAMP    | NO       | NOW()   | 创建时间                       |
| updated_at     | TIMESTAMP    | NO       | NOW()   | 更新时间                       |

**Constraints:**
- PRIMARY KEY: `id`
- INDEX: `type`, `institution`
- CHECK: `balance >= 0`

**Account Types:**
- `TFSA` - Tax-Free Savings Account
- `RRSP` - Registered Retirement Savings Plan
- `FHSA` - First Home Savings Account
- `Checking` - 支票账户
- `Savings` - 储蓄账户
- `Investment` - 投资账户

---

### 4. **insurances** - 保险表

存储家庭保险保单信息。

| Column         | Type         | Nullable | Default | Description          |
|----------------|--------------|----------|---------|----------------------|
| id             | INTEGER      | NO       | AUTO    | 主键                 |
| provider       | VARCHAR(100) | NO       | -       | 保险公司             |
| type           | VARCHAR(50)  | NO       | -       | 保险类型             |
| policy_number  | VARCHAR(100) | YES      | NULL    | 保单号               |
| coverage_amount| DECIMAL(15,2)| YES      | NULL    | 保额                 |
| premium        | DECIMAL(10,2)| YES      | NULL    | 保费（月/年）        |
| premium_frequency| VARCHAR(20)| YES      | NULL    | 缴费频率             |
| renewal_date   | DATE         | YES      | NULL    | 续保日期             |
| beneficiary    | VARCHAR(255) | YES      | NULL    | 受益人               |
| created_at     | TIMESTAMP    | NO       | NOW()   | 创建时间             |
| updated_at     | TIMESTAMP    | NO       | NOW()   | 更新时间             |

**Constraints:**
- PRIMARY KEY: `id`
- INDEX: `type`, `renewal_date`

**Insurance Types:**
- `Life` - 人寿保险
- `Health` - 健康保险
- `Home` - 房屋保险
- `Auto` - 汽车保险
- `Disability` - 残疾保险

---

### 5. **subscriptions** - 订阅表

存储定期订阅服务（流媒体、会员等）。

| Column     | Type         | Nullable | Default  | Description              |
|------------|--------------|----------|----------|--------------------------|
| id         | INTEGER      | NO       | AUTO     | 主键                     |
| name       | VARCHAR(100) | NO       | -        | 订阅名称                 |
| amount     | DECIMAL(10,2)| NO       | -        | 金额                     |
| frequency  | VARCHAR(20)  | NO       | 'monthly'| 频率 (monthly/yearly)    |
| next_due   | DATE         | YES      | NULL     | 下次扣费日期             |
| status     | VARCHAR(20)  | NO       | 'active' | 状态 (active/cancelled)  |
| category   | VARCHAR(50)  | YES      | NULL     | 分类                     |
| created_at | TIMESTAMP    | NO       | NOW()    | 创建时间                 |
| updated_at | TIMESTAMP    | NO       | NOW()    | 更新时间                 |

**Constraints:**
- PRIMARY KEY: `id`
- INDEX: `status`, `next_due`

---

## Relationships

### User Relationships
- **Users → Transactions**: 一对多（用户创建交易）
- **Users → Accounts**: 一对多（用户拥有账户）
- **Users → Insurances**: 一对多（用户拥有保单）
- **Users → Subscriptions**: 一对多（用户拥有订阅）

### Data Flow
```
用户登录 → 查看 Dashboard
   ├─ 获取交易列表 (transactions)
   ├─ 获取账户余额 (accounts)
   ├─ 获取保险信息 (insurances)
   └─ 获取订阅列表 (subscriptions)
```

---

## Indexes

为提高查询性能，以下字段建立了索引：

### transactions
```sql
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_type ON transactions(type);
```

### accounts
```sql
CREATE INDEX idx_accounts_type ON accounts(type);
CREATE INDEX idx_accounts_institution ON accounts(institution);
```

### insurances
```sql
CREATE INDEX idx_insurances_type ON insurances(type);
CREATE INDEX idx_insurances_renewal_date ON insurances(renewal_date);
```

### subscriptions
```sql
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_next_due ON subscriptions(next_due);
```

---

## Database Migrations

使用 Alembic 管理数据库迁移：

```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

---

## Data Integrity Rules

1. **删除规则**:
   - 删除用户时，保留其创建的数据（将 user_id 设为 NULL 或转移到管理员）

2. **更新规则**:
   - 所有表自动更新 `updated_at` 时间戳

3. **验证规则**:
   - 交易金额不能为 0
   - 账户余额不能为负数
   - 日期必须为有效日期格式

---

## Security Considerations

1. **密码存储**: 使用 bcrypt 哈希
2. **敏感数据**: 账户号码应加密存储
3. **访问控制**: 通过 JWT Token 验证用户身份
4. **SQL注入防护**: 使用 SQLAlchemy ORM 参数化查询

---

## Backup Strategy

建议的备份策略：
- **每日备份**: 自动化全量备份
- **保留期**: 30天
- **测试恢复**: 每月测试一次备份恢复流程

```bash
# PostgreSQL 备份命令
pg_dump -U postgres familycfo > backup_$(date +%Y%m%d).sql

# 恢复命令
psql -U postgres familycfo < backup_20260101.sql
```

---

**End of Database Schema Documentation**
