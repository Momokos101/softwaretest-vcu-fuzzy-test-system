import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, AlertCircle, Target, Fingerprint, RotateCcw } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { testTaskAPI } from '@/services/api';
import { toast } from 'sonner';

interface ResultAnalysisProps {
  taskId?: string;
}

export function ResultAnalysis({ taskId }: ResultAnalysisProps = {}) {
  const [timeRange, setTimeRange] = useState('7d');
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载数据
  useEffect(() => {
    if (taskId) {
      loadAnalysisData();
    }
  }, [taskId, timeRange]);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      const [anomaliesData, metricsData] = await Promise.all([
        testTaskAPI.getAnomalies(taskId!, { top_n: 10 }),
        testTaskAPI.getMetrics(taskId!, 100)
      ]);
      
      setAnomalies(anomaliesData);
      setMetrics(metricsData);
    } catch (error: any) {
      console.error('加载分析数据失败:', error);
      toast.error('加载分析数据失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  const performanceTrend = [
    { date: '11-15', traditional: 8, gan: 15, coverage: 65 },
    { date: '11-16', traditional: 12, gan: 22, coverage: 68 },
    { date: '11-17', traditional: 10, gan: 28, coverage: 72 },
    { date: '11-18', traditional: 15, gan: 35, coverage: 75 },
    { date: '11-19', traditional: 11, gan: 31, coverage: 78 },
    { date: '11-20', traditional: 14, gan: 38, coverage: 82 },
    { date: '11-21', traditional: 13, gan: 42, coverage: 85 },
  ];

  const anomalyTypes = [
    { name: '内存泄漏', value: 28, color: '#ef4444' },
    { name: '空指针异常', value: 22, color: '#f97316' },
    { name: '死锁', value: 18, color: '#eab308' },
    { name: '竞态条件', value: 15, color: '#3b82f6' },
    { name: '其他', value: 17, color: '#8b5cf6' },
  ];

  const engineComparison = [
    { metric: '用例生成速度', traditional: 450, gan: 620 },
    { metric: '异常检出率', traditional: 32, gan: 68 },
    { metric: '代码覆盖率', traditional: 68, gan: 85 },
    { metric: '误报率', traditional: 15, gan: 8 },
  ];

  // 处理异常数据
  const topAnomalies = anomalies.length > 0 ? anomalies.map((anomaly: any, index: number) => {
    // 映射严重等级
    const severityMap: { [key: number]: string } = {
      5: '严重',
      4: '高',
      3: '中',
      2: '低',
      1: '轻微'
    };
    
    return {
      id: anomaly.id || `ANO-${index + 1}`,
      type: anomaly.anomaly_type || '未知异常',
      severity: severityMap[anomaly.severity] || '未知',
      location: anomaly.context?.location || anomaly.context?.code_location || '未知位置',
      occurrences: 1, // 后端没有occurrences字段，默认为1
      engine: anomaly.source === 'gan' ? 'GAN' : '传统',
      strategy: '策略0', // 后端没有strategy字段
      reproducibility: anomaly.reproducible ? '100%' : '0%',
    };
  }) : [
    {
      id: 'ANO-2021',
      type: '内存泄漏',
      severity: '高',
      location: 'VCU/sleep_wake.c:245',
      occurrences: 12,
      engine: 'GAN',
      strategy: '策略1',
      reproducibility: '92%',
    },
    {
      id: 'ANO-2018',
      type: '空指针异常',
      severity: '严重',
      location: 'VCU/network_handler.c:178',
      occurrences: 8,
      engine: '传统',
      strategy: '策略2',
      reproducibility: '100%',
    },
    {
      id: 'ANO-2025',
      type: '死锁',
      severity: '高',
      location: 'VCU/thread_manager.c:92',
      occurrences: 7,
      engine: 'GAN',
      strategy: '策略1',
      reproducibility: '78%',
    },
    {
      id: 'ANO-2015',
      type: '竞态条件',
      severity: '中',
      location: 'VCU/data_sync.c:334',
      occurrences: 6,
      engine: 'GAN',
      strategy: '策略0',
      reproducibility: '65%',
    },
    {
      id: 'ANO-2030',
      type: '缓冲区溢出',
      severity: '严重',
      location: 'VCU/input_parser.c:56',
      occurrences: 5,
      engine: '传统',
      strategy: '策略3',
      reproducibility: '100%',
    },
  ];

  const getSeverityBadge = (severity: string) => {
    const styles = {
      严重: 'bg-red-100 text-red-700',
      高: 'bg-orange-100 text-orange-700',
      中: 'bg-yellow-100 text-yellow-700',
      低: 'bg-blue-100 text-blue-700',
    };
    return (
      <span className={`px-2 py-1 rounded text-sm ${styles[severity as keyof typeof styles]}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="p-6 mt-[56px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="mb-1">结果分析</h2>
          <p className="text-sm text-gray-500">测试策略评估 · 异常指纹管理 · 复现率追踪</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">时间范围：</span>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 transition-colors"
          >
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
            <option value="90d">最近90天</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-5 mb-6">
        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">异常指纹总数</div>
              <div className="text-3xl">156</div>
            </div>
            <Fingerprint className="w-8 h-8 text-red-500" />
          </div>
          <div className="flex items-center gap-1 text-sm text-green-600">
            <TrendingUp className="w-4 h-4" />
            <span>去重后30条有效</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">平均信号覆盖率</div>
              <div className="text-3xl">78.5%</div>
            </div>
            <Target className="w-8 h-8 text-blue-500" />
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <span>字段级 + 时序覆盖</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">平均复现率</div>
              <div className="text-3xl">87%</div>
            </div>
            <RotateCcw className="w-8 h-8 text-green-500" />
          </div>
          <div className="flex items-center gap-1 text-sm text-green-600">
            <TrendingUp className="w-4 h-4" />
            <span>测试策略稳定</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">误报率</div>
              <div className="text-3xl">8.3%</div>
            </div>
            <TrendingDown className="w-8 h-8 text-orange-500" />
          </div>
          <div className="flex items-center gap-1 text-sm text-green-600">
            <TrendingDown className="w-4 h-4" />
            <span>-3.1% vs 上周</span>
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="mb-4">异常检出趋势</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={performanceTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="traditional"
                name="传统引擎"
                stroke="#3b82f6"
                strokeWidth={2}
              />
              <Line type="monotone" dataKey="gan" name="GAN引擎" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="mb-4">异常类型分布</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={anomalyTypes}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {anomalyTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Engine Comparison */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 mb-6">
        <h3 className="mb-4">引擎性能对比</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={engineComparison}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="metric" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip />
            <Legend />
            <Bar dataKey="traditional" name="传统引擎" fill="#3b82f6" />
            <Bar dataKey="gan" name="GAN引擎" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Anomalies - 重新设计的现代化表格 */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mt-6">
        <div className="mb-6">
          <h3 className="text-xl mb-1">异常指纹详细列表</h3>
          <p className="text-sm text-gray-500">去重后的有效异常 · 策略标注 · 复现率追踪</p>
        </div>
        
        {/* 现代化卡片式表格 */}
        <div className="space-y-3">
          {topAnomalies.map((anomaly) => (
            <div
              key={anomaly.id}
              className="border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all overflow-hidden bg-gradient-to-r from-white to-slate-50/30"
            >
              <div className="p-5">
                {/* Header Row */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="font-mono text-sm text-slate-700 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
                      {anomaly.id}
                    </div>
                    <div className="text-base font-medium text-slate-900">{anomaly.type}</div>
                    {getSeverityBadge(anomaly.severity)}
                  </div>
                  <button className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-4 py-2 rounded-lg text-sm font-medium transition-all">
                    查看详情
                  </button>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-6 gap-4 mb-3">
                  <div className="col-span-2">
                    <div className="text-xs text-slate-500 mb-1">代码位置</div>
                    <div className="font-mono text-sm text-slate-700 bg-slate-50 px-3 py-1.5 rounded border border-slate-200">
                      {anomaly.location}
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-xs text-slate-500 mb-1">出现次数</div>
                    <div className="text-2xl font-semibold text-red-600">
                      {anomaly.occurrences}
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-slate-500 mb-1">检出引擎</div>
                    <span className={`inline-block px-3 py-1 rounded-lg text-sm font-medium ${
                      anomaly.engine === 'GAN' 
                        ? 'bg-green-100 text-green-700 border border-green-200' 
                        : 'bg-blue-100 text-blue-700 border border-blue-200'
                    }`}>
                      {anomaly.engine}
                    </span>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-slate-500 mb-1">测试策略</div>
                    <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium border border-blue-200">
                      {anomaly.strategy}
                    </span>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-slate-500 mb-1">复现率</div>
                    <div className={`text-2xl font-semibold ${
                      parseInt(anomaly.reproducibility) >= 80 ? 'text-green-600' : 'text-orange-600'
                    }`}>
                      {anomaly.reproducibility}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}