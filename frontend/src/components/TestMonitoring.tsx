import { useState, useEffect } from 'react';
import { ArrowLeft, Pause, Square, Play, Zap, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { testTaskAPI } from '@/services/api';
import wsManager from '@/utils/websocket';
import { toast } from 'sonner';

interface TestMonitoringProps {
  taskId: string;
  onBack: () => void;
}

const comparisonData = [
  { metric: '用例生成', traditional: 450, gan: 380 },
  { metric: '异常触发', traditional: 13, gan: 42 },
  { metric: '代码覆盖', traditional: 68, gan: 85 },
  { metric: '执行效率', traditional: 72, gan: 88 },
];

export function TestMonitoring({ taskId, onBack }: TestMonitoringProps) {
  const [task, setTask] = useState<any>(null);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [status, setStatus] = useState<'running' | 'paused' | 'stopped'>('running');
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载任务数据
  useEffect(() => {
    if (taskId) {
      loadTaskData();
      // 连接WebSocket
      wsManager.connect(taskId, handleWebSocketMessage, handleWebSocketError);
      return () => {
        wsManager.close();
      };
    }
  }, [taskId]);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      const [taskData, metricsData] = await Promise.all([
        testTaskAPI.getById(taskId),
        testTaskAPI.getMetrics(taskId, 100)
      ]);
      
      setTask(taskData);
      setMetrics(metricsData);
      setStatus(taskData.status === 'running' ? 'running' : 
                taskData.status === 'paused' ? 'paused' : 'stopped');
    } catch (error: any) {
      console.error('加载任务数据失败:', error);
      toast.error('加载任务数据失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'metrics_update') {
      setMetrics((prev) => [data.metrics, ...prev].slice(0, 100));
    }
    if (data.type === 'log') {
      setLogs((prev) => [{
        time: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
        source: data.source || '系统',
        message: data.message || '',
      }, ...prev].slice(0, 20));
    }
    if (data.type === 'task_status_update') {
      setStatus(data.status);
    }
  };

  const handleWebSocketError = (error: any) => {
    console.error('WebSocket错误:', error);
  };

  // 处理任务控制
  const handlePause = async () => {
    try {
      await testTaskAPI.pause(taskId);
      setStatus('paused');
      toast.success('任务已暂停');
    } catch (error: any) {
      toast.error('暂停任务失败: ' + (error.message || '未知错误'));
    }
  };

  const handleResume = async () => {
    try {
      await testTaskAPI.start(taskId);
      setStatus('running');
      toast.success('任务已继续');
    } catch (error: any) {
      toast.error('继续任务失败: ' + (error.message || '未知错误'));
    }
  };

  const handleStop = async () => {
    try {
      await testTaskAPI.stop(taskId);
      setStatus('stopped');
      toast.success('任务已停止');
    } catch (error: any) {
      toast.error('停止任务失败: ' + (error.message || '未知错误'));
    }
  };

  // 计算对比数据
  const comparisonData = task ? [
    { 
      metric: '用例生成', 
      traditional: task.traditional_stats?.cases || 0,
      gan: task.gan_stats?.cases || 0
    },
    { 
      metric: '异常触发', 
      traditional: task.traditional_stats?.anomalies || 0,
      gan: task.gan_stats?.anomalies || 0
    },
    { 
      metric: '代码覆盖', 
      traditional: task.total_cases > 0 ? Math.round(((task.traditional_stats?.cases || 0) / task.total_cases) * 100) : 0,
      gan: task.total_cases > 0 ? Math.round(((task.gan_stats?.cases || 0) / task.total_cases) * 100) : 0
    },
    { 
      metric: '执行效率', 
      traditional: task.traditional_stats?.anomaly_rate ? Math.round(task.traditional_stats.anomaly_rate * 100) : 0, 
      gan: task.gan_stats?.anomaly_rate ? Math.round(task.gan_stats.anomaly_rate * 100) : 0
    },
  ] : [
    { metric: '用例生成', traditional: 450, gan: 380 },
    { metric: '异常触发', traditional: 13, gan: 42 },
    { metric: '代码覆盖', traditional: 68, gan: 85 },
    { metric: '执行效率', traditional: 72, gan: 88 },
  ];

  return (
    <div className="p-6 mt-[56px]">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-6 transition-colors group"
      >
        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        返回仪表盘
      </button>

      {/* Task Header */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-6 animate-slide-down">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl mb-1">测试任务 {task?.id || ''}</h2>
              <div className="flex items-center gap-3">
                <span
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-2 ${
                    status === 'running'
                      ? 'bg-green-100 text-green-700'
                      : status === 'paused'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {status === 'running' && <Activity className="w-4 h-4 animate-pulse" />}
                  {status === 'running' ? '运行中' : status === 'paused' ? '已暂停' : '已停止'}
                </span>
                <span className="text-sm text-gray-500">
                  开始于 {task?.started_at ? new Date(task.started_at).toLocaleString('zh-CN') : '-'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            {status === 'running' ? (
              <button
                onClick={handlePause}
                className="flex items-center gap-2 px-5 py-2.5 border-2 border-gray-300 rounded-xl hover:border-yellow-400 hover:bg-yellow-50 transition-all"
              >
                <Pause className="w-5 h-5" />
                暂停
              </button>
            ) : status === 'paused' ? (
              <button
                onClick={handleResume}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:shadow-lg transition-all"
              >
                <Play className="w-5 h-5" />
                继续
              </button>
            ) : null}
            <button
              onClick={handleStop}
              disabled={status === 'stopped'}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Square className="w-5 h-5" />
              紧急停止
            </button>
          </div>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-6 hover-lift animate-slide-up">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl mb-1">双引擎指标对比</h3>
            <p className="text-sm text-gray-500">实时性能数据分析</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={comparisonData} key={comparisonData.length}>
            <defs>
              <linearGradient id="barTraditional" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.4}/>
              </linearGradient>
              <linearGradient id="barGan" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="100%" stopColor="#10b981" stopOpacity={0.4}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="metric" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: 'none', 
                borderRadius: '12px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
            <Bar dataKey="traditional" name="传统引擎" fill="url(#barTraditional)" radius={[8, 8, 0, 0]} />
            <Bar dataKey="gan" name="GAN引擎" fill="url(#barGan)" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Real-time Logs */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden animate-slide-up">
        <div className="p-6 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl mb-1">实时日志</h3>
              <p className="text-sm text-gray-500">系统运行详细记录</p>
            </div>
            <button
              onClick={() => setLogs([])}
              className="text-sm px-4 py-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
            >
              清空日志
            </button>
          </div>
        </div>
        <div className="p-6">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 text-green-400 rounded-xl p-6 h-[320px] overflow-y-auto font-mono text-sm shadow-inner">
            {logs.map((log, index) => (
              <div key={index} className="mb-2 animate-slide-right" style={{ animationDelay: `${index * 0.05}s` }}>
                <span className="text-gray-500">2025-11-21 {log.time}</span>{' '}
                <span className={`${
                  log.source === 'GAN引擎' ? 'text-green-400' : 
                  log.source === '传统引擎' ? 'text-blue-400' : 
                  'text-cyan-400'
                }`}>[{log.source}]</span>{' '}
                <span className="text-gray-300">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}