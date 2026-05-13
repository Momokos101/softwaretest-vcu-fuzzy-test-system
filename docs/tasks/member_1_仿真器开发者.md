# 成员 1 — VCU 仿真器开发者 任务书

---

## 你在答辩中讲什么

**你讲"我们测什么"**——介绍目标应用、它为什么有测试价值、5个输入信号的物理含义、以及你从真实数据库中发现的关键规律。这部分是整个项目的"地基"，让评委理解后面所有测试的意义。

答辩时间：约 3 分钟

---

## 与成员 2 的并行协作说明

**你和成员 2 可以几乎完全并行工作。** 成员 2 的大部分模块（FR 1.0/1.1/2.0/6.0、前端三个页面）完全不依赖你的仿真器。唯一的依赖点是成员 2 的 `simulator_client.py` 和"执行测试用例"功能需要仿真器真正跑起来才能联调。

**第 1 周内必须做一件事：和成员 2 开一个 30 分钟的 API 对齐会。**

会议只需要做一件事：两人当场约定好仿真器的接口格式：
- 请求体字段名和类型（`signal_name`、`value`、`data_type`）
- 响应体字段名和含义（`test_status`、`vehicle_state`、`vehicle_mode`、`ready_flag`…）
- 5 个信号的名称字符串（必须完全一致，中文或英文都行，但两边要统一）

约定好后成员 2 就可以用 mock 数据写 `simulator_client.py`，等你第 1 周末仿真器跑通后，两人只需几个小时完成联调。

**并行时间线：**
```
第 1 周（并行）：
  你：写仿真器核心逻辑
  成员 2：写 FR1/2/6 后端 + 前端三个页面（不需要你的接口）
  同时进行：30 分钟 API 对齐会

第 1 周末：你的仿真器跑通
  → 当天通知成员 2 → 联调 simulator_client（约 2~4 小时）
  → 成员 2 继续写 FR3 的执行功能 + TestCaseDesign.tsx
```

---

## 你负责的代码

### 全新建立 `vcu_simulator/` 目录（独立 FastAPI 服务，端口 8001）

```
vcu_simulator/
├── main.py          FastAPI 入口
├── simulator.py     5 信号判定逻辑（核心）
├── models.py        Pydantic 请求/响应模型
├── constants.py     信号边界常量（来自真实数据库）
└── requirements.txt fastapi, uvicorn, pydantic
```

### 需要实现的 API 端点

| 端点 | 方法 | 说明 |
|-----|-----|-----|
| `/simulate` | POST | 单信号测试（每次发 1 个信号） |
| `/simulate/sleep` | POST | 休眠测试（固定 5 信号组合） |
| `/simulate/batch` | POST | 批量测试（数组输入） |
| `/health` | GET | 健康检查 |
| `/signals` | GET | 返回 5 个信号的边界说明 |
| `/reset` | POST | 重置状态机 |

### 请求 / 响应格式

**`POST /simulate` 请求体：**
```json
{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}
```

**响应体（对应真实数据库字段）：**
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

### 5 个信号的判定逻辑（来自 5 个真实数据库分析）

| 信号 | PASS 条件 → state=170 | FAIL 条件 → state=30 | 特殊值 |
|-----|----------------------|---------------------|-------|
| CC2电压 | [4.8, 7.7]V | <4.8V 或 >7.8V | 12.0V → SLEEP(status=3) |
| CC电压值 | 其他值（如12.0V） | [0.1, 3.9]V | — |
| CP幅值 | 0V 或其他 | [9.1, 12.9]V | — |
| 供电电压 | 0V 或其他 | [9.1, 15.9]V | — |
| 网络唤醒报文使能状态 | 0 | 1 | — |

> ⚠️ 重要：所有 FAIL 的 vehicle_state 统一返回 **30**（不用 12/46，那是偶发噪声）

### 验证方法（完成后立即测试）

```bash
# 启动仿真器
cd vcu_simulator && pip install -r requirements.txt && python main.py

# 测试正常唤醒
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}'
# 期望: test_status=1, vehicle_state=170, ready_flag=1

# 测试越界失败
curl -X POST http://localhost:8001/simulate \
  -H "Content-Type: application/json" \
  -d '{"signal_name": "CC2电压", "value": 9.0, "data_type": "float"}'
# 期望: test_status=4, vehicle_state=30, ready_flag=0

# 测试休眠
curl -X POST http://localhost:8001/simulate/sleep \
  -H "Content-Type: application/json" \
  -d '{"cc2_voltage":12.0,"cc_voltage":12.0,"cp_amplitude":0.0,"supply_voltage":0.0,"network_wake_enable":0.0}'
# 期望: test_status=3, vehicle_state=30
```

---

## 你需要写的文档

### 文档 1：Risk Analysis Report（Artifact 2，10 分）

> 这份报告是关于 VCU 仿真器（目标应用）的风险分析，你最了解这个系统，所以由你来写。

**文件路径：** `docs/Risk_Analysis_Report.md`

