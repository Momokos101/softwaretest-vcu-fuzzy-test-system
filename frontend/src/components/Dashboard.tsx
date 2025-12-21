import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Cpu, ArrowUpRight, Sparkles, Layers, GitBranch, Target, Zap, Link2, CheckCircle2, ChevronDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { testTaskAPI, testPlanAPI } from '@/services/api';
import { toast } from 'sonner';

interface DashboardProps {
  onCreateTest: () => void;
  onViewMonitoring: (taskId: string) => void;
}

const trendData = [
  { date: '11-15', traditional: 8, gan: 15, coverage: 65 },
  { date: '11-16', traditional: 12, gan: 22, coverage: 68 },
  { date: '11-17', traditional: 10, gan: 28, coverage: 72 },
  { date: '11-18', traditional: 15, gan: 35, coverage: 75 },
  { date: '11-19', traditional: 11, gan: 31, coverage: 78 },
  { date: '11-20', traditional: 14, gan: 38, coverage: 82 },
  { date: '11-21', traditional: 13, gan: 42, coverage: 85 },
];

const convergenceData = [
  { round: '1', anomalies: 8 },
  { round: '2', anomalies: 15 },
  { round: '3', anomalies: 21 },
  { round: '4', anomalies: 25 },
  { round: '5', anomalies: 28 },
  { round: '6', anomalies: 29 },
  { round: '7', anomalies: 30 },
];

