# 📋 Phase 6 执行计划：生产环境部署

**计划日期：** 2025-12-30
**预计进度提升：** 97% → 100% (+3%)
**优先级：** 高 🔥
**部署目标：** Jetson Nano（Ubuntu 20.04 ARM64）

---

## 🎯 Phase 6 目标

将 Family Inc. CFO 系统部署到生产环境，实现自动启动、数据备份、监控告警等生产级特性。

---

## 📅 执行步骤

### Step 6.1: 生产环境 Docker Compose 配置 (30%)
**预计时间：** 30-45 分钟
**进度提升：** +1%

#### 任务清单
- [ ] 创建 `docker-compose.prod.yml`
- [ ] 配置生产环境变量
- [ ] 优化资源限制（适配 Jetson Nano）
- [ ] 配置重启策略（`restart: always`）
- [ ] 设置健康检查增强
- [ ] 配置日志驱动和大小限制

#### 技术要点
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  database:
    restart: always
    mem_limit: 512m
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      interval: 30s
      timeout: 5s
      retries: 3

  backend:
    restart: always
    mem_limit: 1g
    environment:
      - LOG_LEVEL=INFO
      - ENABLE_METRICS=true
```

---

### Step 6.2: 自动启动脚本 (20%)
**预计时间：** 20-30 分钟
**进度提升：** +0.6%

#### 任务清单
- [ ] 创建 systemd 服务文件
- [ ] 配置开机自启动
- [ ] 添加服务管理脚本
- [ ] 测试重启后自动启动

#### 实现方案
```bash
# /etc/systemd/system/familycfo.service
[Unit]
Description=Family CFO Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/familycfo
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

---

### Step 6.3: 数据备份系统 (30%)
**预计时间：** 30-40 分钟
**进度提升：** +0.9%

#### 任务清单
- [ ] 创建数据库备份脚本
- [ ] 配置定时备份（cron）
- [ ] 实现备份保留策略（7天本地 + 30天远程）
- [ ] 添加备份状态 Telegram 通知
- [ ] 测试恢复流程

#### 备份策略
```bash
# backup.sh
#!/bin/bash
BACKUP_DIR="/backup/familycfo"
DATE=$(date +%Y%m%d_%H%M%S)

# 数据库备份
docker exec familycfo_db pg_dump -U admin family_cfo > \
  $BACKUP_DIR/db_backup_$DATE.sql

# 上传文件备份
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz backend/uploads/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

# Telegram 通知
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
  -d chat_id=$CHAT_ID \
  -d text="✅ Backup completed: $DATE"
```

**Cron 配置：**
```cron
# 每天凌晨2点备份
0 2 * * * /opt/familycfo/scripts/backup.sh
```

---

### Step 6.4: 监控和告警 (10%)
**预计时间：** 15-20 分钟
**进度提升：** +0.3%

#### 任务清单
- [ ] 创建健康检查脚本
- [ ] 配置容器状态监控
- [ ] 设置磁盘空间告警
- [ ] 配置 Telegram 告警通知
- [ ] 添加性能监控（可选）

#### 监控脚本
```bash
# health_check.sh
#!/bin/bash

# 检查容器状态
UNHEALTHY=$(docker ps --filter "health=unhealthy" -q)
if [ ! -z "$UNHEALTHY" ]; then
  # 发送 Telegram 告警
  curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d chat_id=$CHAT_ID \
    -d text="⚠️ Unhealthy containers detected!"
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
  # 发送告警
  curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d chat_id=$CHAT_ID \
    -d text="⚠️ Disk usage: ${DISK_USAGE}%"
fi
```

**Cron 配置：**
```cron
# 每小时检查一次
0 * * * * /opt/familycfo/scripts/health_check.sh
```

---

### Step 6.5: 日志管理系统 (5%)
**预计时间：** 10-15 分钟
**进度提升：** +0.15%

#### 任务清单
- [ ] 配置日志轮转
- [ ] 设置日志保留策略
- [ ] 添加日志清理脚本
- [ ] 配置日志级别（生产环境）

#### 日志配置
```yaml
# docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    compress: "true"
```

---

### Step 6.6: 安全加固 (3%)
**预计时间：** 10 分钟
**进度提升：** +0.09%

#### 任务清单
- [ ] 修改默认端口（可选）
- [ ] 配置防火墙规则
- [ ] 限制数据库外部访问
- [ ] 启用 HTTPS（可选，使用 Nginx 反向代理）

