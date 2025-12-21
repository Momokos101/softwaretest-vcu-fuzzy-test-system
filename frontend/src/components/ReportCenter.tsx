import { useState, useEffect } from 'react';
import { Download, FileText, Calendar, TrendingUp } from 'lucide-react';
import { reportAPI, testTaskAPI } from '@/services/api';
import { toast } from 'sonner';

export function ReportCenter() {
  const [reports, setReports] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const tasksData = await testTaskAPI.getAll();
      setTasks(tasksData);
      
      // 从已完成的任务生成报告列表
      const completedTasks = tasksData.filter((t: any) => t.status === 'completed');
      const reportsData = completedTasks.map((task: any, index: number) => {
        // 计算覆盖率
        const totalCases = task.total_cases || 0;
        const traditionalCases = task.traditional_stats?.cases || 0;
        const ganCases = task.gan_stats?.cases || 0;
        const coverage = totalCases > 0 ? Math.min(100, Math.round((traditionalCases + ganCases) / totalCases * 100)) : 0;
        
        return {
          id: `RPT-${String(index + 1).padStart(3, '0')}`,
          name: `任务-${task.id}测试报告`,
          date: task.completed_at ? new Date(task.completed_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
          testPlan: task.plan_id || 'TP-0000',
          coverage: coverage,
          anomalies: task.total_anomalies || 0,
          type: 'comprehensive',
          taskId: task.id,
        };
      });
      
      setReports(reportsData);
    } catch (error: any) {
      console.error('加载报告数据失败:', error);
      toast.error('加载报告数据失败: ' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 生成报告
  const handleGenerateReport = async (taskId: string) => {
    try {
      const report = await reportAPI.generate(taskId);
      toast.success('报告生成成功');
      loadData();
      return report;
    } catch (error: any) {
      toast.error('生成报告失败: ' + (error.message || '未知错误'));
    }
  };

  // 下载报告
  const handleDownloadReport = async (taskId: string, reportId: string) => {
    try {
      const blob = await reportAPI.download(taskId, 'pdf');
      // 处理blob响应
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

  // 模拟数据作为fallback
  const mockReports = [
    {
      id: 'RPT-001',
      name: 'VCU休眠唤醒测试综合报告',
      date: '2025-11-21',
      testPlan: 'TP-2045',
      coverage: 87,
      anomalies: 12,
      type: 'comprehensive',
    },
    {
      id: 'RPT-002',
      name: 'GAN vs 传统引擎对比分析',
      date: '2025-11-20',
      testPlan: 'TP-2044',
      coverage: 92,
      anomalies: 18,
      type: 'comparison',
    },
    {
      id: 'RPT-003',
      name: '约束器拦截统计周报',
      date: '2025-11-18',
      testPlan: 'Multiple',
      coverage: 95,
      anomalies: 0,
      type: 'statistics',
    },
  ];

  return (
    <div className="p-6 mt-[56px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="mb-1">报告中心</h2>
          <p className="text-sm text-gray-500">测试报告 · 对比分析 · 一键导出</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-5 mb-6">
        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">总报告数</div>
              <div className="text-3xl">{reports.length}</div>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
          <div className="text-xs text-gray-500">本月生成</div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">平均覆盖度</div>
              <div className="text-3xl">91%</div>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
          <div className="text-xs text-gray-500">持续提升</div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">发现异常</div>
              <div className="text-3xl">30</div>
            </div>
            <Calendar className="w-8 h-8 text-orange-500" />
          </div>
          <div className="text-xs text-gray-500">本月累计</div>
        </div>

        <div className="bg-white rounded-2xl p-5 shadow-lg border border-gray-100 hover-lift">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">下载次数</div>
              <div className="text-3xl">47</div>
            </div>
            <Download className="w-8 h-8 text-blue-600" />
          </div>
          <div className="text-xs text-gray-500">PDF导出</div>
        </div>
      </div>

      {/* Reports List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : (
      <div className="space-y-5">
        {(reports.length > 0 ? reports : mockReports).map((report) => (
          <div
            key={report.id}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 hover:border-blue-300 transition-all animate-fade-in"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg">{report.name}</h3>
                    <span className="text-xs text-gray-500 font-mono">{report.id}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {report.date}
                    </span>
                    <span>测试计划: {report.testPlan}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 max-w-md">
                    <div className="bg-green-50 rounded-lg p-3">
                      <div className="text-xs text-green-600 mb-1">覆盖度</div>
                      <div className="text-xl font-medium text-green-700">{report.coverage}%</div>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-3">
                      <div className="text-xs text-orange-600 mb-1">发现异常</div>
                      <div className="text-xl font-medium text-orange-700">{report.anomalies}</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="text-xs text-blue-600 mb-1">报告类型</div>
                      <div className="text-sm font-medium text-blue-700">
                        {report.type === 'comprehensive' ? '综合报告' : 
                         report.type === 'comparison' ? '对比分析' : '统计报告'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => report.taskId && handleGenerateReport(report.taskId)}
                  className="px-4 py-2.5 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-all flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  生成报告
                </button>
                <button 
                  onClick={() => report.taskId && handleDownloadReport(report.taskId, report.id)}
                  className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-600/20 transition-all flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  下载PDF
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      )}
    </div>
  );
}