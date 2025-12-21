# 前后端API覆盖分析

## 📊 总体情况

| 组件 | 功能总数 | 有API | 无API | 覆盖率 |
|------|---------|-------|-------|--------|
| Dashboard | 8 | 3 | 5 | 37.5% |
| TestManagement | 10 | 8 | 2 | 80% |
| TestMonitoring | 6 | 4 | 2 | 66.7% |
| ResultAnalysis | 5 | 2 | 3 | 40% |
| ReportCenter | 4 | 3 | 1 | 75% |
| ConstraintManager | 6 | 1 | 5 | 16.7% |
| SystemSettings | 8 | 0 | 8 | 0% |
| DataAssetManagement | 6 | 0 | 6 | 0% |
| **总计** | **53** | **21** | **32** | **39.6%** |

---

## ✅ 已有API支持的功能

### 1. Dashboard（仪表盘）

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 获取最近任务列表 | `GET /api/test-tasks` | ✅ 已支持 |
| ✅ 获取任务统计信息 | `GET /api/test-tasks` (聚合计算) | ✅ 已支持 |
| ✅ 获取任务详情 | `GET /api/test-tasks/{task_id}` | ✅ 已支持 |
| ❌ 获取核心模块状态 | - | ❌ 无API |
| ❌ 获取测试轮数统计 | - | ❌ 无API |
| ❌ 获取异常指纹数 | - | ❌ 无API |
| ❌ 获取信号覆盖率 | - | ❌ 无API |
| ❌ 获取趋势图表数据 | - | ❌ 无API |

**需要连接的API**：
```typescript
// 获取任务列表
const tasks = await testTaskAPI.getAll()

// 计算统计信息
const stats = {
  total: tasks.length,
  running: tasks.filter(t => t.status === 'running').length,
  completed: tasks.filter(t => t.status === 'completed').length,
}
```

---

### 2. TestManagement（测试管理）✅ 80%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 获取测试计划列表 | `GET /api/test-plans` | ✅ 已支持 |
| ✅ 获取测试任务列表 | `GET /api/test-tasks` | ✅ 已支持 |
| ✅ 创建测试计划 | `POST /api/test-plans` | ✅ 已支持 |
| ✅ 创建测试任务 | `POST /api/test-tasks` | ✅ 已支持 |
| ✅ 启动任务 | `POST /api/test-tasks/{task_id}/start` | ✅ 已支持 |
| ✅ 暂停任务 | `POST /api/test-tasks/{task_id}/pause` | ✅ 已支持 |
| ✅ 停止任务 | `POST /api/test-tasks/{task_id}/stop` | ✅ 已支持 |
| ✅ 删除测试计划 | `DELETE /api/test-plans/{plan_id}` | ✅ 已支持 |
| ❌ 删除测试任务 | - | ❌ 无API |
| ❌ 更新测试计划 | - | ❌ 无API（有update但可能未实现） |

**需要连接的API**：
```typescript
// 获取测试计划
const plans = await testPlanAPI.getAll()

// 创建测试计划
const newPlan = await testPlanAPI.create({
  name: '测试计划名称',
  description: '描述',
  test_mode: 'both', // 'traditional' | 'gan' | 'both'
})

// 创建并启动任务
const task = await testTaskAPI.create({ plan_id: planId })
await testTaskAPI.start(task.id)

// 暂停/停止任务
await testTaskAPI.pause(taskId)
await testTaskAPI.stop(taskId)
```

---

### 3. TestMonitoring（测试监控）✅ 66.7%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 获取任务详情 | `GET /api/test-tasks/{task_id}` | ✅ 已支持 |
| ✅ 获取监控指标 | `GET /api/test-tasks/{task_id}/metrics` | ✅ 已支持 |
| ✅ 暂停任务 | `POST /api/test-tasks/{task_id}/pause` | ✅ 已支持 |
| ✅ 停止任务 | `POST /api/test-tasks/{task_id}/stop` | ✅ 已支持 |
| ❌ WebSocket实时更新 | `WS /ws/test-tasks/{task_id}` | ⚠️ 有但需实现 |
| ❌ 实时日志流 | - | ❌ 无API |

**需要连接的API**：
```typescript
// 获取任务详情
const task = await testTaskAPI.getById(taskId)

// 获取监控指标
const metrics = await testTaskAPI.getMetrics(taskId)

// WebSocket连接（需要实现）
import wsManager from '@/utils/websocket'
wsManager.connect(taskId, (data) => {
  // 处理实时数据
})
```

---

### 4. ResultAnalysis（结果分析）✅ 40%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 获取异常列表 | `GET /api/test-tasks/{task_id}/anomalies` | ✅ 已支持 |
| ✅ 获取监控指标 | `GET /api/test-tasks/{task_id}/metrics` | ✅ 已支持 |
| ❌ 获取异常趋势数据 | - | ❌ 无API |
| ❌ 获取异常类型分布 | - | ❌ 无API |
| ❌ 获取引擎对比数据 | - | ❌ 无API |

**需要连接的API**：
```typescript
// 获取异常列表
const anomalies = await testTaskAPI.getAnomalies(taskId, {
  top_n: 10,
  source: 'gan', // 可选: 'traditional' | 'gan'
  min_severity: 1
})

// 获取监控指标（用于分析）
const metrics = await testTaskAPI.getMetrics(taskId)
```

---

### 5. ReportCenter（报告中心）✅ 75%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 生成报告 | `POST /api/test-tasks/{task_id}/report` | ✅ 已支持 |
| ✅ 下载报告 | `GET /api/test-tasks/{task_id}/report/download` | ✅ 已支持 |
| ✅ 获取方法对比 | `GET /api/test-tasks/{task_id}/report/comparison` | ✅ 已支持 |
| ❌ 获取报告列表 | - | ❌ 无API |

