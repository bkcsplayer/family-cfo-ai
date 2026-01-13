# Family CFO v3.0 部署完成总结

## 🎉 部署概述

Family CFO v3.0 已成功部署！这是一个全新的 Docker 环境，与 v2.0 完全独立并行运行。

## 📊 版本对比

| 组件 | v2.0 端口 | v3.0 端口 | 容器名称 |
|------|----------|----------|---------|
| 数据库 | 6500 | **6510** | familycfo_db_v3 |
| Backend API | 6501 | **6511** | familycfo_backend_v3 |
| Admin 管理后台 | 6502 | **6512** | familycfo_admin_v3 |
| Mobile 移动端 | 6503 | **6513** | familycfo_mobile_v3 |

## 🚀 启动和停止

### 启动 v3.0
```bash
docker-compose -f docker-compose-v3.yml up -d
```

### 停止 v3.0
```bash
docker-compose -f docker-compose-v3.yml down
```

### 查看日志
```bash
docker-compose -f docker-compose-v3.yml logs -f backend_v3
```

### 重新构建
```bash
docker-compose -f docker-compose-v3.yml build --no-cache
docker-compose -f docker-compose-v3.yml up -d
```

## 🗄️ 数据库信息

### v3.0 数据库配置
- **数据库名**: `family_cfo_v3`
- **用户名**: `admin`
- **密码**: `password123`
- **端口**: `6510`
- **连接字符串**: `postgresql://admin:password123@localhost:6510/family_cfo_v3`

### 数据库表 (v3.0 新增)
1. **categories** - 分层分类系统（收入/支出/资产/负债）
2. **assets_v3** - 增强资产追踪
3. **liabilities** - 负债管理
4. **documents** - 文档管理和 AI 解析

### 系统分类统计
- 💰 收入分类: **22** 个
- 💸 支出分类: **51** 个
- 📈 资产分类: **28** 个
- 📉 负债分类: **19** 个
- **总计: 120** 个系统预定义分类

## 🔌 API 端点

### 基础端点
- **健康检查**: `http://localhost:6511/health`
- **API 文档**: `http://localhost:6511/docs`
- **OpenAPI JSON**: `http://localhost:6511/openapi.json`

### v3.0 新增端点

#### 1. 分类管理 (`/api/categories`)
- `GET /api/categories/` - 列出所有分类（支持筛选）
- `POST /api/categories/` - 创建用户自定义分类
- `GET /api/categories/tree` - 获取分层树形结构
- `GET /api/categories/{id}` - 获取单个分类
- `PUT /api/categories/{id}` - 更新分类
- `DELETE /api/categories/{id}` - 删除分类
- `GET /api/categories/{id}/subcategories` - 获取子分类

#### 2. 资产管理 (`/api/v3/assets`)
- `GET /api/v3/assets` - 列出所有资产
- `POST /api/v3/assets` - 创建新资产
- `GET /api/v3/assets/{id}` - 获取单个资产
- `PUT /api/v3/assets/{id}` - 更新资产
- `DELETE /api/v3/assets/{id}` - 删除资产
- `GET /api/v3/assets/summary` - 资产汇总统计
- `POST /api/v3/assets/{id}/refresh` - 刷新资产价值

#### 3. 负债管理 (`/api/v3/liabilities`)
- `GET /api/v3/liabilities` - 列出所有负债
- `POST /api/v3/liabilities` - 创建新负债
- `GET /api/v3/liabilities/{id}` - 获取单个负债
- `PUT /api/v3/liabilities/{id}` - 更新负债
- `DELETE /api/v3/liabilities/{id}` - 删除负债
- `GET /api/v3/liabilities/summary` - 负债汇总统计

#### 4. 净资产计算
- `GET /api/v3/net-worth` - 计算综合净资产

#### 5. 文档管理 (`/api/v3/documents`)
- `GET /api/v3/documents` - 列出所有文档
- `POST /api/v3/documents` - 上传新文档
- `GET /api/v3/documents/{id}` - 获取文档详情
- `PUT /api/v3/documents/{id}` - 更新文档
- `DELETE /api/v3/documents/{id}` - 删除文档
- `POST /api/v3/documents/{id}/parse` - 触发 AI 解析

## 🇨🇦 加拿大特定功能

### 注册账户分类
- **TFSA** (Tax-Free Savings Account)
- **RRSP** (Registered Retirement Savings Plan)
- **FHSA** (First Home Savings Account)
- **RESP** (Registered Education Savings Plan)

### 政府福利分类
- **CCB** (Canada Child Benefit)
- **GST/HST** 退税
- **OAS** (Old Age Security)
- **CPP** (Canada Pension Plan)
- **EI** (Employment Insurance)

## 🔧 技术栈

### 后端
- **Python 3.11**
- **FastAPI 0.109.0** - Web 框架
- **SQLAlchemy 2.0.25** - ORM
- **Alembic 1.13.1** - 数据库迁移
- **Pydantic 2.5.3** - 数据验证
- **PostgreSQL 15** - 数据库

