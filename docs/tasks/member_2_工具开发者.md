# 成员 2 — AutoTestDesign 工具开发者 任务书

---

## 你在答辩中讲什么

**你讲"我们的工具怎么做到的"**——现场演示工具界面（或播放视频），展示从需求导入到测试用例生成的完整流程，讲解每个 FR 的技术实现。这是答辩中最直观的部分，评委会看你的界面是否真的能用。

答辩时间：约 3 分钟

---

## 与成员 1 的并行协作说明

**你和成员 1 可以几乎完全并行工作。** 你的大部分模块完全不需要等仿真器：

| 你的模块 | 是否需要等仿真器 |
|---------|--------------|
| FR 1.0/1.1 需求导入 + 解析 | ❌ 完全独立，立即开始 |
| FR 2.0 风险评分算法 | ❌ 完全独立，立即开始 |
| FR 6.0 导出服务 | ❌ 完全独立，立即开始 |
| 前端 RequirementInput.tsx | ❌ 完全独立，立即开始 |
| 前端 RiskAnalysis.tsx | ❌ 完全独立，立即开始 |
| 前端 ExportCenter.tsx | ❌ 完全独立，立即开始 |
| FR 3.0 EP/BVA/DT **生成逻辑** | ❌ 完全独立，立即开始 |
| `simulator_client.py` 代码 | ⚠️ 代码能写，联调需等仿真器 |
| FR 3.0 **执行功能** + TestCaseDesign.tsx 执行按钮 | ⚠️ UI 能写，端到端需等仿真器 |

**第 1 周内必须做一件事：和成员 1 开一个 30 分钟的 API 对齐会。**

会议只需要约定两件事：
1. 仿真器请求体格式（字段名、类型）→ 你按这个写 `simulator_client.py`
2. 仿真器响应体格式（所有字段名、含义）→ 你按这个写 Test Oracle 判定逻辑

约定完成后，**你用 mock 数据继续开发**，等成员 1 第 1 周末仿真器跑通，当天通知你联调，2~4 小时搞定。

**并行时间线：**
```
第 1 周（并行）：
  你：写 FR1/2/6 后端 + 前端三个页面 + simulator_client.py（mock）
  成员 1：写仿真器核心逻辑
  同时进行：30 分钟 API 对齐会（约定接口格式）

第 1 周末：成员 1 仿真器跑通，立即通知你
  → 联调 simulator_client（约 2~4 小时）
  → 你继续写 FR3 执行功能 + TestCaseDesign.tsx 执行按钮
```

## 你依赖谁（依赖项极少）

| 你需要的 | 来自 | 时间节点 |
|---------|-----|---------|
| 接口格式约定（30 分钟对齐会） | 成员 1 | **第 1 周内尽快** |
| 仿真器在本地跑通（用于联调） | 成员 1 | **第 1 周末** |

---

## 你负责的代码

### 后端：在现有 `backend/` 基础上新增

**第一步：扩展数据模型（`backend/api/models/schemas.py`）**

新增以下 Pydantic 模型：
```python
class Requirement(BaseModel)           # 单条需求
class ParsedRequirement(BaseModel)     # 解析后的结构化需求
class RiskAnalysisResult(BaseModel)    # 风险评分结果
class TestCase(BaseModel)              # 单条测试用例
class ExecutionResult(BaseModel)       # 单条用例的执行结果
```

**第二步：FR 1.0/1.1 — 需求导入与解析**

新建文件：
- `backend/api/services/requirement_service.py`（CSV/文本/表单三种导入）
- `backend/api/services/requirement_parser.py`（正则解析4类结构）
- `backend/api/routers/requirements.py`（路由，见下表）

| 端点 | 方法 | 说明 |
|-----|-----|-----|
| `/api/requirements/import/csv` | POST | 上传 CSV 文件 |
| `/api/requirements/import/text` | POST | 粘贴文本 |
| `/api/requirements/import/form` | POST | 表单填写 |
| `/api/requirements` | GET | 获取需求列表 |
| `/api/requirements/{id}` | PUT | 修改需求（Interactive Review） |
| `/api/requirements/{id}/parse` | POST | 触发解析 |
| `/api/requirements/{id}/parsed` | PUT | 修改解析结果（Interactive Review） |