**需要连接的API**：
```typescript
// 生成报告
const report = await reportAPI.generate(taskId)

// 下载报告
const blob = await reportAPI.download(taskId, 'pdf')

// 获取方法对比
const comparison = await reportAPI.getComparison(taskId)
```

---

### 6. ConstraintManager（约束管理）⚠️ 16.7%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 获取约束统计 | `GET /api/test-tasks/{task_id}/constraints` | ✅ 已支持 |
| ❌ 获取约束规则列表 | - | ❌ 无API |
| ❌ 创建约束规则 | - | ❌ 无API |
| ❌ 更新约束规则 | - | ❌ 无API |
| ❌ 删除约束规则 | - | ❌ 无API |
| ❌ 启用/禁用约束规则 | - | ❌ 无API |

**需要连接的API**：
```typescript
// 获取约束统计
const stats = await constraintAPI.getStats(taskId)
```

---

### 7. SystemSettings（系统设置）❌ 0%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ❌ 获取系统配置 | - | ❌ 无API |
| ❌ 更新系统配置 | - | ❌ 无API |
| ❌ 获取引擎配置 | - | ❌ 无API |
| ❌ 更新引擎配置 | - | ❌ 无API |
| ❌ 获取GAN模型配置 | - | ❌ 无API |
| ❌ 更新GAN模型配置 | - | ❌ 无API |
| ❌ 获取权限配置 | - | ❌ 无API |
| ❌ 更新权限配置 | - | ❌ 无API |

**需要新增的API**：
```typescript
// 建议新增
GET /api/system/settings
PUT /api/system/settings
GET /api/system/engines
PUT /api/system/engines
GET /api/system/gan-models
PUT /api/system/gan-models
GET /api/system/rbac
PUT /api/system/rbac
```

---

### 8. DataAssetManagement（数据资产管理）❌ 0%覆盖

| 功能 | API端点 | 状态 |
|------|---------|------|
| ❌ 获取DBC文件列表 | - | ❌ 无API |
| ❌ 上传DBC文件 | - | ❌ 无API |
| ❌ 获取训练数据集列表 | - | ❌ 无API |
| ❌ 上传训练数据集 | - | ❌ 无API |
| ❌ 获取模型版本列表 | - | ❌ 无API |
| ❌ 切换模型版本 | - | ❌ 无API |

**需要新增的API**：
```typescript
// 建议新增
GET /api/data-assets/dbc-files
POST /api/data-assets/dbc-files
GET /api/data-assets/training-datasets
POST /api/data-assets/training-datasets
GET /api/data-assets/model-versions
PUT /api/data-assets/model-versions/{version_id}/activate
```

---

## 🔧 GAN相关功能

| 功能 | API端点 | 状态 |
|------|---------|------|
| ✅ 生成单个测试用例 | `POST /api/gan/generate` | ✅ 已支持 |
| ✅ 批量生成测试用例 | `POST /api/gan/generate/batch` | ✅ 已支持 |
| ✅ 格式转换 | `POST /api/gan/convert` | ✅ 已支持 |

**使用示例**：
```typescript
// 生成单个用例
const result = await ganAPI.generate({
  condition: { target_phase: 'wake' },
  sequence_length: 8,
  temperature: 1.0,
  send_to_baic: false
})

// 批量生成
const batchResult = await ganAPI.generateBatch({
  count: 10,
  condition: { target_phase: 'wake' },
  sequence_length: 8
})

// 格式转换
const baicFormat = await ganAPI.convert(ganData)
```

---

## 📋 总结

### ✅ 已完全支持的功能模块

1. **TestManagement** - 80%覆盖，核心功能都有API
2. **ReportCenter** - 75%覆盖，报告生成和下载都有
3. **TestMonitoring** - 66.7%覆盖，基础监控功能有API

### ⚠️ 部分支持的功能模块

1. **Dashboard** - 37.5%覆盖，基础任务列表有，但统计和图表数据缺失
2. **ResultAnalysis** - 40%覆盖，异常列表有，但分析数据缺失
3. **ConstraintManager** - 16.7%覆盖，只有统计接口，缺少规则管理

### ❌ 完全缺失的功能模块

1. **SystemSettings** - 0%覆盖，所有系统配置功能都没有API
2. **DataAssetManagement** - 0%覆盖，所有数据资产管理功能都没有API

---

## 🚀 优先级建议

### 高优先级（核心功能）

1. **Dashboard统计API** - 需要聚合统计接口
2. **WebSocket实时更新** - 需要实现WebSocket连接
3. **异常分析数据API** - 需要趋势和分布数据接口

### 中优先级（重要功能）

1. **约束规则管理API** - 需要CRUD接口
2. **报告列表API** - 需要获取历史报告列表

### 低优先级（辅助功能）

1. **系统配置API** - 可以暂时使用前端配置
2. **数据资产管理API** - 可以暂时使用文件系统管理

---

## 📝 下一步行动

1. **立即可以连接的功能**：
   - TestManagement的所有功能
   - ReportCenter的报告生成和下载
   - TestMonitoring的基础监控
   - GAN生成功能

2. **需要新增API的功能**：
   - Dashboard统计聚合
   - ResultAnalysis分析数据
   - ConstraintManager规则管理
   - SystemSettings系统配置
   - DataAssetManagement数据资产管理

3. **需要实现的功能**：
   - WebSocket实时连接
   - 实时日志流

