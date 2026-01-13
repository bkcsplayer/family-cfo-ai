# Family CFO v3.0 - 实施总结

> **版本**: 3.0
> **实施日期**: 2026-01-01
> **状态**: 🚧 实施中

---

## 🎯 v3.0 核心目标

v3.0版本聚焦于**增强财务数据结构**和**智能化管理**，实现加拿大家庭CFO级别的财务洞察。

### 主要特性

1. **层级化分类系统** - 灵活的收入/支出/资产/负债分类
2. **资产自动估值** - API自动刷新股票、加密货币价值
3. **负债跟踪** - 完整的债务管理和净值计算
4. **AI文档解析** - 智能识别和提取财务文档信息

---

## 📊 数据库架构变更

### 新增表结构

#### 1. Categories (分类表)
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('income', 'expense', 'asset', 'liability')),
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    icon VARCHAR(50),
    color VARCHAR(20),
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**功能**:
- 支持父子级关系（如"收入" > "工资" > "基本工资"）
- 系统预设分类 + 用户自定义分类
- 图标和颜色编码提升用户体验

#### 2. Assets_v3 (资产表 v3)
```sql
CREATE TABLE assets_v3 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    current_value NUMERIC(18,2) NOT NULL,
    purchase_date DATE,
    purchase_value NUMERIC(18,2),
    appreciation_rate NUMERIC(5,2),
    refresh_source VARCHAR(50) DEFAULT 'manual',
    last_refreshed TIMESTAMP,
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    extra_data JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**功能**:
- API自动刷新: `stock_api`, `crypto_api`, `real_estate_api`
- 增值率跟踪
- JSONB灵活存储(ticker, API响应等)

#### 3. Liabilities (负债表)
```sql
CREATE TABLE liabilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    principal_balance NUMERIC(18,2) NOT NULL,
    interest_rate NUMERIC(5,2) NOT NULL,
    payment_frequency VARCHAR(20) DEFAULT 'monthly',
    payment_amount NUMERIC(10,2),
    next_payment_date DATE,
    origination_date DATE,
    maturity_date DATE,
    lender VARCHAR(100),
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    extra_data JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**功能**:
- 支持多种还款频率(weekly, monthly, quarterly等)
- 利率追踪
- 下次还款日期提醒

#### 4. Documents (文档表)
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    upload_date TIMESTAMP DEFAULT NOW(),
    parsed_data JSONB,
    parsing_status VARCHAR(20) DEFAULT 'pending',
    ai_confidence NUMERIC(5,2),
    linked_entity VARCHAR(50),
    linked_id INTEGER,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**功能**:
- AI自动解析(Claude 3.5 Sonnet)
- 关联到交易/资产/负债
- 置信度评分

---

## 🔗 数据关系图

```
┌──────────┐
│  Users   │
└────┬─────┘
     │
     ├─────────┬────────────┬─────────────┬──────────────┐
     │         │            │             │              │
     ▼         ▼            ▼             ▼              ▼
┌──────────┐ ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌───────────┐
│Categories│ │Assets_v3│ │Liabilities│ │Transactions│ │Documents  │
└────┬─────┘ └────┬────┘ └─────┬────┘ └──────────  │ └───────────┘
     │            │            │
     │ parent_id  │category_id │category_id
     └────────────┴────────────┘
         (自引用)      (外键)
```

---

## 🚀 API 端点 (v3.0新增)

### Categories API (`/api/categories`)

| Method | Endpoint | 描述 |
|--------|----------|------|
| GET | `/api/categories/` | 获取所有分类(支持筛选) |
| GET | `/api/categories/tree` | 获取层级树结构 |
| GET | `/api/categories/{id}` | 获取单个分类 |
| GET | `/api/categories/{id}/subcategories` | 获取子分类 |
| POST | `/api/categories/` | 创建新分类 |
| PUT | `/api/categories/{id}` | 更新分类 |
| DELETE | `/api/categories/{id}` | 软删除分类 |

**查询参数**:
- `type`: income/expense/asset/liability
- `is_system`: true/false
- `is_active`: true/false (默认true)

### Assets & Liabilities API (`/api/v3`)

