# 前端端到端测试清单

## 需要测试的接口（共21个）

### 📋 测试计划接口（4个）
1. **GET /api/test-plans** - 获取测试计划列表
   - 测试位置：Dashboard页面、TestManagement页面
   - 检查：列表是否正确显示，数据格式是否正确

2. **POST /api/test-plans** - 创建测试计划
   - 测试位置：点击"创建新测试"按钮
   - 检查：创建后是否出现在列表中

3. **GET /api/test-plans/{id}** - 获取测试计划详情
   - 测试位置：点击计划查看详情
   - 检查：详情信息是否正确显示

4. **DELETE /api/test-plans/{id}** - 删除测试计划
   - 测试位置：TestManagement页面删除按钮
   - 检查：删除后是否从列表中消失

### 🎯 测试任务接口（8个）
5. **GET /api/test-tasks** - 获取测试任务列表
   - 测试位置：Dashboard页面、TestManagement页面
   - 检查：任务列表显示，状态、进度、覆盖率等字段

6. **POST /api/test-tasks** - 创建测试任务
   - 测试位置：创建计划后自动创建
   - 检查：任务是否正确创建

7. **GET /api/test-tasks/{id}** - 获取任务详情
   - 测试位置：TestMonitoring页面
   - 检查：任务详情是否正确显示

8. **POST /api/test-tasks/{id}/start** - 启动任务
   - 测试位置：TestManagement/TestMonitoring页面
   - 检查：状态是否变为running，任务是否开始执行

9. **POST /api/test-tasks/{id}/pause** - 暂停任务
   - 测试位置：TestManagement/TestMonitoring页面
   - 检查：状态是否变为paused

10. **POST /api/test-tasks/{id}/stop** - 停止任务
    - 测试位置：TestManagement/TestMonitoring页面
    - 检查：状态是否变为stopped

11. **GET /api/test-tasks/{id}/anomalies?top_n=10** - 获取异常列表
    - 测试位置：ResultAnalysis页面
    - 检查：异常列表是否正确显示，字段映射是否正确

12. **GET /api/test-tasks/{id}/metrics?limit=100** - 获取监控指标
    - 测试位置：TestMonitoring页面
    - 检查：监控指标是否正确显示，图表是否正常

### 🤖 GAN接口（3个）
13. **POST /api/gan/generate** - 生成单个测试用例
    - 测试位置：可能没有直接UI，通过后端API测试
    - 检查：返回数据格式是否正确

14. **POST /api/gan/generate/batch** - 批量生成
    - 测试位置：可能没有直接UI，通过后端API测试
    - 检查：批量生成是否成功

15. **POST /api/gan/convert** - 格式转换
    - 测试位置：可能没有直接UI，通过后端API测试
    - 检查：转换格式是否正确

### 📊 报告接口（3个）
16. **POST /api/test-tasks/{id}/report** - 生成报告
    - 测试位置：ReportCenter页面
    - 检查：报告是否成功生成，路径是否正确

17. **GET /api/test-tasks/{id}/report/download?format=pdf** - 下载报告
    - 测试位置：ReportCenter页面下载按钮
    - 检查：文件是否能正常下载

18. **GET /api/test-tasks/{id}/report/comparison** - 获取方法对比
    - 测试位置：ReportCenter页面
    - 检查：对比数据是否正确显示

### 🛡️ 约束接口（1个）
19. **GET /api/test-tasks/{id}/constraints** - 获取约束统计
    - 测试位置：ConstraintManager页面
    - 检查：约束统计是否正确显示，拦截原因分布图

### 📈 监控接口（1个）
20. **GET /api/test-tasks/{id}/metrics?limit=100** - 获取监控指标
    - 测试位置：TestMonitoring页面
    - 检查：历史指标是否正确显示

### 🔌 WebSocket（1个）
21. **WS /ws/test-tasks/{id}** - 实时监控
    - 测试位置：TestMonitoring页面
    - 检查：实时日志是否更新，状态是否实时变化

## 测试步骤

### 1. 启动服务
```bash
# 后端（应该已经在运行）
cd backend
python3 run_server.py

# 前端（新终端）
cd frontend
npm install  # 如果还没安装依赖
npm run dev
```

### 2. 打开浏览器
访问 http://localhost:5173

### 3. 测试流程

#### 流程1：创建和启动测试
1. 进入TestManagement页面
2. 点击"创建新测试"
3. 填写测试计划信息
4. 创建后查看任务列表
5. 点击"启动"按钮
6. 观察任务状态变化

#### 流程2：监控测试执行
1. 进入TestMonitoring页面（点击任务详情）
2. 观察实时监控指标
3. 查看实时日志
4. 测试暂停/继续/停止功能
5. 观察WebSocket实时更新

#### 流程3：查看结果和分析
1. 进入ResultAnalysis页面
2. 查看异常列表
3. 查看性能趋势图表
4. 查看引擎对比数据

#### 流程4：生成和下载报告
1. 进入ReportCenter页面
2. 点击"生成报告"
3. 等待报告生成完成
4. 点击"下载PDF"
5. 验证文件下载

#### 流程5：查看约束统计
1. 进入ConstraintManager页面
2. 查看拦截总数
3. 查看拦截原因分布
4. 查看约束规则列表

### 4. 检查点

#### 数据正确性
- [ ] 所有字段正确显示（无undefined/null）
- [ ] 数字格式正确（进度、覆盖率、异常数）
- [ ] 日期时间格式正确
- [ ] 状态标签正确显示

#### 交互响应
- [ ] 按钮点击有响应
- [ ] 加载状态正确显示
- [ ] 错误提示正确显示
- [ ] 成功提示正确显示

#### 实时更新
- [ ] WebSocket连接成功
- [ ] 实时日志更新
- [ ] 状态实时变化
- [ ] 指标实时更新

#### 错误处理
- [ ] 网络错误提示
- [ ] 404错误处理
- [ ] 400错误处理
- [ ] 500错误处理

