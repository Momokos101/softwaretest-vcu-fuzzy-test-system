import { Fragment, useEffect, useMemo, useRef, useState } from 'react';
import { AlertTriangle, CheckCircle, ChevronDown, ChevronRight, Download, FileText, Gauge, Layers3, ListChecks, Pencil, Play, Plus, RefreshCw, Save, Sparkles, Trash2, Upload, X } from 'lucide-react';
import { autoTestAPI } from '../services/api';

const steps = [
  { id: 'concept', label: 'Concept', icon: FileText },
  { id: 'coverage', label: 'Coverage', icon: Layers3 },
  { id: 'strategy', label: 'Strategy', icon: ListChecks },
  { id: 'cases', label: 'Test Cases', icon: Sparkles },
  { id: 'prompts', label: 'Prompts', icon: Save },
  { id: 'results', label: 'Results', icon: Play },
  { id: 'improve', label: 'Optimize (FR7.0)', icon: Gauge },
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
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [rawText, setRawText] = useState('');
  const [selectedReqId, setSelectedReqId] = useState('');
  const [strategy, setStrategy] = useState<any>({ techniques: ['EP', 'BVA'], rationale: '' });
  const [selectedPrompt, setSelectedPrompt] = useState<any>(null);
  // FR 7.0 测试套件优化
  const [prioritized, setPrioritized] = useState<any>(null);
  const [minimized, setMinimized] = useState<any>(null);
  const [showPriority, setShowPriority] = useState(false);
  const [showMinimize, setShowMinimize] = useState(false);
  // 第二轮 fuzz 改进建议（LLM，PROJECT_PLAN §3.9）
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [addedIds, setAddedIds] = useState<Set<string>>(new Set());
  const [improveFailedOnly, setImproveFailedOnly] = useState(true);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const csvInputRef = useRef<HTMLInputElement>(null);

  // Coverage Items CRUD form state
  const [showCoverageForm, setShowCoverageForm] = useState(false);
  const [editingCoverageId, setEditingCoverageId] = useState<string | null>(null);
  const emptyCoverageForm = { requirement_id: '', title: '', description: '', technique: 'EP', iso9126_characteristic: 'Functionality', priority: 'Medium' };
  const [coverageForm, setCoverageForm] = useState(emptyCoverageForm);

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

  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await run(() => autoTestAPI.uploadCSV(file), `CSV 已导入：${file.name}`);
    if (csvInputRef.current) csvInputRef.current.value = '';
  };

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

  const togglePrioritize = async () => {
    if (showPriority) { setShowPriority(false); return; }
    if (!prioritized) {
      setLoading(true);
      setMessage('');
      try {
        const result = await autoTestAPI.optimizePrioritize() as unknown as any;
        setPrioritized(result);
        setMessage(`已按风险(RPN)排序 ${result.total} 条用例`);
      } catch (error: any) {
        setMessage(error?.message || '操作失败');
        setLoading(false);
        return;
      }
      setLoading(false);
    }
    setShowPriority(true);
  };

  const toggleMinimize = async () => {
    if (showMinimize) { setShowMinimize(false); return; }
    if (!minimized) {
      setLoading(true);
      setMessage('');
      try {
        const result = await autoTestAPI.optimizeMinimize() as unknown as any;
        setMinimized(result);
        setMessage(`最小化：${result.before} → ${result.after}（-${result.reduction_pct}%），覆盖保持 ${result.coverage_retained_pct}%`);
      } catch (error: any) {
        setMessage(error?.message || '操作失败');
        setLoading(false);
        return;
      }
      setLoading(false);
    }
    setShowMinimize(true);
  };

  const runImprove = async () => {
    setLoading(true);
    setMessage('');
    setSuggestions([]);
    setAddedIds(new Set());
    try {
      const result = await autoTestAPI.improve({ failed_only: improveFailedOnly, max_suggestions: 10 }) as unknown as any[];
      setSuggestions(result);
      setMessage(`已生成 ${result.length} 条第二轮改进建议`);
      await loadAll();
    } catch (error: any) {
      setMessage(error?.message || '操作失败');
    } finally {
      setLoading(false);
    }
  };

  const addSuggestionToCoverage = async (suggestion: any) => {
    const ci = suggestion.coverage_item;
    await autoTestAPI.createCoverageItem({
      requirement_id: ci.requirement_id,
      title: ci.title,
      description: ci.description,
      technique: ci.technique,
      iso9126_characteristic: ci.iso9126_characteristic,
      priority: ci.priority ?? 'Medium',
    });
    setAddedIds((prev) => new Set(prev).add(suggestion.id));
    await loadAll();
  };

  const openAddCoverageForm = () => {
    setEditingCoverageId(null);
    setCoverageForm({ ...emptyCoverageForm, requirement_id: selectedReqId || (requirements[0]?.id ?? '') });
    setShowCoverageForm(true);
  };

  const openEditCoverageForm = (item: any) => {
    setEditingCoverageId(item.id);
    setCoverageForm({
      requirement_id: item.requirement_id || '',
      title: item.title || '',
      description: item.description || '',
      technique: item.technique || 'EP',
      iso9126_characteristic: item.iso9126_characteristic || 'Functionality',
      priority: item.priority || 'Medium',
    });
    setShowCoverageForm(true);
  };

  const closeCoverageForm = () => {
    setShowCoverageForm(false);
    setEditingCoverageId(null);
    setCoverageForm(emptyCoverageForm);
  };

  const saveCoverageItem = async () => {
    if (!coverageForm.requirement_id.trim() || !coverageForm.title.trim()) {
      setMessage('requirement_id 和 title 必填');
      return;
    }
    const action = editingCoverageId
      ? () => autoTestAPI.updateCoverageItem(editingCoverageId, coverageForm)
      : () => autoTestAPI.createCoverageItem(coverageForm);
    await run(action, editingCoverageId ? 'Coverage Item 已更新' : 'Coverage Item 已创建');
    closeCoverageForm();
  };

  const deleteCoverageItem = async (item: any) => {
    if (!window.confirm(`确认删除 Coverage Item？\n\n${item.requirement_id} | ${item.title}\n\n此操作不可撤销。`)) return;
    await run(() => autoTestAPI.deleteCoverageItem(item.id), 'Coverage Item 已删除');
  };

  const loadAll = async () => {
    const [reqs, riskRows, coverageRows, testRows, promptRows] = await Promise.all([
      autoTestAPI.getRequirements().catch(() => []),
      autoTestAPI.getRiskMatrix().catch(() => []),
      autoTestAPI.getCoverageItems().catch(() => []),
      autoTestAPI.getTestCases().catch(() => []),
      autoTestAPI.getPrompts().catch(() => []),
    ]);
    setRequirements(reqs as unknown as any[]);
    setRisks(riskRows as unknown as any[]);
    setCoverage(coverageRows as unknown as any[]);
    setCases(testRows as unknown as any[]);
    setPrompts(promptRows as unknown as any[]);
    const rows = promptRows as unknown as any[];
    if (!selectedPrompt && rows[0]) setSelectedPrompt(rows[0]);
  };

  const loadResults = async () => {
    const [resultSummary, perf, testRows] = await Promise.all([
      autoTestAPI.getResultsSummary(),
      autoTestAPI.getPerformance(),
      autoTestAPI.getTestCases(),
    ]);
    setSummary(resultSummary);
    setPerformance(perf as unknown as any[]);
    setCases(testRows as unknown as any[]);
  };

  const exportFile = async (format: string) => {
    const blob = await autoTestAPI.exportByFormat(format) as unknown as Blob;
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
            <label className={`px-3 py-2 border rounded inline-flex items-center gap-2 cursor-pointer ${loading ? 'opacity-50 pointer-events-none' : 'hover:bg-slate-50'}`}>
              <Upload className="w-4 h-4" />上传 CSV
              <input ref={csvInputRef} type="file" accept=".csv" className="hidden" onChange={handleCSVUpload} disabled={loading} />
            </label>
            <button disabled={loading || requirements.length === 0} onClick={() => run(() => autoTestAPI.parseAllRequirements(false), '全部需求已重新解析')} className="px-3 py-2 border rounded disabled:bg-slate-100">重新解析全部</button>
          </div>
          <textarea value={rawText} onChange={(event) => setRawText(event.target.value)} className="w-full h-36 p-3 border rounded mb-4" placeholder={"粘贴 VCU 需求文本（方式一）\n或点击「上传 CSV」导入（方式二）\n或点击「加载 V2 Demo」使用演示数据（方式三）"} />
          <RequirementTable requirements={requirements} risks={risks} />
        </section>
      )}

      {activeStep === 'coverage' && (
        <section className="bg-white border rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-lg font-semibold">Coverage Items</h2>
              <div className="text-sm text-slate-500">共 {coverage.length} 条</div>
            </div>
            <div className="flex gap-2">
              <button disabled={loading || showCoverageForm} onClick={openAddCoverageForm} className="px-3 py-2 bg-green-600 text-white rounded inline-flex items-center gap-2 disabled:bg-slate-400">
                <Plus className="w-4 h-4" />添加
              </button>
              <button
                disabled={loading}
                onClick={() => {
                  const existing = coverage.length;
                  const choice = existing === 0
                    ? 'dedupe'
                    : window.prompt(
                        `当前已有 ${existing} 条 Coverage Items。\n\n请选择生成模式：\n  • dedupe  — 只追加 LLM 新建议中尚未存在的项（推荐，幂等安全）\n  • replace — 删除现有所有 CI 后重新生成（破坏性）\n  • append  — 直接追加 LLM 输出（会产生重复，仅诊断用途）\n\n请输入 dedupe / replace / append：`,
                        'dedupe',
                      );
                  if (!choice) return;
                  const mode = choice as 'dedupe' | 'replace' | 'append';
                  if (!['dedupe', 'replace', 'append'].includes(mode)) {
                    setMessage(`无效模式：${choice}（应为 dedupe / replace / append）`);
                    return;
                  }
                  if (mode === 'replace' && !window.confirm(`确认要删除现有 ${existing} 条 Coverage Items 后重新生成？此操作不可撤销。`)) return;
                  void run(() => autoTestAPI.generateCoverageItems(undefined, mode), `覆盖项已生成（mode=${mode}）`);
                }}
                className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400"
              >生成覆盖项</button>
            </div>
          </div>

          {showCoverageForm && (
            <div className="mb-4 border rounded p-4 bg-slate-50">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold">{editingCoverageId ? '编辑 Coverage Item' : '新增 Coverage Item'}</h3>
                <button onClick={closeCoverageForm} className="p-1 hover:bg-slate-200 rounded"><X className="w-4 h-4" /></button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label className="block">
                  <span className="block text-sm font-medium mb-1">Requirement ID *</span>
                  <select value={coverageForm.requirement_id} onChange={(e) => setCoverageForm({ ...coverageForm, requirement_id: e.target.value })} className="w-full p-2 border rounded">
                    {requirements.map((req) => <option key={req.id} value={req.id}>{req.id} {req.title}</option>)}
                  </select>
                </label>
                <label className="block">
                  <span className="block text-sm font-medium mb-1">Technique</span>
                  <select value={coverageForm.technique} onChange={(e) => setCoverageForm({ ...coverageForm, technique: e.target.value })} className="w-full p-2 border rounded">
                    {['EP', 'BVA', 'DT', 'ST', 'SC'].map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </label>
                <label className="block md:col-span-2">
                  <span className="block text-sm font-medium mb-1">Title *</span>
                  <input value={coverageForm.title} onChange={(e) => setCoverageForm({ ...coverageForm, title: e.target.value })} className="w-full p-2 border rounded" placeholder="简短描述这个覆盖目标" />
                </label>
                <label className="block md:col-span-2">
                  <span className="block text-sm font-medium mb-1">Description</span>
                  <textarea value={coverageForm.description} onChange={(e) => setCoverageForm({ ...coverageForm, description: e.target.value })} className="w-full h-20 p-2 border rounded" />
                </label>
                <label className="block">
                  <span className="block text-sm font-medium mb-1">ISO 9126 Characteristic</span>
                  <select value={coverageForm.iso9126_characteristic} onChange={(e) => setCoverageForm({ ...coverageForm, iso9126_characteristic: e.target.value })} className="w-full p-2 border rounded">
                    {['Functionality', 'Reliability', 'Efficiency', 'Maintainability', 'Portability', 'Usability'].map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </label>
                <label className="block">
                  <span className="block text-sm font-medium mb-1">Priority</span>
                  <select value={coverageForm.priority} onChange={(e) => setCoverageForm({ ...coverageForm, priority: e.target.value })} className="w-full p-2 border rounded">
                    {['High', 'Medium', 'Low'].map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </label>
              </div>
              <div className="flex gap-2 mt-3">
                <button disabled={loading} onClick={saveCoverageItem} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">{editingCoverageId ? '保存修改' : '创建'}</button>
                <button disabled={loading} onClick={closeCoverageForm} className="px-3 py-2 border rounded">取消</button>
              </div>
            </div>
          )}

          <div className="overflow-x-auto border rounded">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="p-2 text-left font-medium">requirement_id</th>
                  <th className="p-2 text-left font-medium">title</th>
                  <th className="p-2 text-left font-medium">priority</th>
                  <th className="p-2 text-left font-medium">iso9126</th>
                  <th className="p-2 text-left font-medium">description</th>
                  <th className="p-2 text-left font-medium w-32">操作</th>
                </tr>
              </thead>
              <tbody>
                {coverage.map((item, index) => (
                  <tr key={item.id || `${item.requirement_id}-${index}`} className="border-t hover:bg-slate-50">
                    <td className="p-2 align-top font-mono text-xs">{item.requirement_id || '-'}</td>
                    <td className="p-2 align-top max-w-[260px]">{item.title || '-'}</td>
                    <td className="p-2 align-top">{item.priority || '-'}</td>
                    <td className="p-2 align-top text-xs">{item.iso9126_characteristic || '-'}</td>
                    <td className="p-2 align-top max-w-[360px] truncate text-xs text-slate-600">{item.description || '-'}</td>
                    <td className="p-2 align-top whitespace-nowrap">
                      <button onClick={() => openEditCoverageForm(item)} disabled={loading} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded disabled:opacity-50" title="编辑">
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button onClick={() => deleteCoverageItem(item)} disabled={loading} className="p-1.5 text-red-600 hover:bg-red-50 rounded disabled:opacity-50 ml-1" title="删除">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
                {coverage.length === 0 && (
                  <tr><td colSpan={6} className="p-6 text-center text-slate-500">暂无 Coverage Items，点上方"添加"或"生成覆盖项"创建</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {activeStep === 'strategy' && (
        <section className="bg-white border rounded-lg p-6 space-y-6">
          {/* 总览：每条 Coverage Item 用了哪种技术（技术归属统一在此查看，Coverage 页只展示"覆盖什么"）*/}
          <div>
            <h2 className="text-lg font-semibold">技术总览（Coverage Item × 技术）</h2>
            <p className="text-sm text-slate-500 mt-1 mb-3">每条覆盖项对应的测试技术。共 {coverage.length} 条覆盖项，覆盖 {Array.from(new Set(coverage.map((c) => c.technique))).filter(Boolean).join(' / ')} 五种技术。</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {['EP', 'BVA', 'DT', 'ST', 'SC'].map((t) => {
                const n = coverage.filter((c) => c.technique === t).length;
                return <span key={t} className="text-xs px-2 py-1 rounded border bg-slate-50">{t}: {n} 条</span>;
              })}
            </div>
            <DataTable
              rows={[...coverage].sort((a, b) => (a.requirement_id || '').localeCompare(b.requirement_id || '') || (a.technique || '').localeCompare(b.technique || ''))}
              columns={['requirement_id', 'title', 'technique', 'priority', 'iso9126_characteristic']}
            />
          </div>

          {/* 按需求编辑策略（每条需求用哪几种技术 + rationale）*/}
          <div className="border-t pt-6">
            <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
              <RequirementPicker requirements={requirements} selectedReqId={selectedReqId} onChange={setSelectedReqId} />
              <div>
                <h2 className="text-lg font-semibold mb-3">按需求设置策略</h2>
                <div className="mb-3 text-sm text-slate-600">{selectedRequirement?.title || selectedReqId}</div>
                <TechniqueChecks value={strategy.techniques || []} onChange={(techniques) => setStrategy({ ...strategy, techniques })} />
                <textarea value={strategy.rationale || ''} onChange={(event) => setStrategy({ ...strategy, rationale: event.target.value })} className="w-full h-24 p-3 border rounded mt-3" placeholder="Rationale" />
                <button disabled={loading || !selectedReqId} onClick={() => run(() => autoTestAPI.updateStrategy(selectedReqId, strategy), '策略已保存')} className="mt-3 px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400">保存策略</button>
              </div>
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

          <h3 className="text-base font-semibold mt-6 mb-2">测试用例执行结果（pytest 逐条，点"查看输出"展开 VCU 实际响应）</h3>
          <div className="border rounded overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="text-left p-2">REQ</th>
                  <th className="text-left p-2">技术</th>
                  <th className="text-left p-2">用例</th>
                  <th className="text-left p-2">结果</th>
                  <th className="text-left p-2">详情</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => {
                  const er = c.execution_result || {};
                  const isOpen = expandedCase === c.id;
                  const st = (c.status || 'pending') as string;
                  return (
                    <Fragment key={c.id}>
                      <tr className="border-t">
                        <td className="p-2">{c.requirement_id}</td>
                        <td className="p-2">{c.technique}</td>
                        <td className="p-2">{c.title}</td>
                        <td className="p-2">
                          <span className={st === 'pass' ? 'text-green-600 font-semibold' : st === 'fail' || st === 'error' ? 'text-red-600 font-semibold' : 'text-slate-400'}>{st.toUpperCase()}</span>
                        </td>
                        <td className="p-2">
                          <button className="text-blue-600 hover:underline" onClick={() => setExpandedCase(isOpen ? null : c.id)}>{isOpen ? '收起' : '查看输出'}</button>
                        </td>
                      </tr>
                      {isOpen && (
                        <tr className="bg-slate-50">
                          <td colSpan={5} className="p-3">
                            <div className="grid gap-2 text-xs">
                              <div><span className="font-semibold">输入 (in_data)：</span>{JSON.stringify(er.input ?? c.in_data)}</div>
                              <div><span className="font-semibold">预期 oracle：</span>{JSON.stringify(er.expected ?? c.expected_results)}</div>
                              <div>
                                <span className="font-semibold">VCU 仿真器实际输出：</span>
                                <pre className="bg-white border rounded p-2 mt-1 overflow-auto max-h-72">{JSON.stringify(er.actual_output ?? {}, null, 2)}</pre>
                              </div>
                              {Array.isArray(er.mismatches) && er.mismatches.length > 0 && (
                                <div className="text-red-600"><span className="font-semibold">不匹配：</span>{er.mismatches.join('; ')}</div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
                {cases.length === 0 && (
                  <tr><td colSpan={5} className="p-6 text-center text-slate-500">暂无数据（点"执行全部"运行 pytest）</td></tr>
                )}
              </tbody>
            </table>
          </div>

          <h3 className="text-base font-semibold mt-6 mb-2 text-slate-500">LLM 调用性能日志（NFR Performance，非测试结果）</h3>
          <DataTable rows={performance} columns={['operation', 'elapsed_ms', 'model', 'created_at']} />

          {/* 第二轮 LLM 用例增广建议（Assignment 2 "Mainly" 迭代改进）*/}
          <div className="mt-8 border-t pt-6">
            <h3 className="text-base font-semibold mb-1">第二轮 LLM 用例增广建议</h3>
            <p className="text-sm text-slate-500 mb-3">基于执行结果调用 LLM（improve prompt）提出第二轮覆盖项/用例增广建议，补充遗漏的边界、状态与场景——属 Assignment 2 “Mainly” 段的迭代改进（区别于 FR7.0 纯算法优化）。</p>
            <div className="flex items-center gap-3 mb-4">
              <button disabled={loading} onClick={runImprove} className="px-3 py-2 bg-indigo-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-2">
                <Sparkles className="w-4 h-4" />生成改进建议
              </button>
              <label className="text-sm text-slate-600 inline-flex items-center gap-1.5">
                <input type="checkbox" checked={improveFailedOnly} onChange={(e) => setImproveFailedOnly(e.target.checked)} />
                仅基于失败用例（否则基于全部用例）
              </label>
            </div>
            {suggestions.length > 0 && (
              <div className="space-y-3">
                {suggestions.map((s) => {
                  const added = addedIds.has(s.id);
                  return (
                    <div key={s.id} className={`border rounded p-4 ${added ? 'border-green-300 bg-green-50' : ''}`}>
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-mono text-slate-500">{s.requirement_id}</span>
                            <span className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">{s.coverage_item?.technique}</span>
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">{s.coverage_item?.priority}</span>
                          </div>
                          <div className="font-medium text-sm">{s.title}</div>
                          <div className="text-xs text-slate-600 mt-1">{s.reason}</div>
                          {s.coverage_item?.description && (
                            <div className="text-xs text-slate-500 mt-1">{s.coverage_item.description}</div>
                          )}
                        </div>
                        <button
                          disabled={added || loading}
                          onClick={() => addSuggestionToCoverage(s)}
                          className={`shrink-0 px-3 py-1.5 rounded text-sm inline-flex items-center gap-1.5 ${added ? 'bg-green-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-slate-400'}`}
                        >
                          {added ? <><CheckCircle className="w-4 h-4" />已添加</> : '添加到 Coverage'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      )}

      {activeStep === 'improve' && (
        <section className="bg-white border rounded-lg p-6 space-y-8">
          <div>
            <h2 className="text-lg font-semibold">测试套件优化（FR 7.0 Test Suite Optimization）</h2>
            <p className="text-sm text-slate-500 mt-1">基于<strong>风险</strong>对套件优先级排序，并基于<strong>覆盖效率</strong>最小化套件——覆盖不降。</p>
          </div>

          {/* 1) 风险优先级排序 */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <button disabled={loading} onClick={togglePrioritize} className="px-3 py-2 bg-blue-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-1.5">
                {showPriority ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                按风险(RPN)排序
              </button>
              <span className="text-sm text-slate-500">RPN 升序：RPN=1 风险最高，最先执行（RPN 来自 FR 2.0 风险分析）{showPriority ? '（点击收起）' : ''}</span>
            </div>
            {showPriority && prioritized && (
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {prioritized.bands.map((b: any) => (
                    <span key={b.rpn} className={`text-xs px-2 py-1 rounded border ${b.rpn <= 5 ? 'bg-red-50 border-red-200 text-red-700' : b.rpn <= 10 ? 'bg-yellow-50 border-yellow-200 text-yellow-800' : 'bg-slate-50 border-slate-200 text-slate-600'}`}>
                      RPN {b.rpn}（{b.priority}）: {b.count} 条
                    </span>
                  ))}
                </div>
                <DataTable rows={prioritized.items} columns={['rank', 'requirement_id', 'title', 'technique', 'polarity', 'rpn', 'extent', 'priority', 'status']} />
              </div>
            )}
          </div>

          {/* 2) 覆盖最小化 */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <button disabled={loading} onClick={toggleMinimize} className="px-3 py-2 bg-emerald-600 text-white rounded disabled:bg-slate-400 inline-flex items-center gap-1.5">
                {showMinimize ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                覆盖最小化
              </button>
              <span className="text-sm text-slate-500">贪心 set-cover：覆盖单元 = 需求 × 技术 × 正负向（= Coverage Item × polarity），平手优先保留高风险/低耗时{showMinimize ? '（点击收起）' : ''}</span>
            </div>
            {showMinimize && minimized && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="border rounded p-3 text-center"><div className="text-2xl font-bold">{minimized.before} → {minimized.after}</div><div className="text-xs text-slate-500">用例数（最小化前→后）</div></div>
                  <div className="border rounded p-3 text-center"><div className="text-2xl font-bold text-emerald-600">-{minimized.reduction_pct}%</div><div className="text-xs text-slate-500">削减 {minimized.removed} 条</div></div>
                  <div className="border rounded p-3 text-center"><div className="text-2xl font-bold text-blue-600">{minimized.coverage_retained_pct}%</div><div className="text-xs text-slate-500">覆盖保持（{minimized.coverage_units_retained}/{minimized.coverage_units_total} 单元）</div></div>
                  <div className="border rounded p-3 text-center"><div className="text-sm font-semibold">{minimized.requirements_retained} 需求<br />{minimized.req_technique_retained} 需求×技术</div><div className="text-xs text-slate-500">{minimized.full_coverage_retained ? '✅ 覆盖未降' : '⚠ 覆盖下降'}</div></div>
                </div>
                <div className="text-xs text-slate-500">{minimized.criterion}</div>
                <div>
                  <h3 className="text-sm font-semibold mb-2 text-emerald-700">保留（{minimized.kept.length} 条 — 最小覆盖集）</h3>
                  <DataTable rows={minimized.kept} columns={['requirement_id', 'title', 'technique', 'polarity', 'rpn', 'covers']} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold mb-2 text-slate-500">移除（{minimized.dropped.length} 条 — 覆盖冗余）</h3>
                  <DataTable rows={minimized.dropped} columns={['requirement_id', 'title', 'technique', 'polarity', 'rpn', 'redundant_on']} />
                </div>
              </div>
            )}
          </div>
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
