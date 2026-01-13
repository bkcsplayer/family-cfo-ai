# 📋 Phase 5 执行计划：前端页面开发

**计划日期：** 2025-12-30
**预计进度提升：** 92% → 97% (+5%)
**优先级：** 高 🔥

---

## 🎯 Phase 5 目标

完善前端用户界面，让用户能够通过可视化方式使用预算管理和数据导出功能。

### 核心任务
1. ✨ 预算管理页面（BudgetManager.tsx）
2. 📊 数据导出界面集成
3. 🎨 UI/UX 优化

---

## 📅 执行步骤

### Step 5.1: 预算管理页面开发 (60%)
**预计时间：** 1-2 小时
**进度提升：** +3%

#### 任务清单
- [ ] 创建 `admin/src/views/BudgetManager.tsx`
- [ ] 实现预算列表展示（卡片式布局）
- [ ] 添加进度条组件（显示使用百分比）
- [ ] 实现预算创建表单
- [ ] 实现预算编辑功能
- [ ] 添加预算删除确认对话框
- [ ] 集成超支告警提示（红色/黄色状态）
- [ ] 添加到导航菜单

#### UI 设计要求
```tsx
// 预算卡片布局
┌─────────────────────────────────────────┐
│ Food - Restaurants          [编辑] [删除]│
│                                          │
│ ████████████████░░░░  93.1%             │
│ $465.50 / $500.00                       │
│                                          │
│ ⚠️ Warning: 已接近限额                   │
│ 剩余: $34.50                             │
└─────────────────────────────────────────┘
```

#### 技术栈
- React 19 + TypeScript
- TailwindCSS（样式）
- Fetch API（后端调用）
- React Hooks（状态管理）

---

### Step 5.2: 数据导出界面集成 (30%)
**预计时间：** 30-45 分钟
**进度提升：** +1.5%

#### 任务清单
- [ ] 在交易列表页添加"导出"按钮
- [ ] 创建导出选项下拉菜单
  - CSV 格式
  - Excel 格式（多工作表）
  - 月度报告
- [ ] 实现日期范围选择器
- [ ] 实现分类筛选器
- [ ] 处理文件下载逻辑
- [ ] 添加加载状态和错误提示

#### UI 设计要求
```tsx
// 导出按钮布局
┌────────────────────────────────────────┐
│ 交易列表                    [导出 ▼]   │
│                                         │
│ 下拉菜单：                              │
│ ✓ CSV 格式                              │
│ ✓ Excel 格式（多工作表）                │
│ ✓ 月度报告                              │
│ ✓ 预算状态导出                          │
└────────────────────────────────────────┘
```

---

### Step 5.3: 预算页面路由集成 (5%)
**预计时间：** 10-15 分钟
**进度提升：** +0.25%

#### 任务清单
- [ ] 在 `admin/src/App.tsx` 添加路由
- [ ] 在侧边栏导航添加"预算管理"入口
- [ ] 配置图标和菜单项
- [ ] 测试路由跳转

---

### Step 5.4: API 集成与测试 (5%)
**预计时间：** 15-20 分钟
**进度提升：** +0.25%

#### 任务清单
- [ ] 创建 API 服务文件（budgetService.ts）
- [ ] 实现所有预算 API 调用
- [ ] 实现导出 API 调用
- [ ] 添加错误处理
- [ ] 添加 Loading 状态
- [ ] 端到端测试

---

## 🛠️ 技术实现细节

### 1. 预算管理 API 调用