**解析逻辑（正则，不需要真正的 NLP）：**
```python
# 识别数值范围
RANGE_PATTERNS = [
    r'(\d+\.?\d*)\s*V?\s+to\s+(\d+\.?\d*)\s*V',   # "4.8V to 7.7V"
    r'(?:exceeds|above)\s+(\d+)',                    # "exceeds 170"
    r'(?:below|drops below)\s+(\d+)',                # "below 30"
]
# 识别条件词
CONDITION_KEYWORDS = ['when', 'if', 'while', 'during']
# 识别动作
ACTION_PATTERN = r'(?:shall|must|will)\s+([a-z][a-z\s]+?)(?:\.|,|$)'
```

**第三步：FR 2.0 — 风险分析**

新建：
- `backend/api/services/risk_service.py`（5 维度评分算法）
- `backend/api/routers/risk_analysis.py`

关键算法（权重来自 DESIGN_PLAN.md 第三节）：
```python
score = (
    criticality * 0.35 +
    boundary_sensitivity * 0.25 +
    complexity * 0.20 +
    state_impact * 0.15 +
    testability * 0.05
)
priority = "High" if score >= 7.0 else "Medium" if score >= 4.0 else "Low"
```

**第四步：FR 3.0 — 测试用例生成 + 执行（核心）**

新建：
- `backend/api/services/test_design_service.py`（EP / BVA / 决策表生成器）
- `backend/api/services/simulator_client.py`（调用仿真器的 HTTP 客户端）
- `backend/api/routers/test_design.py`

`simulator_client.py` 核心逻辑：
```python
import httpx

class SimulatorClient:
    BASE_URL = "http://localhost:8001"

    async def simulate(self, signal_name: str, value: float) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.BASE_URL}/simulate",
                json={"signal_name": signal_name, "value": value, "data_type": "float"})
            return r.json()

    async def simulate_sleep(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{self.BASE_URL}/simulate/sleep",
                json={"cc2_voltage": 12.0, "cc_voltage": 12.0,
                      "cp_amplitude": 0.0, "supply_voltage": 0.0,
                      "network_wake_enable": 0.0})
            return r.json()
```

EP 生成逻辑（以 CC2电压为例）：
- 有效类：取 [4.8, 7.7] 中值 = 6.3V，预期 state=170
- 无效低类：取 3.0V，预期 state=30
- 无效高类：取 9.0V，预期 state=30

BVA 生成逻辑：
- 在每个边界两侧各取 delta=0.1V，共 7 个点
- CC2电压：4.7 / 4.8 / 4.9 / 6.3 / 7.7 / 7.8 / 7.9

**第五步：FR 6.0 — 导出**

新建：
- `backend/api/services/export_service.py`（JSON + CSV + Excel）
- `backend/api/routers/export.py`

在 `backend/requirements.txt` 补充：
```
openpyxl>=3.1.0
python-multipart>=0.0.6
httpx>=0.25.0
```

在 `backend/api/main.py` 注册路由：
```python
from api.routers import requirements, risk_analysis, test_design, export
app.include_router(requirements.router, prefix="/api", tags=["需求管理"])
app.include_router(risk_analysis.router, prefix="/api", tags=["风险分析"])
app.include_router(test_design.router, prefix="/api", tags=["测试设计"])
app.include_router(export.router, prefix="/api", tags=["导出"])
```

---

### 前端：在现有 `frontend/src/` 基础上新增

**修改现有文件（最先完成）：**

`Sidebar.tsx` 新增 4 个导航项：
```
需求管理   → view: "requirements"    图标: FileText
风险分析   → view: "risk-analysis"   图标: AlertTriangle
测试设计   → view: "test-design"     图标: Code2
导出中心   → view: "export"          图标: Download
```

`App.tsx` 新增 4 个 case：
```typescript
case "requirements": return <RequirementInput />;
case "risk-analysis": return <RiskAnalysis />;
case "test-design": return <TestCaseDesign />;
case "export": return <ExportCenter />;
```

**新建 4 个页面组件：**

`RequirementInput.tsx`（FR 1.0/1.1）：
- 3 个 Tab：上传 CSV / 粘贴文本 / 手动填写
- 需求列表表格，支持内联编辑（Interactive Review）
- 点击展开解析结果（4 栏：Input Fields / Data Ranges / Conditions / Actions），每栏可编辑

`RiskAnalysis.tsx`（FR 2.0）：
- 风险矩阵散点图（X=Boundary，Y=Criticality）
- 需求列表，显示 Risk Score + 优先级标签
- [调整] 按钮 → 弹窗可手动覆盖分值（Interactive Review）