export function Dashboard({ onCreateTest, onViewMonitoring }: DashboardProps) {
  const [showTraceMatrix, setShowTraceMatrix] = useState(false);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载任务数据
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const tasksData = await testTaskAPI.getAll();
      setTasks(tasksData);
    } catch (error: any) {
      console.error('加载任务失败:', error);
      toast.error('加载任务失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 计算统计信息
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const totalRounds = completedTasks.length;
  const totalAnomalies = tasks.reduce((sum, t) => sum + (t.total_anomalies || 0), 0);
  
  // 计算平均覆盖率（基于统计数据）
  const avgCoverage = tasks.length > 0 
    ? Math.round(tasks.reduce((sum, t) => {
        const totalCases = t.total_cases || 0;
        const traditionalCases = t.traditional_stats?.cases || 0;
        const ganCases = t.gan_stats?.cases || 0;
        const coverage = totalCases > 0 ? Math.min(100, Math.round((traditionalCases + ganCases) / totalCases * 100)) : 0;
        return sum + coverage;
      }, 0) / tasks.length)
    : 0;
  
  const quickStats = [
    { label: '测试轮数', value: String(totalRounds), icon: Activity, color: 'from-blue-600 to-blue-700', change: '+2', subtitle: '已完成任务' },
    { label: '异常指纹数', value: String(totalAnomalies), icon: AlertTriangle, color: 'from-blue-500 to-blue-600', change: '+8', subtitle: '累计异常' },
    { label: '信号覆盖率', value: `${avgCoverage}%`, icon: Target, color: 'from-blue-600 to-blue-700', change: '+12%', subtitle: '平均覆盖率' },
    { label: '活跃模块', value: '5/5', icon: Layers, color: 'from-blue-500 to-blue-600', change: '100%', subtitle: '核心模块' },
  ];

  // 五大核心模块状态
  const coreModules = [
    { name: '北汽被测平台', status: 'running', utilization: 78, icon: Cpu },
    { name: '用例执行模块', status: 'running', utilization: 92, icon: GitBranch },
    { name: '数据库', status: 'running', utilization: 45, icon: Activity },
    { name: '常规变异模块', status: 'idle', utilization: 0, icon: Zap },
    { name: 'GAN变异模块', status: 'running', utilization: 88, icon: Sparkles },
  ];

  // 获取最近任务（最多3个）
  const recentTasks = tasks.slice(0, 3).map((task: any) => {
    const progress = task.total_cases ? Math.min(100, Math.round((task.total_cases / 1000) * 100)) : 0;
    const totalCases = task.total_cases || 0;
    const traditionalCases = task.traditional_stats?.cases || 0;
    const ganCases = task.gan_stats?.cases || 0;
    const coverage = totalCases > 0 ? Math.min(100, Math.round((traditionalCases + ganCases) / totalCases * 100)) : 0;
    
    return {
      id: task.id,
      name: `任务-${task.id}`,
      status: task.status === 'running' ? '执行中' : 
              task.status === 'completed' ? '已完成' : 
              task.status === 'paused' ? '已暂停' : '等待中',
      strategy: '策略0',
      startTime: task.started_at ? new Date(task.started_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
      progress: progress,
      coverage: coverage,
      anomalies: task.total_anomalies || 0,
    };
  });

  // 如果没有任务，使用模拟数据
  const mockRecentTasks = [
    { id: '1', name: 'VCU休眠唤醒-策略2测试', status: '执行中', strategy: '策略2', startTime: '2025-11-21 09:30', progress: 65, coverage: 82, anomalies: 5 },
    { id: '2', name: 'VCU多域并发测试', status: '已完成', strategy: '策略1', startTime: '2025-11-20 14:20', progress: 100, coverage: 78, anomalies: 8 },
    { id: '3', name: 'VCU唤醒时序测试', status: '等待中', strategy: '策略3', startTime: '2025-11-21 16:00', progress: 0, coverage: 0, anomalies: 0 },
  ];
  
  const displayTasks = recentTasks.length > 0 ? recentTasks : mockRecentTasks;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500';
      case 'idle': return 'text-gray-400';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="p-6 mt-[56px]">
      {/* Welcome Section */}
      <div className="mb-8 animate-slide-down">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-3xl">智能模糊测试系统</h2>
              <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 rounded-lg text-sm">
                北汽VCU测试平台
              </span>
            </div>
            <p className="text-gray-600">数据库中心化 + 双模输入生成 + 统一执行接口 + 反馈闭环</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">系统架构版本</div>
            <div className="text-lg font-medium">v2.0 - 五模块协同</div>
          </div>
        </div>
      </div>

      {/* Core Metrics */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        {quickStats.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div
              key={index}
              className="stagger-item bg-white rounded-2xl p-6 shadow-lg hover-lift border border-gray-100 relative overflow-hidden group"
            >
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${metric.color} opacity-10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500`} />
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-br ${metric.color} rounded-xl flex items-center justify-center shadow-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs flex items-center gap-1">
                    <ArrowUpRight className="w-3 h-3" />
                    {metric.change}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-1">{metric.label}</div>
                <div className="text-3xl tracking-tight bg-gradient-to-br from-gray-900 to-gray-600 bg-clip-text text-transparent mb-1">
                  {metric.value}
                </div>
                <div className="text-xs text-gray-500">{metric.subtitle}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Core Modules Status - 软件工程：模块化架构展示 */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-8 animate-slide-up">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl mb-1">核心模块运行状态</h3>
            <p className="text-sm text-gray-500">五大模块协同工作 · 实时监控</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-50 to-green-100 rounded-xl">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-green-700">系统正常</span>
          </div>
        </div>
        <div className="grid grid-cols-5 gap-4">
          {coreModules.map((module, index) => {
            const Icon = module.icon;
            return (
              <div key={index} className="p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 hover:border-blue-300 transition-all group">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(module.status)}`} />
                </div>
                <div className="text-sm font-medium mb-2">{module.name}</div>
                <div className="text-xs text-gray-500 mb-2">负载率</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all"
                      style={{ width: `${module.utilization}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600">{module.utilization}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 软工特色：需求追溯矩阵 + 质量度量仪表盘 */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* 需求追溯矩阵 - 渐进式展示 */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Link2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg">需求追溯矩阵</h3>
                <p className="text-xs text-gray-500">需求 → 测试 → 缺陷全链路追溯</p>
              </div>
            </div>
            <button
              onClick={() => setShowTraceMatrix(!showTraceMatrix)}
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 rounded-lg text-blue-700 text-sm transition-colors"
            >
              <ChevronDown className={`w-4 h-4 transition-transform ${showTraceMatrix ? 'rotate-180' : ''}`} />
              {showTraceMatrix ? '收起' : '展开'}
            </button>
          </div>

          {/* 摘要信息 - 默认显示 */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-lg border border-blue-200">
              <div className="text-xs text-blue-600 mb-1">总需求数</div>
              <div className="text-2xl text-blue-900">15</div>
            </div>
            <div className="p-3 bg-gradient-to-br from-green-50 to-green-100/50 rounded-lg border border-green-200">
              <div className="text-xs text-green-600 mb-1">已追溯</div>
              <div className="text-2xl text-green-900">15/15</div>
            </div>
            <div className="p-3 bg-gradient-to-br from-orange-50 to-orange-100/50 rounded-lg border border-orange-200">
              <div className="text-xs text-orange-600 mb-1">覆盖率</div>
              <div className="text-2xl text-orange-900">87%</div>
            </div>
          </div>

          {/* 详细矩阵表格 - 可折叠 */}
          {showTraceMatrix && (
            <div className="mt-4 max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
              <table className="w-full text-xs">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="text-left py-2 px-3 font-medium">需求ID</th>
                    <th className="text-left py-2 px-3 font-medium">测试用例</th>
                    <th className="text-center py-2 px-3 font-medium">状态</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { id: 'REQ-001', name: 'VCU休眠功能', tests: 8, status: '通过' },
                    { id: 'REQ-002', name: 'VCU唤醒功能', tests: 12, status: '通过' },
                    { id: 'REQ-003', name: '网络管理', tests: 6, status: '进行中' },
                    { id: 'REQ-004', name: '诊断通信', tests: 10, status: '通过' },
                    { id: 'REQ-005', name: '故障处理', tests: 9, status: '通过' },
                  ].map((req) => (
                    <tr key={req.id} className="border-b border-gray-100 hover:bg-blue-50/30">
                      <td className="py-2 px-3">
                        <span className="text-blue-600 font-medium">{req.id}</span>
                      </td>
                      <td className="py-2 px-3">
                        <div>{req.name}</div>
                        <div className="text-gray-500 text-[10px]">{req.tests}个测试用例</div>
                      </td>
                      <td className="py-2 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          req.status === '通过' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {req.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* 质量度量仪表盘 - 环形进度条展示 */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg">质量度量仪表盘</h3>
              <p className="text-xs text-gray-500">关键质量指标实时监测</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* 缺陷密度 */}
            <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100/30 rounded-xl border border-blue-200 text-center group hover:shadow-md transition-shadow">
              <div className="relative inline-block mb-2">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                  <circle 
                    cx="40" cy="40" r="32" 
                    stroke="#3b82f6" 
                    strokeWidth="6" 
                    fill="none"
                    strokeDasharray="201"
                    strokeDashoffset="50"
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="text-lg text-blue-900">2.1</div>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">缺陷密度</div>
              <div className="text-[10px] text-gray-500">bugs/kLOC</div>
            </div>

            {/* 测试效率 */}
            <div className="p-4 bg-gradient-to-br from-green-50 to-green-100/30 rounded-xl border border-green-200 text-center group hover:shadow-md transition-shadow">
              <div className="relative inline-block mb-2">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                  <circle 
                    cx="40" cy="40" r="32" 
                    stroke="#10b981" 
                    strokeWidth="6" 
                    fill="none"
                    strokeDasharray="201"
                    strokeDashoffset="16"
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="text-lg text-green-900">92%</div>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">测试效率</div>
              <div className="text-[10px] text-gray-500">自动化执行率</div>
            </div>

            {/* 复现率 */}
            <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100/30 rounded-xl border border-orange-200 text-center group hover:shadow-md transition-shadow">
              <div className="relative inline-block mb-2">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                  <circle 
                    cx="40" cy="40" r="32" 
                    stroke="#f97316" 
                    strokeWidth="6" 
                    fill="none"
                    strokeDasharray="201"
                    strokeDashoffset="8"
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="text-lg text-orange-900">96%</div>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">复现率</div>
              <div className="text-[10px] text-gray-500 flex items-center justify-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                ≥90%
              </div>
            </div>

            {/* 边界验证 */}
            <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100/30 rounded-xl border border-purple-200 text-center group hover:shadow-md transition-shadow">
              <div className="relative inline-block mb-2">
                <svg className="w-20 h-20 transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                  <circle 
                    cx="40" cy="40" r="32" 
                    stroke="#8b5cf6" 
                    strokeWidth="6" 
                    fill="none"
                    strokeDasharray="201"
                    strokeDashoffset="30"
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <div className="text-lg text-purple-900">85%</div>
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">边界验证</div>
              <div className="text-[10px] text-gray-500">边界用例覆盖</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Tasks - 软件工程：可追溯性 */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden animate-slide-up">
        <div className="p-6 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl mb-1">测试任务执行记录</h3>
              <p className="text-sm text-gray-500">可追溯的测试执行历史 · 策略标注</p>
            </div>
            <button
              onClick={onCreateTest}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg transition-all duration-300 flex items-center gap-2 group"
            >
              <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              创建测试计划
            </button>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {displayTasks.map((task: any, index: number) => (
              <div
                key={task.id || index}
                className="flex items-center gap-4 p-5 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/50 transition-all group cursor-pointer"
                onClick={() => task.id && onViewMonitoring(task.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="font-medium">{task.name}</div>
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                      {task.strategy}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>开始: {task.startTime}</span>
                    <span>•</span>
                    <span>覆盖率: {task.coverage}%</span>
                    <span>•</span>
                    <span>异常数: {task.anomalies}</span>
                  </div>
                </div>
                <div>
                  <span
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      task.status === '执行中'
                        ? 'bg-blue-100 text-blue-700'
                        : task.status === '已完成'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
                <div className="w-48">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-600">进度</span>
                    <span className="text-sm font-medium">{task.progress}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-700 rounded-full transition-all duration-500"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>
                <ArrowUpRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}