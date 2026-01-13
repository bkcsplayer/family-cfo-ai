# 代码审查检查清单

## 项目结构检查

### 目录结构

- [ ] 根目录结构符合标准
- [ ] frontend/ 存在且结构正确
- [ ] backend/ 存在且结构正确
- [ ] database/ 存在迁移文件
- [ ] docs/ 存在基本文档

### 文件命名

- [ ] 组件文件: PascalCase (UserCard.jsx)
- [ ] 工具函数: camelCase (formatDate.js)
- [ ] 样式文件: kebab-case (user-card.css)
- [ ] 数据库表: snake_case 复数 (user_orders)
- [ ] API 路由: kebab-case (/api/user-orders)

### 配置文件

- [ ] .env.example 存在且完整
- [ ] .gitignore 完整
- [ ] docker-compose.yml 正确
- [ ] README.md 包含必要信息

---

## 前端检查 (React)

### 组件结构

- [ ] 组件职责单一
- [ ] Props 有类型定义 (PropTypes/TypeScript)
- [ ] 有默认值设置
- [ ] 正确导出 (default/named)

### Hooks 使用

- [ ] useState 用于简单状态
- [ ] useReducer 用于复杂状态
- [ ] useEffect 依赖数组正确
- [ ] useMemo/useCallback 用于性能优化
- [ ] 自定义 Hooks 以 use 开头

### 性能检查

- [ ] 避免在渲染中创建新对象/函数
- [ ] 列表渲染使用唯一 key
- [ ] 大列表使用虚拟滚动
- [ ] 图片使用懒加载
- [ ] 路由使用懒加载

### TailwindCSS

- [ ] 无内联 style
- [ ] 响应式完整 (sm/md/lg/xl)
- [ ] 深色模式完整 (dark:)
- [ ] 无重复类名组合
- [ ] 合理使用 @apply

### 国际化

- [ ] 无硬编码中文
- [ ] 所有文本使用 t() 函数
- [ ] i18n 文件完整
- [ ] 日期/数字格式化

### 错误处理

- [ ] 有 ErrorBoundary
- [ ] API 错误正确处理
- [ ] 加载状态显示
- [ ] 空状态处理

---

## 后端检查 (FastAPI/Express)

### API 设计

- [ ] 版本控制 (/api/v1/)
- [ ] RESTful 规范
- [ ] 统一响应格式
- [ ] 合理 HTTP 状态码

### 分层架构

- [ ] Controller/Route 只处理请求响应
- [ ] Service 包含业务逻辑
- [ ] Repository 处理数据访问
- [ ] 无跨层调用

### 错误处理

- [ ] 全局错误处理中间件
- [ ] 自定义错误类
- [ ] 错误日志记录
- [ ] 友好错误信息

### 参数验证

- [ ] 请求参数验证
- [ ] 类型检查
- [ ] 边界值检查
- [ ] 枚举值验证

### 认证授权

- [ ] JWT 正确配置
- [ ] Token 过期处理
- [ ] 权限中间件
- [ ] 敏感路由保护

---

## 数据库检查 (PostgreSQL)

### 表设计

- [ ] 表名 snake_case 复数
- [ ] 有主键 (id)
- [ ] 有时间戳 (created_at, updated_at)
- [ ] 软删除 (deleted_at) 如需要
- [ ] 字段类型合适

### 关系设计

- [ ] 外键正确定义
- [ ] 关系类型合理
- [ ] 无循环依赖
- [ ] 级联规则安全

### 索引

- [ ] 主键索引
- [ ] 外键索引
- [ ] 常用查询字段索引
- [ ] 无冗余索引

### 迁移

- [ ] 迁移文件完整
- [ ] 可正向执行
- [ ] 可回滚
- [ ] 有种子数据

---

## 安全检查

### 代码安全

- [ ] 无 SQL 注入
- [ ] 无 XSS 漏洞
- [ ] 无路径遍历
- [ ] 无命令注入

### 认证安全

- [ ] 密码正确加密 (bcrypt)
- [ ] JWT 密钥足够长
- [ ] Token 过期时间合理
- [ ] 敏感操作二次验证

### 数据安全

- [ ] 敏感信息脱敏
- [ ] 日志无敏感数据
- [ ] 错误信息不泄露内部细节
- [ ] 文件上传验证

