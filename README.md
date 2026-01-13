<p align="center">
  <img src="docs/images/admin_dashboard.png" alt="Family CFO Dashboard" width="600">
</p>

<h1 align="center">🏠 Family CFO AI</h1>

<p align="center">
  <strong>智能家庭财务管理系统 | Intelligent Family Financial Management System</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" alt="React">
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/AI-Powered-purple" alt="AI Powered">
</p>

---

## 📋 项目简介

**Family CFO AI** 是一个专为加拿大家庭设计的智能财务管理系统，具备 AI 驱动的收据识别、智能分类和全面的财务分析功能。

### ✨ 核心特性

| 功能 | 描述 |
|------|------|
| 🤖 **AI 收据识别** | OCR 自动识别收据，智能提取商家、金额、日期 |
| 🏷️ **智能分类** | 规则引擎 + AI 混合分类，120+ 预设类别 |
| 💰 **收支管理** | 完整的交易审批工作流 |
| 📈 **资产追踪** | 实时资产价值追踪，支持股票/加密货币 API |
| 📉 **负债管理** | 贷款、信用卡还款提醒 |
| 🏛️ **加拿大账户** | TFSA、RRSP、RESP、FHSA 额度追踪 |
| 💵 **政府福利** | CCB、GST/HST、OAS、CPP 自动记录 |
| 📊 **财务分析** | 净资产、现金流、燃烧率仪表板 |
| 🔔 **智能通知** | Telegram 机器人 + 邮件报告 |

---

## 📸 应用截图

<table>
<tr>
<td width="50%">

### 🖥️ Admin Dashboard
<img src="docs/images/admin_dashboard.png" alt="Admin Dashboard" width="100%">

</td>
<td width="50%">

### 📱 Mobile App
<img src="docs/images/mobile_app.png" alt="Mobile App" width="100%">

</td>
</tr>
<tr>
<td colspan="2">

### 📚 API Documentation
<img src="docs/images/api_docs.png" alt="API Docs" width="100%">

</td>
</tr>
</table>

---

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Git

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/bkcsplayer/family-cfo-ai.git
cd family-cfo-ai

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 3. 启动所有服务
docker-compose up -d

# 4. 访问应用
# Admin Dashboard: http://localhost:6502
# Mobile App:      http://localhost:6503
# API Docs:        http://localhost:6501/docs
```

### 默认登录

```
用户名: admin
密码:   password123
```

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
├─────────────────────────────────────────────────────────────┤
│  Admin Dashboard (React + TailwindCSS)  │  Mobile PWA       │
│         Port 6502                       │    Port 6503      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│                        Port 6501                             │
├─────────────────────────────────────────────────────────────┤
│  Auth │ Transactions │ Assets │ AI/OCR │ Notifications      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│                        Port 6500                             │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| **前端** | React 18, TypeScript, TailwindCSS, Vite |
| **数据库** | PostgreSQL 15 |
| **AI** | OpenRouter API (Claude 3.5 Sonnet) |
| **部署** | Docker, Nginx |

---

## 📁 项目结构

```
family-cfo-ai/
├── backend/                 # FastAPI 后端
│   ├── routers/             # API 路由
│   ├── services/            # 业务服务
│   ├── models.py            # 数据模型
│   └── main.py              # 入口文件
├── admin/                   # Admin 管理后台
│   └── src/
├── frontend/                # 移动端 PWA
│   └── src/
├── docs/                    # 文档 & 截图
├── docker-compose.yml       # Docker 编排
└── README.md
```

---

## 🇨🇦 加拿大专属功能

### 支持的注册账户
- **TFSA** - 免税储蓄账户
- **RRSP** - 注册退休储蓄计划
- **RESP** - 注册教育储蓄计划
- **FHSA** - 首次购房储蓄账户

### 支持的政府福利
- **CCB** - 加拿大儿童福利金
- **GST/HST** - 消费税退税
- **OAS** - 老年保障金
- **CPP** - 加拿大养老金计划

---

## 🔧 配置说明

在 `.env` 文件中配置：

```bash
# 数据库
DATABASE_URL=postgresql://admin:password123@database:5432/family_cfo

# AI 服务 (可选)
OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Telegram 通知 (可选)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_USER_ID=your-user-id

# 邮件服务 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email
```

---

## 📝 API 文档

启动后访问: http://localhost:6501/docs

主要端点:
- `POST /api/auth/token` - 用户登录
- `GET /api/dashboard/stats` - 仪表板数据
- `GET/POST /api/transactions` - 交易管理
- `GET/POST /api/assets` - 资产管理
- `POST /api/upload/receipt` - 收据上传

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

<p align="center">
  Made with ❤️ for better family financial management
</p>
