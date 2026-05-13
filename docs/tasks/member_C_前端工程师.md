# 成员 C — 前端工程师 任务书

---

## 你的定位

你负责所有人能"看见"的部分——四个新功能页面和视频演示。你的工作直接影响答辩时的展示效果。老师在演示阶段会看界面是否清晰、交互是否流畅。**Interactive Review**（可交互修改）是 Assignment 的强制要求，你需要在每个页面都实现内联编辑能力。

---

## 你依赖谁

**依赖成员 A（后端接口）和成员 B（测试设计接口）：**

| 你需要的 | 来自 | 何时能用 |
|---------|-----|---------|
| `API_reference_for_frontend.md`（所有接口说明） | 成员 A | 第1周末 |
| FR 1.0/1.1 接口可用（`/api/requirements/*`） | 成员 A | 第2周初 |
| FR 2.0 接口可用（`/api/risk-analysis/*`） | 成员 B | 第2周末 |
| FR 3.0 接口可用（`/api/test-design/*`） | 成员 B | 第2周末 |
| FR 6.0 接口可用（`/api/export/*`） | 成员 B | 第2周末 |

**等不到接口时怎么办？**

用 Mock 数据先开发。在 `src/services/api.ts` 里加一个 `MOCK_MODE` 开关：
```typescript
const MOCK_MODE = true  // 接口没好时设 true，联调时改 false
```

所有 API 调用先返回 hardcoded 的假数据，UI 跑通后再换真实接口。

---

## 你的任务清单

### 任务 1：修改现有文件（最先完成，打好基础）

**修改 `frontend/src/components/Sidebar.tsx`**

在现有导航里新增 4 个菜单项：
```
需求管理   → view: "requirements"     图标: FileText
风险分析   → view: "risk-analysis"    图标: AlertTriangle
测试设计   → view: "test-design"      图标: Code2
导出中心   → view: "export"           图标: Download
```

**修改 `frontend/src/App.tsx`**

新增 4 个 case：
```typescript
case "requirements":
  return <RequirementInput />;
case "risk-analysis":
  return <RiskAnalysis />;
case "test-design":
  return <TestCaseDesign />;
case "export":
  return <ExportCenter />;
```

**修改 `frontend/src/services/api.ts`**

新增以下 API 方法（接口格式参考成员 A 的 `API_reference_for_frontend.md`）：
```typescript
export const requirementAPI = {
  importCSV: (file: File) => ...,
  importText: (text: string) => ...,
  importForm: (data: RequirementCreate) => ...,
  getAll: () => ...,
  getById: (id: string) => ...,
  update: (id: string, data: any) => ...,
  delete: (id: string) => ...,
  parse: (id: string) => ...,
  getParsed: (id: string) => ...,
  updateParsed: (id: string, data: any) => ...,
}

export const riskAPI = {
  analyzeOne: (reqId: string) => ...,
  analyzeAll: () => ...,
  getReport: () => ...,
  override: (reqId: string, data: any) => ...,
}

export const testDesignAPI = {
  generateEP: (reqIds: string[]) => ...,
  generateBVA: (reqIds: string[], delta: number) => ...,
  generateDecisionTable: (reqIds: string[]) => ...,
  generateAll: (reqIds: string[]) => ...,
  getTestCases: () => ...,
  updateTestCase: (id: string, data: any) => ...,
  deleteTestCase: (id: string) => ...,
  addTestCase: (data: any) => ...,
  executeOne: (id: string) => ...,
  executeAll: () => ...,
  getResults: () => ...,
}

export const exportAPI = {
  downloadJSON: () => ...,
  downloadCSV: () => ...,
  downloadExcel: () => ...,
}
```

---

### 任务 2：RequirementInput.tsx（FR 1.0/1.1）

**UI 结构：**
```
┌─────────────────────────────────────────────────────┐
│  需求管理                                            │
│  ┌─────────┬─────────┬─────────┐                   │
│  │ 上传CSV │ 粘贴文本 │ 手动填写 │  ← Tab 切换       │
│  └─────────┴─────────┴─────────┘                   │
│                                                     │
│  [Tab内容区：上传区/文本框/表单]                      │
│                                                     │
│  ───────── 已导入需求列表 ─────────                  │
│  REQ-001  CC2 Wake Voltage  [High] [解析] [编辑] [删] │
│  REQ-002  Wake State Output [High] [解析] [编辑] [删] │
│  ...                                                │
│                                                     │
│  ── 解析结果面板（点击某条需求展开）──               │
│  Input Fields:    [cc2_voltage ×]  [+ 添加]         │
│  Data Ranges:     4.8V ~ 7.7V  [编辑]               │
│  Conditions:      [wake-up mode ×] [+ 添加]          │
│  Expected Actions:[accept input ×] [+ 添加]          │
└─────────────────────────────────────────────────────┘
```

**关键交互（Interactive Review 要求）：**
- 需求列表每行支持**内联编辑**（点击 Title 直接编辑）
- 解析结果面板的每个字段支持**增删改**
- 修改后调用 `PUT /api/requirements/{id}` 和 `PUT /api/requirements/{id}/parsed`

**VCU 预置数据：**

在 `src/data/vcu_requirements.ts` 中预置 10 条 VCU 需求（从 DESIGN_PLAN.md 第二节 2.5 复制），作为"快速导入示例"按钮的数据源。

---

### 任务 3：RiskAnalysis.tsx（FR 2.0）

