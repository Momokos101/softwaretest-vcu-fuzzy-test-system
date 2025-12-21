import { useState, useEffect } from 'react';
import { Search, Filter, Play, Pause, Trash2, Eye, Plus, Download, FileCode, Layers, Clock, Settings, GitBranch, User, Square } from 'lucide-react';
import { testPlanAPI, testTaskAPI } from '@/services/api';
import { toast } from 'sonner';

interface TestManagementProps {
  onCreateTest: () => void;
  onViewMonitoring: (taskId: string) => void;
}

export function TestManagement({ onCreateTest, onViewMonitoring }: TestManagementProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterStrategy, setFilterStrategy] = useState('all');
  const [tests, setTests] = useState<any[]>([]);
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, plansData] = await Promise.all([
        testTaskAPI.getAll(),
        testPlanAPI.getAll()
      ]);
      
      // 合并任务和计划数据
      const mergedTests = tasksData.map((task: any) => {
        const plan = plansData.find((p: any) => p.id === task.plan_id);
        
        // 计算进度（基于total_cases，假设目标1000）
        const targetCases = 1000;
        const progress = task.total_cases ? Math.min(100, Math.round((task.total_cases / targetCases) * 100)) : 0;
        
        // 计算覆盖率（基于统计数据，这里简化处理）
        const totalCases = task.total_cases || 0;
        const traditionalCases = task.traditional_stats?.cases || 0;
        const ganCases = task.gan_stats?.cases || 0;
        const coverage = totalCases > 0 ? Math.min(100, Math.round((traditionalCases + ganCases) / totalCases * 100)) : 0;
        
        // 计算运行时长
        let duration = '-';
        if (task.started_at) {
          const startTime = new Date(task.started_at);
          const endTime = task.completed_at ? new Date(task.completed_at) : new Date();
          const diffMs = endTime.getTime() - startTime.getTime();
          const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
          const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
          if (diffHours > 0) {
            duration = `${diffHours}小时${diffMinutes}分`;
          } else {
            duration = `${diffMinutes}分`;
          }
        }
        
        return {
          id: task.id,
          name: plan?.name || `任务-${task.id}`,
          type: plan?.test_mode === 'both' ? '传统+GAN' : plan?.test_mode === 'gan' ? 'GAN' : '传统',
          status: task.status === 'running' ? 'running' : 
                  task.status === 'completed' ? 'completed' : 
                  task.status === 'paused' ? 'paused' : 
                  task.status === 'stopped' ? 'stopped' : 'pending',
          strategy: plan?.test_mode || '策略0',
          progress: progress,
          startTime: task.started_at || task.created_at || new Date().toISOString(),
          duration: duration,
          anomalies: task.total_anomalies || 0,
          coverage: coverage,
          dbcFile: plan?.constraint_config?.dbc_file_path || 'VCU_CAN_v2.3.dbc',
          dataFormat: plan?.baseline_log_path?.split('.').pop()?.toUpperCase() || 'BLF',
          requirementId: plan?.description?.match(/REQ-\d+/)?.[0] || 'REQ-001',
          configBaseline: plan?.test_mode || 'v2.0',
          createdBy: '系统',
          plan_id: task.plan_id,
        };
      });
      
      setTests(mergedTests);
      setPlans(plansData);
    } catch (error: any) {
      console.error('加载数据失败:', error);
      toast.error('加载数据失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 旧的模拟数据作为fallback
  const mockTests = [
    {
      id: 1,
      name: 'VCU休眠唤醒-策略2测试',
      type: '传统+GAN',
      status: 'running',
      strategy: '策略2',
      progress: 65,
      startTime: '2025-11-21 09:30',
      duration: '1小时32分',
      anomalies: 8,
      coverage: 82,
      dbcFile: 'VCU_CAN_v2.3.dbc',
      dataFormat: 'BLF',
      requirementId: 'REQ-001',
      configBaseline: 'v2.0',
      createdBy: '张工',
    },
    {
      id: 2,
      name: 'VCU多域并发测试',
      type: 'GAN',
      status: 'completed',
      strategy: '策略1',
      progress: 100,
      startTime: '2025-11-20 14:20',
      duration: '2小时15分',
      anomalies: 15,
      coverage: 78,
      dbcFile: 'VCU_CAN_v2.3.dbc',
      dataFormat: 'ASC',
      requirementId: 'REQ-003',
      configBaseline: 'v2.0',
      createdBy: '李工',
    },
    {
      id: 3,
      name: 'VCU唤醒时序测试',
      type: '传统',
      status: 'pending',
      strategy: '策略3',
      progress: 0,
      startTime: '2025-11-21 16:00',
      duration: '-',
      anomalies: 0,
      coverage: 0,
      dbcFile: 'VCU_CAN_v2.3.dbc',
      dataFormat: 'CSV',
      requirementId: 'REQ-002',
      configBaseline: 'v2.0',
      createdBy: '王工',
    },
    {
      id: 4,
      name: 'VCU上下电循环测试',
      type: '传统+GAN',
      status: 'paused',
      strategy: '策略0',
      progress: 45,
      startTime: '2025-11-21 08:15',
      duration: '3小时10分',
      anomalies: 12,
      coverage: 68,
      dbcFile: 'VCU_CAN_v2.3.dbc',
      dataFormat: 'BLF',
      requirementId: 'REQ-004',
      configBaseline: 'v1.9',
      createdBy: '张工',
    },
    {
      id: 5,
      name: 'VCU网络拥塞模拟测试',
      type: 'GAN',
      status: 'completed',
      strategy: '策略1',
      progress: 100,
      startTime: '2025-11-19 16:45',
      duration: '1小时48分',
      anomalies: 22,
      coverage: 91,
      dbcFile: 'VCU_CAN_v2.2.dbc',
      dataFormat: 'BLF',
      requirementId: 'REQ-003',
      configBaseline: 'v1.9',
      createdBy: '赵工',
    },
  ];

  const filteredTests = (tests.length > 0 ? tests : mockTests).filter((test) => {
    const matchesSearch = test.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || test.status === filterStatus;
    const matchesStrategy = filterStrategy === 'all' || test.strategy === filterStrategy;
    return matchesSearch && matchesStatus && matchesStrategy;
  });

  const getStatusBadge = (status: string) => {
    const styles = {
      running: 'bg-blue-50 text-blue-700 border border-blue-200',
      completed: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
      pending: 'bg-slate-50 text-slate-600 border border-slate-200',
      paused: 'bg-amber-50 text-amber-700 border border-amber-200',
      failed: 'bg-rose-50 text-rose-700 border border-rose-200',
    };

    const labels = {
      running: '执行中',
      completed: '已完成',
      pending: '等待中',
      paused: '已暂停',
      failed: '失败',
    };

    return (
      <span className={`px-3 py-1.5 rounded-lg text-sm font-medium ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    );
  };

  return (
    <div className="p-8 pt-24 bg-slate-50 min-h-screen">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl text-slate-900 mb-2">测试管理</h2>
          <p className="text-slate-600">统一执行接口 · 策略可追溯 · 数据中心化管理</p>
        </div>
        <button
          onClick={onCreateTest}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-600/20 transition-all"
        >
          <Plus className="w-5 h-5" />
          创建新测试
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="text-slate-600">总测试计划</div>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <div className="text-3xl text-slate-900 mb-1">{filteredTests.length}</div>
          <div className="text-xs text-slate-500">全生命周期管理</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="text-slate-600">执行中</div>
            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-pulse shadow-sm shadow-blue-500/50" />
          </div>
          <div className="text-3xl text-blue-600 mb-1">
            {filteredTests.filter((t) => t.status === 'running').length}
          </div>
          <div className="text-xs text-slate-500">实时监控状态</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="text-slate-600">已完成</div>
            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
              <FileCode className="w-5 h-5 text-emerald-600" />
            </div>
          </div>
          <div className="text-3xl text-emerald-600 mb-1">
            {filteredTests.filter((t) => t.status === 'completed').length}
          </div>
          <div className="text-xs text-slate-500">可生成报告</div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-md transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="text-slate-600">异常/暂停</div>
            <div className="w-2.5 h-2.5 bg-rose-500 rounded-full shadow-sm" />
          </div>
          <div className="text-3xl text-rose-600 mb-1">
            {filteredTests.filter((t) => t.status === 'failed' || t.status === 'paused').length}
          </div>
          <div className="text-xs text-slate-500">需人工介入</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜索测试计划名称..."
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all bg-slate-50"
            />
          </div>
          <div className="flex items-center gap-3">
            <Filter className="w-5 h-5 text-slate-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all bg-slate-50"
            >
              <option value="all">全部状态</option>
              <option value="running">执行中</option>
              <option value="completed">已完成</option>
              <option value="pending">等待中</option>
              <option value="paused">已暂停</option>
              <option value="failed">失败</option>
            </select>
            <select
              value={filterStrategy}
              onChange={(e) => setFilterStrategy(e.target.value)}
              className="px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all bg-slate-50"
            >
              <option value="all">全部策略</option>
              <option value="策略0">策略0 - 无约束</option>
              <option value="策略1">策略1 - 单参数</option>
              <option value="策略2">策略2 - 多参数</option>
              <option value="策略3">策略3 - 重复执行</option>
            </select>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="text-gray-500">加载中...</div>
        </div>
      )}

      {/* Test List - Clean Grid Layout */}
      {!loading && (
      <div className="space-y-3">
        {filteredTests.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            暂无测试任务，点击"创建新测试"开始
          </div>
        ) : (
        filteredTests.map((test) => (
          <div
            key={test.id}
            className="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all group"
          >
            <div className="p-6">
              {/* Header Row */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3 flex-1">
                  <h3 className="text-lg text-slate-900 font-medium">{test.name}</h3>
                  <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-xs font-medium border border-blue-200">
                    {test.type}
                  </span>
                  <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md text-xs font-medium border border-slate-200">
                    {test.strategy}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(test.status)}
                  <div className="flex items-center gap-1.5 border-l border-slate-200 pl-3">
                    <button
                      onClick={() => handleViewMonitoring(test.id)}
                      className="p-2 hover:bg-blue-50 rounded-lg transition-colors group/btn"
                      title="查看详情"
                    >
                      <Eye className="w-4 h-4 text-slate-500 group-hover/btn:text-blue-600" />
                    </button>
                    {test.status === 'running' && (
                      <button 
                        onClick={() => handlePause(test.id)}
                        className="p-2 hover:bg-amber-50 rounded-lg transition-colors group/btn" 
                        title="暂停"
                      >
                        <Pause className="w-4 h-4 text-slate-500 group-hover/btn:text-amber-600" />
                      </button>
                    )}
                    {test.status === 'paused' && (
                      <button 
                        onClick={() => handleStart(test.id)}
                        className="p-2 hover:bg-emerald-50 rounded-lg transition-colors group/btn" 
                        title="继续"
                      >
                        <Play className="w-4 h-4 text-slate-500 group-hover/btn:text-emerald-600" />
                      </button>
                    )}
                    {(test.status === 'running' || test.status === 'paused') && (
                      <button 
                        onClick={() => handleStop(test.id)}
                        className="p-2 hover:bg-red-50 rounded-lg transition-colors group/btn" 
                        title="停止"
                      >
                        <Square className="w-4 h-4 text-slate-500 group-hover/btn:text-red-600" />
                      </button>
                    )}
                    {test.status === 'completed' && (
                      <button className="p-2 hover:bg-blue-50 rounded-lg transition-colors group/btn" title="下载报告">
                        <Download className="w-4 h-4 text-slate-500 group-hover/btn:text-blue-600" />
                      </button>
                    )}
                    {test.plan_id && (
                      <button 
                        onClick={() => handleDelete(test.plan_id)}
                        className="p-2 hover:bg-rose-50 rounded-lg transition-colors group/btn" 
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4 text-slate-500 group-hover/btn:text-rose-600" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Metrics Row */}
              <div className="grid grid-cols-7 gap-6 mb-4">
                <div className="col-span-3">
                  <div className="flex items-center justify-between mb-2 text-sm">
                    <span className="text-slate-600">进度</span>
                    <span className="text-slate-900 font-medium">{test.progress}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-700 rounded-full transition-all"
                      style={{ width: `${test.progress}%` }}
                    />
                  </div>
                </div>
                
                <div className="text-center">
                  <div className="text-xs text-slate-500 mb-1">覆盖率</div>
                  <div className={`text-2xl font-semibold ${test.coverage >= 80 ? 'text-emerald-600' : 'text-slate-900'}`}>
                    {test.coverage}%
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-xs text-slate-500 mb-1">异常数</div>
                  <div className="text-2xl font-semibold text-orange-600">
                    {test.anomalies}
                  </div>
                </div>

                <div className="col-span-2 flex items-center gap-2 text-sm text-slate-600">
                  <Clock className="w-4 h-4" />
                  <div>
                    <div className="text-slate-900">{test.startTime}</div>
                    <div className="text-xs text-slate-500">运行 {test.duration}</div>
                  </div>
                </div>
              </div>

              {/* Footer Row - 软工追溯信息：需求ID、配置基线、审计信息 */}
              <div className="flex items-center gap-4 pt-4 border-t border-slate-100 text-xs">
                {/* 需求ID - Tooltip展示完整信息 */}
                <div 
                  className="flex items-center gap-1.5 px-2.5 py-1.5 bg-blue-50 text-blue-700 rounded-md border border-blue-200 hover:bg-blue-100 transition-colors cursor-help group/req"
                  title={`关联需求：${test.requirementId} - VCU相关功能测试`}
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span className="font-medium">{test.requirementId}</span>
                </div>

                {/* 配置基线 - 显示版本 */}
                <div 
                  className="flex items-center gap-1.5 px-2.5 py-1.5 bg-green-50 text-green-700 rounded-md border border-green-200 hover:bg-green-100 transition-colors cursor-help"
                  title={`配置基线版本：${test.configBaseline} (2025-11-20)`}
                >
                  <GitBranch className="w-3.5 h-3.5" />
                  <span className="font-medium">{test.configBaseline}</span>
                </div>

                {/* 创建人 - 审计信息 */}
                <div 
                  className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 text-slate-700 rounded-md border border-slate-200 hover:bg-slate-100 transition-colors cursor-help"
                  title={`创建人：${test.createdBy} | 创建时间：${test.startTime}`}
                >
                  <User className="w-3.5 h-3.5" />
                  <span className="font-medium">{test.createdBy}</span>
                </div>

                <div className="w-px h-4 bg-slate-200" />

                {/* DBC文件和数据格式 */}
                <div className="flex items-center gap-2 text-slate-600">
                  <Settings className="w-3.5 h-3.5" />
                  <span>{test.dbcFile}</span>
                </div>
                <div className="w-px h-4 bg-slate-200" />
                <div className="text-slate-600">{test.dataFormat}</div>
              </div>
            </div>
          </div>
        )))}
      </div>
      )}
    </div>
  );
}