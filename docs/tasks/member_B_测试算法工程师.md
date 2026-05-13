# 成员 B — 测试算法工程师 任务书

---

## 你的定位

你负责 AutoTestDesign 工具最核心的"大脑"：测试用例自动生成逻辑（FR 2.0/3.0）和导出能力（FR 6.0）。你的代码决定了工具"智不智能"，也是 Detailed Test Design 文档（占总分 30%）内容的直接来源——你边写代码边产出文档内容，两件事同步进行。

---

## 你依赖谁

**依赖成员 A，在以下条件满足后开始：**

1. `vcu_simulator` 在本地 8001 端口可以响应请求（成员 A 第1周末交付）
2. `schemas.py` 的新增数据模型与你对齐（第1周内两人30分钟对齐会）
3. 收到 `API_reference_for_frontend.md`（了解已有的 requirements API 格式）

**开始前你需要做的准备：**
- 阅读 `docs/DESIGN_PLAN.md` 第三节（FR 2.0 风险评分算法 + FR 3.0 EP/BVA/决策表设计）
- 阅读 `docs/DESIGN_PLAN.md` 第二节（VCU 仿真器5个信号的边界常量）

---

## 你的任务清单

### 任务 1：FR 2.0 — 风险分析服务

**新建 `backend/api/services/risk_service.py`**

实现 5 维度加权评分（详见 DESIGN_PLAN.md 第三节 FR 2.0）：

| 维度 | 权重 | 说明 |
|-----|-----|-----|
| Criticality | 35% | Safety=10, State Transition=8, State Control=7, Input=6, Timing=4 |
| Boundary Sensitivity | 25% | 有精确数值边界=10，有范围=6，无边界=2 |
| Complexity | 20% | 条件数×2 + 范围数×2，上限10 |
| State Impact | 15% | 影响多状态=10，单状态=6，不影响=2 |
| Testability | 5% | 直接可测=10 |

优先级映射：≥7.0 → High，4.0~6.9 → Medium，<4.0 → Low

**新建 `backend/api/routers/risk_analysis.py`**
```
POST /api/risk-analysis/analyze/{req_id}    分析单条需求
POST /api/risk-analysis/analyze-all         批量分析
GET  /api/risk-analysis/report              获取完整报告
PUT  /api/risk-analysis/{req_id}/override   手动覆盖（Interactive Review）
```

---

### 任务 2：FR 3.0 — 测试用例生成引擎（最重要）

**新建 `backend/api/services/test_design_service.py`**

实现三种黑盒技术的生成逻辑：

#### EP 生成器

```python
class EPGenerator:
    def generate(self, req: ParsedRequirement) -> List[TestCase]:
        cases = []
        for range_spec in req.data_ranges:
            mid = (range_spec.min + range_spec.max) / 2
            cases.append(TestCase(
                id=f"EP-{req.id}-V1",
                signal_name=range_spec.field,
                value=mid,
                expected_status=1,
                expected_state=170,
                technique="EP",
                partition="Valid"
            ))
            # 无效低：取 fail_min - delta
            # 无效高：取 fail_max + delta
        return cases
```

#### BVA 生成器

```python
class BVAGenerator:
    def generate(self, req: ParsedRequirement, delta: float = 0.1) -> List[TestCase]:
        # 对每个数值范围生成7点边界
        # just_below_min, exact_min, just_above_min,
        # nominal, just_below_max, exact_max, just_above_max
```

#### 决策表生成器

```python
class DecisionTableGenerator:
    def generate(self, requirements: List[ParsedRequirement]) -> List[TestCase]:
        # 对多个需求的条件做笛卡尔积
        # 生成每个条件组合对应的规则行
        # 参考 DESIGN_PLAN.md 中的8条规则（DT-R1~R8）
```

**新建 `backend/api/services/simulator_client.py`**

```python
import httpx

class SimulatorClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def simulate(self, signal_name: str, value: float) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/simulate",
                json={"signal_name": signal_name, "value": value, "data_type": "float"})
            resp.raise_for_status()
            return resp.json()

    async def simulate_sleep(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/simulate/sleep",
                json={"cc2_voltage": 12.0, "cc_voltage": 12.0,
                      "cp_amplitude": 0.0, "supply_voltage": 0.0,
                      "network_wake_enable": 0.0})
            return resp.json()

    async def simulate_batch(self, test_cases: list) -> list:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/simulate/batch", json=test_cases)
            return resp.json()
```

