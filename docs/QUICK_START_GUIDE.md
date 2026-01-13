# 🚀 Family Inc. CFO - 快速开始指南

**版本：** 1.0.0
**更新日期：** 2025-12-30
**状态：** 生产就绪 ✅

---

## 📋 系统要求

- Docker Desktop 或 Docker Engine
- 8GB RAM（推荐 16GB）
- 20GB 可用磁盘空间
- Windows/macOS/Linux

---

## ⚡ 5 分钟快速启动

### 1. 启动系统
```bash
cd f:\Augment-coder\familyltdcfo
docker-compose up -d
```

### 2. 等待容器启动（约 30 秒）
```bash
docker-compose ps
```

**预期输出：**
```
NAME                STATUS
familycfo_backend   Up (healthy)
familycfo_db        Up (healthy)
familycfo_admin     Up
familycfo_mobile    Up
```

### 3. 访问系统

| 服务 | 地址 | 用途 |
|------|------|------|
| **后端 API** | http://localhost:6501 | API 接口 |
| **Swagger UI** | http://localhost:6501/docs | API 文档 |
| **Admin 后台** | http://localhost:6502 | 管理界面 |
| **Mobile 应用** | http://localhost:6503 | 移动端 |
| **数据库** | localhost:6500 | PostgreSQL |

### 4. 登录凭据
```
用户名：admin
密码：password123
```

---

## 🧪 测试新功能

### 测试预算管理（Phase 3）✨

#### 步骤 1：获取 Token
```bash
curl -X POST "http://localhost:6501/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

**保存返回的 `access_token`**

#### 步骤 2：创建预算
```bash
curl -X POST "http://localhost:6501/api/budgets/" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Food - Restaurants",
    "monthly_limit": 500.00,
    "alert_threshold": 90.0
  }'
```

#### 步骤 3：查看预算状态
```bash
curl -X GET "http://localhost:6501/api/budgets/status" \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

**详细测试场景：** 查看 [PHASE_3_COMPLETION_REPORT.md](PHASE_3_COMPLETION_REPORT.md)

---

### 测试数据导出（Phase 4）✨

#### 导出交易数据（CSV）
```bash
curl -X GET "http://localhost:6501/api/export/transactions/csv?start_date=2025-12-01&end_date=2025-12-31" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -o transactions.csv
```

#### 导出交易数据（Excel 多工作表）
```bash
curl -X GET "http://localhost:6501/api/export/transactions/excel?start_date=2025-12-01&end_date=2025-12-31" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -o transactions.xlsx
```

#### 导出预算状态
```bash
curl -X GET "http://localhost:6501/api/export/budgets/excel" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -o budgets.xlsx
```

#### 导出月度报告
```bash
curl -X GET "http://localhost:6501/api/export/monthly-report/csv?year=2025&month=12" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -o monthly_report.csv
```

**详细测试场景：** 查看 [PHASE_4_COMPLETION_REPORT.md](PHASE_4_COMPLETION_REPORT.md)

---

## 📱 使用前端界面测试

### 选项 1：Swagger UI（推荐）
1. 打开浏览器：http://localhost:6501/docs
2. 点击右上角 "Authorize" 按钮
3. 输入 Token：`Bearer <YOUR_TOKEN>`
4. 点击 "Authorize"
5. 测试所有端点

### 选项 2：Admin Dashboard
1. 打开浏览器：http://localhost:6502
2. 登录：admin / password123
3. 打开浏览器开发者工具（F12）
4. 在 Console 中测试 API

---

## 🛠️ 常用命令

### 查看日志
```bash
# 查看所有日志
docker-compose logs

# 查看后端日志
docker-compose logs backend

# 实时查看日志
docker-compose logs -f backend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启后端
docker-compose restart backend
```

### 停止系统
```bash
docker-compose down
```

### 完全重置（删除数据）
```bash
docker-compose down -v
docker-compose up -d
```

---

## 🔍 健康检查

### 检查后端健康
```bash
curl http://localhost:6501/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "All systems operational"
}
```

### 检查 IMAP 邮件监听器
```bash
curl http://localhost:6501/api/email/listener/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "message": "IMAP connection successful"
}
```

---

## 📊 数据库直接查询

### 查看所有预算
```bash
docker exec familycfo_db psql -U admin -d family_cfo -c "SELECT * FROM budgets;"
```

### 查看本月交易
```bash
docker exec familycfo_db psql -U admin -d family_cfo -c "
  SELECT date, merchant, amount, category
  FROM transactions
  WHERE date >= date_trunc('month', CURRENT_DATE)
  ORDER BY date DESC
  LIMIT 20;
"
```

