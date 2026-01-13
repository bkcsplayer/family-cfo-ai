#!/bin/bash
#
# Family CFO One-Click Deployment Script
# Deploys the complete system to production environment
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/familycfo"
BACKUP_DIR="/backup/familycfo"
CURRENT_DIR=$(pwd)

echo "========================================================"
echo "🚀 Family CFO Production Deployment"
echo "========================================================"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# 1. Check prerequisites
print_info "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { print_error "Docker not found! Please install Docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { print_error "Docker Compose not found! Please install Docker Compose first."; exit 1; }
print_success "Prerequisites OK"

# 2. Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root or with sudo"
    exit 1
fi

# 3. Create installation directory
print_info "Creating directories..."
mkdir -p "$INSTALL_DIR"/{scripts,backups/database,backups/uploads,logs}
mkdir -p "$BACKUP_DIR"
print_success "Directories created"

# 4. Copy files to installation directory
print_info "Copying project files..."
cp -r "$CURRENT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
cd "$INSTALL_DIR"
print_success "Files copied"

# 5. Check environment file
if [ ! -f .env.production ]; then
    print_warning ".env.production not found!"
    if [ -f .env ]; then
        print_info "Using existing .env file"
    else
        print_error "No environment file found! Please create .env.production first."
        print_info "Template available at: .env.production.example"
        exit 1
    fi
else
    print_info "Using .env.production"
    cp .env.production .env
fi

# 6. Make scripts executable
print_info "Setting up scripts..."
chmod +x scripts/*.sh
print_success "Scripts configured"

# 7. Pull Docker images
print_info "Pulling Docker images (this may take a while)..."
docker-compose -f docker-compose.prod.yml pull
print_success "Images pulled"

# 8. Build and start services
print_info "Building and starting services..."
docker-compose -f docker-compose.prod.yml up -d --build
print_success "Services started"

# 9. Wait for services to be ready
print_info "Waiting for services to be ready (60 seconds)..."
sleep 60

# 10. Health check
print_info "Running health checks..."
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:6501/health > /dev/null 2>&1; then
        print_success "Backend health check passed"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Backend health check failed after $MAX_RETRIES attempts"
        print_info "Check logs with: docker-compose -f docker-compose.prod.yml logs backend"
        exit 1
    fi
    print_info "Waiting for backend... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 10
done

# 11. Configure systemd service
print_info "Configuring systemd service..."
cp scripts/familycfo.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable familycfo
systemctl start familycfo
print_success "Systemd service configured"

# 12. Set up cron jobs
print_info "Setting up cron jobs..."
# Backup every day at 2 AM
(crontab -l 2>/dev/null | grep -v "familycfo/scripts/backup.sh"; echo "0 2 * * * $INSTALL_DIR/scripts/backup.sh >> $INSTALL_DIR/logs/backup.log 2>&1") | crontab -
# Health check every hour
(crontab -l 2>/dev/null | grep -v "familycfo/scripts/health_check.sh"; echo "0 * * * * $INSTALL_DIR/scripts/health_check.sh >> $INSTALL_DIR/logs/health.log 2>&1") | crontab -
print_success "Cron jobs configured"

# 13. Get system IP
SYSTEM_IP=$(hostname -I | awk '{print $1}')

# 14. Final status
echo ""
echo "========================================================"
print_success "Deployment completed successfully!"
echo "========================================================"
echo ""
echo "📊 System Information:"
echo "   Installation directory: $INSTALL_DIR"
echo "   Backup directory: $BACKUP_DIR"
echo ""
echo "🌐 Access URLs:"
echo "   Backend API:    http://$SYSTEM_IP:6501"
echo "   Admin Dashboard: http://$SYSTEM_IP:6502"
echo "   Mobile App:     http://$SYSTEM_IP:6503"
echo "   API Docs:       http://$SYSTEM_IP:6501/docs"
echo ""
echo "🔧 Management Commands:"
echo "   Start:   systemctl start familycfo"
echo "   Stop:    systemctl stop familycfo"
echo "   Restart: systemctl restart familycfo"
echo "   Status:  systemctl status familycfo"
echo "   Logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "💾 Backup:"
echo "   Manual backup: $INSTALL_DIR/scripts/backup.sh"
echo "   Auto backup:   Daily at 2:00 AM"
echo "   Location:      $BACKUP_DIR"
echo ""
echo "🏥 Health Check:"
echo "   Manual check:  $INSTALL_DIR/scripts/health_check.sh"
echo "   Auto check:    Every hour"
echo ""
print_warning "Remember to:"
echo "   1. Change default passwords in .env"
echo "   2. Configure firewall rules"
echo "   3. Set up external backups"
echo "   4. Test the system thoroughly"
echo ""
echo "========================================================"
