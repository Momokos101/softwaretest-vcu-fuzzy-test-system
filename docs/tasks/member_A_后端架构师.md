# 成员 A — 后端架构师 任务书

---

## 你的定位

你是全组的**关键路径**。VCU 仿真器和后端骨架必须最先完成，因为成员 B 的算法、成员 C 的前端都要对接你的接口。你的代码完成越早，其他人就能越早联调。

---

## 你依赖谁

**你不依赖任何人的代码**，但你在开始之前需要：

- 阅读 `docs/DESIGN_PLAN.md` 的 **第二节（VCU 仿真器设计）** 和 **第三节 FR 1.0/1.1**，理解接口格式
- 和成员 B 对齐 `schemas.py` 里新增的数据模型，避免后续冲突（可以一起开一个 30 分钟的对齐会）

---

## 你的任务清单

### 任务 1：VCU 行为仿真器（⭐ 最高优先级，第一周完成）

新建目录 `vcu_simulator/`，实现一个独立的 FastAPI 服务（端口 8001）。

**文件结构：**
```
vcu_simulator/
├── main.py         FastAPI 入口
├── simulator.py    核心判定逻辑（VCUSimulator 类）
├── models.py       Pydantic 请求/响应模型
├── constants.py    信号边界常量
└── requirements.txt
```

**需要实现的 API：**

| 端点 | 方法 | 说明 |
|-----|-----|-----|
| `/simulate` | POST | 单信号测试（5种信号之一） |
| `/simulate/sleep` | POST | 休眠测试（固定5信号组合） |
| `/simulate/batch` | POST | 批量执行（数组输入） |
| `/health` | GET | 健康检查 |
| `/signals` | GET | 返回5个信号的边界说明 |
| `/reset` | POST | 重置状态机 |

**`/simulate` 请求格式：**
```json
{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}
```

**`/simulate` 响应格式：**
```json
{
  "test_status": 1,
  "vehicle_state": 170,
  "vehicle_mode": 5,
  "ready_flag": 1,
  "bms_wake_cmd": 1,
  "mcu_wake_cmd": 1,
  "battery_voltage": 12.92,
  "actual_duration": 100.4,
  "detail": "CC2电压=6.3V ∈ [4.8,7.7]V → 正常唤醒"
}
```

**5个信号的判定逻辑（来自真实数据库分析）：**

| 信号 | PASS 条件 | FAIL 条件 | PASS时state | FAIL时state |
|-----|---------|---------|-----------|-----------|
| CC2电压 | [4.8, 7.7]V | <4.8V 或 >7.8V | 170 | 30 |
| CC2电压 | 精确12.0V | — | 30(SLEEP/status=3) | — |
| CC2电压 | 7.8V灰色边界 | — | — | 30(FAIL/status=4) |
| CC电压值 | 其他值 | [0.1, 3.9]V | 170 | 30 |
| CP幅值 | 0V或其他 | [9.1, 12.9]V | 170 | 30 |
| 供电电压 | 0V或其他 | [9.1, 15.9]V | 170 | 30 |
| 网络唤醒报文使能状态 | 0 | 1 | 170 | 30 |

> ⚠️ 注意：所有 FAIL 情况的 vehicle_state 统一为 **30**。state=12/46 是数据库中偶发的与电压无关的异常，不在仿真器中模拟。

**验证方法（完成后立刻用 curl 测一下）：**
```bash
# 测试正常唤醒
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}'
# 期望: test_status=1, vehicle_state=170

# 测试越界
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 9.0, "data_type": "float"}'
# 期望: test_status=4, vehicle_state=30

# 测试休眠
curl -X POST http://localhost:8001/simulate/sleep \
  -H "Content-Type: application/json" \
  -d '{"cc2_voltage": 12.0, "cc_voltage": 12.0, "cp_amplitude": 0.0, "supply_voltage": 0.0, "network_wake_enable": 0.0}'
# 期望: test_status=3, vehicle_state=30
```

---

### 任务 2：Backend schemas.py 扩展（和成员 B 对齐后完成）

在 `backend/api/models/schemas.py` 中新增以下模型（与成员 B 协商数据结构后确定）：

```python
# 需求相关
class Requirement(BaseModel)          # 单条需求
class ParsedRequirement(BaseModel)    # 解析后的结构化需求
class RequirementCreate(BaseModel)    # 创建需求的请求体

# 风险分析相关
class RiskAnalysisResult(BaseModel)   # 风险评分结果

# 测试用例相关
class TestCase(BaseModel)             # 单条测试用例
class TestSuite(BaseModel)            # 测试套件（按技术分组）
class ExecutionResult(BaseModel)      # 单条用例的执行结果
```

