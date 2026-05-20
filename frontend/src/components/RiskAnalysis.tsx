import { useEffect, useState } from 'react';
import { Scatter, ScatterChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { SlidersHorizontal } from 'lucide-react';
import { autoTestAPI } from '../services/api';

const dimensionLabels: Record<string, string> = {
  criticality: 'Criticality',
  boundary_sensitivity: 'Boundary',
  complexity: 'Complexity',
  state_impact: 'State Impact',
  testability: 'Testability',
};

export function RiskAnalysis() {
  const [requirements, setRequirements] = useState<any[]>([]);
  const [riskResults, setRiskResults] = useState<any[]>([]);
  const [editing, setEditing] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [reqs, risks] = await Promise.all([
      autoTestAPI.getRequirements(),
      autoTestAPI.getRiskMatrix(),
    ]);
    setRequirements(reqs as any[]);
    setRiskResults(risks as any[]);
  };

  const analyzeRisk = async (req: any) => {
    setLoading(true);
    try {
      if (!req.parsed) await autoTestAPI.parseRequirement(req.id);
      await autoTestAPI.analyzeRisk(req.id);
      await loadData();
    } finally {
      setLoading(false);
    }
  };

  const openAdjust = (result: any) => {
    setEditing({ requirement_id: result.requirement_id, dimensions: { ...result.dimensions } });
  };

  const saveAdjust = async () => {
    if (!editing) return;
    await autoTestAPI.adjustRisk(editing.requirement_id, editing.dimensions);
    setEditing(null);
    await loadData();
  };

  const resultByReq = Object.fromEntries(riskResults.map((risk) => [risk.requirement_id, risk]));
  const matrixData = riskResults.map((risk) => ({
    x: risk.dimensions.boundary_sensitivity,
    y: risk.dimensions.criticality,
    z: risk.total_score,
    name: risk.requirement_id.slice(0, 8),
    priority: risk.priority,
  }));

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">风险分析</h1>

      <section className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">风险矩阵</h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 16, right: 24, bottom: 16, left: 8 }}>
              <CartesianGrid />
              <XAxis type="number" dataKey="x" domain={[0, 10]} name="Boundary" />
              <YAxis type="number" dataKey="y" domain={[0, 10]} name="Criticality" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={matrixData} fill="#2563eb" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">需求风险列表</h2>
        <div className="space-y-3">
          {requirements.map((req) => {
            const risk = resultByReq[req.id];
            return (
              <div key={req.id} className="border rounded p-4">
                <div className="flex justify-between gap-4">
                  <div className="flex-1">
                    <div className="text-xs text-slate-500">{req.id}</div>
                    <div className="mt-1">{req.raw_text}</div>
                    {risk && (
                      <div className="grid grid-cols-2 md:grid-cols-6 gap-2 mt-3 text-sm">
                        <Metric label="Score" value={risk.total_score.toFixed(2)} />
                        <Metric label="Priority" value={risk.priority} highlight={priorityClass(risk.priority)} />
                        {Object.keys(dimensionLabels).map((key) => (
                          <Metric key={key} label={dimensionLabels[key]} value={risk.dimensions[key].toFixed(1)} />
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 items-start">
                    <button onClick={() => analyzeRisk(req)} disabled={loading} className="px-3 py-2 bg-blue-600 text-white rounded text-sm disabled:bg-slate-400">
                      分析
                    </button>
                    {risk && (
                      <button onClick={() => openAdjust(risk)} className="px-3 py-2 bg-slate-700 text-white rounded text-sm inline-flex items-center gap-1">
                        <SlidersHorizontal className="w-4 h-4" />调整
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
          {requirements.length === 0 && <div className="text-slate-500">暂无需求</div>}
        </div>
      </section>

      {editing && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-[520px] p-6">
            <h3 className="text-lg font-semibold mb-4">调整风险分值</h3>
            <div className="space-y-3">
              {Object.keys(dimensionLabels).map((key) => (
                <label key={key} className="grid grid-cols-[140px_1fr_60px] gap-3 items-center">
                  <span className="text-sm">{dimensionLabels[key]}</span>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={editing.dimensions[key]}
                    onChange={(event) => setEditing({
                      ...editing,
                      dimensions: { ...editing.dimensions, [key]: Number(event.target.value) },
                    })}
                  />
                  <input
                    type="number"
                    min="0"
                    max="10"
                    step="0.5"
                    value={editing.dimensions[key]}
                    onChange={(event) => setEditing({
                      ...editing,
                      dimensions: { ...editing.dimensions, [key]: Number(event.target.value) },
                    })}
                    className="p-1 border rounded"
                  />
                </label>
              ))}
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button onClick={() => setEditing(null)} className="px-4 py-2 bg-slate-100 rounded">取消</button>
              <button onClick={saveAdjust} className="px-4 py-2 bg-blue-600 text-white rounded">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value, highlight }: { label: string; value: string; highlight?: string }) {
  return (
    <div className="bg-slate-50 rounded p-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`font-semibold ${highlight || ''}`}>{value}</div>
    </div>
  );
}

function priorityClass(priority: string) {
  if (priority === 'High') return 'text-red-700';
  if (priority === 'Medium') return 'text-yellow-700';
  return 'text-green-700';
}
