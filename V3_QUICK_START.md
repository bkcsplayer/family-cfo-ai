# Family CFO v3.0 快速开始指南

## 🚀 访问地址

### v3.0 应用
- **Admin 管理后台**: http://localhost:6512
- **Mobile 移动端**: http://localhost:6513
- **Backend API 文档**: http://localhost:6511/docs
- **数据库端口**: 6510

### v2.0 应用（仍在运行）
- **Admin 管理后台**: http://localhost:6502
- **Mobile 移动端**: http://localhost:6503
- **Backend API 文档**: http://localhost:6501/docs
- **数据库端口**: 6500

## 🔐 登录凭证

### 管理员账户
```
用户名: admin
密码: admin123
```

⚠️ **重要**: 首次登录后请立即修改密码！

## 🔑 API 认证示例

### 1. 获取访问令牌
```bash
curl -X POST http://localhost:6511/api/auth/token \
  -d "username=admin&password=admin123"
```

响应:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2. 使用令牌调用 API
```bash
TOKEN="your_access_token_here"

# 获取收入分类
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:6511/api/categories/?type=income&is_system=true"

# 获取分类树
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:6511/api/categories/tree"

# 获取资产列表
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:6511/api/v3/assets"

# 计算净资产
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:6511/api/v3/net-worth"
```

## 📊 v3.0 核心功能测试

### 创建用户自定义分类
```bash
curl -X POST http://localhost:6511/api/categories/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的自定义收入",
    "type": "income",
    "description": "自定义收入分类",
    "icon": "💰",
    "color": "#10B981"
  }'
```

### 创建资产
```bash
curl -X POST http://localhost:6511/api/v3/assets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "主要住宅",
    "category_id": 1,
    "current_value": 800000.00,
    "purchase_date": "2020-01-15",
    "purchase_value": 650000.00,
    "refresh_source": "manual",
    "notes": "多伦多市区公寓"
  }'
```

### 创建负债
```bash
curl -X POST http://localhost:6511/api/v3/liabilities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "房屋抵押贷款",
    "category_id": 1,
    "principal_balance": 500000.00,
    "interest_rate": 3.5,
    "payment_frequency": "monthly",
    "payment_amount": 2500.00,
    "next_payment_date": "2026-02-01",
    "lender": "TD Canada Trust"
  }'
```

## 🗄️ 数据库管理

### 连接到 v3.0 数据库
```bash
# 使用 Docker
docker exec -it familycfo_db_v3 psql -U admin family_cfo_v3

# 或使用端口连接
psql -h localhost -p 6510 -U admin -d family_cfo_v3
```

密码: `password123`

### 查看系统分类
```sql
-- 按类型统计分类数量
SELECT type, COUNT(*) as count
FROM categories
WHERE is_system = true
GROUP BY type;

-- 查看收入分类
SELECT id, name, icon, description
FROM categories
WHERE type = 'income' AND is_system = true
ORDER BY name;
```

## 🐳 Docker 管理命令

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
# 所有服务
docker-compose -f docker-compose-v3.yml logs -f

# 仅后端
docker-compose -f docker-compose-v3.yml logs -f backend_v3

# 仅数据库
docker-compose -f docker-compose-v3.yml logs -f database_v3
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f docker-compose-v3.yml restart

# 仅重启后端
docker-compose -f docker-compose-v3.yml restart backend_v3
```

### 查看容器状态
```bash
docker ps --filter "name=v3"
```

### 进入容器
```bash
# 进入后端容器
docker exec -it familycfo_backend_v3 bash

# 进入数据库容器
docker exec -it familycfo_db_v3 sh
```

## 🔄 数据库操作

### 运行迁移
```bash
docker exec familycfo_backend_v3 alembic upgrade head
```

### 查看迁移历史
```bash
docker exec familycfo_backend_v3 alembic history
```

### 播种系统分类
```bash
echo "y" | docker exec -i familycfo_backend_v3 python scripts/seed_system_categories.py
```

### 创建新用户
```bash
docker exec familycfo_backend_v3 python -c "
import hashlib
from database import SessionLocal
from models import User

