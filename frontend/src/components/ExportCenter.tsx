import { useState } from 'react';
import { Download } from 'lucide-react';
import { autoTestAPI } from '../services/api';

export function ExportCenter() {
  const [format, setFormat] = useState<'json' | 'csv' | 'excel'>('excel');
  const [scope, setScope] = useState({
    include_requirements: true,
    include_risk_analysis: true,
    include_test_cases: true,
    include_execution_results: true,
    include_ep_cases: true,
    include_bva_cases: true,
    include_dt_cases: true,
    include_traceability_matrix: true
  });
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const blob = await autoTestAPI.export({ format, scope }) as Blob;

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export_${Date.now()}.${format === 'excel' ? 'xlsx' : format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">导出中心</h1>

      <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
        <div className="mb-6">
          <label className="block text-sm font-medium mb-3">导出格式</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="json"
                checked={format === 'json'}
                onChange={(e) => setFormat(e.target.value as any)}
                className="mr-2"
              />
              JSON
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="csv"
                checked={format === 'csv'}
                onChange={(e) => setFormat(e.target.value as any)}
                className="mr-2"
              />
              CSV
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="excel"
                checked={format === 'excel'}
                onChange={(e) => setFormat(e.target.value as any)}
                className="mr-2"
              />
              Excel
            </label>
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-3">导出范围</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Checkbox label="需求数据" checked={scope.include_requirements} onChange={(checked) => setScope({...scope, include_requirements: checked})} />
            <Checkbox label="风险分析结果" checked={scope.include_risk_analysis} onChange={(checked) => setScope({...scope, include_risk_analysis: checked})} />
            <Checkbox label="测试用例" checked={scope.include_test_cases} onChange={(checked) => setScope({...scope, include_test_cases: checked})} />
            <Checkbox label="执行结果" checked={scope.include_execution_results} onChange={(checked) => setScope({...scope, include_execution_results: checked})} />
            <Checkbox label="EP用例" checked={scope.include_ep_cases} onChange={(checked) => setScope({...scope, include_ep_cases: checked})} />
            <Checkbox label="BVA用例" checked={scope.include_bva_cases} onChange={(checked) => setScope({...scope, include_bva_cases: checked})} />
            <Checkbox label="DT用例" checked={scope.include_dt_cases} onChange={(checked) => setScope({...scope, include_dt_cases: checked})} />
            <Checkbox label="追踪矩阵" checked={scope.include_traceability_matrix} onChange={(checked) => setScope({...scope, include_traceability_matrix: checked})} />
          </div>
        </div>

        <button
          onClick={handleExport}
          disabled={loading}
          className="w-full px-4 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 inline-flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          {loading ? '导出中...' : '导出'}
        </button>
      </div>
    </div>
  );
}

function Checkbox({ label, checked, onChange }: { label: string; checked: boolean; onChange: (checked: boolean) => void }) {
  return (
    <label className="flex items-center">
              <input
                type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
                className="mr-2"
              />
      {label}
    </label>
  );
}
