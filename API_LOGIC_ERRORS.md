# API接口逻辑错误检查报告

## 检查结果

### ✅ 正确的接口

1. **测试计划API** - 完全匹配
   - `GET /api/test-plans` ✅
   - `GET /api/test-plans/{id}` ✅
   - `POST /api/test-plans` ✅
   - `DELETE /api/test-plans/{id}` ✅

2. **测试任务API** - 完全匹配
   - `GET /api/test-tasks` ✅
   - `GET /api/test-tasks/{id}` ✅
   - `POST /api/test-tasks/{id}/start` ✅
   - `POST /api/test-tasks/{id}/pause` ✅
   - `POST /api/test-tasks/{id}/stop` ✅
   - `GET /api/test-tasks/{id}/anomalies` ✅
   - `GET /api/test-tasks/{id}/metrics` ✅

3. **GAN API** - 完全匹配
   - `POST /api/gan/generate` ✅
   - `POST /api/gan/generate/batch` ✅
   - `POST /api/gan/convert` ✅

4. **约束API** - 完全匹配
   - `GET /api/test-tasks/{task_id}/constraints` ✅

5. **监控API** - 完全匹配
   - `GET /api/test-tasks/{task_id}/metrics` ✅

### ⚠️ 发现的问题

#### 1. **报告下载API路径不一致** - 🔴 严重

**问题：**
- 前端调用：`GET /api/test-tasks/${taskId}/report/download?format=pdf`
- 后端路由：`GET /api/test-tasks/{task_id}/report/download?format=pdf`
- 前端代码中直接使用 `fetch` 而不是通过 `api.ts`，且URL硬编码

**位置：**
- `frontend/src/components/ReportCenter.tsx:59`

**问题代码：**
```typescript
const response = await fetch(`http://localhost:8000/api/test-tasks/${taskId}/report/download?format=pdf`);
```

**修复建议：**
1. 应该使用 `reportAPI.download(taskId, format)` 而不是直接 `fetch`
2. 移除硬编码的 `http://localhost:8000`
3. 确保使用统一的API基础URL

#### 2. **报告API参数传递问题** - 🟡 中等

**问题：**
- 前端：`reportAPI.generate(taskId)` - 只传递taskId
- 后端：`POST /api/test-tasks/{task_id}/report` - 接受可选的 `TestReportRequest`
- 后端代码中如果 `request` 为 `None`，会创建一个新的 `TestReportRequest(task_id=task_id)`

**分析：**
- 这个逻辑是正确的，但前端应该可以传递更多参数（如报告类型、格式等）

**建议：**
- 前端可以扩展 `generate` 方法支持可选参数

#### 3. **异常列表API参数问题** - 🟡 中等

**问题：**
- 前端调用：`testTaskAPI.getAnomalies(taskId, { top_n: 10 })`
- 后端路由：`GET /api/test-tasks/{task_id}/anomalies?top_n=10&source=None&min_severity=1`
- 前端传递的是对象 `{ top_n: 10 }`，但后端期望的是查询参数

**分析：**
- 前端使用 `{ params: options }` 是正确的，axios会自动转换为查询参数
- 但需要确保参数名称匹配：`top_n` vs `topN`

**检查：**
- 前端：`options.top_n` 或 `options.topN`？
- 后端：`top_n: int = 10`

**结论：**
- 如果前端传递 `{ top_n: 10 }`，axios会转换为 `?top_n=10`，这是正确的
- 但如果前端传递 `{ topN: 10 }`，则不会匹配

#### 4. **监控指标API参数问题** - 🟡 中等

**问题：**
- 前端调用：`testTaskAPI.getMetrics(taskId, 100)`
- 后端路由：`GET /api/test-tasks/{task_id}/metrics?limit=100`
- 前端传递的是位置参数 `limit`，后端期望查询参数 `limit`

**分析：**
- 前端使用 `{ params: { limit } }` 是正确的
- 但需要检查实际调用时是否正确传递

**检查代码：**
```typescript
getMetrics: (id: string, limit?: number) => api.get(`/api/test-tasks/${id}/metrics`, { params: { limit } }),
```

**结论：**
- 这是正确的，axios会将 `{ params: { limit } }` 转换为 `?limit=100`

#### 5. **测试任务创建API不一致** - 🟡 中等

**问题：**
- 前端：`testTaskAPI.create(data)` - 传递完整数据对象
- 后端：`POST /api/test-tasks` - 期望 `TaskStartRequest`，只包含 `plan_id`