---

### 任务 3：Backend FR 1.0/1.1 实现

新建文件：

**`backend/api/services/requirement_parser.py`**
- 正则解析 Input Fields（识别信号名词）
- 正则解析 Data Ranges（识别数值范围表达式如 "4.8V to 7.7V"、"exceeds 170"）
- 正则解析 Conditions（识别 when/if/while 等触发条件）
- 正则解析 Expected Actions（识别 shall/must/will + 动词）

**`backend/api/services/requirement_service.py`**
- CSV 导入：`pandas.read_csv()`
- 文本导入：按行分割，识别 `REQ-\d+` 格式
- 直接输入：JSON 反序列化
- 持久化：保存到 `backend/data/requirements/` 目录

**`backend/api/routers/requirements.py`**
```
POST /api/requirements/import/csv
POST /api/requirements/import/text
POST /api/requirements/import/form
GET  /api/requirements
GET  /api/requirements/{id}
PUT  /api/requirements/{id}
DELETE /api/requirements/{id}
POST /api/requirements/{id}/parse
GET  /api/requirements/{id}/parsed
PUT  /api/requirements/{id}/parsed
```

**在 `backend/api/main.py` 中注册路由：**
```python
from api.routers import requirements, risk_analysis, test_design, export
app.include_router(requirements.router, prefix="/api", tags=["需求管理"])
app.include_router(risk_analysis.router, prefix="/api", tags=["风险分析"])
app.include_router(test_design.router, prefix="/api", tags=["测试设计"])
app.include_router(export.router, prefix="/api", tags=["导出"])
```
> 后三个路由文件由成员 B 实现，你先把 `include_router` 占位写上

---

### 任务 4：你需要写的文档

#### 4.1 写给 Test Plan 的三节（交给成员 E 汇总进 Test Plan）

**Chapter: Chosen Testing Framework and Rationale**

写清楚以下内容（参考 DESIGN_PLAN.md 中的测试策略描述）：
- 为什么选 pytest + httpx 而不是 unittest 或 Java/JUnit
- pytest-parametrize 如何实现 EP/BVA 的参数化执行
- 和目标应用（VCU 仿真器）的集成方式
- 大约 300~400 字

**Chapter: Cost Estimation**

填写以下表格并加一段分析：

| 活动 | 手动工作量（人时） | 工具辅助后（人时） | 节省比例 |
|-----|----------------|----------------|---------|
| 需求导入与解析 | 6h | 1h | 83% |
| 风险分析 | 5h | 1h | 80% |
| EP/BVA 用例设计 | 20h | 3h | 85% |
| 决策表设计 | 8h | 2h | 75% |
| 测试脚本开发 | 15h | 5h | 67% |
| 执行与结果收集 | 10h | 2h | 80% |
| **合计** | **64h** | **14h** | **78%** |

**Chapter: Schedule / Checklist**

用 4 周的 Checklist 格式写，参考 DESIGN_PLAN.md 实施顺序章节

#### 4.2 写一份技术接口说明（交给成员 C）

格式：Markdown 文件，命名 `docs/tasks/API_reference_for_frontend.md`

内容：列出你实现的所有 API 端点，每个端点写清楚：
- URL + HTTP 方法
- 请求体的 JSON 字段和类型
- 响应体的 JSON 字段和类型
- 一个示例 curl 命令

这份文件是成员 C 开发前端时的对接文档，写得越清楚，联调越顺。

#### 4.3 写一份仿真器说明文档（交给成员 D）

格式：Markdown，命名 `docs/tasks/simulator_spec_for_doc.md`

内容：
- VCU 仿真器的5个信号名称、物理含义、有效/无效区间（用表格）
- 三种 test_status 的含义（1=PASS/3=SLEEP/4=FAIL）
- 输出字段说明（vehicle_state、vehicle_mode、ready_flag 的所有可能值）
- db_15 的批次差异说明（CC2上界扩展到8.1V）

成员 D 写 Risk Analysis Report 时，全部从这份文件取数据。

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| 仿真器在本地跑通 + curl 验证截图 | 成员 B（联调） | 第1周末 |
| `API_reference_for_frontend.md` | 成员 C | 第1周末 |
| `simulator_spec_for_doc.md` | 成员 D | 第1周末 |
| `schemas.py` 新增模型（和B对齐后） | 成员 B | 第1周内 |
| FR 1.0/1.1 后端 API 可调用 | 成员 B、C | 第2周初 |
| Test Plan 三节文字（Framework/Cost/Schedule） | 成员 E | 第3周初 |