### 前端
- **React 18** with TypeScript
- **Vite** - 构建工具
- **Nginx** - Web 服务器

## 📝 数据库迁移

### 当前迁移版本
```
c7fc163ae2f7 - Add v3.0 tables (categories, assets_v3, liabilities, documents)
```

### 运行迁移
```bash
docker exec familycfo_backend_v3 alembic upgrade head
```

### 查看当前版本
```bash
docker exec familycfo_backend_v3 alembic current
```

### 回滚到上一个版本
```bash
docker exec familycfo_backend_v3 alembic downgrade -1
```

## 🌱 数据播种

### 系统分类播种
```bash
echo "y" | docker exec -i familycfo_backend_v3 python scripts/seed_system_categories.py
```

### 测试数据播种
```bash
docker exec familycfo_backend_v3 python scripts/seed_mock_data.py
```

## 🔐 身份验证

### 登录端点
```bash
curl -X POST http://localhost:6511/api/auth/token \
  -d "username=admin&password=admin123"
```

### 使用 Token
```bash
TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:6511/api/categories/
```

## 🌐 访问应用

### v3.0 应用地址
- **Admin 管理后台**: http://localhost:6512
- **Mobile 移动端**: http://localhost:6513
- **API 文档**: http://localhost:6511/docs

### v2.0 应用地址（仍在运行）
- **Admin 管理后台**: http://localhost:6502
- **Mobile 移动端**: http://localhost:6503
- **API 文档**: http://localhost:6501/docs

## 📊 v3.0 新功能亮点

### 1. 灵活的分类系统
- ✅ 4 种类型：收入、支出、资产、负债
- ✅ 父子关系支持（无限层级）
- ✅ 系统预定义 + 用户自定义
- ✅ 图标和颜色自定义
- ✅ 软删除（is_active 标志）

### 2. 增强的资产追踪
- ✅ 多种刷新来源（手动、股票API、加密货币API、房地产API）
- ✅ 购买价值 vs 当前价值
- ✅ 增值率自动计算
- ✅ 最后刷新时间戳
- ✅ JSONB 额外数据存储

### 3. 完整的负债管理
- ✅ 本金余额追踪
- ✅ 利率和还款频率
- ✅ 下次还款日期提醒
- ✅ 贷款机构信息
- ✅ 起始日期和到期日期

### 4. 智能文档管理
- ✅ 文件上传和存储
- ✅ AI 解析状态追踪
- ✅ 解析置信度评分
- ✅ 实体链接（交易、保险等）
- ✅ 结构化解析数据存储

### 5. 净资产仪表板
- ✅ 总资产计算
- ✅ 总负债计算
- ✅ 净资产 = 资产 - 负债
- ✅ 按分类的资产细分
- ✅ 按分类的负债细分

## 🐛 故障排查

### 容器无法启动
```bash
# 查看日志
docker-compose -f docker-compose-v3.yml logs backend_v3

# 重新构建
docker-compose -f docker-compose-v3.yml build --no-cache backend_v3
docker-compose -f docker-compose-v3.yml up -d
```

### 数据库连接问题
```bash
# 检查数据库容器状态
docker ps --filter "name=familycfo_db_v3"

# 进入数据库容器
docker exec -it familycfo_db_v3 psql -U admin -d family_cfo_v3
```

### API 端点 404 错误
```bash
# 确认路由注册
curl http://localhost:6511/openapi.json | python -m json.tool | grep "/api/categories"

# 重启后端容器
docker-compose -f docker-compose-v3.yml restart backend_v3
```

## 🔄 从 v2.0 迁移数据

### 导出 v2.0 数据
```bash
docker exec familycfo_db pg_dump -U admin family_cfo > backup_v2.sql
```

### 导入到 v3.0
```bash
# 需要手动调整 SQL 以适配 v3.0 schema
docker exec -i familycfo_db_v3 psql -U admin family_cfo_v3 < backup_v2_modified.sql
```

## 📈 下一步计划

### 短期目标
1. ✅ 完成后端 v3.0 API
2. ⏳ 更新前端集成 v3.0 端点
3. ⏳ 实现资产价格 API 集成
4. ⏳ 实现 AI 文档解析功能

### 中期目标
1. ⏳ 财务规划和建议引擎
2. ⏳ 预算预测和趋势分析
3. ⏳ 移动端推送通知
4. ⏳ 数据导出和备份功能

### 长期目标
1. ⏳ 多用户家庭账户支持
2. ⏳ 银行账户自动同步
3. ⏳ 高级财务报表生成
4. ⏳ 税务优化建议

## 🎯 版本信息

- **版本号**: 3.0.0
- **发布日期**: 2026-01-01
- **数据库版本**: PostgreSQL 15
- **Python 版本**: 3.11
- **Node 版本**: 18

## 📞 支持和文档

- **API 文档**: http://localhost:6511/docs
- **GitHub Issues**: [报告问题](https://github.com/yourusername/familyltdcfo/issues)
- **技术文档**: 查看 `docs/` 目录

---

🎊 恭喜！Family CFO v3.0 已成功部署并运行！
