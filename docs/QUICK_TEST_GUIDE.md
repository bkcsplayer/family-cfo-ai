# 🧪 快速测试指南

**测试版本：** v1.0.1
**测试日期：** 2025-12-30
**预计测试时间：** 10-15分钟

---

## 🚀 开始测试

### 前提条件检查

```bash
# 1. 检查所有容器是否运行
docker ps

# 应该看到4个容器：
# - familycfo_db
# - familycfo_backend
# - familycfo_admin
# - familycfo_mobile
```

### 访问地址

- **Admin Dashboard:** http://localhost:6502
- **Mobile App:** http://localhost:6503
- **Backend API:** http://localhost:6501
- **API Docs:** http://localhost:6501/docs

默认登录：
- 用户名：`admin`
- 密码：`password123`

---

## 测试 #1: FHSA账户显示 ✅

**时间：** 2分钟

### 步骤：

1. 打开 http://localhost:6502
2. 登录系统
3. 点击左侧菜单 **"Benefits & Equity"**
4. 点击 **"Add Account"** 按钮
5. 填写表单：
   - Type: 选择 **FHSA**
   - Holder: 输入 `测试用户`
   - Institution: 输入 `TD Bank`
   - Current Value: 输入 `10000`
   - Available Room: 输入 `5000`
6. 点击 **"Save Account"**

### 预期结果：

✅ 账户立即出现在列表中，显示为 **"FHSA"** 而不是 "TFSA"

✅ 账户卡片显示：
- 类型：FHSA / 测试用户
- 机构：TD Bank
- 金额：$10,000

### 如果失败：

❌ 如果显示为TFSA，刷新浏览器缓存（Ctrl+Shift+R）

---

## 测试 #2: 资产创建和显示 ✅

**时间：** 2分钟

### 步骤：

1. 在Admin Dashboard中
2. 点击左侧菜单 **"Asset Hub"**
3. 点击 **"Add Asset"** 按钮
4. 填写表单：
   - Asset Type: 选择 **Vehicle**
   - Name: 输入 `2023 Tesla Model 3`
   - Value: 输入 `50000`
   - Equity: 输入 `30000`
5. 点击保存

### 预期结果：

✅ 资产**立即**出现在Asset Hub列表中

✅ 资产卡片显示：
- 名称：2023 Tesla Model 3
- 类型：Vehicle 图标
- 价值：$50,000
- Equity: $30,000

### 如果失败：

❌ 检查浏览器控制台是否有错误
❌ 刷新页面，资产应该持久化存在

---

## 测试 #3: 交易审核流程 ✅

**时间：** 3分钟

### 步骤：

1. 在Admin Dashboard中
2. 确保在 **"Cockpit"** (Dashboard) 页面
3. 点击右上角 **"Manual Entry"** 按钮
4. 填写表单：
   - Merchant: 输入 `Starbucks`
   - Amount: 输入 `25.50`
   - Type: 选择 **Expense**
   - Category: 输入 `Dining`
   - Date: 选择今天的日期
5. 点击 **"Add to Queue"**

### 预期结果：

✅ 弹出提示："Transaction added to review queue!"

✅ **自动跳转**到 "Review Workbench" 页面

✅ 在Review Workbench中看到刚添加的交易：
- Merchant: Starbucks
- Amount: $25.50
- Category: Dining
- 状态：Draft Mode

✅ 看到三个操作按钮：
- 🗑️ 删除按钮（左侧灰色）
- "Skip" 按钮（中间）
- ✓ "Approve & Post" 按钮（右侧紫色）

6. 点击 **"Approve & Post"** 按钮

### 预期结果：

✅ 交易被批准

✅ 从审核队列中消失

✅ 如果队列为空，显示 "All Caught Up!" 消息

### 验证：

7. 返回 **Dashboard** (点击左侧"Cockpit")
8. 检查 "Review Queue (Inbox)" 部分

✅ 应该显示 "ALL CLEAR"（如果没有其他待审核交易）

---

## 测试 #4: Review Workbench多种操作 ✅

**时间：** 2分钟

