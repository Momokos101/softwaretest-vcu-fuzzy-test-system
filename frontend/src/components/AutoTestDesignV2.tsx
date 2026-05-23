import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, Download, FileText, Gauge, Layers3, ListChecks, Play, RefreshCw, Save, Sparkles } from 'lucide-react';
import { autoTestAPI } from '../services/api';

const steps = [
  { id: 'concept', label: 'Concept', icon: FileText },
  { id: 'coverage', label: 'Coverage', icon: Layers3 },
  { id: 'strategy', label: 'Strategy', icon: ListChecks },
  { id: 'cases', label: 'Test Cases', icon: Sparkles },
  { id: 'prompts', label: 'Prompts', icon: Save },
  { id: 'results', label: 'Results', icon: Play },
  { id: 'improve', label: 'Improve', icon: Gauge },
] as const;

type StepId = typeof steps[number]['id'];

export function AutoTestDesignV2() {
  const [activeStep, setActiveStep] = useState<StepId>('concept');
  const [requirements, setRequirements] = useState<any[]>([]);
  const [risks, setRisks] = useState<any[]>([]);
  const [coverage, setCoverage] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [prompts, setPrompts] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [performance, setPerformance] = useState<any[]>([]);
  const [rawText, setRawText] = useState('');
  const [selectedReqId, setSelectedReqId] = useState('');
  const [strategy, setStrategy] = useState<any>({ techniques: ['EP', 'BVA'], rationale: '' });
  const [selectedPrompt, setSelectedPrompt] = useState<any>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void loadAll();
  }, []);

  useEffect(() => {
    if (!selectedReqId && requirements[0]) setSelectedReqId(requirements[0].id);
  }, [requirements, selectedReqId]);

  useEffect(() => {
    if (selectedReqId) {
      void autoTestAPI.getStrategy(selectedReqId).then(setStrategy).catch(() => undefined);
    }
  }, [selectedReqId]);

  const selectedRequirement = useMemo(
    () => requirements.find((item) => item.id === selectedReqId),
    [requirements, selectedReqId],
  );

  const run = async (action: () => Promise<any>, done: string) => {
    setLoading(true);
    setMessage('');
    try {
      await action();
      setMessage(done);
      await loadAll();
    } catch (error: any) {
      setMessage(error?.message || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  const loadAll = async () => {
    const [reqs, riskRows, coverageRows, testRows, promptRows] = await Promise.all([
      autoTestAPI.getRequirements().catch(() => []),
      autoTestAPI.getRiskMatrix().catch(() => []),
      autoTestAPI.getCoverageItems().catch(() => []),
      autoTestAPI.getTestCases().catch(() => []),
      autoTestAPI.getPrompts().catch(() => []),
    ]);
    setRequirements(reqs as any[]);
    setRisks(riskRows as any[]);
    setCoverage(coverageRows as any[]);
    setCases(testRows as any[]);
    setPrompts(promptRows as any[]);
    if (!selectedPrompt && (promptRows as any[])[0]) setSelectedPrompt((promptRows as any[])[0]);
  };

  const loadResults = async () => {
    const [resultSummary, perf] = await Promise.all([
      autoTestAPI.getResultsSummary(),
      autoTestAPI.getPerformance(),
    ]);
    setSummary(resultSummary);
    setPerformance(perf as any[]);
  };

  const exportFile = async (format: string) => {
    const blob = await autoTestAPI.exportByFormat(format) as Blob;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `autotestdesign_v2.${format === 'excel' ? 'xlsx' : format}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-8">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold">AutoTestDesign V2</h1>
          <div className="text-sm text-slate-500">LLM-driven VCU test design workflow</div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => void loadAll()} className="px-3 py-2 border rounded inline-flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />刷新
          </button>
          <button onClick={() => void exportFile('excel')} className="px-3 py-2 bg-slate-800 text-white rounded inline-flex items-center gap-2">
            <Download className="w-4 h-4" />Excel
          </button>
        </div>
      </div>

      <div className="bg-white border rounded-lg mb-6 overflow-x-auto">
        <div className="flex min-w-max">
          {steps.map((step) => {
            const Icon = step.icon;
            const active = activeStep === step.id;
            return (
              <button
                key={step.id}
                onClick={() => setActiveStep(step.id)}
                className={`px-4 py-3 flex items-center gap-2 border-r text-sm ${active ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 hover:bg-slate-50'}`}
              >
                <Icon className="w-4 h-4" />{step.label}
              </button>
            );
          })}
        </div>
      </div>

      {message && (
        <div className="mb-4 px-4 py-3 rounded border bg-slate-50 text-sm text-slate-700 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />{message}
        </div>
      )}

      {activeStep === 'concept' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <button disabled={loading} onClick={() => run(() => autoTestAPI.loadDemo(true), '已加载 V2 24 条 Demo 需求')} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">加载 V2 Demo</button>
            <button disabled={loading || !rawText.trim()} onClick={() => run(() => autoTestAPI.parseRawRequirements(rawText), 'LLM 解析完成')} className="px-3 py-2 bg-green-600 text-white rounded disabled:bg-slate-400">解析文本</button>
            <button disabled={loading || requirements.length === 0} onClick={() => run(() => autoTestAPI.parseAllRequirements(false), '全部需求已重新解析')} className="px-3 py-2 border rounded disabled:bg-slate-100">重新解析全部</button>
          </div>
          <textarea value={rawText} onChange={(event) => setRawText(event.target.value)} className="w-full h-36 p-3 border rounded mb-4" placeholder="粘贴 VCU 需求文本" />
          <RequirementTable requirements={requirements} risks={risks} />
        </section>
      )}

      {activeStep === 'coverage' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Coverage Items</h2>
            <button disabled={loading} onClick={() => run(() => autoTestAPI.generateCoverageItems(), '覆盖项已生成')} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">生成覆盖项</button>
          </div>
          <DataTable rows={coverage} columns={['requirement_id', 'title', 'technique', 'priority', 'description']} />
        </section>
      )}

      {activeStep === 'strategy' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
            <RequirementPicker requirements={requirements} selectedReqId={selectedReqId} onChange={setSelectedReqId} />
            <div>
              <h2 className="text-lg font-semibold mb-3">Strategy</h2>
              <div className="mb-3 text-sm text-slate-600">{selectedRequirement?.title || selectedReqId}</div>
              <TechniqueChecks value={strategy.techniques || []} onChange={(techniques) => setStrategy({ ...strategy, techniques })} />
              <textarea value={strategy.rationale || ''} onChange={(event) => setStrategy({ ...strategy, rationale: event.target.value })} className="w-full h-24 p-3 border rounded mt-3" placeholder="Rationale" />
              <button disabled={loading || !selectedReqId} onClick={() => run(() => autoTestAPI.updateStrategy(selectedReqId, strategy), '策略已保存')} className="mt-3 px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">保存策略</button>
            </div>
          </div>
        </section>
      )}

      {activeStep === 'cases' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <button disabled={loading || !selectedReqId} onClick={() => run(() => autoTestAPI.regenerateStrategy(selectedReqId), '指定需求用例已重新生成')} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">生成当前需求</button>
            <button disabled={loading} onClick={() => run(() => autoTestAPI.generateAllTestCases({ regenerate: true }), '全部用例已生成')} className="px-3 py-2 bg-green-600 text-white rounded disabled:bg-slate-400">生成全部</button>
          </div>
          <DataTable rows={cases} columns={['requirement_id', 'title', 'technique', 'type', 'status', 'oracle_reasoning']} />
        </section>
      )}

      {activeStep === 'prompts' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-4">
            <div className="border rounded divide-y">
              {prompts.map((prompt) => (
                <button key={prompt.type} onClick={() => setSelectedPrompt(prompt)} className={`w-full text-left p-3 ${selectedPrompt?.type === prompt.type ? 'bg-blue-50 text-blue-700' : ''}`}>{prompt.type}</button>
              ))}
            </div>
            {selectedPrompt && (
              <div className="space-y-3">
                <textarea value={selectedPrompt.system_prompt} onChange={(event) => setSelectedPrompt({ ...selectedPrompt, system_prompt: event.target.value })} className="w-full h-44 p-3 border rounded font-mono text-xs" />
                <textarea value={selectedPrompt.user_prompt} onChange={(event) => setSelectedPrompt({ ...selectedPrompt, user_prompt: event.target.value })} className="w-full h-28 p-3 border rounded font-mono text-xs" />
                <button disabled={loading} onClick={() => run(() => autoTestAPI.updatePrompt(selectedPrompt.type, selectedPrompt), 'Prompt 已保存')} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">保存 Prompt</button>
              </div>
            )}
          </div>
        </section>
      )}

      {activeStep === 'results' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <button disabled={loading || cases.length === 0} onClick={() => run(() => autoTestAPI.execute(), '执行完成').then(loadResults)} className="px-3 py-2 bg-green-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-2">
              <Play className="w-4 h-4" />执行全部
            </button>
            <button onClick={() => void loadResults()} className="px-3 py-2 border rounded">刷新结果</button>
          </div>
          {summary && <Summary summary={summary} />}
          <DataTable rows={performance} columns={['operation', 'elapsed_ms', 'model', 'created_at']} />
        </section>
      )}

      {activeStep === 'improve' && (
        <section className="bg-white border rounded-lg p-6">
          <button disabled={loading} onClick={() => run(() => autoTestAPI.improve({ failed_only: true, max_suggestions: 10 }), '第二轮改进建议已生成')} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400 mb-4">生成改进建议</button>
          <DataTable rows={coverage.filter((item) => item.priority === 'High')} columns={['requirement_id', 'title', 'technique', 'priority', 'description']} />
        </section>
      )}
    </div>
  );
}

