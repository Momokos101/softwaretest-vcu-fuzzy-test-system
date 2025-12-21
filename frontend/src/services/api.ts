import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果是blob响应，直接返回blob对象
    if (response.config.responseType === 'blob') {
      return response.data
    }
    // 其他响应返回data字段
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    
    // 统一错误处理
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      const message = error.response.data?.detail || error.response.data?.message || '未知错误'
      
      return Promise.reject({
        status,
        message,
        data: error.response.data,
      })
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject({
        status: 0,
        message: '网络错误，请检查网络连接',
      })
    } else {
      // 其他错误
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误',
      })
    }
  }
)

export default api

// API方法
export const testPlanAPI = {
  // 获取所有测试计划
  getAll: () => api.get('/api/test-plans'),
  // 获取单个测试计划
  getById: (id: string) => api.get(`/api/test-plans/${id}`),
  // 创建测试计划
  create: (data: any) => api.post('/api/test-plans', data),
  // 更新测试计划
  update: (id: string, data: any) => api.put(`/api/test-plans/${id}`, data),
  // 删除测试计划
  delete: (id: string) => api.delete(`/api/test-plans/${id}`),
}

export const testTaskAPI = {
  // 获取所有测试任务
  getAll: () => api.get('/api/test-tasks'),
  // 获取单个测试任务
  getById: (id: string) => api.get(`/api/test-tasks/${id}`),
  // 创建测试任务
  create: (data: any) => api.post('/api/test-tasks', data),
  // 启动任务
  start: (id: string) => api.post(`/api/test-tasks/${id}/start`),
  // 暂停任务
  pause: (id: string) => api.post(`/api/test-tasks/${id}/pause`),
  // 停止任务
  stop: (id: string) => api.post(`/api/test-tasks/${id}/stop`),
  // 获取异常列表
  getAnomalies: (id: string, options?: any) => api.get(`/api/test-tasks/${id}/anomalies`, { params: options }),
  // 获取监控指标
  getMetrics: (id: string, limit?: number) => api.get(`/api/test-tasks/${id}/metrics`, { params: { limit } }),
}

export const ganAPI = {
  // 生成单个测试用例
  generate: (data: any) => api.post('/api/gan/generate', data),
  // 批量生成
  generateBatch: (data: any) => api.post('/api/gan/generate/batch', data),
  // 格式转换
  convert: (data: any) => api.post('/api/gan/convert', data),
}

export const reportAPI = {
  // 生成报告
  generate: (taskId: string) => api.post(`/api/test-tasks/${taskId}/report`),
  // 下载报告（返回blob）
  download: (taskId: string, format: string = 'pdf') => {
    return api.get(`/api/test-tasks/${taskId}/report/download`, {
      params: { format },
      responseType: 'blob', // 指定响应类型为blob
    });
  },
  // 获取方法对比
  getComparison: (taskId: string) => api.get(`/api/test-tasks/${taskId}/report/comparison`),
}

export const constraintAPI = {
  // 获取约束统计
  getStats: (taskId: string) => api.get(`/api/test-tasks/${taskId}/constraints`),
}

