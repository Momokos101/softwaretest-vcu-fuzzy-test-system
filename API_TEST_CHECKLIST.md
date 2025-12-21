# API接口测试清单

## 📋 测试计划管理接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 1 | `/api/test-plans` | GET | 获取所有测试计划列表 | Dashboard, TestManagement | ⬜ 待测试 | 🔴 高 |
| 2 | `/api/test-plans/{id}` | GET | 获取单个测试计划详情 | TestManagement | ⬜ 待测试 | 🟡 中 |
| 3 | `/api/test-plans` | POST | 创建测试计划 | TestManagement | ⬜ 待测试 | 🔴 高 |
| 4 | `/api/test-plans/{id}` | PUT | 更新测试计划 | TestManagement | ⬜ 待测试 | 🟡 中 |
| 5 | `/api/test-plans/{id}` | DELETE | 删除测试计划 | TestManagement | ⬜ 待测试 | 🟡 中 |

## 📋 测试任务管理接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 6 | `/api/test-tasks` | GET | 获取所有测试任务列表 | Dashboard, TestManagement, ReportCenter | ⬜ 待测试 | 🔴 高 |
| 7 | `/api/test-tasks/{id}` | GET | 获取单个测试任务详情 | TestMonitoring, ResultAnalysis | ⬜ 待测试 | 🔴 高 |
| 8 | `/api/test-tasks` | POST | 创建测试任务 | TestManagement | ⬜ 待测试 | 🔴 高 |
| 9 | `/api/test-tasks/{id}/start` | POST | 启动测试任务 | TestManagement, TestMonitoring | ⬜ 待测试 | 🔴 高 |
| 10 | `/api/test-tasks/{id}/pause` | POST | 暂停测试任务 | TestManagement, TestMonitoring | ⬜ 待测试 | 🔴 高 |
| 11 | `/api/test-tasks/{id}/stop` | POST | 停止测试任务 | TestManagement, TestMonitoring | ⬜ 待测试 | 🔴 高 |
| 12 | `/api/test-tasks/{id}/anomalies` | GET | 获取任务异常列表 | ResultAnalysis | ⬜ 待测试 | 🔴 高 |
| 13 | `/api/test-tasks/{id}/metrics` | GET | 获取任务监控指标 | TestMonitoring, ResultAnalysis | ⬜ 待测试 | 🔴 高 |

## 📋 GAN生成接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 14 | `/api/gan/generate` | POST | 生成单个测试用例 | - | ⬜ 待测试 | 🟡 中 |
| 15 | `/api/gan/generate/batch` | POST | 批量生成测试用例 | - | ⬜ 待测试 | 🟡 中 |
| 16 | `/api/gan/convert` | POST | 转换数据格式 | - | ⬜ 待测试 | 🟡 中 |

## 📋 测试报告接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 17 | `/api/test-tasks/{id}/report` | POST | 生成测试报告 | ReportCenter | ⬜ 待测试 | 🔴 高 |
| 18 | `/api/test-tasks/{id}/report/download` | GET | 下载测试报告（PDF/Markdown） | ReportCenter | ⬜ 待测试 | 🔴 高 |
| 19 | `/api/test-tasks/{id}/report/comparison` | GET | 获取方法对比数据 | ReportCenter | ⬜ 待测试 | 🟡 中 |

## 📋 约束管理接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 20 | `/api/test-tasks/{id}/constraints` | GET | 获取约束统计信息 | ConstraintManager | ⬜ 待测试 | 🟡 中 |

## 📋 WebSocket实时通信接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 21 | `/ws/test-tasks/{task_id}` | WebSocket | 实时监控数据推送 | TestMonitoring | ⬜ 待测试 | 🔴 高 |

## 📋 系统健康检查接口

| 序号 | 接口路径 | 方法 | 功能描述 | 前端组件 | 测试状态 | 优先级 |
|------|---------|------|---------|---------|---------|--------|
| 22 | `/api/health` | GET | 健康检查 | - | ⬜ 待测试 | 🟢 低 |

---

## 🎯 测试优先级说明

- 🔴 **高优先级**：核心功能，必须测试
- 🟡 **中优先级**：重要功能，建议测试
- 🟢 **低优先级**：辅助功能，可选测试

## 📝 测试状态说明

- ⬜ **待测试**：尚未测试
- 🟦 **测试中**：正在测试
- ✅ **已通过**：测试通过
- ❌ **失败**：测试失败
- ⚠️ **部分通过**：部分功能正常

## 🔍 测试建议

### 1. 基础功能测试（高优先级）
- 先测试健康检查接口，确保后端服务正常
- 测试计划创建、查询、删除
- 测试任务创建、启动、暂停、停止
- 测试报告生成和下载

### 2. 数据流测试
- 创建测试计划 → 创建任务 → 启动任务 → 查看监控 → 查看异常 → 生成报告
- 验证整个流程的数据一致性

### 3. 错误处理测试
- 测试无效ID的请求
- 测试缺失参数的请求
- 测试状态冲突（如暂停已停止的任务）

### 4. 性能测试
- 批量生成接口的响应时间
- WebSocket连接的稳定性
- 大量数据查询的性能

### 5. 边界条件测试
- 空列表查询
- 最大/最小参数值
- 并发请求处理

---

## 🛠️ 测试工具建议

1. **浏览器开发者工具**：测试前端API调用
2. **Postman/Insomnia**：独立测试后端API
3. **curl命令**：快速验证接口
4. **自动化测试脚本**：批量测试

---

## 📅 测试记录模板

```markdown
### 测试日期：YYYY-MM-DD

#### 接口：[接口名称]
- **请求**：`[方法] [路径]`
- **请求参数**：`{参数详情}`
- **响应状态**：`200 OK`
- **响应数据**：`{数据示例}`
- **测试结果**：✅ 通过 / ❌ 失败
- **备注**：`[问题描述]`
```

