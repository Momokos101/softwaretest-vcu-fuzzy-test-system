# 快速启动前端

## 前提条件
需要先安装Node.js（如果未安装）

## 一键启动（推荐）

```bash
cd /Users/siri-iii/Desktop/软工项目
./setup_frontend.sh
```

## 手动启动

### 步骤1: 检查Node.js
```bash
node --version
npm --version
```

如果显示版本号，继续下一步。
如果显示"command not found"，请先安装Node.js（见INSTALL_NODE.md）

### 步骤2: 安装依赖
```bash
cd frontend
npm install
```

### 步骤3: 启动服务
```bash
npm run dev
```

前端将在 **http://localhost:3000** 启动（根据vite.config.ts配置）

## 需要测试的接口

启动后，在浏览器中测试以下功能：

### Dashboard页面
- [ ] 页面加载
- [ ] 显示任务统计
- [ ] 显示最近任务列表
- [ ] 点击任务进入监控页面

### TestManagement页面
- [ ] 获取测试计划列表
- [ ] 获取测试任务列表
- [ ] 创建新测试
- [ ] 启动/暂停/停止任务
- [ ] 删除测试计划
- [ ] 搜索和筛选功能

### TestMonitoring页面
- [ ] 获取任务详情
- [ ] 获取监控指标
- [ ] WebSocket实时连接
- [ ] 实时日志更新
- [ ] 暂停/继续/停止功能
- [ ] 双引擎对比图表

### ResultAnalysis页面
- [ ] 获取异常列表
- [ ] 异常数据正确显示
- [ ] 性能趋势图表
- [ ] 引擎对比数据

### ReportCenter页面
- [ ] 获取报告列表
- [ ] 生成测试报告
- [ ] 下载PDF报告
- [ ] 获取方法对比

### ConstraintManager页面
- [ ] 获取约束统计
- [ ] 拦截原因分布图
- [ ] 约束规则列表

## 测试检查清单

### 基础功能
- [ ] 所有页面能正常加载
- [ ] 无控制台错误
- [ ] API调用成功
- [ ] 数据正确显示

### 数据流
- [ ] 创建计划 → 创建任务 → 启动 → 监控
- [ ] 状态变化正常
- [ ] 实时数据更新

### 错误处理
- [ ] 网络错误提示
- [ ] 404/400/500错误处理
- [ ] 加载状态显示