**章节结构：**

**第 1 章：目标应用概述**
- VCU 唤醒-休眠控制模块是什么（用外行能懂的语言）
- 在电动汽车充电系统中的位置和作用
- 为什么使用软件仿真器代替真实台架（SIL 是行业标准流程）
- 仿真器的 API 设计（你写的接口）

**第 2 章：测试范围与边界**
- 测试对象：5 个输入信号（名称 + 物理含义 + 有效/无效区间）
- 不在范围内：VCU 内部固件逻辑、CAN 总线物理层

**第 3 章：需求列表**

从 `docs/DESIGN_PLAN.md` 第二节 2.5 复制 10 条 VCU 需求，整理成表格：

| ID | Title | Description | Category |
|----|-------|-------------|----------|
| REQ-001 | CC2 Wake Voltage Valid Range | ... | Input Validation |
| ... | | | |

**第 4 章：风险评估方法**
- 5 维度评分算法说明（Criticality/Boundary/Complexity/State Impact/Testability）
- 每个维度的权重和评分标准
- 优先级映射（≥7.0=High，4.0~6.9=Medium，<4.0=Low）

**第 5 章：风险分析结果**

填写完整的评分表（参考 DESIGN_PLAN.md 第三节 FR 2.0 中的预期结果）：

| 需求ID | Criticality | Boundary | Complexity | State | Testability | 总分 | 优先级 | 理由 |
|--------|------------|---------|-----------|-------|------------|------|-------|-----|
| REQ-001 | 6 | 10 | 4 | 6 | 10 | 7.35 | High | CC2有精确边界4.8/7.7V |
| ... |

**第 6 章：风险矩阵图**
- 气泡图（X=Boundary Sensitivity，Y=Criticality，颜色=优先级）
- 可以截工具界面的图，或用 Excel/PPT 制作

**第 7 章：测试优先级建议**
- 基于风险分，给出推荐的测试执行顺序

### 文档 2：给成员 2 的接口说明文档

**文件路径：** `docs/tasks/simulator_api_for_tool.md`

内容：列出仿真器所有 API 端点，写清楚：
- URL + 方法
- 请求体字段（名称/类型/说明）
- 响应体字段（名称/类型/含义）
- 一个 curl 示例

**第 1 周末前交给成员 2。**

### 文档 3：给成员 3 的仿真器说明文档

**文件路径：** `docs/tasks/simulator_spec_for_tester.md`

内容：
- 5 个信号的物理含义、有效/无效区间（用表格）
- test_status 的含义（1=PASS / 3=SLEEP / 4=FAIL）
- 输出字段说明（vehicle_state / vehicle_mode / ready_flag 所有可能值）
- 真实数据库的 3 个重要发现（CC2=4.8V 能唤醒 / 休眠固定5信号 / db_15 扩展上界）
- 10 条 VCU 需求的最终版本

**第 1 周末前交给成员 3，让他开始写测试计划框架。**

### 文档 4：Test Plan —— Test Items 章节

**交给成员 5 汇总。**

内容（约 400 字 + 表格）：
- 功能测试项（7 个测试套件对应的功能特性）
- 非功能测试项（响应时间 <120s）
- 系统架构描述（三个服务的框图：工具 + 仿真器）

---

## 你依赖谁

**你不依赖任何人的代码。** 你是整个项目的关键路径第一步。

---

## 你需要交付给谁

| 交付物 | 交给谁 | 时间节点 |
|-------|-------|---------|
| 仿真器在本地跑通 + curl 验证截图 | 成员 2（开始工具后端开发） | **第 1 周末** |
| `simulator_api_for_tool.md` | 成员 2 | **第 1 周末** |
| `simulator_spec_for_tester.md` | 成员 3 | **第 1 周末** |
| `Risk_Analysis_Report.md` 草稿 | 成员 5 | 第 2 周末 |
| Test Plan: Test Items 章节 | 成员 5 | 第 2 周末 |
| Risk Report 最终版 | 成员 5 | 第 3 周初 |

---

## 答辩讲稿要点（约 3 分钟）

1. **目标应用是什么**（30s）
   > "我们的目标应用是 VCU 唤醒-休眠行为仿真器，模拟的是电动汽车整车控制器在充电接入时的唤醒和休眠判断逻辑。"

2. **为什么可以用仿真器而不是真实硬件**（30s）
   > "汽车行业标准流程是先对 SIL 仿真模型测试，再接入真实台架。我们基于 5 个真实 BAIC VCU HIL 测试数据库——9615 条记录——建立了仿真逻辑，老师也了解这个项目背景。"

3. **5 个输入信号**（60s）
   > 展示信号表格，重点讲 CC2 电压的物理含义和边界值。

4. **3 个真实数据发现**（60s）
   > "CC2=4.8V 能成功唤醒、休眠测试 5 个信号全部固定、db_15 上界扩展到 8.1V——这说明真实 VCU 行为比规格说明复杂，这正是我们需要系统化测试工具的原因。"