### 配置安全

- [ ] 无硬编码密钥
- [ ] 环境变量正确使用
- [ ] CORS 正确配置
- [ ] Rate Limiting 配置

---

## 性能检查

### 前端性能

- [ ] 首屏加载 < 3s
- [ ] 图片压缩
- [ ] 代码分割
- [ ] 缓存策略

### 后端性能

- [ ] 无 N+1 查询
- [ ] 合理分页
- [ ] 缓存热点数据
- [ ] 异步处理耗时操作

### 数据库性能

- [ ] 查询使用索引
- [ ] 无全表扫描
- [ ] 连接池配置
- [ ] 慢查询日志

---

## 代码质量

### 可读性

- [ ] 命名有意义
- [ ] 函数不超过 50 行
- [ ] 组件不超过 300 行
- [ ] 适当注释

### 可维护性

- [ ] DRY 原则
- [ ] 单一职责
- [ ] 低耦合
- [ ] 高内聚

### 可测试性

- [ ] 依赖注入
- [ ] 纯函数优先
- [ ] Mock 友好
- [ ] 有单元测试

---

## 不必要文件检查

### 必须删除

| 模式 | 说明 |
|------|------|
| `node_modules/` | npm 缓存 |
| `__pycache__/` | Python 缓存 |
| `*.pyc` | Python 编译文件 |
| `.pytest_cache/` | pytest 缓存 |
| `dist/` | 构建产物 |
| `build/` | 构建产物 |
| `.DS_Store` | macOS 文件 |
| `Thumbs.db` | Windows 文件 |
| `*.log` | 日志文件 |
| `*.tmp` | 临时文件 |
| `.env` | 环境配置 (不应提交) |

### 可能删除

| 模式 | 说明 |
|------|------|
| `*.bak` | 备份文件 |
| `*.old` | 旧版本文件 |
| `*_backup.*` | 备份文件 |
| `*.orig` | 原始文件 |
| `deprecated/` | 废弃目录 |
| `unused_*` | 未使用文件 |

### 需检查后删除

| 检查点 | 操作 |
|--------|------|
| 空目录 | 确认无用后删除 |
| 重复文件 | 保留一个 |
| 未引用文件 | 确认无用后删除 |
| 注释代码 | 删除或恢复 |

---

## 问题严重级别

### P0 - 严重 (必须立即修复)

- 安全漏洞 (SQL注入、XSS等)
- 数据泄露风险
- 系统崩溃风险
- 敏感信息暴露

### P1 - 警告 (应该修复)

- 潜在 Bug
- 性能问题
- 错误处理不完整
- 代码质量问题

### P2 - 建议 (建议优化)

- 代码风格
- 命名规范
- 注释完善
- 结构优化

### P3 - 提示 (可选优化)

- 最佳实践
- 新特性建议
- 工具推荐
- 文档完善

---

## 检查命令汇总

### 通用

```bash
# 查找大文件
find . -type f -size +10M

# 查找空目录
find . -type d -empty

# 查找重复文件
fdupes -r .

# 统计代码行数
cloc .
```

### 前端

```bash
# ESLint
npx eslint src/ --ext .js,.jsx,.ts,.tsx

# Prettier
npx prettier --check src/

# TypeScript
npx tsc --noEmit

# 未使用依赖
npx depcheck

# 未使用导出
npx ts-prune

# Bundle 分析
npx source-map-explorer build/static/js/*.js
```

### 后端 (Python)

```bash
# 代码风格
flake8 src/
black --check src/

# 类型检查
mypy src/

# 安全检查
bandit -r src/

# 依赖安全
safety check
pip-audit

# 未使用导入
autoflake --check src/
```

### 后端 (Node.js)

```bash
# ESLint
npx eslint src/

# 安全审计
npm audit

# 未使用依赖
npx depcheck

# 代码复杂度
npx complexity-report src/
```

### 数据库

```bash
# PostgreSQL 慢查询日志
# 在 postgresql.conf 中设置:
# log_min_duration_statement = 1000

# 索引建议
# 使用 pg_stat_statements 扩展

# 表膨胀检查
SELECT schemaname, relname, 
       n_dead_tup, n_live_tup,
       round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```