### 查看数据库迁移历史
```bash
docker exec familycfo_backend alembic history
```

---

## 🧪 OCR 测试

### 上传收据图片
```bash
curl -X POST "http://localhost:6501/api/upload/receipt" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -F "file=@/path/to/receipt.jpg"
```

**支持的图片格式：** JPG, PNG, PDF

---

## 📧 Telegram 通知测试

### 手动发送测试消息
```bash
curl -X POST "http://localhost:6501/api/monitoring/test-telegram"
```

**查看 Telegram：** 应该收到测试消息

---

## 🗂️ 文档索引

| 文档 | 内容 | 文件大小 |
|------|------|---------|
| **ALL_PHASES_COMPLETION_SUMMARY.md** | 全阶段总结 | 12 KB |
| **FINAL_PROJECT_SUMMARY.md** | 项目总结 | 15 KB |
| **PHASE_3_COMPLETION_REPORT.md** | 预算管理测试指南 | 13 KB |
| **PHASE_4_COMPLETION_REPORT.md** | 数据导出测试指南 | 11 KB |
| **IMPLEMENTATION_PROGRESS.md** | Phase 1 & 2 报告 | 15 KB |
| **PROJECT_REVIEW_REPORT.md** | 完整项目审查 | 60+ KB |
| **QUICK_START_GUIDE.md** | 本文档 | - |

---

## 🐛 故障排除

### 问题 1：容器启动失败
**症状：** `docker-compose up -d` 报错

**解决：**
```bash
# 停止所有容器
docker-compose down

# 删除旧卷（警告：会删除数据）
docker-compose down -v

# 重新启动
docker-compose up -d
```

---

### 问题 2：数据库连接失败
**症状：** 后端日志显示数据库连接错误

**解决：**
```bash
# 检查数据库容器
docker-compose ps database

# 查看数据库日志
docker-compose logs database

# 重启数据库
docker-compose restart database
```

---

### 问题 3：Token 过期
**症状：** API 返回 401 Unauthorized

**解决：** 重新登录获取新 Token
```bash
curl -X POST "http://localhost:6501/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

---

### 问题 4：端口被占用
**症状：** `Bind for 0.0.0.0:6501 failed: port is already allocated`

**解决：**
```bash
# Windows
netstat -ano | findstr :6501

# macOS/Linux
lsof -i :6501

# 修改 docker-compose.yml 中的端口映射
```

---

## 🔐 安全配置

### 生产环境建议
1. **修改默认密码**
   ```bash
   # 在容器中运行
   docker exec -it familycfo_backend python
   >>> from passlib.context import CryptContext
   >>> pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   >>> print(pwd_context.hash("your_new_password"))
   ```

2. **配置 HTTPS**
   - 使用 Nginx 反向代理
   - 申请 SSL 证书（Let's Encrypt）

3. **限制 CORS**
   - 修改 `backend/main.py` 中的 `origins` 列表

4. **启用防火墙**
   - 仅开放必要端口

---

## 📞 获取帮助

### 查看实时日志
```bash
docker-compose logs -f backend
```

### 进入容器调试
```bash
# 进入后端容器
docker exec -it familycfo_backend bash

# 进入数据库容器
docker exec -it familycfo_db bash
```

### API 文档
http://localhost:6501/docs

---

## 🎯 下一步

### 已完成功能（92%）
- ✅ 预算管理系统
- ✅ 数据导出功能
- ✅ OCR 收据扫描
- ✅ AI 交易分类
- ✅ IMAP 邮件监听
- ✅ Telegram 通知

### 待开发功能（8%）
- [ ] 预算管理前端页面
- [ ] 数据导出前端界面
- [ ] 生产环境部署脚本

---

## ✨ 特色功能

### 1. OCR 收据扫描
- 支持 JPG/PNG/PDF
- AI 提取商家、金额、日期
- 自动分类
- 文件存档

### 2. IMAP 邮件监听
- 自动检测邮件收据
- 附件下载和 OCR
- 自动创建交易

### 3. 智能分类
- 139 条商家规则
- AI 备用分类
- 14 主分类 + 40+ 子分类

### 4. Telegram 通知
- 交易创建通知
- 预算超支告警
- 系统状态通知

### 5. 预算管理
- 自动计算月度支出
- 超支告警（自定义阈值）
- 软删除机制

### 6. 数据导出
- CSV/Excel 双格式
- 多工作表汇总
- 月度财务报告

---

**快速开始指南完成！** ✅
**开始探索您的家庭财务管理系统吧！** 🚀

---

**最后更新：** 2025-12-30 13:00 PST
