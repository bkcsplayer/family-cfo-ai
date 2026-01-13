---
name: code-structure-reviewer
description: 专业代码结构检查与优化工具。以高级全栈程序员视角全面审查项目：(1) 前端架构检查（React/TailwindCSS），(2) 后端架构检查（FastAPI/Express），(3) 数据库设计审查（PostgreSQL），(4) 代码质量与安全检查，(5) 性能优化建议，(6) 自动清理不必要文件，(7) 修复常见问题，(8) 生成详细审查报告。适用于全栈项目的代码质量保障。
---

# Code Structure Reviewer

以高级全栈程序员视角，全面审查和优化项目代码。

## 触发条件

用户请求以下任一操作时触发此 Skill：
- "检查代码" / "审查代码" / "review code"
- "优化项目" / "清理项目"
- "检查架构" / "架构审查"
- "找出问题" / "代码问题"
- "删除不必要的文件"

## 审查流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     代码审查工作流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 扫描项目  →  2. 结构分析  →  3. 代码检查  →  4. 生成报告     │
│       │              │              │              │            │
│       ▼              ▼              ▼              ▼            │
│  识别技术栈      检查目录结构    静态分析      问题清单          │
│  识别框架        检查文件命名    依赖检查      优化建议          │
│  识别入口        检查模块划分    安全检查      清理列表          │
│                                                                 │
│  5. 自动修复  →  6. 手动确认  →  7. 清理文件  →  8. 最终报告     │
│       │              │              │              │            │
│       ▼              ▼              ▼              ▼            │
│  修复简单问题    用户确认修复    删除废弃文件   完整审查报告      │
│  格式化代码      确认优化方案    清理缓存      改进清单          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 审查维度

### 1. 项目结构检查

```yaml
结构合规性:
  - 是否遵循标准目录结构
  - 模块划分是否清晰
  - 职责是否单一
  - 层级是否合理 (最多3-4层)

文件组织:
  - 命名是否规范 (kebab-case/PascalCase)
  - 相关文件是否在一起
  - index 文件是否合理导出
  - 是否有孤立文件

配置检查:
  - 环境配置是否完整 (.env.example)
  - Docker 配置是否正确
  - 依赖版本是否锁定
  - Git 忽略是否完整
```

### 2. 前端检查 (React + TailwindCSS)

```yaml
组件质量:
  - 组件是否职责单一
  - Props 是否有类型定义
  - 是否有默认值
  - 是否正确使用 memo/useMemo/useCallback
  - 是否有不必要的重渲染

TailwindCSS:
  - 是否有内联样式 (应避免)
  - 是否有重复的类名组合
  - 响应式是否完整 (sm/md/lg/xl)
  - 深色模式是否完整
  - 是否正确使用 @apply

状态管理:
  - 状态是否在正确层级
  - 是否过度使用全局状态
  - 是否有状态冗余
  - 异步状态处理是否正确

国际化:
  - 是否有硬编码文本
  - i18n key 是否完整
  - 是否有缺失翻译
  - 日期/数字格式化

性能:
  - 是否有大型组件需要拆分
  - 懒加载是否正确
  - 图片是否优化
  - Bundle 是否过大
```

### 3. 后端检查 (FastAPI / Express)

```yaml
API 设计:
  - RESTful 规范是否正确
  - 版本控制 (/api/v1/)
  - 响应格式是否统一
  - 错误处理是否完整
  - HTTP 状态码是否正确

代码结构:
  - 是否遵循分层架构
  - Controller/Service/Repository 分离
  - 业务逻辑是否在 Service 层
  - 是否有跨层调用

安全检查:
  - SQL 注入防护
  - XSS 防护
  - CORS 配置
  - 认证授权
  - 敏感数据处理
  - Rate Limiting

性能:
  - N+1 查询问题
  - 缺失索引
  - 缓存策略
  - 连接池配置
  - 异步处理
```

### 4. 数据库检查 (PostgreSQL)