`TestCaseDesign.tsx`（FR 3.0 + 执行）：
- 技术选择按钮：EP / BVA / Decision Table / All
- BVA delta 参数输入框
- 测试用例表格（每行支持内联编辑，Interactive Review）
- [执行所有用例] 按钮 → 实时更新 PASS/FAIL 状态
- FAIL 行高亮为红色，显示 actual vs expected 差异

`ExportCenter.tsx`（FR 6.0）：
- 格式选择：JSON / CSV / Excel
- 范围勾选框（需求/风险/EP用例/BVA用例/DT用例/追踪矩阵）
- 下载按钮

---

## 你需要写的文档

### 文档 1：Artifact 1 的工具说明部分

> 你开发了工具，工具的技术说明由你来写。

**更新 `README.md`（项目根目录）**

在"System Architecture"部分详细描述：
- 三个服务的启动方式
- 每个 FR 对应的 API 端点
- 工具的完整功能列表

**录制 Demo 视频（约 6 分钟）**

按以下脚本录制：
| 时间 | 内容 |
|-----|-----|
| 0:00~0:30 | 展示两个终端（仿真器 8001 + 工具 8000 都在运行） |
| 0:30~1:30 | 上传 VCU 需求 CSV，查看解析结果 |
| 1:30~2:00 | 手动修改一个 Data Range（Interactive Review） |
| 2:00~3:00 | 执行风险分析，调整一个 Risk Score（Interactive Review） |
| 3:00~4:30 | 生成 BVA 用例，编辑一条，点击执行全部，看 PASS/FAIL |
| 4:30~5:00 | 导出 Excel，打开展示多 Sheet |

### 文档 2：Test Plan —— Testing Framework & Cost Estimation 两节

**交给成员 5 汇总。**

**Testing Framework and Rationale（约 300 字）：**
- 为什么选 httpx 作为调用仿真器的 HTTP 客户端
- 工具内部如何串联 FR1→FR2→FR3→执行→FR6 的数据流
- 前端 Interactive Review 的实现方式（内联编辑 + PUT API）

**Cost Estimation（填写表格）：**

| 活动 | 手动工作量 | 工具辅助后 | 节省 |
|-----|----------|----------|-----|
| 需求解析 | 6h | 1h | 83% |
| 风险评估 | 5h | 1h | 80% |
| EP/BVA 用例设计 | 20h | 3h | 85% |
| 决策表设计 | 8h | 2h | 75% |
| 测试执行与记录 | 10h | 2h | 80% |
| **合计** | **49h** | **9h** | **82%** |

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| 后端 FR1.0/1.1 API 可调用 | 成员 3（开始联调测试） | 第 2 周初 |
| 后端 FR2.0/3.0/6.0 全部可用 | 成员 3（开始实际测试） | 第 2 周末 |
| 前端 4 个页面联调完成 | 成员 3（用工具做演示截图） | 第 3 周中 |
| Demo 视频 `AutoTestDesign_Demo.mp4` | 成员 5 | 第 4 周初 |
| 工具各页面截图（约 8 张） | 成员 4、5（PPT 用） | 第 3 周末 |
| Test Plan 两节文字 | 成员 5 | 第 3 周初 |

---

## 答辩讲稿要点（约 3 分钟）

1. **工具架构一句话**（20s）
   > "工具包含前端 React 界面和后端 FastAPI，通过 HTTP 调用 VCU 仿真器执行测试，整个流程是：需求导入 → 解析 → 风险分析 → 用例生成 → 执行 → 导出。"

2. **现场演示或播放视频**（2 min）
   - 展示需求导入和解析（FR 1.0/1.1）
   - 展示风险分析界面（FR 2.0）
   - 重点展示：测试用例生成 + 调用仿真器执行 + PASS/FAIL 结果（FR 3.0）
   - 展示 Excel 导出（FR 6.0）

3. **Interactive Review 强调**（30s）
   > "作业要求工具必须支持用户交互式修改，我们在每个阶段都实现了内联编辑——用户可以修改解析结果、覆盖风险分值、编辑测试用例，这不是可选功能，是设计的核心。"

4. **GAN 的补充作用**（10s）
   > "现有 GAN 模型负责生成 CC2 电压的时序序列，补充静态 EP/BVA 覆盖不到的动态边界穿越场景。"
