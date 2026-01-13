# 常见问题修复指南

## 安全问题修复

### SQL 注入

```python
# ❌ 错误 - 字符串拼接
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# ✅ 正确 - 参数化查询 (Python)
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# ✅ 正确 - ORM (SQLAlchemy)
user = session.query(User).filter(User.id == user_id).first()

# ✅ 正确 - 参数化查询 (Node.js)
const query = 'SELECT * FROM users WHERE id = $1';
await pool.query(query, [userId]);
```

### XSS 防护

```jsx
// ❌ 错误 - 直接插入 HTML
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ 正确 - 使用文本内容
<div>{userContent}</div>

// ✅ 如果必须插入 HTML，使用 DOMPurify
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

### 敏感信息

```python
# ❌ 错误 - 硬编码密钥
SECRET_KEY = "my-secret-key-12345"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ✅ 正确 - 使用环境变量
import os
SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ✅ 正确 - 使用 dotenv
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## 前端问题修复

### 无用重渲染

```jsx
// ❌ 错误 - 每次渲染创建新函数
function ParentComponent() {
  return <ChildComponent onClick={() => doSomething()} />;
}

// ✅ 正确 - 使用 useCallback
function ParentComponent() {
  const handleClick = useCallback(() => {
    doSomething();
  }, []);
  
  return <ChildComponent onClick={handleClick} />;
}

// ❌ 错误 - 每次渲染创建新对象
function ParentComponent() {
  return <ChildComponent style={{ color: 'red' }} />;
}

// ✅ 正确 - 使用 useMemo 或常量
const style = { color: 'red' };
function ParentComponent() {
  return <ChildComponent style={style} />;
}
```

### 缺少 Key

```jsx
// ❌ 错误 - 使用索引作为 key
{items.map((item, index) => (
  <Item key={index} data={item} />
))}

// ✅ 正确 - 使用唯一标识符
{items.map((item) => (
  <Item key={item.id} data={item} />
))}
```

### 内存泄漏

```jsx
// ❌ 错误 - 未清理副作用
useEffect(() => {
  const subscription = api.subscribe(handleData);
  // 缺少清理函数
}, []);

// ✅ 正确 - 清理副作用
useEffect(() => {
  const subscription = api.subscribe(handleData);
  return () => {
    subscription.unsubscribe();
  };
}, []);

// ❌ 错误 - 未取消的请求
useEffect(() => {
  fetchData().then(setData);
}, []);

// ✅ 正确 - 使用 AbortController
useEffect(() => {
  const controller = new AbortController();
  
  fetchData({ signal: controller.signal })
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') throw err;
    });
  
  return () => controller.abort();
}, []);
```

### 错误边界

```jsx
// ✅ 添加 ErrorBoundary
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}

// 使用
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

## 后端问题修复

### N+1 查询

```python
# ❌ 错误 - N+1 查询
users = session.query(User).all()
for user in users:
    print(user.orders)  # 每个用户触发一次查询

# ✅ 正确 - 预加载 (SQLAlchemy)
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.orders)).all()

# ✅ 正确 - 显式 JOIN
users = session.query(User).join(User.orders).all()
```

```javascript
// ❌ 错误 - N+1 查询 (Node.js)
const users = await User.findAll();
for (const user of users) {
  const orders = await Order.findAll({ where: { userId: user.id } });
}

// ✅ 正确 - 预加载 (Sequelize)
const users = await User.findAll({
  include: [{ model: Order }]
});

// ✅ 正确 - 批量查询
const users = await User.findAll();
const userIds = users.map(u => u.id);
const orders = await Order.findAll({
  where: { userId: { [Op.in]: userIds } }
});
```

### 统一响应格式

```python
# ✅ FastAPI 统一响应
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: str = ""
    error_code: Optional[str] = None

# 成功响应
@app.get("/users/{id}")
async def get_user(id: int):
    user = await user_service.get(id)
    return Response(success=True, data=user)

# 错误响应
@app.exception_handler(NotFoundException)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=Response(
            success=False,
            message=str(exc),
            error_code="NOT_FOUND"
        ).dict()
    )
```

```javascript
// ✅ Express 统一响应
const sendResponse = (res, data, message = 'Success') => {
  res.json({
    success: true,
    data,
    message
  });
};

const sendError = (res, status, message, errorCode) => {
  res.status(status).json({
    success: false,
    message,
    error_code: errorCode
  });
};

