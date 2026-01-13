# Family CFO - Docker Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Quick Start

### 1. Clone and Configure

```bash
git clone <repository-url>
cd familyltdcfo

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Build and Start

```bash
# Build all images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 3. Access Applications

- **Mobile App:** http://localhost:6503
- **Admin Dashboard:** http://localhost:6502
- **API Documentation:** http://localhost:6501/docs
- **Database:** localhost:6500

**Default Login:** admin / password123

## Service Management

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f admin
docker compose logs -f frontend
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart backend
```

### Stop Services

```bash
# Stop all
docker compose stop

# Stop and remove
docker compose down

# Stop and remove with volumes (WARNING: deletes data)
docker compose down -v
```

## Database Management

### Backup Database

```bash
docker exec familycfo_db pg_dump -U admin family_cfo > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
cat backup_20251228.sql | docker exec -i familycfo_db psql -U admin -d family_cfo
```

### Access Database

```bash
docker exec -it familycfo_db psql -U admin -d family_cfo
```

## Deployment to Jetson Nano

### 1. Prepare Jetson

```bash
# SSH to Jetson
ssh user@jetson-nano.local

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### 2. Transfer Files

```bash
# From your development machine
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  familyltdcfo/ user@jetson-nano.local:~/familyltdcfo/
```

### 3. Deploy

```bash
# On Jetson
cd ~/familyltdcfo

# Configure environment
cp .env.example .env
nano .env

# Build and start
docker compose up -d

# Enable auto-start
sudo systemctl enable docker
```

## Environment Variables

### Required

```env
# Database
DATABASE_URL=postgresql://admin:password123@database:5432/family_cfo

# AI Service
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_USER_ID=your_user_id_here

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_password_here
```

### Optional

```env
# Feature Flags
TELEGRAM_NOTIFICATIONS_ENABLED=true
EMAIL_NOTIFICATIONS_ENABLED=true
TELEGRAM_NOTIFY_NEW_TRANSACTIONS=true
TELEGRAM_NOTIFY_LARGE_EXPENSES=true
TELEGRAM_LARGE_EXPENSE_THRESHOLD=500.00
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker compose logs backend

# Common issues:
# 1. Database not ready - wait 10 seconds and restart
docker compose restart backend

# 2. Missing environment variables - check .env
docker compose config
```

### Frontend shows blank page

```bash
# Rebuild frontend
docker compose build admin frontend
docker compose up -d admin frontend

# Check nginx logs
docker compose logs admin
docker compose logs frontend
```

### Database connection failed

```bash
# Check database is running
docker compose ps database

# Test connection
docker exec familycfo_db pg_isready -U admin

# Restart database
docker compose restart database
```

## Performance Tuning

### For Jetson Nano (4GB RAM)

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Enable Swap (if needed)

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Monitoring

### Health Checks

```bash
# Check all services
curl http://localhost:6501/health
curl http://localhost:6502
curl http://localhost:6503
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose build
docker compose up -d
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup (WARNING: removes everything)
docker system prune -a --volumes
```

## Security

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Use strong database password
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable Docker security scanning
- [ ] Review CORS settings
- [ ] Disable debug mode

### SSL/HTTPS Setup

Use nginx-proxy or Traefik for automatic SSL:

```bash
# Example with Let's Encrypt
docker run -d -p 80:80 -p 443:443 \
  --name nginx-proxy \
  -v /var/run/docker.sock:/tmp/docker.sock:ro \
  nginxproxy/nginx-proxy

docker run -d \
  --name nginx-proxy-acme \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --volumes-from nginx-proxy \
  nginxproxy/acme-companion
```

## Support

For issues and questions:
- Check logs: `docker compose logs`
- Review documentation in `docs/`
- Open issue on GitHub

## License

MIT
