#!/bin/bash
#
# Family CFO Restore Script
# Restores PostgreSQL database from backup
#

set -e

# Configuration
CONTAINER_NAME="familycfo_db_prod"
DB_USER="admin"
DB_NAME="family_cfo"

# Check arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Example:"
    echo "  $0 /backup/familycfo/database/db_backup_20251230_140000.sql.gz"
    echo ""
    echo "Available backups:"
    ls -lh /backup/familycfo/database/db_backup_*.sql.gz 2>/dev/null | tail -10
    exit 1
fi

BACKUP_FILE="$1"

# Validate backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=========================================================="
echo "Family CFO Database Restore"
echo "=========================================================="
echo "Backup file: $BACKUP_FILE"
echo "Container: $CONTAINER_NAME"
echo "Database: $DB_NAME"
echo "=========================================================="
echo ""
echo "⚠️  WARNING: This will OVERWRITE the current database!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Database container is not running!"
    exit 1
fi

echo ""
echo "📦 Preparing restore..."

# Decompress backup if needed
TEMP_SQL="/tmp/restore_temp_$$.sql"
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "📂 Decompressing backup..."
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"
else
    cp "$BACKUP_FILE" "$TEMP_SQL"
fi

# Drop existing connections
echo "🔌 Dropping existing connections..."
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
    2>/dev/null || true

# Drop and recreate database
echo "🗑️  Dropping database..."
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || {
    echo "❌ Failed to drop database"
    rm -f "$TEMP_SQL"
    exit 1
}

echo "🆕 Creating fresh database..."
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || {
    echo "❌ Failed to create database"
    rm -f "$TEMP_SQL"
    exit 1
}

# Restore database
echo "📥 Restoring database from backup..."
cat "$TEMP_SQL" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1 || {
    echo "❌ Failed to restore database"
    rm -f "$TEMP_SQL"
    exit 1
}

# Clean up
rm -f "$TEMP_SQL"

# Verify restore
echo "🔍 Verifying restore..."
RECORD_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')

echo ""
echo "=========================================================="
echo "✅ Database restored successfully!"
echo "📊 Statistics:"
echo "   - Tables: $RECORD_COUNT"
echo "   - Backup: $(basename $BACKUP_FILE)"
echo "   - Size: $(du -h $BACKUP_FILE | cut -f1)"
echo "=========================================================="
echo ""
echo "⚠️  Note: You may need to restart the backend service:"
echo "   docker-compose -f docker-compose.prod.yml restart backend"

exit 0
