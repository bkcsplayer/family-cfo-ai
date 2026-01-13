#!/bin/bash
#
# Family CFO Health Check Script
# Monitors container health, disk space, and sends alerts
#

set -e

# Configuration
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_ADMIN_USER_ID}"
DISK_WARNING_THRESHOLD=85
DISK_CRITICAL_THRESHOLD=95
MEMORY_WARNING_THRESHOLD=90

# Function to send Telegram notification
send_telegram() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_CHAT_ID}" \
            -d text="${message}" \
            -d parse_mode="Markdown" > /dev/null 2>&1 || true
    fi
}

# Initialize status
ALL_HEALTHY=true
ALERTS=()

# 1. Check container health status
echo "🏥 Checking container health..."
UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null)
if [ -n "$UNHEALTHY" ]; then
    ALL_HEALTHY=false
    ALERTS+=("⚠️ *Unhealthy Containers:*\n\`$UNHEALTHY\`")
    echo "❌ Found unhealthy containers: $UNHEALTHY"
else
    echo "✅ All containers healthy"
fi

# 2. Check if required containers are running
echo "🐳 Checking required containers..."
REQUIRED_CONTAINERS=("familycfo_db_prod" "familycfo_backend_prod" "familycfo_admin_prod" "familycfo_mobile_prod")
for container in "${REQUIRED_CONTAINERS[@]}"; do
    if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        ALL_HEALTHY=false
        ALERTS+=("⚠️ *Container Not Running:*\n\`$container\`")
        echo "❌ Container not running: $container"
    fi
done

# 3. Check disk space
echo "💾 Checking disk space..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -ge "$DISK_CRITICAL_THRESHOLD" ]; then
    ALL_HEALTHY=false
    ALERTS+=("🚨 *Critical: Disk Usage* \`${DISK_USAGE}%\`\nFree up space immediately!")
    echo "🚨 CRITICAL: Disk usage at ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -ge "$DISK_WARNING_THRESHOLD" ]; then
    ALERTS+=("⚠️ *Warning: Disk Usage* \`${DISK_USAGE}%\`\nConsider cleaning up")
    echo "⚠️ WARNING: Disk usage at ${DISK_USAGE}%"
else
    echo "✅ Disk usage OK: ${DISK_USAGE}%"
fi

# 4. Check memory usage
echo "🧠 Checking memory usage..."
if command -v free > /dev/null; then
    MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$MEMORY_USAGE" -ge "$MEMORY_WARNING_THRESHOLD" ]; then
        ALERTS+=("⚠️ *High Memory Usage:* \`${MEMORY_USAGE}%\`")
        echo "⚠️ High memory usage: ${MEMORY_USAGE}%"
    else
        echo "✅ Memory usage OK: ${MEMORY_USAGE}%"
    fi
fi

# 5. Check backend API response
echo "🌐 Checking backend API..."
if ! curl -f -s -m 5 http://localhost:6501/health > /dev/null 2>&1; then
    ALL_HEALTHY=false
    ALERTS+=("⚠️ *Backend API Not Responding*\nCheck backend container logs")
    echo "❌ Backend API not responding"
else
    echo "✅ Backend API responding"
fi

# 6. Check database connectivity
echo "🗄️  Checking database..."
if ! docker exec familycfo_db_prod pg_isready -U admin -d family_cfo > /dev/null 2>&1; then
    ALL_HEALTHY=false
    ALERTS+=("⚠️ *Database Not Ready*\nCheck database container")
    echo "❌ Database not ready"
else
    echo "✅ Database ready"
fi

# Send alerts if any issues found
if [ ${#ALERTS[@]} -gt 0 ]; then
    MESSAGE="🚨 *Family CFO Health Alert*\n\n$(printf '%s\n\n' "${ALERTS[@]}")\n_Time: $(date '+%Y-%m-%d %H:%M:%S')_"
    send_telegram "$MESSAGE"
    echo ""
    echo "=========================================================="
    echo "❌ Health check found ${#ALERTS[@]} issue(s)"
    echo "=========================================================="
    exit 1
else
    echo ""
    echo "=========================================================="
    echo "✅ All health checks passed"
    echo "=========================================================="
    exit 0
fi