| Method | Endpoint | 描述 |
|--------|----------|------|
| GET | `/api/v3/assets` | 获取所有资产 |
| GET | `/api/v3/assets/summary` | 资产汇总(按分类) |
| GET | `/api/v3/assets/{id}` | 获取单个资产 |
| POST | `/api/v3/assets` | 创建新资产 |
| PUT | `/api/v3/assets/{id}` | 更新资产 |
| DELETE | `/api/v3/assets/{id}` | 软删除资产 |
| GET | `/api/v3/liabilities` | 获取所有负债 |
| GET | `/api/v3/liabilities/summary` | 负债汇总 |
| POST | `/api/v3/liabilities` | 创建新负债 |
| PUT | `/api/v3/liabilities/{id}` | 更新负债 |
| DELETE | `/api/v3/liabilities/{id}` | 软删除负债 |
| **GET** | **`/api/v3/net-worth`** | **净值计算** |

---

## 💼 系统预设分类

### 收入类别 (Income)
```
💼 Employment Income
   ├─ 💵 Salary
   ├─ 🎁 Bonus
   ├─ ⏰ Overtime
   └─ 📊 Commission

📈 Investment Income
   ├─ 💰 Dividends
   ├─ 🏦 Interest
   ├─ 📊 Capital Gains
   ├─ 🇨🇦 TFSA Returns
   └─ 🇨🇦 RRSP Returns

🏛️ Government Benefits
   ├─ 👶 CCB (Canada Child Benefit)
   ├─ 💳 GST/HST Credit
   ├─ 👴 OAS (Old Age Security)
   └─ 🏦 CPP (Canada Pension)

💸 Other Income
   ├─ 🏠 Rental Income
   ├─ 🏢 Business Income
   ├─ 💻 Freelance Income
   └─ 🛡️ Insurance Claims
```

### 支出类别 (Expense)
```
🏠 Housing
   ├─ 🏢 Rent
   ├─ 🏦 Mortgage Payment
   ├─ 🏛️ Property Tax
   ├─ 🛡️ Home Insurance
   └─ 🔧 Home Maintenance

⚡ Utilities
   ├─ 💡 Electricity
   ├─ 💧 Water & Sewer
   ├─ 🔥 Natural Gas
   ├─ 🌐 Internet
   └─ 📱 Phone

🚗 Transportation
   ├─ ⛽ Fuel
   ├─ 🛡️ Car Insurance
   ├─ 🔧 Car Maintenance
   └─ 🚇 Public Transit

🍽️ Food & Dining
   ├─ 🛒 Groceries
   ├─ 🍴 Restaurants
   └─ ☕ Coffee & Snacks

🏥 Healthcare
   ├─ 🛡️ Health Insurance Premium
   ├─ 👨‍⚕️ Doctor Visits
   ├─ 💊 Prescriptions
   └─ 🦷 Dental
```

### 资产类别 (Asset)
```
🏘️ Real Estate
   ├─ 🏠 Primary Residence
   ├─ 🏢 Investment Property
   └─ 🌳 Vacant Land

📊 Investments
   ├─ 📈 Stocks
   ├─ 📄 Bonds
   ├─ 📊 Mutual Funds
   ├─ 📉 ETFs
   └─ ₿ Cryptocurrency

🇨🇦 Registered Accounts (Canada)
   ├─ 💰 TFSA
   ├─ 👴 RRSP
   ├─ 🏠 FHSA
   └─ 🎓 RESP

💵 Savings & Cash
   ├─ 🏦 Checking Account
   ├─ 💰 Savings Account
   ├─ 📜 GIC
   └─ 💵 Cash
```

### 负债类别 (Liability)
```
🏠 Mortgage
   ├─ 🏠 Primary Mortgage
   ├─ 🏦 Home Equity Loan
   └─ 🏢 Investment Property Mortgage

🚗 Auto Loans
   ├─ 🚙 Car Loan
   └─ 📝 Car Lease

💳 Credit Cards
   ├─ 💳 Credit Card
   └─ 🏦 Line of Credit

🎓 Student Loans
   ├─ 🏛️ Federal Student Loan
   └─ 🏦 Private Student Loan
```

---

## 📐 财务计算公式

### 净值 (Net Worth)
```python
net_worth = sum(assets_v3.current_value) - sum(liabilities.principal_balance)
```