### 步骤：

1. 再次创建一笔手动交易（重复测试#3的步骤1-5）
2. 在Review Workbench中

### 测试Skip功能：

3. 点击 **"Skip"** 按钮

✅ 交易保留在队列中
✅ 如果有多笔交易，跳到下一笔

### 测试Delete功能：

4. 点击左侧的 **🗑️ 删除按钮**

✅ 交易被删除
✅ 从队列中移除

### 测试Approve功能：

5. 创建第三笔交易
6. 点击 **"Approve & Post"**

✅ 交易被批准并记录

---

## 测试 #5: Mobile OCR收据上传 ✅

**时间：** 3分钟

### 准备：

找一张收据图片（或任意图片用于测试）

### 步骤：

1. 打开 http://localhost:6503
2. 登录（如需要）
3. 确保在 **"Transaction Terminal"** 标签页
4. 点击底部的 **📷 相机图标** 或 **上传按钮**
5. 选择一张收据图片上传

### 预期结果：

✅ 立即显示成功消息：

```
✅ Receipt uploaded successfully!

File: 20251230_XXXXXX_XXXXXXXX.png

AI is analyzing your receipt in the background.
The transaction will appear in your list shortly.
```

✅ **不再显示** "AI analysis unavailable" 错误

6. 等待 **5-10秒**

7. 检查交易列表

### 预期结果：

✅ 新交易出现在列表顶部

✅ 交易包含AI提取的信息：
- Merchant名称
- 金额
- 分类
- 状态：Pending（待审核）

### 如果AI处理失败：

- 检查OPENROUTER_API_KEY是否配置
- 查看后端日志：`docker logs familycfo_backend`
- 即使AI失败，也不会显示误导性错误

---

## 🎯 完整测试检查清单

完成所有测试后，确认：

- [ ] ✅ FHSA账户正确显示为FHSA
- [ ] ✅ 资产创建后立即显示
- [ ] ✅ 手动交易自动跳转到Review Workbench
- [ ] ✅ Review Workbench有三个操作选项
- [ ] ✅ Approve功能正常工作
- [ ] ✅ Skip功能正常工作
- [ ] ✅ Delete功能正常工作
- [ ] ✅ OCR上传显示友好的后台处理消息
- [ ] ✅ OCR处理后交易自动出现

---

## 🐛 如果遇到问题

### 问题1：前端更改未生效

**解决：**
```bash
# 硬刷新浏览器缓存
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# 或重启admin容器
docker restart familycfo_admin
```

### 问题2：API错误

**检查后端日志：**
```bash
docker logs familycfo_backend --tail 50
```

**重启后端：**
```bash
docker restart familycfo_backend
```

### 问题3：数据库连接错误

**重启所有服务：**
```bash
docker-compose restart
```

### 问题4：OCR不工作

**检查OCR服务状态：**
```bash
curl http://localhost:6501/api/upload/health
```

**应该返回：**
```json
{
    "status": "healthy",
    "ocr_enabled": true,
    "ocr_model": "anthropic/claude-3.5-sonnet"
}
```

**如果ocr_enabled为false：**
- 检查.env文件中的OPENROUTER_API_KEY
- 重启backend容器

---

## 📊 测试结果记录

| 测试项 | 状态 | 备注 |
|--------|------|------|
| FHSA账户显示 | ⬜ 待测试 | |
| 资产创建显示 | ⬜ 待测试 | |
| 交易审核流程 | ⬜ 待测试 | |
| Review操作选项 | ⬜ 待测试 | |
| OCR收据上传 | ⬜ 待测试 | |

完成测试后，请将⬜更新为✅或❌

---

## 🎉 测试完成后

如果所有测试通过：

1. ✅ 所有bug已修复
2. ✅ 系统功能正常
3. ✅ 可以开始正常使用

如果有测试失败：

1. 记录失败的测试项
2. 检查错误消息
3. 查看相关日志
4. 报告问题以便进一步修复

---

**测试指南版本：** 1.0
**最后更新：** 2025-12-30

祝测试顺利！🚀