#### 防火墙配置
```bash
# 仅允许本地访问数据库
sudo ufw allow 6501/tcp  # Backend API
sudo ufw allow 6502/tcp  # Admin Dashboard
sudo ufw allow 6503/tcp  # Mobile App
sudo ufw deny 6500/tcp   # Database (内部访问)
```

---

### Step 6.7: 部署文档和脚本 (2%)
**预计时间：** 5-10 分钟
**进度提升：** +0.06%

#### 任务清单
- [ ] 创建一键部署脚本
- [ ] 编写生产部署文档
- [ ] 创建故障恢复手册
- [ ] 准备迁移检查清单

---

## 🛠️ 技术实现细节

### 1. 生产环境目录结构

```
/opt/familycfo/
├── docker-compose.prod.yml    生产环境配置
├── .env.production            生产环境变量
├── scripts/
│   ├── deploy.sh             一键部署脚本
│   ├── backup.sh             数据库备份脚本
│   ├── restore.sh            数据恢复脚本
│   ├── health_check.sh       健康检查脚本
│   └── cleanup.sh            日志清理脚本
├── backups/
│   ├── database/             数据库备份
│   └── uploads/              文件备份
└── logs/
    ├── backend.log           后端日志
    ├── database.log          数据库日志
    └── system.log            系统日志
```

---

### 2. 一键部署脚本

```bash
#!/bin/bash
# deploy.sh - 一键部署到生产环境

set -e

echo "🚀 Starting Family CFO deployment..."

# 1. 检查环境
echo "📋 Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker not found!"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose not found!"; exit 1; }

# 2. 创建目录
echo "📁 Creating directories..."
sudo mkdir -p /opt/familycfo/{scripts,backups/database,backups/uploads,logs}
sudo mkdir -p /backup/familycfo

# 3. 复制文件
echo "📦 Copying files..."
sudo cp -r . /opt/familycfo/
cd /opt/familycfo

# 4. 配置环境变量
if [ ! -f .env.production ]; then
    echo "⚠️  .env.production not found! Please create it first."
    exit 1
fi
cp .env.production .env

# 5. 拉取镜像
echo "🐳 Pulling Docker images..."
docker-compose -f docker-compose.prod.yml pull

# 6. 启动服务
echo "🎬 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 7. 等待服务就绪
echo "⏳ Waiting for services to be ready..."
sleep 30

# 8. 健康检查
echo "🏥 Running health checks..."
curl -f http://localhost:6501/health || { echo "Backend health check failed!"; exit 1; }

# 9. 配置 systemd 服务
echo "⚙️  Configuring systemd service..."
sudo cp scripts/familycfo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable familycfo
sudo systemctl start familycfo

# 10. 配置 cron 任务
echo "⏰ Setting up cron jobs..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/familycfo/scripts/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 * * * * /opt/familycfo/scripts/health_check.sh") | crontab -

echo "✅ Deployment completed successfully!"
echo "🌐 Access the application at:"
echo "   Backend: http://$(hostname -I | awk '{print $1}'):6501"
echo "   Admin: http://$(hostname -I | awk '{print $1}'):6502"
echo "   Mobile: http://$(hostname -I | awk '{print $1}'):6503"
```

---

### 3. 环境变量模板

```bash
# .env.production

# Database
DATABASE_URL=postgresql://admin:CHANGE_THIS_PASSWORD@database:5432/family_cfo
POSTGRES_USER=admin
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
POSTGRES_DB=family_cfo

# AI Services
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Telegram (Required for alerts)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_USER_ID=your_user_id_here
TELEGRAM_NOTIFICATIONS_ENABLED=true

# Email
SMTP_HOST=server.cloudcone.email
SMTP_PORT=587
SMTP_USERNAME=receipe@khtain.com
SMTP_PASSWORD=your_password_here
EMAIL_FROM_ADDRESS=receipe@khtain.com
EMAIL_NOTIFICATIONS_ENABLED=true

# IMAP
IMAP_HOST=server.cloudcone.email
IMAP_PORT=993
IMAP_USERNAME=receipe@khtain.com
IMAP_PASSWORD=your_password_here
IMAP_LISTENER_ENABLED=true
IMAP_CHECK_INTERVAL=300

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENABLE_SCHEDULED_TASKS=true

# Backup
BACKUP_RETENTION_DAYS=7
REMOTE_BACKUP_ENABLED=false
```

---

### 4. Jetson Nano 优化配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  database:
    image: postgres:15-alpine
    restart: always
    mem_limit: 512m           # Jetson Nano 内存限制
    cpus: 1.0                 # CPU 限制
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 30s
      timeout: 5s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    mem_limit: 1g             # 后端内存限制
    cpus: 2.0
    depends_on:
      database:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=INFO
    volumes:
      - ./backend/uploads:/app/uploads
    ports:
      - "6501:6501"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6501/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
    driver: local