db = SessionLocal()
password_hash = hashlib.sha256('your_password'.encode()).hexdigest()

user = User(
    username='newuser',
    password_hash=password_hash,
    display_name='New User',
    role='Editor',  # 可选: Admin, Editor, Viewer
    status='Active'
)

db.add(user)
db.commit()
print(f'用户 {user.username} 创建成功！')
db.close()
"
```

## 📈 v3.0 新功能说明

### 1. 分层分类系统
- 支持 4 种类型：收入、支出、资产、负债
- 无限层级的父子关系
- 系统预定义分类（120个） + 用户自定义
- 每个分类可设置图标和颜色

### 2. 资产管理
- 追踪购买价值和当前价值
- 自动计算增值率
- 支持多种刷新来源：
  - 手动 (manual)
  - 股票 API (stock_api)
  - 加密货币 API (crypto_api)
  - 房地产 API (real_estate_api)

### 3. 负债管理
- 本金余额追踪
- 利率和还款频率
- 下次还款日期提醒
- 支持多种还款频率：
  - 每周 (weekly)
  - 双周 (biweekly)
  - 每月 (monthly)
  - 每季度 (quarterly)
  - 半年 (semi_annually)
  - 每年 (annually)

### 4. 净资产计算
- 自动计算：总资产 - 总负债 = 净资产
- 按分类细分统计
- 实时更新

### 5. 文档管理
- 文件上传和存储
- AI 文档解析（待实现）
- 与交易、保险等实体关联

## 🇨🇦 加拿大特定功能

### 注册账户类型
- **TFSA** - Tax-Free Savings Account
- **RRSP** - Registered Retirement Savings Plan
- **FHSA** - First Home Savings Account
- **RESP** - Registered Education Savings Plan

### 政府福利
- **CCB** - Canada Child Benefit
- **GST/HST** - 商品和服务税退税
- **OAS** - Old Age Security
- **CPP** - Canada Pension Plan
- **EI** - Employment Insurance

## 🛠️ 故障排查

### 问题: 容器无法启动
```bash
# 查看错误日志
docker-compose -f docker-compose-v3.yml logs backend_v3

# 重新构建镜像
docker-compose -f docker-compose-v3.yml build --no-cache backend_v3
docker-compose -f docker-compose-v3.yml up -d
```

### 问题: 无法连接数据库
```bash
# 检查数据库容器状态
docker ps --filter "name=familycfo_db_v3"

# 查看数据库日志
docker logs familycfo_db_v3

# 测试数据库连接
docker exec familycfo_db_v3 pg_isready -U admin
```

### 问题: API 返回 401 未授权
```bash
# 重新获取新的访问令牌
curl -X POST http://localhost:6511/api/auth/token \
  -d "username=admin&password=admin123"
```

### 问题: 前端显示 unhealthy
这是一个已知的健康检查问题（IPv6 vs IPv4），不影响实际功能。前端服务可以正常访问。

## 📚 相关文档

- [完整部署文档](V3_DEPLOYMENT_SUMMARY.md)
- [API 交互文档](http://localhost:6511/docs)
- [数据库设计](docs/V3_DATABASE_DESIGN.md)
- [实施总结](docs/V3_IMPLEMENTATION_SUMMARY.md)

## 🎯 下一步

1. **登录系统**: 使用 admin/admin123 登录
2. **修改密码**: 首次登录后立即修改密码
3. **浏览分类**: 查看 120 个预定义的系统分类
4. **添加资产**: 开始记录您的资产
5. **添加负债**: 记录贷款和其他负债
6. **查看净资产**: 实时查看您的财务状况

---

🎉 **欢迎使用 Family CFO v3.0！**
