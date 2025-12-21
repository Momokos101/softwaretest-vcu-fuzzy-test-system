# 启动前端服务步骤

## 1. 安装Node.js（如果未安装）

### macOS安装方式：
```bash
# 方式1: 使用Homebrew
brew install node

# 方式2: 从官网下载
# 访问 https://nodejs.org/ 下载安装包
```

### 验证安装：
```bash
node --version
npm --version
```

## 2. 安装前端依赖

```bash
cd frontend
npm install
```

## 3. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:5173 启动

## 4. 测试接口

打开浏览器访问 http://localhost:5173，然后测试以下功能：

### 需要测试的接口清单：

#### 测试计划相关（4个）
1. ✅ 获取测试计划列表 - Dashboard/TestManagement页面
2. ✅ 创建测试计划 - 点击"创建新测试"按钮
3. ✅ 获取单个测试计划详情 - 点击计划查看详情
4. ✅ 删除测试计划 - TestManagement页面删除按钮

#### 测试任务相关（8个）
5. ✅ 获取测试任务列表 - Dashboard/TestManagement页面
6. ✅ 创建测试任务 - 创建计划后自动创建任务
7. ✅ 获取任务详情 - TestMonitoring页面
8. ✅ 启动任务 - TestManagement/TestMonitoring页面
9. ✅ 暂停任务 - TestManagement/TestMonitoring页面
10. ✅ 停止任务 - TestManagement/TestMonitoring页面
11. ✅ 获取异常列表 - ResultAnalysis页面
12. ✅ 获取监控指标 - TestMonitoring页面

#### GAN相关（3个）
13. ✅ 生成单个测试用例 - 通过后端API测试（前端可能没有直接UI）
14. ✅ 批量生成测试用例 - 通过后端API测试
15. ✅ 格式转换 - 通过后端API测试

#### 报告相关（3个）
16. ✅ 生成报告 - ReportCenter页面
17. ✅ 下载报告 - ReportCenter页面下载按钮
18. ✅ 获取方法对比 - ReportCenter页面

#### 约束相关（1个）
19. ✅ 获取约束统计 - ConstraintManager页面

#### 监控相关（1个）
20. ✅ 获取监控指标 - TestMonitoring页面（实时更新）

#### WebSocket（1个）
21. ✅ WebSocket实时通信 - TestMonitoring页面（实时日志和状态更新）

## 5. 测试检查点

### 功能测试：
- [ ] 页面能否正常加载
- [ ] API调用是否成功
- [ ] 数据是否正确显示
- [ ] 错误提示是否正常
- [ ] 加载状态是否显示

### 数据流测试：
- [ ] 创建计划 → 创建任务 → 启动任务 → 查看监控
- [ ] 任务状态变化：pending → running → paused → running → stopped
- [ ] 实时数据更新（用例数、异常数）
- [ ] WebSocket消息接收

### UI交互测试：
- [ ] 按钮点击响应
- [ ] 表单提交
- [ ] 数据筛选和搜索
- [ ] 图表显示
- [ ] 报告生成和下载

