# 自动审查脚本

## 完整审查脚本

```bash
#!/bin/bash
# review.sh - 项目完整审查脚本

set -e

PROJECT_ROOT=$(pwd)
REPORT_DIR="$PROJECT_ROOT/docs/code-review"
DATE=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/review-report-$DATE.md"

# 创建报告目录
mkdir -p "$REPORT_DIR"

echo "# 🔍 代码审查报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**审查时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "**项目路径**: $PROJECT_ROOT" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ===============================
# 1. 项目结构检查
# ===============================
echo "## 📁 项目结构" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
tree -L 2 -I 'node_modules|__pycache__|.git|venv|dist|build' >> "$REPORT_FILE" 2>/dev/null || ls -la >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ===============================
# 2. 代码统计
# ===============================
echo "## 📊 代码统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if command -v cloc &> /dev/null; then
    echo '```' >> "$REPORT_FILE"
    cloc . --exclude-dir=node_modules,venv,dist,build,__pycache__ --quiet >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "提示: 安装 cloc 可获得详细代码统计" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# ===============================
# 3. 前端检查
# ===============================
if [ -d "frontend" ] || [ -d "src" ]; then
    echo "## 🎨 前端检查" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # ESLint 检查
    if [ -f "package.json" ]; then
        echo "### ESLint 检查" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        npx eslint . --ext .js,.jsx,.ts,.tsx --format compact 2>&1 | head -50 >> "$REPORT_FILE" || echo "ESLint 未配置或发现问题" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # 未使用依赖检查
        echo "### 未使用依赖" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        npx depcheck 2>&1 | head -30 >> "$REPORT_FILE" || echo "depcheck 未安装" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
fi

# ===============================
# 4. 后端检查 (Python)
# ===============================
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    echo "## 🐍 Python 后端检查" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    cd backend
    
    # Flake8 检查
    echo "### Flake8 代码风格" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    flake8 . --exclude=venv,__pycache__ --max-line-length=120 2>&1 | head -50 >> "$REPORT_FILE" || echo "Flake8 未安装" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # 安全检查
    echo "### Bandit 安全检查" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    bandit -r . -f txt 2>&1 | head -50 >> "$REPORT_FILE" || echo "Bandit 未安装" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    cd "$PROJECT_ROOT"
fi

# ===============================
# 5. 后端检查 (Node.js)
# ===============================
if [ -d "backend" ] && [ -f "backend/package.json" ]; then
    echo "## 📦 Node.js 后端检查" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    cd backend
    
    # npm audit
    echo "### npm 安全审计" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    npm audit 2>&1 | head -50 >> "$REPORT_FILE" || echo "npm audit 失败" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    cd "$PROJECT_ROOT"
fi

# ===============================
# 6. 文件检查
# ===============================
echo "## 🗑️ 不必要文件" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 大文件
echo "### 大文件 (>10MB)" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
find . -type f -size +10M -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null >> "$REPORT_FILE" || echo "无大文件" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 备份文件
echo "### 备份文件" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
find . -name "*.bak" -o -name "*.old" -o -name "*.orig" -o -name "*_backup.*" 2>/dev/null | grep -v node_modules >> "$REPORT_FILE" || echo "无备份文件" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 日志文件
echo "### 日志文件" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
find . -name "*.log" 2>/dev/null | grep -v node_modules >> "$REPORT_FILE" || echo "无日志文件" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 空目录
echo "### 空目录" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
find . -type d -empty -not -path "./.git/*" 2>/dev/null >> "$REPORT_FILE" || echo "无空目录" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ===============================
# 7. 配置检查
# ===============================
echo "## ⚙️ 配置检查" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# .env 文件
echo "### 环境配置" >> "$REPORT_FILE"
if [ -f ".env" ]; then
    echo "⚠️ 警告: .env 文件存在，确保不要提交到 Git" >> "$REPORT_FILE"
fi
if [ -f ".env.example" ]; then
    echo "✅ .env.example 存在" >> "$REPORT_FILE"
else
    echo "❌ 缺少 .env.example" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# .gitignore 检查
