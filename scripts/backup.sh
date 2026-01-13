#!/bin/bash
#
# Family CFO Backup Script
# Backs up PostgreSQL database and uploaded files
#

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup/familycfo}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
CONTAINER_NAME="familycfo_db_prod"
DB_USER="admin"
DB_NAME="family_cfo"

# Telegram configuration
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_ADMIN_USER_ID}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/uploads"

echo "==========================================================  "
echo "Starting Family CFO Backup - $(date)"
echo "=========================================================="

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

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Database container is not running!"
    send_telegram "⚠️ *Backup Failed*: Database container not running"
    exit 1
fi

# 1. Backup PostgreSQL database
echo "📦 Backing up database..."
if docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/database/db_backup_$DATE.sql" 2>/dev/null; then
    # Compress the backup
    gzip "$BACKUP_DIR/database/db_backup_$DATE.sql"
    DB_SIZE=$(du -h "$BACKUP_DIR/database/db_backup_$DATE.sql.gz" | cut -f1)
    echo "✅ Database backup completed: $DB_SIZE"
else
    echo "❌ Database backup failed!"
    send_telegram "⚠️ *Backup Failed*: Database dump error"
    exit 1
fi

# 2. Backup uploaded files
echo "📦 Backing up uploaded files..."
if [ -d "/opt/familycfo/backend/uploads" ]; then
    if tar -czf "$BACKUP_DIR/uploads/uploads_$DATE.tar.gz" -C /opt/familycfo/backend uploads/ 2>/dev/null; then
        UPLOADS_SIZE=$(du -h "$BACKUP_DIR/uploads/uploads_$DATE.tar.gz" | cut -f1)
        echo "✅ Uploads backup completed: $UPLOADS_SIZE"
    else
        echo "⚠️ Uploads backup failed (non-critical)"
    fi
else
    echo "ℹ️  No uploads directory found, skipping"
fi

# 3. Clean up old backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR/database" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR/uploads" -name "uploads_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# 4. Calculate backup stats
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR/database" 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo "=========================================================="
echo "✅ Backup completed successfully!"
echo "📊 Statistics:"
echo "   - Database backup: $DB_SIZE"
echo "   - Uploads backup: ${UPLOADS_SIZE:-N/A}"
echo "   - Total backups: $BACKUP_COUNT"
echo "   - Total size: $TOTAL_SIZE"
echo "   - Retention: $RETENTION_DAYS days"
echo "=========================================================="

# 5. Send success notification
send_telegram "✅ *Backup Completed*

📊 Statistics:
• Database: \`$DB_SIZE\`
• Uploads: \`${UPLOADS_SIZE:-N/A}\`
• Total: \`$TOTAL_SIZE\` ($BACKUP_COUNT backups)
• Date: \`$(date +%Y-%m-%d\ %H:%M)\`"

exit 0
