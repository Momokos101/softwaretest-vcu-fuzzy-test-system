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

// AutoTestDesign API
export const autoTestAPI = {
  // 需求管理
  parseRawRequirements: (rawText: string, persist: boolean = true) => api.post('/api/requirements/parse', { raw_text: rawText, source: 'text', persist }),
  loadDemo: (replace: boolean = false) => api.get('/api/requirements/demo', { params: { replace } }),
  importCSV: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/requirements/import/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadCSV: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/requirements/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  importText: (text: string) => api.post('/api/requirements/import/text', { raw_text: text }),
  createRequirement: (data: any) => api.post('/api/requirements/import/form', data),
  getRequirements: () => api.get('/api/requirements'),
  getRequirement: (id: string) => api.get(`/api/requirements/${id}`),
  updateRequirement: (id: string, data: any) => api.put(`/api/requirements/${id}`, data),
  deleteRequirement: (id: string) => api.delete(`/api/requirements/${id}`),
  parseRequirement: (id: string) => api.post(`/api/requirements/${id}/parse`),
  parseAllRequirements: (onlyUnparsed: boolean = true) => api.post('/api/requirements/parse-all', null, { params: { only_unparsed: onlyUnparsed } }),
  getParsed: (id: string) => api.get(`/api/requirements/${id}/parsed`),
  updateParsed: (id: string, data: any) => api.put(`/api/requirements/${id}/parsed`, data),

  // 风险分析
  analyzeRisk: (id: string) => api.post(`/api/risk-analysis/${id}`),
  getRiskAnalysis: (id: string) => api.get(`/api/risk-analysis/${id}`),
  adjustRisk: (id: string, data: { tech_risk: number; business_risk: number; iso9126_characteristic?: string; reasoning?: string }) => api.put(`/api/risk-analysis/${id}`, data),
  getRiskMatrix: () => api.get('/api/risk-analysis/matrix/data'),
  analyzeAllRisks: () => api.post('/api/risk-analysis/analyze-all'),

  // 覆盖项与策略
  generateCoverageItems: (requirementIds?: string[]) => api.post('/api/coverage-items/generate', requirementIds || null),
  getCoverageItems: (reqId?: string) => api.get('/api/coverage-items', { params: { requirement_id: reqId } }),
  createCoverageItem: (data: any) => api.post('/api/coverage-items', data),
  updateCoverageItem: (id: string, data: any) => api.put(`/api/coverage-items/${id}`, data),
  deleteCoverageItem: (id: string) => api.delete(`/api/coverage-items/${id}`),
  getStrategy: (reqId: string) => api.get(`/api/strategies/${reqId}`),
  updateStrategy: (reqId: string, data: any) => api.put(`/api/strategies/${reqId}`, data),
  regenerateStrategy: (reqId: string) => api.post(`/api/strategies/${reqId}/regenerate`),
  getPrompts: () => api.get('/api/prompts'),
  getPrompt: (type: string) => api.get(`/api/prompts/${type}`),
  updatePrompt: (type: string, data: any) => api.put(`/api/prompts/${type}`, data),

  // 测试用例
  generateTestCases: (data: any) => api.post('/api/test-cases/generate', data),
  generateAllTestCases: (data: any) => api.post('/api/test-cases/generate-all', data),
  getTestCases: (reqId?: string) => api.get('/api/test-cases', { params: { requirement_id: reqId } }),
  getTestCase: (id: string) => api.get(`/api/test-cases/${id}`),
  updateTestCase: (id: string, data: any) => api.put(`/api/test-cases/${id}`, data),
  deleteTestCase: (id: string) => api.delete(`/api/test-cases/${id}`),
  executeTestCase: (id: string) => api.post(`/api/test-cases/${id}/execute`),
  executeBatch: (ids: string[]) => api.post('/api/test-cases/execute/batch', { test_case_ids: ids }),
  execute: (ids?: string[]) => api.post('/api/execute', { test_case_ids: ids || null, reset_before_run: true }),
  getResultsSummary: () => api.get('/api/results/summary'),
  improve: (data: any) => api.post('/api/improve', data),
  getPerformance: () => api.get('/api/performance'),

  // 导出
  export: (data: any) => api.post('/api/export', data, { responseType: 'blob' }),
  exportByFormat: (format: string) => api.get(`/api/export/${format}`, { responseType: 'blob' }),
}