echo "### .gitignore 检查" >> "$REPORT_FILE"
if [ -f ".gitignore" ]; then
    missing=()
    for pattern in "node_modules" ".env" "__pycache__" "*.log" ".DS_Store" "dist" "build"; do
        if ! grep -q "$pattern" .gitignore 2>/dev/null; then
            missing+=("$pattern")
        fi
    done
    if [ ${#missing[@]} -eq 0 ]; then
        echo "✅ .gitignore 包含常见忽略项" >> "$REPORT_FILE"
    else
        echo "⚠️ .gitignore 缺少: ${missing[*]}" >> "$REPORT_FILE"
    fi
else
    echo "❌ 缺少 .gitignore" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# ===============================
# 8. 总结
# ===============================
echo "## 📋 审查总结" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "审查报告已生成: $REPORT_FILE" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "请根据报告内容进行相应修复。" >> "$REPORT_FILE"

echo "✅ 审查完成! 报告已保存到: $REPORT_FILE"
```

---

## 前端专项检查

```bash
#!/bin/bash
# review-frontend.sh

echo "🎨 前端代码审查..."

# 1. ESLint 检查
echo "=== ESLint 检查 ==="
npx eslint src/ --ext .js,.jsx,.ts,.tsx

# 2. TypeScript 检查
echo "=== TypeScript 检查 ==="
npx tsc --noEmit

# 3. 未使用导出
echo "=== 未使用导出 ==="
npx ts-prune 2>/dev/null || echo "安装: npm install -g ts-prune"

# 4. 未使用依赖
echo "=== 未使用依赖 ==="
npx depcheck

# 5. 检查硬编码文本
echo "=== 硬编码中文文本 ==="
grep -rn --include="*.jsx" --include="*.tsx" --include="*.js" --include="*.ts" "[\u4e00-\u9fa5]" src/ | head -20

# 6. 检查内联样式
echo "=== 内联样式 ==="
grep -rn --include="*.jsx" --include="*.tsx" "style={{" src/ | head -20

# 7. 检查 console.log
echo "=== Console.log ==="
grep -rn --include="*.jsx" --include="*.tsx" --include="*.js" --include="*.ts" "console.log" src/ | head -20

echo "✅ 前端检查完成"
```

---

## 后端专项检查 (Python)

```bash
#!/bin/bash
# review-backend-python.sh

echo "🐍 Python 后端代码审查..."

cd backend 2>/dev/null || cd .

# 1. 代码风格
echo "=== Flake8 代码风格 ==="
flake8 . --exclude=venv,__pycache__ --max-line-length=120

# 2. 类型检查
echo "=== MyPy 类型检查 ==="
mypy . --ignore-missing-imports 2>/dev/null || echo "安装: pip install mypy"

# 3. 安全检查
echo "=== Bandit 安全检查 ==="
bandit -r . -f txt 2>/dev/null || echo "安装: pip install bandit"

# 4. 依赖安全
echo "=== 依赖安全检查 ==="
pip-audit 2>/dev/null || safety check 2>/dev/null || echo "安装: pip install pip-audit"

# 5. 检查 print 语句
echo "=== Print 语句 ==="
grep -rn --include="*.py" "^\s*print(" . | grep -v __pycache__ | head -20

# 6. 检查 TODO/FIXME
echo "=== TODO/FIXME 注释 ==="
grep -rn --include="*.py" -E "TODO|FIXME|XXX|HACK" . | grep -v __pycache__ | head -20

echo "✅ Python 后端检查完成"
```

---

## 后端专项检查 (Node.js)

```bash
#!/bin/bash
# review-backend-nodejs.sh

echo "📦 Node.js 后端代码审查..."

cd backend 2>/dev/null || cd .

# 1. ESLint 检查
echo "=== ESLint 检查 ==="
npx eslint . --ext .js,.ts

# 2. 安全审计
echo "=== npm 安全审计 ==="
npm audit

# 3. 未使用依赖
echo "=== 未使用依赖 ==="
npx depcheck

# 4. 检查 console.log
echo "=== Console.log ==="
grep -rn --include="*.js" --include="*.ts" "console.log" src/ | head -20

# 5. 检查 TODO/FIXME
echo "=== TODO/FIXME 注释 ==="
grep -rn --include="*.js" --include="*.ts" -E "TODO|FIXME|XXX|HACK" src/ | head -20

echo "✅ Node.js 后端检查完成"
```

---

## 数据库检查 (PostgreSQL)

```sql
-- review-database.sql - 数据库审查脚本

-- 1. 检查没有主键的表
SELECT 
    t.table_schema,
    t.table_name
FROM information_schema.tables t
LEFT JOIN information_schema.table_constraints tc
    ON t.table_schema = tc.table_schema
    AND t.table_name = tc.table_name
    AND tc.constraint_type = 'PRIMARY KEY'
WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    AND tc.constraint_name IS NULL;

-- 2. 检查没有索引的外键
SELECT
    tc.table_name,
    kcu.column_name,
    'Missing index on foreign key' as issue
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
LEFT JOIN pg_indexes pi
    ON pi.tablename = tc.table_name
    AND pi.indexdef LIKE '%' || kcu.column_name || '%'
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND pi.indexname IS NULL;

-- 3. 检查表大小
SELECT 
    schemaname,
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;

-- 4. 检查未使用的索引
SELECT 
    schemaname,
    relname as table_name,
    indexrelname as index_name,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 5. 检查表膨胀
SELECT 
    schemaname,
    relname as table_name,
    n_dead_tup as dead_rows,
    n_live_tup as live_rows,
    round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 20;

-- 6. 检查缺少时间戳的表
SELECT table_name
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns c
        WHERE c.table_name = t.table_name
        AND c.column_name IN ('created_at', 'createdat', 'create_time')
    );

-- 7. 检查慢查询 (需要开启 pg_stat_statements)
SELECT 
    query,
    calls,
    round(total_exec_time::numeric, 2) as total_time_ms,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

---

## 清理脚本

```bash
#!/bin/bash
# cleanup.sh - 项目清理脚本

set -e

echo "🧹 开始清理项目..."
echo ""

# 计算初始大小
INITIAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "初始大小: $INITIAL_SIZE"
echo ""

# 询问确认
read -p "确定要清理项目吗? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消清理"
    exit 0
fi

echo ""
echo "=== 删除缓存文件 ==="

# Node.js
find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ node_modules"
find . -name ".npm" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .npm"

# Python
find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ __pycache__"
find . -name "*.pyc" -delete 2>/dev/null && echo "✓ *.pyc"
find . -name "*.pyo" -delete 2>/dev/null && echo "✓ *.pyo"
find . -name ".pytest_cache" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .pytest_cache"
find . -name ".mypy_cache" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .mypy_cache"
find . -name "*.egg-info" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ *.egg-info"

echo ""
echo "=== 删除构建产物 ==="

find . -name "dist" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ dist"
find . -name "build" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ build"
find . -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .next"
find . -name ".nuxt" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .nuxt"

echo ""
echo "=== 删除系统文件 ==="

find . -name ".DS_Store" -delete 2>/dev/null && echo "✓ .DS_Store"
find . -name "Thumbs.db" -delete 2>/dev/null && echo "✓ Thumbs.db"

echo ""
echo "=== 删除临时文件 ==="

find . -name "*.log" -delete 2>/dev/null && echo "✓ *.log"
find . -name "*.tmp" -delete 2>/dev/null && echo "✓ *.tmp"
find . -name "*.temp" -delete 2>/dev/null && echo "✓ *.temp"

echo ""
echo "=== 删除测试覆盖率 ==="

find . -name "coverage" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ coverage"
find . -name "htmlcov" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ htmlcov"
find . -name ".coverage" -delete 2>/dev/null && echo "✓ .coverage"
find . -name ".nyc_output" -type d -prune -exec rm -rf {} + 2>/dev/null && echo "✓ .nyc_output"

echo ""
echo "=== 删除空目录 ==="
find . -type d -empty -delete 2>/dev/null && echo "✓ 空目录"

# 计算最终大小
FINAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo ""
echo "================================"
echo "清理前: $INITIAL_SIZE"
echo "清理后: $FINAL_SIZE"
echo "================================"
echo ""
echo "✅ 清理完成!"
```

---

## 使用说明

```bash
# 1. 添加执行权限
chmod +x review.sh cleanup.sh

# 2. 运行完整审查
./review.sh

# 3. 运行清理
./cleanup.sh

# 4. 运行数据库审查 (PostgreSQL)
psql -d your_database -f review-database.sql
```
