import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Plus, Edit, Trash2, TrendingUp, XCircle, CheckCircle } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { Toggle } from './Toggle';
import { constraintAPI, testTaskAPI } from '@/services/api';
import { toast } from 'sonner';

interface ConstraintManagerProps {
  taskId?: string;
}

export function ConstraintManager({ taskId }: ConstraintManagerProps = {}) {
  const [activeTab, setActiveTab] = useState('rules');
  const [constraintStats, setConstraintStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // 加载约束统计
  useEffect(() => {
    if (taskId) {
      loadConstraintStats();
    }
  }, [taskId]);

  const loadConstraintStats = async () => {
    try {
      setLoading(true);
      const stats = await constraintAPI.getStats(taskId!);
      setConstraintStats(stats);
    } catch (error: any) {
      console.error('加载约束统计失败:', error);
      toast.error('加载约束统计失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 约束规则列表
  const constraintRules = [
    {
      id: 'CR-001',
      name: '信号白名单检查',
      type: 'whitelist',
      enabled: true,
      priority: 'high',
      hitRate: 15,
      description: '仅允许DBC定义的合法信号ID',
    },
    {
      id: 'CR-002',
      name: '功能安全禁发列表',
      type: 'blacklist',
      enabled: true,
      priority: 'critical',
      hitRate: 3,
      description: '禁止发送安全关键信号（刹车、转向等）',
    },
    {
      id: 'CR-003',
      name: '数值物理范围检查',
      type: 'range',
      enabled: true,
      priority: 'high',
      hitRate: 28,
      description: '检查信号值是否在物理范围内',
    },
    {
      id: 'CR-004',
      name: 'CRC校验规则',
      type: 'crc',
      enabled: true,
      priority: 'medium',
      hitRate: 8,
      description: '验证CRC校验和正确性',
    },
    {
      id: 'CR-005',
      name: '计数器连续性检查',
      type: 'counter',
      enabled: true,
      priority: 'medium',
      hitRate: 5,
      description: '检查报文计数器递增规律',
    },
    {
      id: 'CR-006',
      name: 'DLC长度验证',
      type: 'dlc',
      enabled: true,
      priority: 'high',
      hitRate: 12,
      description: '验证数据长度符合DBC定义',
    },
    {
      id: 'CR-007',
      name: '发送速率限制',
      type: 'rate',
      enabled: true,
      priority: 'medium',
      hitRate: 6,
      description: '限制报文发送频率上限',
    },
  ];

  // 拦截统计数据（从API获取或使用模拟数据）
  const interceptionStats = constraintStats?.interception_reasons ? (() => {
    // 后端返回的是Dict[str, int]，需要转换为数组格式
    const reasons = constraintStats.interception_reasons;
    const total = Object.values(reasons).reduce((sum: number, count: any) => sum + count, 0);
    
    return Object.entries(reasons).map(([reason, count]: [string, any]) => ({
      reason: reason,
      count: count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
    }));
  })() : [
    { reason: '范围越界', count: 856, percentage: 35 },
    { reason: '白名单拦截', count: 458, percentage: 19 },
    { reason: 'DLC不匹配', count: 367, percentage: 15 },
    { reason: '功能安全', count: 289, percentage: 12 },
    { reason: 'CRC错误', count: 245, percentage: 10 },
    { reason: '速率超限', count: 183, percentage: 7 },
    { reason: '其他', count: 52, percentage: 2 },
  ];

  const interceptionTrend = [
    { date: '11-15', traditional: 45, gan: 128 },
    { date: '11-16', traditional: 52, gan: 156 },
    { date: '11-17', traditional: 38, gan: 142 },
    { date: '11-18', traditional: 61, gan: 178 },
    { date: '11-19', traditional: 43, gan: 165 },
    { date: '11-20', traditional: 58, gan: 189 },
    { date: '11-21', traditional: 47, gan: 172 },
  ];

  const pieColors = ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#8b5cf6', '#ec4899', '#6b7280'];

  const getPriorityBadge = (priority: string) => {
    const styles = {
      critical: 'bg-red-100 text-red-700',
      high: 'bg-orange-100 text-orange-700',
      medium: 'bg-yellow-100 text-yellow-700',
      low: 'bg-blue-100 text-blue-700',
    };
    const labels = {
      critical: '严重',
      high: '高',
      medium: '中',
      low: '低',
    };
    return (
      <span className={`px-2 py-1 rounded text-sm ${styles[priority as keyof typeof styles]}`}>
        {labels[priority as keyof typeof labels]}
      </span>
    );
  };

  return (
    <div className="p-6 mt-[56px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="mb-1">统一约束器管理</h2>
          <p className="text-sm text-gray-500">系统安全护栏 · 合规性校验 · 拦截统计分析</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg transition-all">
          <Plus className="w-5 h-5" />
          添加约束规则
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-5 mb-6">
        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">总规则数</div>
              <div className="text-3xl">{constraintRules.length}</div>
            </div>
            <Shield className="w-8 h-8 text-blue-500" />
          </div>
          <div className="text-xs text-gray-500">
            启用 {constraintRules.filter(r => r.enabled).length} / {constraintRules.length}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">今日拦截总数</div>
              <div className="text-3xl">
                {constraintStats ? constraintStats.total_intercepted?.toLocaleString() || '0' : '2,450'}
              </div>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
          <div className="flex items-center gap-1 text-xs text-red-600">
            <TrendingUp className="w-3 h-3" />
            <span>+12% vs 昨日</span>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">通过率</div>
              <div className="text-3xl">
                {constraintStats && constraintStats.total_passed && constraintStats.total_intercepted
                  ? `${Math.round((constraintStats.total_passed / (constraintStats.total_passed + constraintStats.total_intercepted)) * 100)}%`
                  : '73.5%'}
              </div>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <div className="text-xs text-gray-500">
            {constraintStats 
              ? `${constraintStats.total_passed || 0} / ${(constraintStats.total_passed || 0) + (constraintStats.total_intercepted || 0)} 通过`
              : '6,835 / 9,285 通过'}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">平均延迟</div>
              <div className="text-3xl">0.8ms</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-500" />
          </div>
          <div className="text-xs text-green-600">性能良好</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('rules')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'rules'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            约束规则配置
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'stats'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            拦截统计分析
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`pb-3 px-2 transition-colors ${
              activeTab === 'logs'
                ? 'border-b-2 border-blue-600 text-blue-600 font-medium'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            实时拦截日志
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'rules' && (
            <div className="space-y-4 animate-fade-in">
              <div className="mb-4">
                <h3 className="text-lg mb-2">约束规则列表</h3>
                <p className="text-sm text-gray-500">配置和管理所有出站测试序列的安全校验规则</p>
              </div>

              {constraintRules.map((rule) => (
                <div
                  key={rule.id}
                  className="p-5 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 hover:border-blue-300 transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        rule.enabled ? 'bg-green-100' : 'bg-gray-100'
                      }`}>
                        <Shield className={`w-5 h-5 ${rule.enabled ? 'text-green-600' : 'text-gray-400'}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{rule.name}</span>
                          <span className="text-xs text-gray-500 font-mono">{rule.id}</span>
                        </div>
                        <div className="text-sm text-gray-600">{rule.description}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getPriorityBadge(rule.priority)}
                      <div className="text-right mr-4">
                        <div className="text-sm text-gray-600">今日触发</div>
                        <div className="text-lg font-medium">{rule.hitRate}次</div>
                      </div>
                      <Toggle
                        checked={rule.enabled}
                        onChange={() => {}}
                        size="sm"
                      />
                      <button className="p-2 hover:bg-blue-50 rounded-lg transition-colors">
                        <Edit className="w-4 h-4 text-blue-600" />
                      </button>
                      <button className="p-2 hover:bg-red-100 rounded-lg transition-colors">
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="space-y-6 animate-fade-in">
              <div className="grid grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div>
                  <h3 className="text-lg mb-4">拦截原因分布</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={interceptionStats}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name} ${percentage}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {interceptionStats.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Bar Chart */}
                <div>
                  <h3 className="text-lg mb-4">拦截趋势（双模对比）</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={interceptionTrend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="traditional" name="传统引擎" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="gan" name="GAN引擎" fill="#10b981" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Detailed Stats Table */}
              <div>
                <h3 className="text-lg mb-4">详细拦截统计</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                        <th className="text-left py-3 px-4">拦截原因</th>
                        <th className="text-left py-3 px-4">拦截次数</th>
                        <th className="text-left py-3 px-4">占比</th>
                        <th className="text-left py-3 px-4">趋势</th>
                      </tr>
                    </thead>
                    <tbody>
                      {interceptionStats.map((stat, index) => (
                        <tr key={index} className="border-b border-gray-100 hover:bg-blue-50/30">
                          <td className="py-3 px-4">{stat.reason}</td>
                          <td className="py-3 px-4 font-medium">{stat.count.toLocaleString()}</td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                                <div
                                  className="bg-gradient-to-r from-blue-600 to-blue-700 h-2 rounded-full"
                                  style={{ width: `${stat.percentage}%` }}
                                />
                              </div>
                              <span className="text-sm">{stat.percentage}%</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-sm text-green-600 flex items-center gap-1">
                              <TrendingUp className="w-4 h-4" />
                              +{Math.floor(Math.random() * 20)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="animate-fade-in">
              <h3 className="text-lg mb-4">实时拦截日志</h3>
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 text-green-400 rounded-xl p-6 h-[500px] overflow-y-auto font-mono text-sm">
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:15] [范围越界] 信号 VCU_SpeedReq 值 255 超出范围 [0-200]</div>
                <div className="mb-2 text-red-400">[2025-11-21 14:32:14] [功能安全] 禁止发送 BrakeCommand 信号</div>
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:13] [DLC不匹配] 报文 0x123 DLC=6 与义不符（期望8）</div>
                <div className="mb-2 text-green-400">[2025-11-21 14:32:12] [通过] 报文 0x456 校验通过</div>
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:11] [CRC错误] 报文 0x789 CRC校验失败</div>
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:10] [速率超限] 报文 0x234 发送频率 120Hz 超限（上限100Hz）</div>
                <div className="mb-2 text-green-400">[2025-11-21 14:32:09] [通过] 报文 0x345 校验通过</div>
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:08] [白名单拦] 知号 ID 0xFFF</div>
                <div className="mb-2 text-green-400">[2025-11-21 14:32:07] [通过] 报文 0x567 校验通过</div>
                <div className="mb-2 text-yellow-400">[2025-11-21 14:32:06] [计数器] 报文 0x678 计数器跳变</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}