```

---

## 🧪 测试计划

### 部署前测试
- [ ] 在测试环境验证所有脚本
- [ ] 测试备份和恢复流程
- [ ] 验证健康检查正常工作
- [ ] 测试自动重启机制

### 部署后验证
- [ ] 所有容器正常运行
- [ ] API 端点可访问
- [ ] 前端页面加载正常
- [ ] 数据库连接正常
- [ ] 定时任务正常执行
- [ ] Telegram 通知正常

### 压力测试（可选）
- [ ] 模拟大量交易导入
- [ ] 测试并发用户访问
- [ ] 验证内存使用在限制范围内

---

## 📊 进度里程碑

| Step | 任务 | 预计时间 | 进度提升 | 累计进度 |
|------|------|---------|---------|---------|
| 6.1 | 生产环境配置 | 30-45m | +1% | 98% |
| 6.2 | 自动启动脚本 | 20-30m | +0.6% | 98.6% |
| 6.3 | 数据备份系统 | 30-40m | +0.9% | 99.5% |
| 6.4 | 监控和告警 | 15-20m | +0.3% | 99.8% |
| 6.5 | 日志管理 | 10-15m | +0.15% | 99.95% |
| 6.6 | 安全加固 | 10m | +0.09% | 99.94% |
| 6.7 | 部署文档 | 5-10m | +0.06% | 100% |

**总计：** 97% → 100% (+3%)

---

## 🎯 验收标准

### 系统稳定性
- ✅ 重启后自动启动所有服务
- ✅ 容器崩溃后自动重启
- ✅ 健康检查异常自动告警

### 数据安全
- ✅ 每日自动备份数据库
- ✅ 备份文件正确保留7天
- ✅ 恢复流程验证通过

### 监控告警
- ✅ 容器异常 Telegram 通知
- ✅ 磁盘空间告警正常
- ✅ 备份状态通知正常

### 性能指标
- ✅ 内存使用 < 2GB（总计）
- ✅ API 响应时间 < 500ms
- ✅ 系统运行稳定 > 24小时

---

## 💡 Jetson Nano 特殊考虑

### 硬件限制
- **CPU：** 4核 ARM Cortex-A57
- **内存：** 4GB LPDDR4
- **存储：** MicroSD 卡（建议使用 SSD）

### 优化建议
1. **使用 ARM 优化镜像**
   - postgres:15-alpine（ARM64）
   - python:3.11-slim（ARM64）

2. **限制资源使用**
   - 数据库：512MB RAM
   - 后端：1GB RAM
   - 前端：静态文件，几乎无需资源

3. **减少日志大小**
   - 最大10MB每个日志文件
   - 最多保留3个旧文件

4. **使用 SSD 存储**
   - 数据库性能提升10倍
   - 减少 SD 卡磨损

---

## 🚀 执行顺序

### 阶段1：准备工作
1. 创建生产环境配置文件
2. 准备环境变量
3. 编写部署脚本

### 阶段2：核心功能
4. 配置自动启动
5. 实现数据备份
6. 设置监控告警

### 阶段3：优化和文档
7. 配置日志管理
8. 安全加固
9. 编写部署文档

---

## 📝 文件清单

### 新增文件
```
docker-compose.prod.yml           生产环境 Docker Compose
.env.production.example           环境变量模板
scripts/deploy.sh                 一键部署脚本
scripts/backup.sh                 数据库备份脚本
scripts/restore.sh                数据恢复脚本
scripts/health_check.sh           健康检查脚本
scripts/cleanup.sh                日志清理脚本
scripts/familycfo.service         Systemd 服务文件
DEPLOYMENT_GUIDE.md               部署指南
MAINTENANCE_GUIDE.md              维护手册
```

---

## 🎨 运维管理命令

### 服务管理
```bash
# 启动服务
sudo systemctl start familycfo

# 停止服务
sudo systemctl stop familycfo

# 重启服务
sudo systemctl restart familycfo

# 查看状态
sudo systemctl status familycfo

# 查看日志
sudo journalctl -u familycfo -f
```

### Docker 管理
```bash
# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend

# 更新镜像
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 备份管理
```bash
# 手动备份
/opt/familycfo/scripts/backup.sh

# 恢复数据库
/opt/familycfo/scripts/restore.sh /backup/familycfo/db_backup_20251230.sql

# 查看备份列表
ls -lh /backup/familycfo/
```

---

**Phase 6 执行计划完成！**
**准备开始部署到生产环境？** 🚀
