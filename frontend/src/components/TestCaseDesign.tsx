import { useEffect, useState } from 'react';
import { ChevronDown, ChevronRight, Download, Play } from 'lucide-react';
import { autoTestAPI } from '../services/api';

type TechniqueChoice = 'EP' | 'BVA' | 'DT' | 'ST' | 'SC' | 'ALL';

export function TestCaseDesign() {
  const [requirements, setRequirements] = useState<any[]>([]);
  const [testCases, setTestCases] = useState<any[]>([]);
  const [selectedReqIds, setSelectedReqIds] = useState<string[]>([]);
  const [technique, setTechnique] = useState<TechniqueChoice>('ALL');
  const [bvaDelta, setBvaDelta] = useState(0.1);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [reqs, cases] = await Promise.all([
        autoTestAPI.getRequirements(),
        autoTestAPI.getTestCases(),
      ]);
      setRequirements(Array.isArray(reqs) ? reqs.filter((r) => r.parsed) : []);
      setTestCases(Array.isArray(cases) ? cases : []);
    } catch {
      // backend unreachable — keep empty state
    }
  };

  const generateCases = async () => {
    if (selectedReqIds.length === 0) return;
    setLoading(true);
    try {
      const techniques = technique === 'ALL' ? ['EP', 'BVA', 'DT'] : [technique];
      await Promise.all(
        selectedReqIds.map((requirementId) =>
          autoTestAPI.generateTestCases({ requirement_id: requirementId, techniques, bva_delta: bvaDelta })
        )
      );
      await loadData();
    } finally {
      setLoading(false);
    }
  };

  const executeAll = async () => {
    if (testCases.length === 0) return;
    setLoading(true);
    try {
      const ids = testCases.map((tc) => tc.id);
      const results = await autoTestAPI.executeBatch(ids) as unknown as any[];
      setTestCases(results);
    } finally {
      setLoading(false);
    }
  };

  const executeOne = async (id: string) => {
    setLoading(true);
    try {
      const result = await autoTestAPI.executeTestCase(id);
      setTestCases((cur) => cur.map((tc) => (tc.id === id ? result : tc)));
    } finally {
      setLoading(false);
    }
  };

  const toggleRequirement = (id: string) =>
    setSelectedReqIds((cur) => cur.includes(id) ? cur.filter((r) => r !== id) : [...cur, id]);

  const toggleExpanded = (id: string) =>
    setExpanded((cur) => ({ ...cur, [id]: !cur[id] }));

  const executedCases = testCases.filter((tc) => tc.execution_result);
  const passCount = testCases.filter((tc) => tc.status === 'pass').length;
  const failCount = testCases.filter((tc) => tc.status === 'fail' || tc.status === 'error').length;

  const exportExcel = async () => {
    const blob = await autoTestAPI.export({
      format: 'excel',
      scope: {
        include_requirements: false,
        include_parsed_requirements: false,
        include_risk_analysis: false,
        include_coverage_items: false,
        include_strategies: false,
        include_test_cases: true,
        include_execution_results: true,
        include_traceability_matrix: false,
        include_bq_new_cases: false,
      },
    }) as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'autotestdesign_v2_test_cases.xlsx';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-8">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h1 className="text-2xl font-bold">测试设计</h1>
        <button onClick={() => void exportExcel()} className="px-3 py-2 bg-slate-800 text-white rounded inline-flex items-center gap-2">
          <Download className="w-4 h-4" />Excel
        </button>
      </div>

      <section className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">生成测试用例</h2>
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px_160px_auto] gap-4 items-end">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">选择已解析需求（可多选）</span>
              <div className="flex gap-2 text-xs">
                <button onClick={() => setSelectedReqIds(requirements.map((r) => r.id))} className="text-blue-700 hover:underline">全选</button>
                <button onClick={() => setSelectedReqIds([])} className="text-slate-600 hover:underline">清空</button>
              </div>
            </div>
            <div className="max-h-44 overflow-y-auto border rounded divide-y">
              {requirements.map((req) => (
                <label key={req.id} className="flex gap-2 p-2 hover:bg-slate-50 cursor-pointer">
                  <input type="checkbox" checked={selectedReqIds.includes(req.id)} onChange={() => toggleRequirement(req.id)} className="mt-1" />
                  <span className="text-sm">
                    <span className="font-mono font-medium text-xs">{req.id}</span>
                    <span className="ml-2 text-slate-700">{(req.title || req.raw_text || '').slice(0, 100)}</span>
                  </span>
                </label>
              ))}
              {requirements.length === 0 && <div className="p-3 text-sm text-slate-500">暂无已解析需求</div>}
            </div>
            <div className="mt-1 text-xs text-slate-500">已选 {selectedReqIds.length} 条</div>
          </div>

          <div>
            <span className="block text-sm font-medium mb-2">测试技术</span>
            <div className="inline-flex rounded border overflow-hidden flex-wrap">
              {(['EP', 'BVA', 'DT', 'ST', 'SC', 'ALL'] as TechniqueChoice[]).map((t) => (
                <button key={t} onClick={() => setTechnique(t)}
                  className={`px-3 py-2 text-sm ${technique === t ? 'bg-blue-600 text-white' : 'bg-white text-slate-700'}`}>
                  {t}
                </button>
              ))}
            </div>
          </div>

          <label>
            <span className="block text-sm font-medium mb-2">BVA Delta</span>
            <input type="number" min="0.01" step="0.01" value={bvaDelta} onChange={(e) => setBvaDelta(Number(e.target.value))} className="w-full p-2 border rounded" />
          </label>

          <button onClick={generateCases} disabled={loading || selectedReqIds.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">
            生成
          </button>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg font-semibold">测试用例列表</h2>
            <div className="text-sm text-slate-500 mt-1">共 {testCases.length} 条测试用例</div>
            {executedCases.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-1 text-xs">
                <SummaryBadge label="通过" value={passCount} className="bg-green-100 text-green-800" />
                <SummaryBadge label="失败/错误" value={failCount} className="bg-red-100 text-red-800" />
                <SummaryBadge label="待执行" value={testCases.length - executedCases.length} className="bg-yellow-100 text-yellow-800" />
              </div>
            )}
          </div>
          <button onClick={executeAll} disabled={loading || testCases.length === 0}
            className="px-4 py-2 bg-green-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-2">
            <Play className="w-4 h-4" />执行全部
          </button>
        </div>

        <div className="space-y-2">
          {testCases.map((tc, index) => {
            const actual = tc.execution_result?.actual_output;
            const resultType = actual?.result_type;
            const open = expanded[tc.id];
            return (
              <div key={tc.id} className={`border rounded ${tc.status === 'fail' || tc.status === 'error' ? 'border-red-200 bg-red-50' : ''}`}>
                <div className="flex items-center gap-3 p-3">
                  <button onClick={() => toggleExpanded(tc.id)} className="p-1 rounded hover:bg-slate-100">
                    {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </button>
                  <span className="w-8 text-xs text-slate-500 text-right">{index + 1}</span>
                  <span className="text-xs font-mono bg-slate-100 px-1.5 py-0.5 rounded">{tc.technique}</span>
                  <span className="text-sm flex-1 truncate">{tc.title}</span>
                  <span className="text-xs text-slate-500">{tc.requirement_id}</span>
                  {tc.execution_result ? (
                    <>
                      <ResultTypeBadge resultType={resultType} />
                      <VerdictBadge status={tc.status} />
                    </>
                  ) : (
                    <span className="text-xs text-slate-400 px-2 py-1">待执行</span>
                  )}
                  <button onClick={() => executeOne(tc.id)} disabled={loading}
                    className="px-2 py-1 bg-green-600 text-white rounded text-xs disabled:bg-slate-400 inline-flex items-center gap-1">
                    <Play className="w-3 h-3" />执行
                  </button>
                </div>

                {open && (
                  <div className="border-t px-4 pb-4 pt-3 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-medium mb-2 text-xs uppercase tracking-wide text-slate-500">输入数据</div>
                      <div className="space-y-1">
                        {(tc.in_data || []).map((inp: any, i: number) => (
                          <div key={i} className="flex gap-2">
                            <span className="text-slate-600 min-w-[100px]">{inp.name}</span>
                            <span className="font-mono">{inp.value}{inp.unit ? ` ${inp.unit}` : ''}</span>
                            {inp.duration != null && <span className="text-slate-400">duration={inp.duration}ms</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="font-medium mb-2 text-xs uppercase tracking-wide text-slate-500">预期输出</div>
                      <div className="space-y-1">
                        {(tc.expected_results || []).map((exp: any, i: number) => (
                          <div key={i} className="flex gap-2">
                            <span className="text-slate-600 min-w-[140px]">{exp.name}</span>
                            <span className="text-slate-400">{exp.operator}</span>
                            <span className="font-mono">{String(exp.value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    {tc.execution_result && actual && (
                      <div className="md:col-span-2">
                        <div className="font-medium mb-2 text-xs uppercase tracking-wide text-slate-500">执行结果</div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          <ResultField label="result_type" value={actual.result_type} />
                          <ResultField label="vehicle_state" value={actual.vehicle_state} />
                          <ResultField label="bus_message_flag" value={actual.bus_message_flag} />
                          <ResultField label="power_current" value={actual.power_current} />
                          <ResultField label="actual_duration" value={actual.actual_duration} />
                          <ResultField label="power_alarm_flag" value={actual.power_alarm_flag} />
                          <ResultField label="bus_off_flag" value={actual.bus_off_flag} />
                          <ResultField label="耗时(ms)" value={tc.execution_result.elapsed_ms} />
                        </div>
                        {actual.detail && (
                          <div className="mt-2 text-xs text-slate-600 bg-slate-50 rounded p-2">{actual.detail}</div>
                        )}
                        {(tc.execution_result.mismatches || []).length > 0 && (
                          <div className="mt-2 text-xs text-red-700 space-y-0.5">
                            {tc.execution_result.mismatches.map((m: string, i: number) => (
                              <div key={i}>✗ {m}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                    {tc.oracle_reasoning && (
                      <div className="md:col-span-2 text-xs text-slate-500 italic">{tc.oracle_reasoning}</div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          {testCases.length === 0 && (
            <div className="p-6 text-center text-slate-500">暂无测试用例，请先选择需求并点击"生成"</div>
          )}
        </div>
      </section>
    </div>
  );
}

function ResultField({ label, value }: { label: string; value: any }) {
  if (value === null || value === undefined) return null;
  return (
    <div className="bg-white border rounded p-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="font-mono text-sm">{String(value)}</div>
    </div>
  );
}

function ResultTypeBadge({ resultType }: { resultType?: string }) {
  const map: Record<string, string> = {
    expected: 'bg-blue-100 text-blue-800',
    error: 'bg-orange-100 text-orange-800',
    stuck: 'bg-purple-100 text-purple-800',
  };
  const cls = map[resultType ?? ''] ?? 'bg-gray-100 text-gray-700';
  return <span className={`px-2 py-0.5 rounded text-xs ${cls}`}>{resultType ?? 'unknown'}</span>;
}

function VerdictBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pass: 'bg-green-100 text-green-800',
    fail: 'bg-red-100 text-red-800',
    error: 'bg-purple-100 text-purple-800',
    pending: 'bg-yellow-100 text-yellow-800',
  };
  const labels: Record<string, string> = { pass: '通过', fail: '失败', error: '错误', pending: '待执行' };
  return <span className={`px-2 py-0.5 rounded text-xs ${map[status] ?? ''}`}>{labels[status] ?? status}</span>;
}

function SummaryBadge({ label, value, className }: { label: string; value: number; className: string }) {
  return <span className={`px-2 py-0.5 rounded ${className}`}>{label}: {value}</span>;
}
