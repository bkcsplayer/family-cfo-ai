#!/bin/bash
#
# Family CFO Cleanup Script
# Cleans up old logs and Docker resources
#

set -e

echo "========================================================"
echo "🧹 Family CFO Cleanup Script"
echo "========================================================"

# 1. Clean up old log files
echo "📝 Cleaning up old logs..."
find /opt/familycfo/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true
find /opt/familycfo/logs -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
echo "✅ Old logs cleaned"

# 2. Clean up Docker
echo "🐳 Cleaning up Docker resources..."
docker system prune -f --volumes --filter "until=168h" 2>/dev/null || true
echo "✅ Docker cleanup done"

# 3. Show disk usage
echo ""
echo "💾 Current disk usage:"
df -h / | tail -1
echo ""

echo "=========================================================="
echo "✅ Cleanup completed"
echo "=========================================================="