function RequirementTable({ requirements, risks }: { requirements: any[]; risks: any[] }) {
  const riskByReq = Object.fromEntries(risks.map((risk) => [risk.requirement_id, risk]));
  const rows = requirements.map((req) => ({ ...req, rpn: riskByReq[req.id]?.rpn, extent: riskByReq[req.id]?.extent }));
  return <DataTable rows={rows} columns={['id', 'module', 'title', 'priority', 'parsed', 'rpn', 'extent']} />;
}

function RequirementPicker({ requirements, selectedReqId, onChange }: { requirements: any[]; selectedReqId: string; onChange: (id: string) => void }) {
  return (
    <label>
      <span className="block text-sm font-medium mb-2">Requirement</span>
      <select value={selectedReqId} onChange={(event) => onChange(event.target.value)} className="w-full p-2 border rounded">
        {requirements.map((req) => <option key={req.id} value={req.id}>{req.id} {req.title}</option>)}
      </select>
    </label>
  );
}

function TechniqueChecks({ value, onChange }: { value: string[]; onChange: (value: string[]) => void }) {
  const all = ['EP', 'BVA', 'DT', 'ST', 'SC'];
  return (
    <div className="flex flex-wrap gap-2">
      {all.map((item) => (
        <label key={item} className={`px-3 py-2 border rounded cursor-pointer ${value.includes(item) ? 'bg-blue-600 text-white' : 'bg-white'}`}>
          <input type="checkbox" checked={value.includes(item)} onChange={() => onChange(value.includes(item) ? value.filter((v) => v !== item) : [...value, item])} className="sr-only" />
          {item}
        </label>
      ))}
    </div>
  );
}

function Summary({ summary }: { summary: any }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
      <Metric label="Total" value={summary.total} />
      <Metric label="Passed" value={summary.passed} />
      <Metric label="Failed" value={summary.failed} />
      <Metric label="Errors" value={summary.errors} />
      <Metric label="Pass Rate" value={`${Math.round((summary.pass_rate || 0) * 100)}%`} />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: any }) {
  return (
    <div className="border rounded p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-xl font-semibold">{value}</div>
    </div>
  );
}

function DataTable({ rows, columns }: { rows: any[]; columns: string[] }) {
  return (
    <div className="overflow-x-auto border rounded">
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>{columns.map((col) => <th key={col} className="p-2 text-left font-medium">{col}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id || `${row.requirement_id}-${index}`} className="border-t">
              {columns.map((col) => <td key={col} className="p-2 align-top max-w-[360px] truncate">{formatCell(row[col])}</td>)}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr><td colSpan={columns.length} className="p-6 text-center text-slate-500">暂无数据</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(value: any) {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