```yaml
表设计:
  - 命名规范 (snake_case, 复数)
  - 主键设计 (UUID vs SERIAL)
  - 必备字段 (id, created_at, updated_at)
  - 软删除字段 (deleted_at)
  - 字段类型是否合适

关系设计:
  - 外键是否正确
  - 关系类型是否合理
  - 是否有循环依赖
  - 级联删除是否安全

索引检查:
  - 常用查询是否有索引
  - 外键是否有索引
  - 是否有冗余索引
  - 复合索引顺序是否正确

迁移文件:
  - 是否有完整迁移历史
  - 迁移是否可回滚
  - 是否有数据迁移脚本
```

### 5. 安全审查

```yaml
认证授权:
  - JWT 配置是否安全
  - Token 过期时间
  - Refresh Token 机制
  - 权限控制粒度

数据安全:
  - 密码是否正确加密
  - 敏感信息是否脱敏
  - 日志是否泄露敏感信息
  - 环境变量是否安全

依赖安全:
  - 是否有已知漏洞
  - 依赖是否过时
  - 是否有不必要的依赖
```

### 6. 不必要文件检测

```yaml
应该删除的文件类型:
  # 缓存和临时文件
  - node_modules/
  - __pycache__/
  - *.pyc
  - .pytest_cache/
  - .coverage
  - .cache/
  - *.log
  - *.tmp
  
  # 构建产物
  - dist/
  - build/
  - .next/
  - .nuxt/
  - *.egg-info/
  
  # IDE 和编辑器
  - .idea/
  - .vscode/ (除非项目配置)
  - *.swp
  - *.swo
  - .DS_Store
  - Thumbs.db
  
  # 测试产物
  - coverage/
  - htmlcov/
  - .nyc_output/
  
  # 敏感文件
  - .env (不应提交)
  - *.pem
  - *.key
  - secrets.json
  
  # 废弃代码
  - *.bak
  - *.old
  - *_backup.*
  - *.orig
  - unused_*.js
  - deprecated/

可能不必要:
  - 空目录
  - 重复文件
  - 超大文件 (>10MB)
  - 未使用的依赖
  - 注释掉的代码块
  - 未使用的导入
  - 未使用的变量/函数
  - 示例/测试数据文件
```

## 审查报告格式

```markdown
# 🔍 代码审查报告

**项目**: [项目名称]
**审查时间**: YYYY-MM-DD HH:mm
**审查员**: Claude (Senior Full-Stack Developer)

---

## 📊 总体评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 结构 | ⭐⭐⭐⭐☆ | 结构清晰，部分可优化 |
| 前端 | ⭐⭐⭐☆☆ | 存在性能问题 |
| 后端 | ⭐⭐⭐⭐⭐ | 优秀 |
| 数据库 | ⭐⭐⭐⭐☆ | 缺少部分索引 |
| 安全 | ⭐⭐⭐⭐☆ | 良好，有改进空间 |
| **总分** | **4.0/5.0** | |

---

## 🚨 严重问题 (必须修复)

### [P0-001] SQL 注入风险
- **位置**: `backend/src/repositories/user_repo.py:45`
- **问题**: 直接拼接 SQL 字符串
- **影响**: 高危安全漏洞
- **修复**: 使用参数化查询

```python
# ❌ 错误
query = f"SELECT * FROM users WHERE name = '{name}'"

