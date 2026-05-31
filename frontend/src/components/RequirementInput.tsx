import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { ChevronDown, ChevronRight, Download, FileText, PlayCircle, Plus, Save, Upload } from 'lucide-react';
import { autoTestAPI } from '../services/api';

type Tab = 'csv' | 'text' | 'form';

export function RequirementInput() {
  const [activeTab, setActiveTab] = useState<Tab>('text');
  const [requirements, setRequirements] = useState<any[]>([]);
  const [parsedById, setParsedById] = useState<Record<string, any>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [editingRaw, setEditingRaw] = useState<Record<string, string>>({});
  const [editingParsed, setEditingParsed] = useState<Record<string, any>>({});
  const [textInput, setTextInput] = useState('');
  const [formInput, setFormInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadRequirements();
  }, []);

  const loadRequirements = async () => {
    try {
      const raw = await autoTestAPI.getRequirements();
      const reqs = Array.isArray(raw) ? raw : [];
      setRequirements(reqs);
      setEditingRaw(Object.fromEntries(reqs.map((req) => [req.id, req.raw_text])));
    } catch {
      // backend unreachable — keep empty state
    }
  };

  const importCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      await autoTestAPI.importCSV(file);
      await loadRequirements();
    } finally {
      setLoading(false);
      event.target.value = '';
    }
  };

  const importCSVAndParse = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      await autoTestAPI.importCSV(file);
      await parseAll(true);
    } finally {
      setLoading(false);
      event.target.value = '';
    }
  };

  const importText = async () => {
    if (!textInput.trim()) return;
    setLoading(true);
    try {
      await autoTestAPI.importText(textInput);
      setTextInput('');
      await loadRequirements();
    } finally {
      setLoading(false);
    }
  };

  const importForm = async () => {
    if (!formInput.trim()) return;
    setLoading(true);
    try {
      await autoTestAPI.createRequirement({ source: 'form', raw_text: formInput });
      setFormInput('');
      await loadRequirements();
    } finally {
      setLoading(false);
    }
  };

  const saveRequirement = async (id: string) => {
    setLoading(true);
    setMessage('');
    try {
      await autoTestAPI.updateRequirement(id, { raw_text: editingRaw[id] || '' });
      setParsedById((current) => {
        const next = { ...current };
        delete next[id];
        return next;
      });
      await loadRequirements();
      setMessage(`需求 ${id} 已保存`);
    } catch (error: any) {
      setMessage(error?.message || `需求 ${id} 保存失败`);
    } finally {
      setLoading(false);
    }
  };

  const parseRequirement = async (id: string) => {
    const parsed = await autoTestAPI.parseRequirement(id);
    setParsedById((current) => ({ ...current, [id]: parsed }));
    setEditingParsed((current) => ({ ...current, [id]: toEditableParsed(parsed) }));
    setExpanded((current) => ({ ...current, [id]: true }));
    await loadRequirements();
  };

  const parseAll = async (onlyUnparsed = true) => {
    const parsedList = await autoTestAPI.parseAllRequirements(onlyUnparsed) as unknown as any[];
    setParsedById(Object.fromEntries(parsedList.map((parsed) => [parsed.requirement_id, parsed])));
    setEditingParsed(Object.fromEntries(parsedList.map((parsed) => [parsed.requirement_id, toEditableParsed(parsed)])));
    setExpanded((current) => ({
      ...current,
      ...Object.fromEntries(parsedList.slice(0, 1).map((parsed) => [parsed.requirement_id, true])),
    }));
    await loadRequirements();
  };

  const loadParsed = async (id: string) => {
    if (parsedById[id]) return;
    const parsed = await autoTestAPI.getParsed(id);
    setParsedById((current) => ({ ...current, [id]: parsed }));
    setEditingParsed((current) => ({ ...current, [id]: toEditableParsed(parsed) }));
  };

  const toggleParsed = async (req: any) => {
    const open = !expanded[req.id];
    setExpanded((current) => ({ ...current, [req.id]: open }));
    if (open && req.parsed) await loadParsed(req.id);
  };

  const saveParsed = async (id: string) => {
    const editable = editingParsed[id];
    let parsed;
    try {
      parsed = {
        ...parsedById[id],
        input_fields: JSON.parse(editable.input_fields || '[]'),
        conditions: JSON.parse(editable.conditions || '[]'),
        actions: splitLines(editable.actions),
        data_ranges: JSON.parse(editable.data_ranges || '{}'),
      };
    } catch (err) {
      alert(`保存失败：Input Fields / Conditions / Data Ranges 必须是合法 JSON。\n\n${err instanceof Error ? err.message : String(err)}`);
      return;
    }
    const saved = await autoTestAPI.updateParsed(id, parsed);
    setParsedById((current) => ({ ...current, [id]: saved }));
    setEditingParsed((current) => ({ ...current, [id]: toEditableParsed(saved) }));
  };

  const updateParsedField = (id: string, key: string, value: string) => {
    setEditingParsed((current) => ({
      ...current,
      [id]: { ...current[id], [key]: value },
    }));
  };

  const exportExcel = async () => {
    const blob = await autoTestAPI.export({
      format: 'excel',
      scope: {
        include_requirements: true,
        include_parsed_requirements: true,
        include_risk_analysis: false,
        include_coverage_items: false,
        include_strategies: false,
        include_test_cases: false,
        include_execution_results: false,
        include_traceability_matrix: false,
        include_bq_new_cases: false,
      },
    }) as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'autotestdesign_v2_requirements.xlsx';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-8">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h1 className="text-2xl font-bold">需求管理</h1>
        <button onClick={() => void exportExcel()} className="px-3 py-2 bg-slate-800 text-white rounded inline-flex items-center gap-2">
          <Download className="w-4 h-4" />Excel
        </button>
      </div>

      {message && (
        <div className="mb-4 px-4 py-3 rounded border bg-slate-50 text-sm text-slate-700">
          {message}
        </div>
      )}

      <section className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex gap-2 mb-6">
          <TabButton active={activeTab === 'csv'} onClick={() => setActiveTab('csv')} icon={<Upload className="w-4 h-4" />} label="上传CSV" />
          <TabButton active={activeTab === 'text'} onClick={() => setActiveTab('text')} icon={<FileText className="w-4 h-4" />} label="粘贴文本" />
          <TabButton active={activeTab === 'form'} onClick={() => setActiveTab('form')} icon={<Plus className="w-4 h-4" />} label="手动填写" />
        </div>

        {activeTab === 'csv' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <label className="block">
              <span className="block text-sm font-medium mb-2">上传CSV</span>
              <input type="file" accept=".csv" onChange={importCSV} disabled={loading} className="w-full p-3 border rounded" />
            </label>
            <label className="block">
              <span className="block text-sm font-medium mb-2">上传并自动解析CSV</span>
              <input type="file" accept=".csv" onChange={importCSVAndParse} disabled={loading} className="w-full p-3 border rounded" />
            </label>
          </div>
        )}

        {activeTab === 'text' && (
          <div className="space-y-3">
            <textarea value={textInput} onChange={(event) => setTextInput(event.target.value)} className="w-full h-32 p-3 border rounded" />
            <button onClick={importText} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400">导入</button>
          </div>
        )}

        {activeTab === 'form' && (
          <div className="space-y-3">
            <input value={formInput} onChange={(event) => setFormInput(event.target.value)} className="w-full p-3 border rounded" />
            <button onClick={importForm} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400">添加</button>
          </div>
        )}
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
          <div>
            <h2 className="text-lg font-semibold">需求列表</h2>
            <div className="text-sm text-slate-500">
              共 {requirements.length} 条，已解析 {requirements.filter((req) => req.parsed).length} 条
            </div>
          </div>
          <button
            onClick={() => parseAll(true)}
            disabled={loading || requirements.length === 0}
            className="px-3 py-2 bg-green-600 text-white rounded text-sm inline-flex items-center gap-1 disabled:bg-slate-400"
          >
            <PlayCircle className="w-4 h-4" />解析全部未解析
          </button>
        </div>
        <div className="space-y-3">
          {requirements.map((req) => (
            <div key={req.id} className="border rounded p-4">
              <div className="flex gap-3 items-start">
                <button onClick={() => toggleParsed(req)} className="mt-2 p-1 rounded hover:bg-slate-100">
                  {expanded[req.id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>
                <div className="flex-1">
                  <div className="text-xs text-slate-500 mb-2">{req.id}</div>
                  <textarea
                    value={editingRaw[req.id] || ''}
                    onChange={(event) => setEditingRaw({ ...editingRaw, [req.id]: event.target.value })}
                    className="w-full min-h-[72px] p-2 border rounded"
                  />
                  <div className="flex gap-2 mt-3">
                    <button disabled={loading} onClick={() => saveRequirement(req.id)} className="px-3 py-1.5 bg-slate-700 text-white rounded text-sm inline-flex items-center gap-1 disabled:bg-slate-400">
                      <Save className="w-4 h-4" />{loading ? '保存中...' : '保存需求'}
                    </button>
                    <button onClick={() => parseRequirement(req.id)} className="px-3 py-1.5 bg-green-600 text-white rounded text-sm">解析</button>
                    <span className={`px-2 py-1.5 text-xs rounded ${req.parsed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                      {req.parsed ? '已解析' : '未解析'}
                    </span>
                  </div>
                </div>
              </div>

              {expanded[req.id] && editingParsed[req.id] && (
                <div className="mt-4 grid grid-cols-1 xl:grid-cols-4 gap-3">
                  <ParsedEditor title="Input Fields" value={editingParsed[req.id].input_fields} onChange={(value) => updateParsedField(req.id, 'input_fields', value)} />
                  <ParsedEditor title="Data Ranges JSON" value={editingParsed[req.id].data_ranges} onChange={(value) => updateParsedField(req.id, 'data_ranges', value)} />
                  <ParsedEditor title="Conditions" value={editingParsed[req.id].conditions} onChange={(value) => updateParsedField(req.id, 'conditions', value)} />
                  <ParsedEditor title="Actions" value={editingParsed[req.id].actions} onChange={(value) => updateParsedField(req.id, 'actions', value)} />
                  <div className="xl:col-span-4">
                    <button onClick={() => saveParsed(req.id)} className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm">保存解析结果</button>
                    <span className="ml-3 text-sm text-slate-500">Confidence: {parsedById[req.id]?.parse_confidence}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
          {requirements.length === 0 && <div className="text-slate-500">暂无需求</div>}
        </div>
      </section>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: ReactNode; label: string }) {
  return (
    <button onClick={onClick} className={`px-4 py-2 rounded inline-flex items-center gap-2 ${active ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
      {icon}{label}
    </button>
  );
}

function ParsedEditor({ title, value, onChange }: { title: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium mb-1">{title}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} className="w-full h-32 p-2 border rounded font-mono text-xs" />
    </label>
  );
}

function toEditableParsed(parsed: any) {
  return {
    input_fields: JSON.stringify(parsed.input_fields || [], null, 2),
    data_ranges: JSON.stringify(parsed.data_ranges || {}, null, 2),
    conditions: JSON.stringify(parsed.conditions || [], null, 2),
    actions: (parsed.actions || []).join('\n'),
  };
}

function splitLines(value: string) {
  return value.split(/\n|,/).map((item) => item.trim()).filter(Boolean);
}
