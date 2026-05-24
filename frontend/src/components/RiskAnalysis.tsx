import { useEffect, useState } from 'react';
import { Scatter, ScatterChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { SlidersHorizontal } from 'lucide-react';
import { autoTestAPI } from '../services/api';

const ISO9126_OPTIONS = ['Functionality', 'Reliability', 'Efficiency', 'Maintainability', 'Usability', 'Portability'];

export function RiskAnalysis() {
  const [requirements, setRequirements] = useState<any[]>([]);
  const [riskResults, setRiskResults] = useState<any[]>([]);
  const [editing, setEditing] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [reqs, risks] = await Promise.all([
        autoTestAPI.getRequirements(),
        autoTestAPI.getRiskMatrix(),
      ]);
      setRequirements(Array.isArray(reqs) ? reqs : []);
      setRiskResults(Array.isArray(risks) ? risks : []);
    } catch {
      // backend unreachable — keep empty state
    }
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
    setEditing({
      requirement_id: result.requirement_id,
      tech_risk: result.tech_risk ?? 3,
      business_risk: result.business_risk ?? 3,
      iso9126_characteristic: result.iso9126_characteristic ?? 'Functionality',
      reasoning: result.reasoning ?? '',
    });
  };

  const saveAdjust = async () => {
    if (!editing) return;
    await autoTestAPI.adjustRisk(editing.requirement_id, {
      tech_risk: editing.tech_risk,
      business_risk: editing.business_risk,
      iso9126_characteristic: editing.iso9126_characteristic,
      reasoning: editing.reasoning,
    });
    setEditing(null);
    await loadData();
  };

  const resultByReq = Object.fromEntries(riskResults.map((r) => [r.requirement_id, r]));

  // Scatter: x = tech_risk (1=高风险 左), y = business_risk (1=高风险 下)
  const matrixData = riskResults.map((r) => ({
    x: r.tech_risk ?? 3,
    y: r.business_risk ?? 3,
    rpn: r.rpn ?? 0,
    name: r.requirement_id ?? '',
    extent: r.extent ?? '',
  }));

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">风险分析</h1>

      <section className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-1">Tech × Business Risk 矩阵</h2>
        <p className="text-xs text-slate-500 mb-4">坐标值 1 = Very High Risk，5 = Very Low Risk；左下角（RPN 最小）优先测试</p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 16, right: 24, bottom: 16, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" dataKey="x" domain={[1, 5]} name="Tech Risk" label={{ value: 'Tech Risk', position: 'insideBottom', offset: -4 }} />
              <YAxis type="number" dataKey="y" domain={[1, 5]} name="Business Risk" label={{ value: 'Business Risk', angle: -90, position: 'insideLeft' }} />
              <ReferenceLine x={3} stroke="#f59e0b" strokeDasharray="4 4" />
              <ReferenceLine y={3} stroke="#f59e0b" strokeDasharray="4 4" />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (!payload?.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="bg-white border rounded p-2 text-xs shadow">
                      <div className="font-medium">{d.name}</div>
                      <div>Tech Risk: {d.x} | Business Risk: {d.y}</div>
                      <div>RPN: {d.rpn} — {d.extent}</div>
                    </div>
                  );
                }}
              />
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
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-slate-500">{req.id}</span>
                      {req.module && <span className="px-1.5 py-0.5 text-xs bg-slate-100 rounded">Module {req.module}</span>}
                    </div>
                    <div className="text-sm text-slate-800">{req.title || req.raw_text}</div>
                    {risk && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        <Badge label="RPN" value={risk.rpn} highlight={rpnClass(risk.rpn)} />
                        <Badge label="Extent" value={risk.extent} highlight={extentClass(risk.extent)} />
                        <Badge label="Tech Risk" value={risk.tech_risk} />
                        <Badge label="Business Risk" value={risk.business_risk} />
                        <Badge label="ISO 9126" value={risk.iso9126_characteristic} />
                      </div>
                    )}
                    {risk?.reasoning && (
                      <div className="mt-2 text-xs text-slate-500 italic">{risk.reasoning}</div>
                    )}
                  </div>
                  <div className="flex gap-2 items-start shrink-0">
                    <button
                      onClick={() => analyzeRisk(req)}
                      disabled={loading}
                      className="px-3 py-2 bg-blue-600 text-white rounded text-sm disabled:bg-slate-400"
                    >
                      {risk ? '重新分析' : '分析'}
                    </button>
                    {risk && (
                      <button
                        onClick={() => openAdjust(risk)}
                        className="px-3 py-2 bg-slate-700 text-white rounded text-sm inline-flex items-center gap-1"
                      >
                        <SlidersHorizontal className="w-4 h-4" />调整
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
          {requirements.length === 0 && <div className="text-slate-500">暂无需求，请先在"需求管理"页面导入需求</div>}
        </div>
      </section>

      {editing && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-[480px] p-6">
            <h3 className="text-lg font-semibold mb-4">手动调整风险评分</h3>
            <div className="space-y-4">
              <label className="block">
                <span className="text-sm font-medium">ISO 9126 特性</span>
                <select
                  value={editing.iso9126_characteristic}
                  onChange={(e) => setEditing({ ...editing, iso9126_characteristic: e.target.value })}
                  className="mt-1 w-full p-2 border rounded"
                >
                  {ISO9126_OPTIONS.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              </label>

              <RiskSlider
                label="Tech Risk（技术风险）"
                hint="1=Very High（最易出错），5=Very Low"
                value={editing.tech_risk}
                onChange={(v) => setEditing({ ...editing, tech_risk: v })}
              />
              <RiskSlider
                label="Business Risk（业务风险）"
                hint="1=Very High（影响最大），5=Very Low"
                value={editing.business_risk}
                onChange={(v) => setEditing({ ...editing, business_risk: v })}
              />

              <div className="bg-slate-50 rounded p-3 text-sm">
                <div>RPN = Tech × Business = <strong>{editing.tech_risk * editing.business_risk}</strong></div>
                <div className="text-slate-500 mt-1">{extentDescription(editing.tech_risk * editing.business_risk)}</div>
              </div>

              <label className="block">
                <span className="text-sm font-medium">说明（可选）</span>
                <input
                  value={editing.reasoning}
                  onChange={(e) => setEditing({ ...editing, reasoning: e.target.value })}
                  className="mt-1 w-full p-2 border rounded text-sm"
                  placeholder="说明调整理由..."
                />
              </label>
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

function RiskSlider({ label, hint, value, onChange }: { label: string; hint: string; value: number; onChange: (v: number) => void }) {
  return (
    <label className="block">
      <div className="flex justify-between items-baseline mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-sm font-bold text-blue-700">{value}</span>
      </div>
      <p className="text-xs text-slate-500 mb-1">{hint}</p>
      <input
        type="range" min="1" max="5" step="1"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-slate-400 mt-0.5">
        <span>1 Very High</span><span>3 Medium</span><span>5 Very Low</span>
      </div>
    </label>
  );
}

function Badge({ label, value, highlight }: { label: string; value: any; highlight?: string }) {
  return (
    <div className="bg-slate-50 border rounded px-2 py-1 text-xs">
      <span className="text-slate-500">{label}: </span>
      <span className={`font-semibold ${highlight || ''}`}>{value ?? '-'}</span>
    </div>
  );
}

function rpnClass(rpn: number) {
  if (rpn <= 5) return 'text-red-700';
  if (rpn <= 10) return 'text-orange-600';
  if (rpn <= 15) return 'text-yellow-700';
  return 'text-green-700';
}

function extentClass(extent: string) {
  if (extent === 'Extensive') return 'text-red-700';
  if (extent === 'Broad') return 'text-orange-600';
  if (extent === 'Cursory') return 'text-yellow-700';
  return 'text-green-700';
}

function extentDescription(rpn: number) {
  if (rpn <= 5) return 'Extensive — 需要最充分测试（Suite A/B/C/D/E/F 全量）';
  if (rpn <= 10) return 'Broad — 全面测试（≥95% 通过率）';
  if (rpn <= 15) return 'Cursory — 一般测试';
  return 'Low Priority — 低优先级';
}