### 储蓄率 (Savings Rate)
```python
savings_rate = (monthly_income - monthly_expenses) / monthly_income * 100
```

### 债务收入比 (Debt-to-Income Ratio)
```python
dti_ratio = sum(monthly_debt_payments) / monthly_gross_income
```

### 应急基金月数 (Emergency Fund Months)
```python
emergency_months = liquid_assets / average_monthly_expenses
```

---

## 🔧 技术实现细节

### SQLAlchemy 模型
- 位置: `backend/models.py` (第138-246行)
- 特性:
  - 自引用外键 (Category.parent_id)
  - JSONB字段 (extra_data)
  - 级联删除 (ON DELETE CASCADE)
  - 软删除 (is_active标志)

### Pydantic Schemas
- 位置: `backend/schemas.py` (第259-411行)
- 包含:
  - Base, Create, Update, Response schemas
  - CategoryTree (递归嵌套)
  - NetWorthSummary, FinancialHealthMetrics

### API路由
- Categories: `backend/routers/categories.py` (266行)
- Assets/Liabilities: `backend/routers/assets_v3.py` (412行)

### 数据库迁移
- 文件: `backend/alembic/versions/c7fc163ae2f7_*.py`
- 命令: `alembic upgrade head`
- 状态: ✅ 已应用

---

## 🐛 已修复问题

### 问题1: SQLAlchemy保留字段冲突
**错误**: `InvalidRequestError: Attribute name 'metadata' is reserved`

**原因**: SQLAlchemy Declarative API保留了`metadata`字段名

**解决方案**:
- 将所有`metadata`字段重命名为`extra_data`
- 更新models.py, schemas.py, migration文件
- 重新构建Docker镜像

---

## 📋 待完成任务

- [x] 创建SQLAlchemy模型
- [x] 创建Pydantic schemas
- [x] 创建Alembic迁移
- [x] 创建API路由
- [x] 修复metadata字段冲突
- [ ] 重新构建backend镜像
- [ ] 测试所有API端点
- [ ] 生成系统预设分类数据
- [ ] 更新seed_mock_data.py支持v3.0
- [ ] 创建前端UI组件
- [ ] 编写API使用文档

---

## 🚀 部署说明

### 1. 应用数据库迁移
```bash
docker exec familycfo_backend alembic upgrade head
```

### 2. 生成系统分类
```bash
docker exec familycfo_backend python scripts/seed_system_categories.py
```

### 3. 重启服务
```bash
docker-compose restart backend
```

### 4. 验证API
```bash
curl http://localhost:6501/api/categories/tree
```

---

## 📊 API使用示例

### 创建资产
```bash
curl -X POST http://localhost:6501/api/v3/assets \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tesla Stock",
    "category_id": 15,
    "current_value": 45000.00,
    "purchase_date": "2023-01-15",
    "purchase_value": 30000.00,
    "refresh_source": "stock_api",
    "extra_data": {"ticker": "TSLA", "shares": 100}
  }'
```

### 查询净值
```bash
curl http://localhost:6501/api/v3/net-worth \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "total_assets": 450000.00,
  "total_liabilities": 250000.00,
  "net_worth": 200000.00,
  "asset_breakdown": {
    "Real Estate": 300000.00,
    "Stocks": 100000.00,
    "TFSA": 50000.00
  },
  "liability_breakdown": {
    "Mortgage": 200000.00,
    "Credit Card": 5000.00
  },
  "last_updated": "2026-01-01T12:00:00Z"
}
```

---

## 🔮 v3.1 规划

1. **资产自动刷新服务**
   - 集成股票API (Alpha Vantage, Yahoo Finance)
   - 集成加密货币API (CoinGecko, Binance)
   - 定时任务每日更新

2. **AI文档解析**
   - 集成Claude API
   - 自动识别收据、账单、保险单
   - 置信度评分和人工审核

3. **移动端UI**
   - React组件库
   - 资产负债可视化
   - 净值趋势图

4. **高级分析**
   - 资产配置建议
   - 债务优化策略
   - 退休计划模拟

---

**文档最后更新**: 2026-01-01
**作者**: Claude (Anthropic AI)
**项目版本**: v3.0 (实施中)