// 使用
app.get('/users/:id', async (req, res) => {
  try {
    const user = await userService.get(req.params.id);
    sendResponse(res, user);
  } catch (err) {
    sendError(res, 404, 'User not found', 'USER_NOT_FOUND');
  }
});
```

### 错误处理中间件

```python
# ✅ FastAPI 全局错误处理
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class AppException(Exception):
    def __init__(self, status_code: int, message: str, error_code: str):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 记录日志
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )
```

```javascript
// ✅ Express 全局错误处理
class AppError extends Error {
  constructor(statusCode, message, errorCode) {
    super(message);
    this.statusCode = statusCode;
    this.errorCode = errorCode;
  }
}

// 错误处理中间件 (放在路由之后)
app.use((err, req, res, next) => {
  console.error(err);
  
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      success: false,
      message: err.message,
      error_code: err.errorCode
    });
  }
  
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error_code: 'INTERNAL_ERROR'
  });
});
```

---

## 数据库问题修复

### 添加索引

```sql
-- 外键索引
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 常用查询字段索引
CREATE INDEX idx_users_email ON users(email);

-- 复合索引 (注意顺序，最常用的放前面)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- 部分索引 (只索引部分数据)
CREATE INDEX idx_orders_pending ON orders(created_at) 
WHERE status = 'pending';
```

### 添加必备字段

```sql
-- 添加时间戳字段
ALTER TABLE users 
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 添加软删除字段
ALTER TABLE users 
ADD COLUMN deleted_at TIMESTAMP NULL;

-- 创建更新触发器
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 规范化表名

```sql
-- 从单数改为复数
ALTER TABLE user RENAME TO users;
ALTER TABLE order RENAME TO orders;
ALTER TABLE product RENAME TO products;

-- 从驼峰改为蛇形
ALTER TABLE userOrder RENAME TO user_orders;
ALTER TABLE productCategory RENAME TO product_categories;
```

---

## 文件清理脚本

### 删除不必要文件

```bash
#!/bin/bash
# cleanup.sh

echo "🧹 开始清理项目..."

# 删除 Node.js 缓存
find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name ".npm" -type d -prune -exec rm -rf {} + 2>/dev/null

# 删除 Python 缓存
find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name ".pytest_cache" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name ".mypy_cache" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name "*.egg-info" -type d -prune -exec rm -rf {} + 2>/dev/null

# 删除构建产物
find . -name "dist" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name "build" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null

# 删除 IDE 文件
find . -name ".idea" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null

# 删除系统文件
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null

# 删除日志文件
find . -name "*.log" -delete 2>/dev/null

# 删除临时文件
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null

# 删除备份文件
find . -name "*.bak" -delete 2>/dev/null
find . -name "*.old" -delete 2>/dev/null
find . -name "*.orig" -delete 2>/dev/null

# 删除测试覆盖率
find . -name "coverage" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name "htmlcov" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name ".coverage" -delete 2>/dev/null

# 删除空目录
find . -type d -empty -delete 2>/dev/null

echo "✅ 清理完成!"
```

### 查找未使用文件

```bash
#!/bin/bash
# find-unused.sh

echo "🔍 查找未使用的文件..."

# 查找可能未使用的 JS/TS 文件
echo "=== 可能未使用的 JS/TS 文件 ==="
for file in $(find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | grep -v node_modules); do
  basename=$(basename "$file" | sed 's/\.[^.]*$//')
  # 检查是否被引用
  if ! grep -r --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" -l "$basename" . | grep -v "$file" > /dev/null 2>&1; then
    echo "  $file"
  fi
done

# 查找可能未使用的 Python 文件
echo "=== 可能未使用的 Python 文件 ==="
for file in $(find . -name "*.py" | grep -v __pycache__ | grep -v venv); do
  basename=$(basename "$file" .py)
  if [[ "$basename" != "__init__" ]] && [[ "$basename" != "main" ]]; then
    if ! grep -r --include="*.py" -l "import $basename\|from.*$basename" . | grep -v "$file" > /dev/null 2>&1; then
      echo "  $file"
    fi
  fi
done

echo "⚠️  请手动确认这些文件是否真的未使用"
```

---

## .gitignore 模板

```gitignore
# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Build outputs
dist/
build/
.next/
.nuxt/
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local
*.pem
*.key

# Logs
*.log
logs/

# Test
coverage/
htmlcov/
.coverage
.pytest_cache/
.nyc_output/

# Temp
*.tmp
*.temp
*.bak
*.old

# Uploads (if not needed in repo)
uploads/
!uploads/.gitkeep

# Database
*.sqlite
*.db
database/backups/
```
