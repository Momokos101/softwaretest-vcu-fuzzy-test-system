import { useEffect, useState } from 'react';
import { Play, Save } from 'lucide-react';
import { autoTestAPI } from '../services/api';

type TechniqueChoice = 'ep' | 'bva' | 'dt' | 'all';

export function TestCaseDesign() {
  const [requirements, setRequirements] = useState<any[]>([]);
  const [testCases, setTestCases] = useState<any[]>([]);
  const [selectedReqIds, setSelectedReqIds] = useState<string[]>([]);
  const [technique, setTechnique] = useState<TechniqueChoice>('all');
  const [bvaDelta, setBvaDelta] = useState(0.1);
  const [editing, setEditing] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [reqs, cases] = await Promise.all([
      autoTestAPI.getRequirements(),
      autoTestAPI.getTestCases(),
    ]);
    setRequirements((reqs as any[]).filter((req) => req.parsed));
    setTestCases(cases as any[]);
    setEditing(Object.fromEntries((cases as any[]).map((tc) => [tc.id, { ...tc }])));
  };

  const generateCases = async () => {
    if (selectedReqIds.length === 0) return;
    setLoading(true);
    try {
      const techniques = technique === 'all' ? ['ep', 'bva', 'dt'] : [technique];
      await Promise.all(
        selectedReqIds.map((requirementId) =>
          autoTestAPI.generateTestCases({
            requirement_id: requirementId,
            techniques,
            bva_delta: bvaDelta,
          })
        )
      );
      await loadData();
    } finally {
      setLoading(false);
    }
  };

  const saveCase = async (id: string) => {
    await saveCaseDraft(id);
    await loadData();
  };

  const executeAll = async () => {
    if (testCases.length === 0) return;
    setLoading(true);
    try {
      const ids = testCases.map((tc) => tc.id);
      await Promise.all(ids.map((id) => saveCaseDraft(id)));
      const results = await autoTestAPI.executeBatch(ids);
      setTestCases(results as any[]);
      setEditing(Object.fromEntries((results as any[]).map((tc) => [tc.id, { ...tc }])));
    } finally {
      setLoading(false);
    }
  };

  const executeOne = async (id: string) => {
    setLoading(true);
    try {
      await saveCaseDraft(id);
      const result = await autoTestAPI.executeTestCase(id);
      setTestCases((current) => current.map((tc) => (tc.id === id ? result : tc)));
      setEditing((current) => ({ ...current, [id]: { ...(result as any) } }));
    } finally {
      setLoading(false);
    }
  };

  const saveCaseDraft = async (id: string) => {
    const draft = editing[id];
    if (!draft) return;
    const expected = deriveExpected(draft.expected_result);
    await autoTestAPI.updateTestCase(id, {
      signal_name: draft.signal_name,
      test_value: Number(draft.test_value),
      expected_result: draft.expected_result,
      expected_status: expected.status,
      expected_vehicle_state: expected.vehicleState,
    });
  };

  const toggleRequirement = (id: string) => {
    setSelectedReqIds((current) =>
      current.includes(id) ? current.filter((reqId) => reqId !== id) : [...current, id]
    );
  };

  const selectAllRequirements = () => {
    setSelectedReqIds(requirements.map((req) => req.id));
  };

  const clearSelectedRequirements = () => {
    setSelectedReqIds([]);
  };

  const updateDraft = (id: string, key: string, value: any) => {
    setEditing((current) => ({
      ...current,
      [id]: { ...current[id], [key]: value },
    }));
  };

  const executedCases = testCases.filter((tc) => tc.execution_result);
  const vcuCounts = executedCases.reduce(
    (counts, tc) => {
      const label = vcuResultLabel(tc.execution_result?.test_status);
      counts[label] = (counts[label] || 0) + 1;
      return counts;
    },
    {} as Record<string, number>
  );

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">测试设计</h1>

      <section className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">生成测试用例</h2>
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px_160px_auto] gap-4 items-end">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="block text-sm font-medium">选择需求（可多选）</span>
              <div className="flex gap-2 text-xs">
                <button onClick={selectAllRequirements} className="text-blue-700 hover:underline">全选</button>
                <button onClick={clearSelectedRequirements} className="text-slate-600 hover:underline">清空</button>
              </div>
            </div>
            <div className="max-h-44 overflow-y-auto border rounded divide-y">
              {requirements.map((req) => (
                <label key={req.id} className="flex gap-2 p-2 hover:bg-slate-50">
                  <input
                    type="checkbox"
                    checked={selectedReqIds.includes(req.id)}
                    onChange={() => toggleRequirement(req.id)}
                    className="mt-1"
                  />
                  <span className="text-sm">
                    <span className="font-medium">{req.id.slice(0, 8)}</span>
                    <span className="ml-2 text-slate-700">{req.raw_text.slice(0, 110)}</span>
                  </span>
                </label>
              ))}
              {requirements.length === 0 && <div className="p-3 text-sm text-slate-500">暂无已解析需求</div>}
            </div>
            <div className="mt-2 text-xs text-slate-500">已选择 {selectedReqIds.length} 条需求</div>
          </div>

          <div>
            <span className="block text-sm font-medium mb-2">测试技术</span>
            <div className="inline-flex rounded border overflow-hidden">
              {(['ep', 'bva', 'dt', 'all'] as TechniqueChoice[]).map((item) => (
                <button
                  key={item}
                  onClick={() => setTechnique(item)}
                  className={`px-3 py-2 text-sm ${technique === item ? 'bg-blue-600 text-white' : 'bg-white text-slate-700'}`}
                >
                  {item.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <label>
            <span className="block text-sm font-medium mb-2">BVA Delta</span>
            <input type="number" min="0.01" step="0.01" value={bvaDelta} onChange={(event) => setBvaDelta(Number(event.target.value))} className="w-full p-2 border rounded" />
          </label>

          <button onClick={generateCases} disabled={loading || selectedReqIds.length === 0} className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">
            生成所选需求用例
          </button>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg font-semibold">测试用例列表</h2>
            {executedCases.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2 text-xs">
                <SummaryBadge label="用例判定通过" value={testCases.filter((tc) => tc.status === 'pass').length} className="bg-green-100 text-green-800" />
                <SummaryBadge label="用例判定失败" value={testCases.filter((tc) => tc.status === 'fail' || tc.status === 'error').length} className="bg-red-100 text-red-800" />
                <SummaryBadge label="VCU PASS" value={vcuCounts.PASS || 0} className="bg-blue-100 text-blue-800" />
                <SummaryBadge label="VCU FAIL" value={vcuCounts.FAIL || 0} className="bg-orange-100 text-orange-800" />
                <SummaryBadge label="VCU SLEEP" value={vcuCounts.SLEEP || 0} className="bg-slate-100 text-slate-800" />
              </div>
            )}
          </div>
          <button onClick={executeAll} disabled={loading || testCases.length === 0} className="px-4 py-2 bg-green-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-2">
            <Play className="w-4 h-4" />执行所有用例
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="p-2 text-left">技术</th>
                <th className="p-2 text-left">信号</th>
                <th className="p-2 text-left">测试值</th>
                <th className="p-2 text-left">预期</th>
                <th className="p-2 text-left">VCU输出</th>
                <th className="p-2 text-left">用例判定</th>
                <th className="p-2 text-left">状态码对比</th>
                <th className="p-2 text-left">操作</th>
              </tr>
            </thead>
            <tbody>
              {testCases.map((tc) => {
                const draft = editing[tc.id] || tc;
                const failed = tc.status === 'fail' || tc.status === 'error';
                return (
                  <tr key={tc.id} className={`border-t ${failed ? 'bg-red-50' : ''}`}>
                    <td className="p-2 font-medium">{tc.technique.toUpperCase()}</td>
                    <td className="p-2">
                      <input value={draft.signal_name} onChange={(event) => updateDraft(tc.id, 'signal_name', event.target.value)} className="w-44 p-1 border rounded" />
                    </td>
                    <td className="p-2">
                      <input type="number" value={draft.test_value} onChange={(event) => updateDraft(tc.id, 'test_value', event.target.value)} className="w-24 p-1 border rounded" />
                    </td>
                    <td className="p-2">
                      <select value={draft.expected_result} onChange={(event) => updateDraft(tc.id, 'expected_result', event.target.value)} className="p-1 border rounded">
                        <option value="PASS">PASS</option>
                        <option value="FAIL">FAIL</option>
                        <option value="SLEEP">SLEEP</option>
                      </select>
                    </td>
                    <td className="p-2">
                      {tc.execution_result ? (
                        <span className={`px-2 py-1 rounded text-xs ${vcuBadgeClass(tc.execution_result.test_status)}`}>
                          {vcuResultLabel(tc.execution_result.test_status)}
                        </span>
                      ) : (
                        <span className="text-slate-400">未执行</span>
                      )}
                    </td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs ${verdictClass(tc.status)}`}>{verdictLabel(tc.status)}</span>
                    </td>
                    <td className="p-2 min-w-[280px]">
                      {tc.execution_result ? (
                        <div className="text-xs text-slate-700">
                          <div>actual: {tc.execution_result.test_status ?? '-'} / {tc.execution_result.vehicle_state ?? '-'}</div>
                          <div>expected: {tc.expected_status} / {tc.expected_vehicle_state}</div>
                          <div className={tc.execution_result.match_expected ? 'text-green-700' : 'text-red-700'}>{tc.execution_result.detail}</div>
                        </div>
                      ) : (
                        <span className="text-slate-400">未执行</span>
                      )}
                    </td>
                    <td className="p-2">
                      <div className="flex flex-wrap gap-2">
                        <button onClick={() => saveCase(tc.id)} className="px-2 py-1 bg-slate-700 text-white rounded inline-flex items-center gap-1">
                          <Save className="w-4 h-4" />保存
                        </button>
                        <button onClick={() => executeOne(tc.id)} disabled={loading} className="px-2 py-1 bg-green-600 text-white rounded inline-flex items-center gap-1 disabled:bg-slate-400">
                          <Play className="w-4 h-4" />执行
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {testCases.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-slate-500">暂无测试用例</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function deriveExpected(expected: string) {
  if (expected === 'PASS') return { status: 1, vehicleState: 170 };
  if (expected === 'SLEEP') return { status: 3, vehicleState: 30 };
  return { status: 4, vehicleState: 30 };
}

function SummaryBadge({ label, value, className }: { label: string; value: number; className: string }) {
  return <span className={`px-2 py-1 rounded ${className}`}>{label}: {value}</span>;
}

function verdictLabel(status: string) {
  if (status === 'pass') return '通过';
  if (status === 'fail') return '失败';
  if (status === 'error') return '错误';
  return '待执行';
}

function verdictClass(status: string) {
  if (status === 'pass') return 'bg-green-100 text-green-800';
  if (status === 'fail') return 'bg-red-100 text-red-800';
  if (status === 'error') return 'bg-purple-100 text-purple-800';
  return 'bg-yellow-100 text-yellow-800';
}

function vcuResultLabel(status?: number) {
  if (status === 1) return 'PASS';
  if (status === 3) return 'SLEEP';
  if (status === 4) return 'FAIL';
  return 'UNKNOWN';
}

function vcuBadgeClass(status?: number) {
  if (status === 1) return 'bg-blue-100 text-blue-800';
  if (status === 3) return 'bg-slate-100 text-slate-800';
  if (status === 4) return 'bg-orange-100 text-orange-800';
  return 'bg-gray-100 text-gray-800';
}