```typescript
// admin/src/services/budgetService.ts

interface Budget {
  id: number;
  category: string;
  monthly_limit: number;
  current_spent: number;
  alert_threshold: number;
  is_active: boolean;
}

interface BudgetStatus {
  id: number;
  category: string;
  monthly_limit: number;
  current_spent: number;
  remaining: number;
  percentage_used: number;
  alert_threshold: number;
  is_over_budget: boolean;
  is_near_limit: boolean;
}

const API_BASE = 'http://localhost:6501';

export const budgetService = {
  // 获取所有预算
  async getAllBudgets(token: string): Promise<Budget[]> {
    const response = await fetch(`${API_BASE}/api/budgets/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  // 获取预算状态
  async getBudgetStatus(token: string): Promise<BudgetStatus[]> {
    const response = await fetch(`${API_BASE}/api/budgets/status`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  // 创建预算
  async createBudget(token: string, data: {
    category: string;
    monthly_limit: number;
    alert_threshold?: number;
  }): Promise<Budget> {
    const response = await fetch(`${API_BASE}/api/budgets/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // 更新预算
  async updateBudget(token: string, id: number, data: Partial<Budget>): Promise<Budget> {
    const response = await fetch(`${API_BASE}/api/budgets/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // 删除预算
  async deleteBudget(token: string, id: number): Promise<void> {
    await fetch(`${API_BASE}/api/budgets/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  },

  // 检查告警
  async checkAlerts(token: string) {
    const response = await fetch(`${API_BASE}/api/budgets/check-alerts`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
};
```

---

### 2. 导出功能实现

```typescript
// admin/src/services/exportService.ts

const API_BASE = 'http://localhost:6501';

export const exportService = {
  // 导出交易 CSV
  async exportTransactionsCSV(
    token: string,
    startDate?: string,
    endDate?: string,
    category?: string
  ) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (category) params.append('category', category);

    const response = await fetch(
      `${API_BASE}/api/export/transactions/csv?${params}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  },

  // 导出交易 Excel
  async exportTransactionsExcel(
    token: string,
    startDate?: string,
    endDate?: string
  ) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await fetch(
      `${API_BASE}/api/export/transactions/excel?${params}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_${new Date().toISOString().split('T')[0]}.xlsx`;
    a.click();
  },

  // 导出预算 Excel
  async exportBudgetsExcel(token: string) {
    const response = await fetch(
      `${API_BASE}/api/export/budgets/excel`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `budgets_${new Date().toISOString().split('T')[0]}.xlsx`;
    a.click();
  },

  // 导出月度报告
  async exportMonthlyReport(token: string, year: number, month: number) {
    const response = await fetch(
      `${API_BASE}/api/export/monthly-report/csv?year=${year}&month=${month}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `monthly_report_${year}_${month}.csv`;
    a.click();
  }
};
```

---

### 3. 预算卡片组件示例

```tsx
// admin/src/components/BudgetCard.tsx

interface BudgetCardProps {
  budget: BudgetStatus;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export const BudgetCard: React.FC<BudgetCardProps> = ({ budget, onEdit, onDelete }) => {
  const getStatusColor = () => {
    if (budget.is_over_budget) return 'bg-red-500';
    if (budget.is_near_limit) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (budget.is_over_budget) return '⚠️ 超支！';
    if (budget.is_near_limit) return '⚠️ 接近限额';
    return '✅ 正常';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">{budget.category}</h3>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(budget.id)}
            className="text-blue-600 hover:text-blue-800"
          >
            编辑
          </button>
          <button
            onClick={() => onDelete(budget.id)}
            className="text-red-600 hover:text-red-800"
          >
            删除
          </button>
        </div>
      </div>

      {/* 进度条 */}
      <div className="mb-2">
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`${getStatusColor()} h-4 rounded-full transition-all`}
            style={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
          />
        </div>
      </div>

      {/* 金额信息 */}
      <div className="flex justify-between text-sm mb-2">
        <span className="font-medium">
          ${budget.current_spent.toFixed(2)} / ${budget.monthly_limit.toFixed(2)}
        </span>
        <span className={budget.is_over_budget ? 'text-red-600' : 'text-gray-600'}>
          {budget.percentage_used.toFixed(1)}%
        </span>
      </div>

      {/* 状态提示 */}
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-600">
          剩余: ${budget.remaining.toFixed(2)}
        </span>
        <span className={`text-sm font-medium ${
          budget.is_over_budget ? 'text-red-600' :
          budget.is_near_limit ? 'text-yellow-600' :
          'text-green-600'
        }`}>
          {getStatusText()}
        </span>
      </div>
    </div>
  );
};
```

---

## 🧪 测试计划

### 单元测试
- [ ] BudgetCard 组件渲染测试
- [ ] budgetService API 调用测试
- [ ] exportService 文件下载测试

### 集成测试
- [ ] 创建预算流程测试
- [ ] 更新预算流程测试
- [ ] 删除预算流程测试
- [ ] 导出功能端到端测试

### UI/UX 测试
- [ ] 响应式布局测试（桌面/平板/手机）
- [ ] 加载状态显示测试
- [ ] 错误处理显示测试
- [ ] 进度条动画测试

---

## 📊 进度里程碑

| Step | 任务 | 预计时间 | 进度提升 | 累计进度 |
|------|------|---------|---------|---------|
| 5.1 | 预算管理页面 | 1-2h | +3% | 95% |
| 5.2 | 导出界面集成 | 30-45m | +1.5% | 96.5% |
| 5.3 | 路由集成 | 10-15m | +0.25% | 96.75% |
| 5.4 | API 测试 | 15-20m | +0.25% | 97% |

**总计：** 92% → 97% (+5%)

---

## 🎯 验收标准

### 预算管理页面
- ✅ 可以查看所有预算列表
- ✅ 可以创建新预算
- ✅ 可以编辑现有预算
- ✅ 可以删除预算
- ✅ 进度条正确显示使用百分比
- ✅ 超支状态正确标识（红色/黄色/绿色）
- ✅ 实时显示剩余额度

### 导出功能
- ✅ 可以导出 CSV 格式
- ✅ 可以导出 Excel 格式
- ✅ 可以选择日期范围
- ✅ 可以按分类筛选
- ✅ 文件自动下载
- ✅ 文件命名规范（含日期）

---

## 🚀 执行顺序

### 第一阶段：核心功能开发
1. 创建 budgetService.ts
2. 创建 exportService.ts
3. 创建 BudgetCard 组件
4. 创建 BudgetManager 页面

### 第二阶段：UI 集成
5. 添加路由配置
6. 集成导航菜单
7. 在交易列表添加导出按钮

### 第三阶段：测试验证
8. 功能测试
9. UI/UX 测试
10. 端到端测试

---

## 📝 文件清单

### 新增文件
```
admin/src/services/budgetService.ts       预算 API 服务
admin/src/services/exportService.ts       导出 API 服务
admin/src/views/BudgetManager.tsx         预算管理页面
admin/src/components/BudgetCard.tsx       预算卡片组件
admin/src/components/BudgetForm.tsx       预算表单组件
admin/src/components/ExportButton.tsx     导出按钮组件
```

### 修改文件
```
admin/src/App.tsx                         添加路由
admin/src/components/Sidebar.tsx          添加导航项
admin/src/views/TransactionReview.tsx     集成导出按钮
```

---

## 🎨 UI/UX 设计原则

1. **一致性**：保持与现有页面风格一致
2. **直观性**：功能一目了然，无需说明
3. **响应式**：支持桌面和移动端
4. **反馈性**：操作有明确的视觉反馈
5. **容错性**：错误提示清晰，易于恢复

---

## 🔧 开发环境准备

### 检查现有前端
```bash
# 查看 Admin 前端文件结构
ls -la admin/src/

# 启动开发服务器（如果需要）
cd admin
npm run dev
```

### 依赖检查
```bash
# 确认已安装必要的依赖
# React 19, TypeScript, TailwindCSS
```

---

## 💡 下一步行动

**立即开始：**
1. 探索 admin 前端代码结构
2. 创建 budgetService.ts 文件
3. 开发 BudgetManager 页面
4. 集成到路由系统

**预计完成时间：** 2-3 小时
**优先级：** 高 🔥

---

**Phase 5 执行计划完成！**
**准备开始实施？** 🚀