**分析：**
- 后端路由期望的是 `TaskStartRequest`，应该只包含 `plan_id`
- 前端如果传递完整数据对象，可能会有字段不匹配的问题

**建议：**
- 前端应该只传递 `{ plan_id: string }`
- 或者后端应该接受更多字段

#### 6. **WebSocket路径问题** - 🟡 中等

**问题：**
- 前端WebSocket连接：`ws://localhost:8000/ws/monitoring/${taskId}`
- 需要检查后端WebSocket路由是否匹配

**需要检查：**
- 后端WebSocket路由定义
- 路径格式是否一致

#### 7. **响应拦截器问题** - 🟡 中等

**问题：**
- 前端响应拦截器：`return response.data`
- 这意味着所有API响应都会被提取 `data` 字段

**潜在问题：**
- 如果后端返回的是直接数据（不是 `{ data: ... }`），这是正确的
- 但如果后端返回的是 `{ data: ..., message: ... }` 格式，可能会丢失其他字段

**检查：**
- 需要确认后端响应格式

#### 8. **错误处理不完整** - 🟡 中等

**问题：**
- 前端响应拦截器只记录错误，不处理HTTP状态码
- 所有错误都会抛出，但前端组件中的错误处理可能不够统一

**建议：**
- 添加统一的错误处理逻辑
- 根据HTTP状态码进行不同的处理

## 需要修复的问题

### 🔴 高优先级

1. **修复报告下载API调用**
   - 移除硬编码URL
   - 使用统一的API服务

### 🟡 中优先级

2. **统一异常列表参数命名**
   - 确保前端使用 `top_n` 而不是 `topN`

3. **检查测试任务创建参数**
   - 确保前端只传递 `plan_id`

4. **检查WebSocket路由**
   - 确保前后端路径一致

5. **完善错误处理**
   - 添加HTTP状态码处理
   - 统一错误消息格式

## 修复建议

### 1. 修复报告下载API

```typescript
// frontend/src/services/api.ts
export const reportAPI = {
  // ...
  download: (taskId: string, format: string = 'pdf') => {
    return api.get(`/api/test-tasks/${taskId}/report/download`, {
      params: { format },
      responseType: 'blob', // 重要：指定响应类型为blob
    });
  },
}
```

```typescript
// frontend/src/components/ReportCenter.tsx
const handleDownloadReport = async (taskId: string, reportId: string) => {
  try {
    const response = await reportAPI.download(taskId, 'pdf');
    // 处理blob响应
    const blob = new Blob([response], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${reportId}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('报告下载成功');
  } catch (error: any) {
    toast.error('下载报告失败: ' + (error.message || '未知错误'));
  }
};
```

### 2. 统一异常列表参数

```typescript
// frontend/src/components/ResultAnalysis.tsx
const loadAnalysisData = async () => {
  try {
    const [anomaliesData, metricsData] = await Promise.all([
      testTaskAPI.getAnomalies(taskId!, { top_n: 10 }), // 使用 top_n
      testTaskAPI.getMetrics(taskId!, 100)
    ]);
    // ...
  }
};
```

### 3. 检查测试任务创建

```typescript
// 确保前端只传递 plan_id
testTaskAPI.create({ plan_id: planId })
```

### 4. 完善错误处理

```typescript
// frontend/src/services/api.ts
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    
    // 统一错误处理
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status;
      const message = error.response.data?.detail || error.response.data?.message || '未知错误';
      
      // 根据状态码进行不同处理
      if (status === 404) {
        // 资源不存在
      } else if (status === 401) {
        // 未授权，可能需要重新登录
      } else if (status >= 500) {
        // 服务器错误
      }
      
      return Promise.reject({
        status,
        message,
        data: error.response.data,
      });
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject({
        status: 0,
        message: '网络错误，请检查网络连接',
      });
    } else {
      // 其他错误
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误',
      });
    }
  }
);
```

## 总结

### ✅ 正确的地方
- 大部分API路径和方法匹配正确
- 参数传递方式基本正确
- 错误处理框架已建立

### ⚠️ 需要修复
- 报告下载API硬编码URL
- 异常列表参数命名需要确认
- 错误处理需要完善
- WebSocket路径需要验证

### 📋 建议
1. 立即修复报告下载API的硬编码问题
2. 统一所有API调用都通过 `api.ts`
3. 完善错误处理逻辑
4. 添加API测试用例验证所有接口