# ✅ 正确
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (name,))
```

---

## ⚠️ 警告 (建议修复)

### [P1-001] 缺少错误边界
- **位置**: `frontend/src/App.jsx`
- **问题**: 未包裹 ErrorBoundary
- **影响**: 错误会导致整个应用崩溃
- **修复**: 添加 React ErrorBoundary

---

## 💡 优化建议

### [P2-001] 组件可拆分
- **位置**: `frontend/src/pages/Dashboard.jsx`
- **问题**: 组件过大 (500+ 行)
- **建议**: 拆分为多个子组件

---

## 🗑️ 可删除文件

### 确认删除 (明确无用)

| 文件/目录 | 大小 | 原因 |
|----------|------|------|
| `node_modules/` | 234MB | 缓存，可重新安装 |
| `__pycache__/` | 12MB | Python 缓存 |
| `.DS_Store` | 4KB | macOS 系统文件 |
| `backend/test_backup.py` | 15KB | 备份文件 |

### 建议检查后删除

| 文件/目录 | 大小 | 原因 |
|----------|------|------|
| `frontend/src/pages/OldPage.jsx` | 8KB | 可能已废弃 |
| `backend/src/utils/deprecated.py` | 3KB | 命名暗示废弃 |

---

## 📈 性能建议

1. **添加缓存**: 高频查询添加 Redis 缓存
2. **懒加载**: Dashboard 页面的图表组件懒加载
3. **数据库索引**: `orders.user_id` 添加索引

---

## ✅ 修复清单

- [ ] [P0-001] 修复 SQL 注入
- [ ] [P0-002] 修复 XSS 漏洞
- [ ] [P1-001] 添加错误边界
- [ ] [P1-002] 完善错误处理
- [ ] [P2-001] 拆分大组件
- [ ] [P2-002] 优化性能

---

## 📝 修复代码

### [P0-001] SQL 注入修复

**文件**: `backend/src/repositories/user_repo.py`

```python
# 原代码 (第 45-48 行)
def get_user_by_name(self, name: str):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return self.db.execute(query)

# 修复后
def get_user_by_name(self, name: str):
    query = "SELECT * FROM users WHERE name = :name"
    return self.db.execute(query, {"name": name})
```

---

**审查完成** ✓
```

## 自动修复功能

### 可自动修复的问题

```yaml
格式问题:
  - 代码缩进不一致
  - 末尾空白
  - 文件末尾换行
  - import 排序

简单问题:
  - 未使用的 import
  - 空的代码块
  - console.log/print 语句
  - 重复的 CSS 类名

配置问题:
  - .gitignore 补全
  - .env.example 生成
  - ESLint/Prettier 配置
```

### 需确认修复的问题

```yaml
结构调整:
  - 移动文件位置
  - 重命名文件
  - 合并/拆分文件

代码重构:
  - 提取公共函数
  - 拆分大组件
  - 重构复杂逻辑

删除操作:
  - 删除废弃文件
  - 删除未使用代码
  - 清理依赖
```

## 使用方式

### 完整审查

```
用户: 帮我审查这个项目的代码
Claude: 
1. 扫描项目结构
2. 分析每个模块
3. 生成完整审查报告
4. 列出可删除文件
5. 提供修复代码
```

### 针对性审查

```
用户: 只检查前端代码
Claude: 仅审查 frontend/ 目录

用户: 检查数据库设计
Claude: 仅审查 database/ 和 models/

用户: 找出可删除的文件
Claude: 扫描并列出所有不必要文件
```

### 自动修复

```
用户: 帮我修复所有问题
Claude:
1. 列出可自动修复的问题
2. 用户确认后执行修复
3. 列出需要手动修复的问题
4. 提供修复代码示例
```

## 检查命令

### 前端检查命令

```bash
# ESLint 检查
npx eslint src/ --ext .js,.jsx,.ts,.tsx

# TypeScript 检查
npx tsc --noEmit

# 未使用依赖
npx depcheck

# Bundle 分析
npx webpack-bundle-analyzer
```

### 后端检查命令 (Python)

```bash
# 代码风格
flake8 src/

# 类型检查
mypy src/

# 安全检查
bandit -r src/

# 依赖安全
pip-audit
```

### 后端检查命令 (Node.js)

```bash
# ESLint 检查
npx eslint src/

# 安全审计
npm audit

# 未使用依赖
npx depcheck
```

## 输出文件

审查完成后生成：

```
project-root/
└── docs/
    └── code-review/
        ├── review-report-YYYYMMDD.md   # 完整审查报告
        ├── fix-checklist.md            # 修复清单
        ├── cleanup-list.md             # 清理文件列表
        └── optimization-guide.md       # 优化指南
```

## 审查检查清单 (内部使用)

详见 [references/checklist.md](references/checklist.md)