**新建 `backend/api/routers/test_design.py`**
```
POST /api/test-design/generate/ep
POST /api/test-design/generate/bva          # 支持 ?delta=0.1 参数
POST /api/test-design/generate/decision-table
POST /api/test-design/generate/gan          # 调用现有 /api/gan/generate
POST /api/test-design/generate/all
GET  /api/test-design/test-cases
PUT  /api/test-design/test-cases/{id}
DELETE /api/test-design/test-cases/{id}
POST /api/test-design/test-cases            # 手动新增
POST /api/test-design/execute/{id}          # 调用仿真器执行单条
POST /api/test-design/execute-all           # 批量执行
GET  /api/test-design/results
```

---

### 任务 3：FR 6.0 — 导出服务

**新建 `backend/api/services/export_service.py`**

实现三种格式：
- JSON：标准化格式（参考 DESIGN_PLAN.md 第三节 FR 6.0 的 JSON 结构）
- CSV：`pandas.DataFrame` 转 CSV
- Excel：`openpyxl` 生成多 Sheet（Requirements / Risk Analysis / Test Cases - EP / BVA / DT / Traceability Matrix）

**新建 `backend/api/routers/export.py`**
```
GET /api/export/json
GET /api/export/csv
GET /api/export/excel
```

在 `backend/requirements.txt` 中补充：
```
openpyxl>=3.1.0
python-multipart>=0.0.6
httpx>=0.25.0
```

---

### 任务 4：pytest 脚本编写和执行

**完善 `tests/test_vcu_simulator.py`**

参考 DESIGN_PLAN.md 第三节中的完整 pytest 脚本，共约 37 条参数化用例 + 1 条独立休眠测试。

**实际在仿真器上运行：**
```bash
cd /path/to/project
source backend/venv/bin/activate
pytest tests/test_vcu_simulator.py -v --tb=short > docs/tasks/pytest_results.txt 2>&1
```

把结果文件 `pytest_results.txt` 保存好——成员 D 写 Detailed Test Design 的 Result Analysis 章节需要用这份输出。

---

### 任务 5：你需要写的文档

> 你写代码的同时同步写这两部分，不要留到最后。

#### 5.1 Detailed Test Design → Test Case Design（交给成员 E 汇总）

文件：`docs/tasks/detailed_test_case_design.md`

内容：
- 完整的 EP 测试用例表格（12条，参考 DESIGN_PLAN.md 第三节 3.1）
- 完整的 BVA 测试用例表格（24条，参考 DESIGN_PLAN.md 第三节 3.2）
- 完整的决策表（8条规则，参考 DESIGN_PLAN.md 第三节 3.3）
- 每种技术的一句话选型理由（为什么对这个信号用这个技术）
- **工具截图**：从 TestCaseDesign 页面截图展示"自动生成"的过程（联调后补充）

#### 5.2 Detailed Test Design → Test Result Analysis（交给成员 E 汇总）

文件：`docs/tasks/test_result_analysis.md`

内容：
- pytest 执行结果汇总表（Pass/Fail/Error 各多少条）
- 哪些 BVA 边界点表现符合预期，哪些出现意外（如有）
- 需求 × 测试用例追踪矩阵（REQ-001~010 各被哪些用例覆盖）
- "improvement with evidence"：第一轮发现哪里覆盖不足，添加了什么新用例

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| FR 2.0/3.0/6.0 后端 API 可调用 | 成员 C（前端对接） | 第2周末 |
| `pytest_results.txt`（执行结果） | 成员 D、E | 第3周初 |
| `detailed_test_case_design.md` | 成员 E（汇总进 Artifact 4） | 第3周初 |
| `test_result_analysis.md` | 成员 E（汇总进 Artifact 4） | 第3周末 |
| EP/BVA/DT 在前端的截图（联调后） | 成员 E（用于 PPT） | 第3周末 |