**UI 结构：**
```
┌─────────────────────────────────────────────────────┐
│  风险分析               [批量分析所有需求]             │
│                                                     │
│  风险矩阵（散点图）                                  │
│  Y轴: Criticality  X轴: Boundary Sensitivity         │
│  气泡颜色: High=红/Medium=橙/Low=绿                  │
│                                                     │
│  需求风险列表                                        │
│  REQ-001  ● High   7.35  [调整] ← 点击弹出覆盖对话框│
│  REQ-002  ● High   8.30  [调整]                     │
│  ...                                                │
└─────────────────────────────────────────────────────┘
```

**关键交互（Interactive Review 要求）：**
- [调整] 按钮打开一个 Dialog，显示 5 个维度的当前分值（滑块或数字输入框）
- 用户修改后点击"保存覆盖"→ 调用 `PUT /api/risk-analysis/{id}/override`
- 列表实时更新颜色和分数

**图表库推荐：** 使用已有的 `chart.tsx`（shadcn/ui）或 recharts。

---

### 任务 4：TestCaseDesign.tsx（FR 3.0 + 执行）

**UI 结构：**
```
┌─────────────────────────────────────────────────────┐
│  测试设计                                            │
│                                                     │
│  [选择需求 ▼]  [EP] [BVA] [决策表] [GAN] [全部]     │
│  BVA delta: [0.1V ▼]                               │
│  [生成测试用例]                                     │
│                                                     │
│  测试用例表格:                                       │
│  ID     | 技术 | 信号名 | 值   | 预期state | 状态  │
│  EP-CC2 | EP   | CC2电压| 6.3 | 170      | ⏳待执行│
│  BVA-1  | BVA  | CC2电压| 4.8 | 170      | ✅PASS │
│  BVA-6  | BVA  | CC2电压| 7.8 | 30       | ❌FAIL │
│  [编辑] [删除] 每行                                 │
│  [+ 手动添加用例]                                   │
│                                                     │
│  ─────── 执行控制 ─────                             │
│  [执行所有用例]   进度: ████░░░░ 18/37              │
│  Pass: 34  Fail: 3  Error: 0                        │
└─────────────────────────────────────────────────────┘
```

**关键交互（Interactive Review 要求）：**
- 每行用例可以点击**内联编辑** value 和 expected_state
- [+ 手动添加用例] 打开 Dialog 填写新用例
- 执行时每条用例状态实时更新（轮询 `/api/test-design/results` 或 WebSocket）
- FAIL 的行高亮为红色，并显示 actual_state vs expected_state 的差异

---

### 任务 5：ExportCenter.tsx（FR 6.0）

**UI 结构：**
```
┌─────────────────────────────────────────────────────┐
│  导出中心                                            │
│                                                     │
│  导出格式:  [● JSON]  [○ CSV]  [○ Excel]            │
│                                                     │
│  导出范围:                                           │
│  ☑ Requirements（需求列表）                         │
│  ☑ Risk Analysis（风险分析报告）                    │
│  ☑ Test Cases - EP                                  │
│  ☑ Test Cases - BVA                                │
│  ☑ Test Cases - Decision Table                     │
│  ☑ Traceability Matrix（追踪矩阵）                  │
│  ☑ Execution Results（执行结果）                    │
│                                                     │
│  预览:                                               │
│  ┌──────────────────────────────┐                   │
│  │ {"tool": "AutoTestDesign"... │                   │
│  └──────────────────────────────┘                   │
│                                                     │
│  [下载 JSON]                                        │
└─────────────────────────────────────────────────────┘
```

---

### 任务 6：视频 Demo 录制

**脚本（约 6 分钟）：**

| 时间 | 内容 | 操作 |
|-----|-----|-----|
| 0:00~0:30 | 介绍两个服务（仿真器 + 工具） | 展示两个终端：8001 和 8000 都在运行 |
| 0:30~1:30 | 导入 VCU 需求 CSV | 上传预置的 requirements.csv，展示解析结果 |
| 1:30~2:00 | 手动修改一个解析结果（Interactive Review） | 编辑 REQ-001 的 Data Range |
| 2:00~3:00 | 执行风险分析，调整一个 Risk Score（Interactive Review） | 覆盖 REQ-006 的分值 |
| 3:00~4:30 | 生成 BVA 测试用例，编辑一条（Interactive Review），执行全部 | 展示 PASS/FAIL 结果 |
| 4:30~5:00 | 导出 Excel | 打开下载的文件展示多 Sheet |
| 5:00~6:00 | 可选：展示状态机/优化功能（FR 4.0/7.0） | — |

**录制要求：**
- 分辨率至少 1080p
- 不要出现错误弹窗（先在本地完整走一遍再录制）
- 文件命名：`AutoTestDesign_Demo.mp4`

---

### 任务 7：你需要写的文档

#### 7.1 更新 `README.md`（项目根目录）

补充"视频演示"一节，加上 Demo 视频的链接或说明。

#### 7.2 更新 `frontend/README.md`

补充新增的 4 个页面说明（在 Navigation Pages 表格里加入）。

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| Sidebar + App.tsx 修改完成（让B调试用） | 成员 B（联调时需要前端页面存在） | 第2周初 |
| 4个前端页面联调完成 | 成员 E（PPT截图用） | 第3周末 |
| `AutoTestDesign_Demo.mp4` | 成员 E（提交 Artifact 1） | 第4周初 |
| 更新后的 README.md | 成员 E（整合文档） | 第3周末 |
| 工具各页面截图（约8~10张） | 成员 E（PPT用） | 第3周末 |
