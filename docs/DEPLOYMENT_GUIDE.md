# 🚀 Family Inc. CFO - 生产环境部署指南

**版本：** 1.0.0
**更新日期：** 2025-12-30
**目标平台：** Jetson Nano (Ubuntu 20.04 ARM64) / 通用 Linux

---

## 📋 目录

1. [部署前准备](#部署前准备)
2. [一键部署](#一键部署)
3. [手动部署步骤](#手动部署步骤)
4. [配置说明](#配置说明)
5. [验证部署](#验证部署)
6. [故障排除](#故障排除)
7. [维护操作](#维护操作)

---

## 🔧 部署前准备

### 硬件要求

**最低配置：**
- CPU: 4核 ARM Cortex-A57 或更高
- 内存: 4GB RAM
- 存储: 32GB（推荐使用 SSD）
- 网络: 以太网或 Wi-Fi

**推荐配置：**
- CPU: 6核或更高
- 内存: 8GB RAM
- 存储: 64GB SSD
- 网络: 千兆以太网

### 软件要求

- **操作系统：** Ubuntu 20.04 LTS (ARM64) 或更新版本
- **Docker：** 20.10+
- **Docker Compose：** 2.0+
- **Git：** 2.25+（用于获取代码）

### 安装 Docker 和 Docker Compose

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose -y

# 验证安装
docker --version
docker-compose --version
```

---

## ⚡ 一键部署

### 步骤 1：下载项目

```bash
# 克隆项目（或通过其他方式获取代码）
git clone <your-repo-url> /tmp/familycfo
cd /tmp/familycfo
```

### 步骤 2：配置环境变量

```bash
# 复制环境变量模板
cp .env.production.example .env.production

# 编辑环境变量（重要！）
nano .env.production
```

**必须修改的配置项：**
```bash
# 数据库密码（生成强密码）
POSTGRES_PASSWORD=<强密码>
DATABASE_URL=postgresql://admin:<强密码>@database:5432/family_cfo

# JWT 密钥（生成随机密钥）
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Telegram 配置
TELEGRAM_BOT_TOKEN=<你的bot token>
TELEGRAM_ADMIN_USER_ID=<你的user id>

# OpenRouter AI 配置
OPENROUTER_API_KEY=<你的API密钥>

# 邮件配置
SMTP_PASSWORD=<SMTP密码>
IMAP_PASSWORD=<IMAP密码>
```

### 步骤 3：执行一键部署

```bash
# 给部署脚本执行权限
chmod +x scripts/deploy.sh

# 执行部署（需要 sudo）
sudo ./scripts/deploy.sh
```

**部署过程约需 5-10 分钟，将自动完成：**
- ✅ 检查系统要求
- ✅ 创建目录结构
- ✅ 拉取 Docker 镜像
- ✅ 启动所有服务
- ✅ 配置自动启动
- ✅ 设置定时任务

---

## 🔨 手动部署步骤

如果一键部署失败或需要自定义，可以按以下步骤手动部署：

### 1. 创建目录

```bash
sudo mkdir -p /opt/familycfo/{scripts,backups,logs}
sudo mkdir -p /backup/familycfo
```

### 2. 复制文件

```bash
sudo cp -r . /opt/familycfo/
cd /opt/familycfo
```

### 3. 配置环境

```bash
sudo cp .env.production.example .env.production
sudo nano .env.production
sudo cp .env.production .env
```

### 4. 启动服务

```bash
# 拉取镜像
sudo docker-compose -f docker-compose.prod.yml pull

# 构建并启动
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 查看日志
sudo docker-compose -f docker-compose.prod.yml logs -f
```

### 5. 配置 Systemd

```bash
sudo cp scripts/familycfo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable familycfo
sudo systemctl start familycfo
```

### 6. 配置 Cron 任务

```bash
# 编辑 crontab
sudo crontab -e

# 添加以下行
0 2 * * * /opt/familycfo/scripts/backup.sh >> /opt/familycfo/logs/backup.log 2>&1
0 * * * * /opt/familycfo/scripts/health_check.sh >> /opt/familycfo/logs/health.log 2>&1
```

---

## ⚙️ 配置说明

### 环境变量详解

#### 数据库配置
```bash
DATABASE_URL=postgresql://admin:password@database:5432/family_cfo
POSTGRES_USER=admin              # 数据库用户名
POSTGRES_PASSWORD=password123     # 数据库密码（必须修改）
POSTGRES_DB=family_cfo           # 数据库名称
```

#### AI 服务配置
```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxx  # OpenRouter API 密钥
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

#### 通知配置
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF  # Bot token
TELEGRAM_ADMIN_USER_ID=123456789   # 管理员 User ID
TELEGRAM_NOTIFICATIONS_ENABLED=true
```

#### 邮件配置
```bash
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=password

IMAP_HOST=imap.example.com
IMAP_PORT=993
IMAP_USERNAME=user@example.com
IMAP_PASSWORD=password
IMAP_LISTENER_ENABLED=true
```

---

## ✅ 验证部署

### 1. 检查容器状态

```bash
docker ps
```

**预期输出：** 4个容器运行中（database, backend, admin, mobile）

### 2. 测试 API

```bash
# 健康检查
curl http://localhost:6501/health

# 预期响应
{
  "status": "healthy",
  "database": "connected",
  "message": "All systems operational"
}
```

### 3. 访问前端

打开浏览器访问：
- **Admin Dashboard：** `http://<IP地址>:6502`
- **Mobile App：** `http://<IP地址>:6503`
- **API Docs：** `http://<IP地址>:6501/docs`

默认登录凭据：
- 用户名：`admin`
- 密码：`password123` （请立即修改！）

### 4. 测试备份

```bash
sudo /opt/familycfo/scripts/backup.sh
```

检查备份文件：
```bash
ls -lh /backup/familycfo/database/
```

### 5. 测试健康检查

```bash
sudo /opt/familycfo/scripts/health_check.sh
```

---

## 🐛 故障排除

### 问题 1：容器无法启动

**症状：** `docker-compose up` 失败

**解决步骤：**
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs

# 检查端口占用
sudo netstat -tulpn | grep 650

# 清理并重启
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### 问题 2：数据库连接失败

**症状：** Backend 日志显示数据库连接错误

**解决步骤：**
```bash
# 检查数据库容器
docker logs familycfo_db_prod

# 进入数据库容器测试
docker exec -it familycfo_db_prod psql -U admin -d family_cfo

# 检查环境变量
docker exec familycfo_backend_prod env | grep DATABASE
```

### 问题 3：内存不足

**症状：** 容器被 OOM Killer 杀死

**解决步骤：**
```bash
# 检查内存使用
docker stats

# 调整内存限制（编辑 docker-compose.prod.yml）
# 减少 mem_limit 值

# 启用 swap（如果未启用）
sudo swapon --show
```

### 问题 4：磁盘空间不足

**症状：** 磁盘使用率 > 90%

**解决步骤：**
```bash
# 运行清理脚本
sudo /opt/familycfo/scripts/cleanup.sh

# 手动清理 Docker
sudo docker system prune -a --volumes

# 检查大文件
sudo du -sh /opt/familycfo/* | sort -h
```

---

## 🔧 维护操作

### 日常维护

#### 查看日志
```bash
# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 系统日志
sudo journalctl -u familycfo -f
```

#### 重启服务
```bash
# 重启所有服务
sudo systemctl restart familycfo

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart backend
```

#### 更新系统
```bash
cd /opt/familycfo

# 拉取最新镜像
docker-compose -f docker-compose.prod.yml pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 清理旧镜像
docker image prune -a
```

### 备份管理

#### 手动备份
```bash
sudo /opt/familycfo/scripts/backup.sh
```

#### 查看备份
```bash
ls -lh /backup/familycfo/database/
ls -lh /backup/familycfo/uploads/
```

#### 恢复数据库
```bash
sudo /opt/familycfo/scripts/restore.sh /backup/familycfo/database/db_backup_20251230_140000.sql.gz
```

### 监控

#### 查看系统状态
```bash
# 容器状态
docker ps

# 资源使用
docker stats

# 磁盘空间
df -h

# 内存使用
free -h
```

#### 健康检查
```bash
sudo /opt/familycfo/scripts/health_check.sh
```

---

## 🔒 安全建议

### 必做项
1. ✅ 修改默认密码（数据库、JWT密钥）
2. ✅ 配置防火墙规则
3. ✅ 使用强密码
4. ✅ 定期更新系统
5. ✅ 启用自动备份

### 推荐项
1. 🔐 配置 HTTPS（使用 Nginx 反向代理）
2. 🔐 限制数据库外部访问
3. 🔐 配置 fail2ban 防止暴力破解
4. 🔐 定期审查日志
5. 🔐 备份到远程位置

### 防火墙配置
```bash
# 安装 UFW
sudo apt install ufw -y

# 允许必要端口
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 6501/tcp   # Backend
sudo ufw allow 6502/tcp   # Admin
sudo ufw allow 6503/tcp   # Mobile

# 拒绝数据库端口（仅内部访问）
sudo ufw deny 6500/tcp

# 启用防火墙
sudo ufw enable
```

---

## 📞 获取帮助

### 日志位置
- **应用日志：** `/opt/familycfo/logs/`
- **Docker 日志：** `docker-compose logs`
- **系统日志：** `journalctl -u familycfo`
- **备份日志：** `/opt/familycfo/logs/backup.log`

### 常用命令速查

| 操作 | 命令 |
|------|------|
| 启动服务 | `sudo systemctl start familycfo` |
| 停止服务 | `sudo systemctl stop familycfo` |
| 重启服务 | `sudo systemctl restart familycfo` |
| 查看状态 | `sudo systemctl status familycfo` |
| 查看日志 | `docker-compose logs -f` |
| 备份数据 | `sudo /opt/familycfo/scripts/backup.sh` |
| 健康检查 | `sudo /opt/familycfo/scripts/health_check.sh` |
| 清理空间 | `sudo /opt/familycfo/scripts/cleanup.sh` |

---

## 🎉 部署完成检查清单

部署完成后，请确认以下项目：

- [ ] 所有4个容器正常运行
- [ ] Backend API 响应正常（`/health`）
- [ ] Admin Dashboard 可访问
- [ ] Mobile App 可访问
- [ ] 可以成功登录
- [ ] 数据库连接正常
- [ ] 备份脚本正常工作
- [ ] Telegram 通知正常
- [ ] 定时任务已配置
- [ ] Systemd 服务已启用
- [ ] 防火墙规则已配置
- [ ] 已修改默认密码
- [ ] 日志正常记录

---

**部署指南完成！** ✅
**祝您使用愉快！** 🚀

**最后更新：** 2025-12-30
