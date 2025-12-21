# API连接优先级指南

## 🎯 快速连接清单

### ✅ 第一优先级：立即可以连接（已有完整API）

#### 1. TestManagement组件
**状态**: ✅ 80%功能有API，可以立即连接

**需要连接的API**：
```typescript
// 在 TestManagement.tsx 中添加
import { testPlanAPI, testTaskAPI } from '@/services/api'
import { useEffect, useState } from 'react'

// 获取测试计划列表
const [plans, setPlans] = useState([])
useEffect(() => {
  testPlanAPI.getAll().then(setPlans)
}, [])

// 创建测试计划
const handleCreatePlan = async (data) => {
  const newPlan = await testPlanAPI.create(data)
  // 刷新列表
}

// 创建并启动任务
const handleStartTask = async (planId) => {
  const task = await testTaskAPI.create({ plan_id: planId })
  await testTaskAPI.start(task.id)
  // 刷新列表
}

// 暂停/停止任务
const handlePause = async (taskId) => {
  await testTaskAPI.pause(taskId)
}

const handleStop = async (taskId) => {
  await testTaskAPI.stop(taskId)
}
```

#### 2. ReportCenter组件
**状态**: ✅ 75%功能有API，可以立即连接

**需要连接的API**：
```typescript
// 在 ReportCenter.tsx 中添加
import { reportAPI } from '@/services/api'

// 生成报告
const handleGenerateReport = async (taskId) => {
  const report = await reportAPI.generate(taskId)
  // 显示报告信息
}

// 下载报告
const handleDownloadReport = async (taskId) => {
  const blob = await reportAPI.download(taskId, 'pdf')
  // 创建下载链接
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${taskId}.pdf`
  a.click()
}

// 获取方法对比
const handleGetComparison = async (taskId) => {
  const comparison = await reportAPI.getComparison(taskId)
  // 显示对比数据
}
```

#### 3. TestMonitoring组件
**状态**: ✅ 66.7%功能有API，可以立即连接

**需要连接的API**：
```typescript
// 在 TestMonitoring.tsx 中添加
import { testTaskAPI } from '@/services/api'
import wsManager from '@/utils/websocket'

// 获取任务详情和指标
useEffect(() => {
  const loadData = async () => {
    const task = await testTaskAPI.getById(taskId)
    const metrics = await testTaskAPI.getMetrics(taskId)
    // 更新状态
  }
  loadData()
}, [taskId])

// WebSocket实时更新
useEffect(() => {
  wsManager.connect(taskId, (data) => {
    // 处理实时数据
    if (data.type === 'metrics_update') {
      // 更新指标
    }
    if (data.type === 'log') {
      // 添加日志
    }
  })
  
  return () => wsManager.close()
}, [taskId])

// 暂停/停止任务
const handlePause = async () => {
  await testTaskAPI.pause(taskId)
}

const handleStop = async () => {
  await testTaskAPI.stop(taskId)
}
```

#### 4. ResultAnalysis组件
**状态**: ✅ 40%功能有API，可以连接基础功能

**需要连接的API**：
```typescript
// 在 ResultAnalysis.tsx 中添加
import { testTaskAPI } from '@/services/api'

// 获取异常列表
useEffect(() => {
  const loadAnomalies = async () => {
    const anomalies = await testTaskAPI.getAnomalies(taskId, {
      top_n: 10,
      source: undefined, // 获取所有
      min_severity: 1
    })
    // 更新异常列表
  }
  loadAnomalies()
}, [taskId])

// 获取监控指标（用于分析）
useEffect(() => {
  const loadMetrics = async () => {
    const metrics = await testTaskAPI.getMetrics(taskId, 100)
    // 处理指标数据，生成趋势图表
  }
  loadMetrics()
}, [taskId])
```

#### 5. ConstraintManager组件
**状态**: ⚠️ 16.7%功能有API，只能连接统计功能

**需要连接的API**：
```typescript
// 在 ConstraintManager.tsx 中添加
import { constraintAPI } from '@/services/api'

// 获取约束统计
useEffect(() => {
  const loadStats = async () => {
    const stats = await constraintAPI.getStats(taskId)
    // 更新统计信息
  }
  loadStats()
}, [taskId])
```

---

### ⚠️ 第二优先级：需要新增API或使用模拟数据

#### 1. Dashboard组件
**状态**: ⚠️ 37.5%功能有API

**可以连接的部分**：
```typescript
// 获取任务列表
const tasks = await testTaskAPI.getAll()

// 计算基础统计
const stats = {
  total: tasks.length,
  running: tasks.filter(t => t.status === 'running').length,
  completed: tasks.filter(t => t.status === 'completed').length,
}
```

**需要新增API的部分**：
- 核心模块状态（需要系统状态API）
- 测试轮数统计（需要聚合统计API）
- 异常指纹数（需要聚合统计API）
- 信号覆盖率（需要聚合统计API）
- 趋势图表数据（需要时间序列API）

**临时方案**：使用模拟数据，或从任务列表聚合计算

#### 2. SystemSettings组件
**状态**: ❌ 0%功能有API

**临时方案**：
- 使用前端localStorage存储配置
- 或创建简单的配置API

**建议新增API**：
```typescript
// 建议新增
GET /api/system/settings
PUT /api/system/settings
```

#### 3. DataAssetManagement组件
**状态**: ❌ 0%功能有API

**临时方案**：
- 使用文件系统管理
- 或创建简单的文件管理API

**建议新增API**：
```typescript
// 建议新增
GET /api/data-assets/dbc-files
POST /api/data-assets/dbc-files
GET /api/data-assets/training-datasets
POST /api/data-assets/training-datasets
GET /api/data-assets/model-versions
```

---

## 📊 连接进度跟踪

### 已完成连接
- [ ] TestManagement - 测试计划/任务管理
- [ ] ReportCenter - 报告生成和下载
- [ ] TestMonitoring - 基础监控功能
- [ ] ResultAnalysis - 异常列表
- [ ] ConstraintManager - 约束统计

### 需要新增API
- [ ] Dashboard - 统计聚合API
- [ ] Dashboard - 趋势图表API
- [ ] ResultAnalysis - 分析数据API
- [ ] ConstraintManager - 规则管理API
- [ ] SystemSettings - 系统配置API
- [ ] DataAssetManagement - 数据资产管理API

### 需要实现功能
- [ ] WebSocket实时连接
- [ ] 实时日志流

---

## 🚀 快速开始

### 步骤1: 连接TestManagement（最简单）

1. 打开 `frontend/src/components/TestManagement.tsx`
2. 导入API服务
3. 替换模拟数据为API调用
4. 测试功能

### 步骤2: 连接ReportCenter

1. 打开 `frontend/src/components/ReportCenter.tsx`
2. 添加报告生成和下载功能
3. 测试功能

### 步骤3: 连接TestMonitoring

1. 打开 `frontend/src/components/TestMonitoring.tsx`
2. 添加API调用和WebSocket连接
3. 测试实时更新

---

## 💡 提示

1. **先连接有API的功能**：TestManagement、ReportCenter、TestMonitoring
2. **使用模拟数据**：对于没有API的功能，暂时使用模拟数据
3. **逐步新增API**：根据优先级逐步新增后端API
4. **测试每个功能**：连接API后立即测试，确保正常工作

