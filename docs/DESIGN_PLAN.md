# AutoTestDesign 系统设计方案

> Assignment 2 (Final Project) — 基于现有 VCU 智能模糊测试系统改造

---

## 一、项目定位与核心架构

### 1.1 两个系统，职责明确

本项目由**两个独立部分**组成，对应 Assignment 要求的"工具"与"目标应用"：

```
┌──────────────────────────────────────────────────────────┐
│              AutoTestDesign Tool（我们的工具）              │
│                                                          │
│  需求输入 → 解析 → 风险分析 → 测试用例生成 → 执行 → 导出    │
│  FR1.0    FR1.1   FR2.0     FR3.0(+GAN)  FR5.0  FR6.0   │
│                                                          │
│  ✦ GAN 模型负责生成补充的 CC2 电压序列测试数据              │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP POST /simulate
                         │ 发送单个信号（name + value）
                         ↓
┌──────────────────────────────────────────────────────────┐
│          VCU 行为仿真器（目标应用，我们新建）               │
│                                                          │
│  支持 5 种独立输入信号（每次测试发送其中一个）：            │
│   CC2电压 / CC电压值 / CP幅值 / 供电电压 / 网络唤醒报文   │
│                                                          │
│  Output: { test_status, vehicle_state, vehicle_mode,     │
│            ready_flag, cc2_voltage_actual, detail }      │
└──────────────────────────────────────────────────────────┘
```

**AutoTestDesign Tool** 是我们开发的测试工具，负责：
- 管理 VCU 软件需求（FR 1.0/1.1）
- 评估每条需求的测试风险（FR 2.0）
- 用 EP / BVA / 决策表自动生成测试用例（FR 3.0）
- 调用仿真器 API 执行测试并检验结果（FR 5.0）
- 以 JSON / CSV / Excel 导出完整测试制品（FR 6.0）
- 支持用户在每个阶段交互式审阅和修改（Interactive Review）

**VCU 行为仿真器** 是我们的目标应用，负责：
- 接收 5 种不同信号之一的测试输入
- 按照 VCU 唤醒-休眠逻辑返回系统状态
- 无需连接物理硬件即可验证 VCU 行为

### 1.2 为什么选择 VCU 仿真器作为目标应用

1. **业务真实性**：汽车行业在接入真实台架前，标准流程是先对 SIL 仿真模型测试，完全符合工程惯例
2. **5个独立输入信号**：CC2电压、CC电压值、CP幅值、供电电压、网络唤醒——每个信号都有清晰的有效/无效区间，天然适合 EP 和 BVA
3. **多状态多条件**：正常唤醒/异常失败/休眠三种测试策略，以及 5 个信号的组合，适合决策表
4. **数据真实**：所有边界值均来自真实 BAIC VCU HIL 测试数据库（5个DB，共 9615 条记录）
5. **老师背景**：负责本课的老师熟悉该项目背景，理解仿真器代替真实台架的合理性

### 1.3 测试数据生成整体架构

AutoTestDesign Tool 对 5 种输入信号采用**分层生成策略**，核心设计原则是：**让生成方法与信号的物理特征和测试目的精确匹配**。

```
                    AutoTestDesign Tool — 测试数据生成层
                    =====================================

  ┌─────────────────────────────────────────────────────────────┐
  │  信号           生成方法              依据                   │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  CC2电压   →   EP + BVA（主）        PASS/FAIL双侧区间      │
  │            →   GAN序列（辅）         时序边界穿越场景        │
  │                                                             │
  │  CC电压值  →   EP + BVA              纯失效区间[0.1,3.9]V   │
  │                                                             │
  │  CP幅值    →   EP + BVA              纯失效区间[9.1,12.9]V  │
  │                                                             │
  │  供电电压  →   EP + BVA              纯失效区间[9.1,15.9]V  │
  │                                                             │
  │  网络唤醒  →   EP（穷举）            二值信号，仅0和1       │
  │                                                             │
  └────────────────────────┬────────────────────────────────────┘
                           │  每次发送单信号 POST /simulate
                           ↓
              VCU 行为仿真器（目标应用）
```

**GAN 在工具中的定位**（仅作用于 CC2 电压）：

```
EP/BVA 覆盖的场景：  单次注入一个离散电压值 → 检验该值对应的输出状态
GAN 覆盖的场景：     注入连续变化的8步电压序列 → 检验VCU在动态过程中
                     是否在正确位置发生状态转变（边界穿越检测）

EP/BVA → 验证"什么电压值导致什么状态"（静态）
GAN    → 验证"电压如何变化时VCU会在何处转变"（动态）
```

### 1.4 现有代码的复用策略

| 现有模块 | 归属 | 复用方式 |
|---------|------|---------|
| FastAPI 骨架 + 路由结构 | AutoTestDesign Tool | 新增 FR 1.0~7.0 路由 |
| GAN 模型（Conv1D cGAN） | AutoTestDesign Tool | 专用于 CC2 电压时序序列生成 |
| 报告服务（JSON/Markdown） | AutoTestDesign Tool | 扩展为 FR 6.0 导出 |
| React 前端 + shadcn/ui | AutoTestDesign Tool | 新增 4 个功能页面 |
| configs/config_vcu_*.py | VCU 仿真器 | 仿真逻辑直接引用这些常量 |
| data/vcu/*.npy | AutoTestDesign Tool | GAN 模型已训练数据，验证仿真结果 |

---

## 二、VCU 行为仿真器（目标应用）设计

> **数据基础**：以下所有字段名、数值边界、状态编码均来自对 5 个真实 BAIC VCU HIL 测试数据库的完整分析（db_10 / db_11 / db_15 / db / db_2，共 **9615 条**测试记录），具备充分的真实依据。

---

### 2.1 五大输入信号全景分析

从真实数据中，完整的测试体系包含 **5 种独立输入信号**，每种信号对应不同的物理含义和有效区间：

| 信号名 | 物理含义 | 测试策略 | 有效区间（PASS→state=170） | 无效区间（FAIL→state=30） |
|--------|---------|---------|--------------------------|------------------------|
| **CC2电压** | AC 充电唤醒电压（主唤醒信号） | strategy=0（正常唤醒）+ strategy=1（越界） | **[4.8, 7.7]V** | <4.8V 或 >7.7V；7.8V 为灰色边界 |
| **CC电压值** | 充电枪 CC 接触电压（线缆健康检测） | strategy=1（异常注入） | >4.0V（正常接线或无枪） | **[0.1, 3.9]V**（接触不良/错误线阻） |
| **CP幅值** | 控制导引信号幅值（AC 充电协议） | strategy=1（异常注入） | 0.0V（待机状态） | **[9.1, 12.9]V**（协议冲突或幅值异常） |
| **供电电压** | 外部交流供电电压 | strategy=1（异常注入） | 0.0V（无外部供电） | **[9.1, 15.9]V**（意外供电/过压） |
| **网络唤醒报文使能状态** | 网络远程唤醒使能（二值） | strategy=1（异常注入） | 0（未使能） | **1**（使能时与 CC2 唤醒冲突→FAIL） |

**三种测试策略的完整含义**：

| strategy | type | 触发方式 | 预期结果 | 数据量（5DB合计） |
|---------|------|---------|---------|----------------|
| **0**（正常唤醒） | 1 | 仅发送 CC2电压（单信号，在有效区间内） | status=1, state=170 | ~2168 条 |
| **1**（异常注入） | 1 | 仅发送某一信号（单信号，在无效区间内） | status=4, state=30 | ~4380 条 |
| **-3**（休眠测试） | 2 | 发送固定5信号组合（CC2=12.0V + 其他=0） | status=3, state=30 | ~3308 条 |

**核心输出字段（真实 actual_output.data 的关键子集）**：

| 字段名 | 正常唤醒（status=1） | 休眠（status=3） | 失败（status=4） |
|--------|-------------------|----------------|----------------|
| `整车State状态` | **170** | **30** | **30**（主要）/ 12/46（偶发） |
| `整车模式` | **5**（唤醒模式） | **2**（休眠模式） | **2** |
| `动力防盗允许READY标志位` | **1** | **0** | **0** |
| `整车禁止READY标志位` | 1 | 0 | 0 |
| `BMS低压唤醒指令` | 1（恒定） | 1（恒定） | 1（恒定） |
| `MCU低压唤醒指令` | 1（恒定） | 1（恒定） | 1（恒定） |
| `蓄电池电压` | 12.92V（恒定） | 12.92V（恒定） | 12.92V（恒定） |

---

### 2.2 仿真器定位

VCU 仿真器是一个**独立的轻量 FastAPI 服务**（端口 8001），以真实数据库的字段和边界为蓝本实现 VCU 单信号响应逻辑。每次测试只传入**一个信号**（名称+值），仿真器判断该信号是否在有效区间内，返回对应的 VCU 状态。

---

### 2.3 核心 API

**单信号测试接口（唤醒测试 strategy=0/1）**：

```
POST http://localhost:8001/simulate
Content-Type: application/json

请求体（对应真实 type=1 的 actual_input 格式）：
{
  "signal_name": "CC2电压",   // 5种信号之一
  "value": 6.3,               // 该信号的测试值
  "data_type": "float"        // float 或 int
}

响应体（对应真实 actual_output 关键字段）：
{
  "test_status": 1,           // 1=PASS, 3=SLEEP, 4=FAIL
  "vehicle_state": 170,       // 整车State状态
  "vehicle_mode": 5,          // 整车模式 (5=唤醒, 2=休眠)
  "ready_flag": 1,            // 动力防盗允许READY标志位
  "bms_wake_cmd": 1,          // BMS低压唤醒指令（恒定=1）
  "mcu_wake_cmd": 1,          // MCU低压唤醒指令（恒定=1）
  "battery_voltage": 12.92,   // 蓄电池电压（恒定）
  "actual_duration": 100.4,   // 模拟测试时长（秒，基于真实均值）
  "detail": "CC2电压=6.3V ∈ [4.8,7.7]V → 正常唤醒 vehicle_state=170"
}
```

**休眠测试接口（strategy=-3，固定5信号）**：

```
POST http://localhost:8001/simulate/sleep
Content-Type: application/json

请求体（对应真实 type=2 的固定组合）：
{
  "cc2_voltage": 12.0,               // 固定值，触发休眠
  "cc_voltage": 12.0,                // 固定值
  "cp_amplitude": 0.0,               // 固定值
  "supply_voltage": 0.0,             // 固定值
  "network_wake_enable": 0.0         // 固定值
}

响应体：
{
  "test_status": 3,           // 3=SLEEP（正常休眠，不是FAIL）
  "vehicle_state": 30,
  "vehicle_mode": 2,
  "ready_flag": 0,
  "actual_duration": 100.3
}
```

**批量测试接口**：

```
POST /simulate/batch
[
  {"signal_name": "CC2电压", "value": 4.8},
  {"signal_name": "CC2电压", "value": 4.9},
  {"signal_name": "CC电压值", "value": 2.0}
]
→ 返回数组，每条对应一个响应
```

**附加端点**：

```
GET  /health          健康检查
GET  /signals         返回5个信号的名称、类型、有效/无效区间说明
POST /reset           重置状态机
```

---

### 2.4 重要数据说明（核查5个数据库后的修正）

> 以下三点是对原始推断的数据驱动修正，在实现仿真器和编写测试报告时必须准确使用：

**修正 1：CC2 越界时 vehicle_state 统一为 30（非 12/46）**
- 跨5个DB统计：CC2 < 4.8V 的全部35条记录 → vehicle_state=**30**（无一例外）
- CC2 ∈ [8.0, 12.0)V 的全部37条记录 → vehicle_state=**30**（1条偶发 state=185）
- 之前推断"CC2<3V → state=12，CC2∈(8,12)V → state=46"**不成立**
- state=12、state=46 确实存在于数据库，但它们是**偶发的非电压相关异常态**，无法通过特定电压值可靠触发

**修正 2：CC2=4.8V 能成功唤醒 VCU（status 含义的澄清）**
- db_2.db 中 CC2=4.8V 的 6 条记录：type=1, strategy=1, **test_status=4**，但 **vehicle_state=170, mode=5, ready=1**
- test_status=4 是因为这批记录被作为 strategy=1（期望失败）的异常注入测试，测试框架期望 state=30，实际 VCU 输出了 state=170，所以测试框架判定"异常"
- **VCU 硬件行为本身**：CC2=4.8V → vehicle_state=170（成功唤醒）
- 结论：4.8V 是真实的 VCU 唤醒下界，BVA 中 CC2=4.8V → 仿真器应返回 state=170（PASS）

**修正 3：db_15 CC2 有效上界扩展至 8.1V（批次配置差异）**
- db_10、db_11、db.db、db_2.db：CC2 strategy=0 PASS 最大值 ≤ 7.8V
- **db_15**：CC2 strategy=0 PASS 最大值 = **8.1V**（939 条 PASS 记录，含 7.8V/7.9V/8.0V/8.1V）
- 同时 db_15 也有 7.8V/7.9V/8.0V → FAIL（strategy=1 测试中）
- 说明 db_15 代表不同 VCU 固件版本或硬件批次，有效区间扩展到 [4.9, 8.1]V
- **仿真器采用主流配置（4DB一致）：valid = [4.8, 7.7]V**，并在 `/signals` 端点说明 db_15 配置差异

---

### 2.5 仿真器状态判定逻辑（数据核查后最终版）

```python
class VCUSimulator:

    # 来自真实数据的边界常量（核查5个DB后确认）
    SIGNAL_RULES = {
        "CC2电压": {
            "valid_min": 4.8,    # db_2确认：4.8V → vehicle_state=170（VCU成功唤醒）
            "valid_max": 7.7,    # 4DB一致：7.7V为稳定上界；db_15异常扩展至8.1V（批次差异）
            "boundary": 7.8,     # 灰色区域：db_10有PASS/FAIL，其余DB均FAIL
            "sleep_trigger": 12.0,
            # ⚠️ 注意：CC2越界时 vehicle_state 统一为 30
            # state=12/46 是数据库中偶发的与电压无关的异常态，不在仿真器中模拟
        },
        "CC电压值": {
            "fail_min": 0.1,   # 数据库中该信号的最小测试值
            "fail_max": 3.9,   # 数据库中该信号 status=4 的最大值
            # 0.1~3.9V → FAIL; 其他 → PASS
        },
        "CP幅值": {
            "fail_min": 9.1,
            "fail_max": 12.9,
            # 9.1~12.9V → FAIL; 0V → PASS（待机状态）
        },
        "供电电压": {
            "fail_min": 9.1,
            "fail_max": 15.9,
            # 9.1~15.9V → FAIL; 0V → PASS（无外部供电）
        },
        "网络唤醒报文使能状态": {
            "fail_value": 1.0,
            # 1.0 → FAIL (176/177条确认); 0.0 → PASS
        }
    }

    def simulate(self, signal_name: str, value: float) -> dict:
        
        if signal_name == "CC2电压":
            v = value
            if self.SIGNAL_RULES["CC2电压"]["valid_min"] <= v <= self.SIGNAL_RULES["CC2电压"]["valid_max"]:
                return self._pass(detail=f"CC2电压={v}V ∈ [4.8,7.7]V → 正常唤醒")
            elif abs(v - 12.0) < 0.05:
                return self._sleep(detail=f"CC2电压={v}V = 12.0V → 触发休眠")
            elif abs(v - 7.8) < 0.05:
                return self._fail(state=30, detail=f"CC2电压={v}V 在灰色边界7.8V → FAIL")
            else:
                # 所有越界情况统一返回 state=30
                # (state=12/46 在真实数据中偶发但与电压无直接关联，不在仿真器中模拟)
                return self._fail(state=30, detail=f"CC2电压={v}V 越界 → FAIL (state=30)")

        elif signal_name == "CC电压值":
            if 0.1 <= value <= 3.9:
                return self._fail(state=30, detail=f"CC电压值={value}V ∈ [0.1,3.9]V → 接触不良FAIL")
            else:
                return self._pass(detail=f"CC电压值={value}V 正常 → PASS")

        elif signal_name == "CP幅值":
            if 9.1 <= value <= 12.9:
                return self._fail(state=30, detail=f"CP幅值={value}V ∈ [9.1,12.9]V → 协议冲突FAIL")
            else:
                return self._pass(detail=f"CP幅值={value}V 正常 → PASS")

        elif signal_name == "供电电压":
            if 9.1 <= value <= 15.9:
                return self._fail(state=30, detail=f"供电电压={value}V ∈ [9.1,15.9]V → 过压FAIL")
            else:
                return self._pass(detail=f"供电电压={value}V 正常 → PASS")

        elif signal_name == "网络唤醒报文使能状态":
            if value == 1.0:
                return self._fail(state=30, detail="网络唤醒使能=1 与CC2唤醒冲突 → FAIL")
            else:
                return self._pass(detail="网络唤醒使能=0 不干扰CC2唤醒 → PASS")

    def _pass(self, detail=""):
        return {"test_status": 1, "vehicle_state": 170, "vehicle_mode": 5,
                "ready_flag": 1, "bms_wake_cmd": 1, "mcu_wake_cmd": 1,
                "battery_voltage": 12.92, "actual_duration": 100.4, "detail": detail}

    def _fail(self, state=30, detail=""):
        return {"test_status": 4, "vehicle_state": state, "vehicle_mode": 2,
                "ready_flag": 0, "bms_wake_cmd": 1, "mcu_wake_cmd": 1,
                "battery_voltage": 12.92, "actual_duration": 100.6, "detail": detail}

    def _sleep(self, detail=""):
        return {"test_status": 3, "vehicle_state": 30, "vehicle_mode": 2,
                "ready_flag": 0, "bms_wake_cmd": 1, "mcu_wake_cmd": 1,
                "battery_voltage": 12.92, "actual_duration": 100.3, "detail": detail}
```

---

### 2.5 VCU 仿真器需求（完整版 10 条）

基于 5 个信号的真实数据，更新 VCU 需求 CSV：

```csv
ID,Title,Description,Category
REQ-001,CC2 Wake Voltage Valid Range,"System shall accept CC2 voltage in [4.8V, 7.7V] as valid wake-up signal and output vehicle_state=170 vehicle_mode=5 ready_flag=1. Value 7.8V is a boundary case observed to FAIL in majority of real tests.",Input Validation
REQ-002,CC2 Voltage Below Valid Range,"System shall output test_status=4 vehicle_state=30 vehicle_mode=2 ready_flag=0 when CC2 voltage is below 4.8V. All 35 real test records with CC2 < 4.8V confirm vehicle_state=30.",Input Validation
REQ-003,CC2 Voltage Above Valid Range,"System shall output test_status=4 vehicle_state=30 vehicle_mode=2 ready_flag=0 when CC2 voltage exceeds 7.8V and is not the sleep trigger 12.0V. Real data: 37/38 records confirm state=30.",Input Validation
REQ-004,Sleep Trigger Voltage,"System shall output test_status=3 vehicle_state=30 vehicle_mode=2 ready_flag=0 when CC2 voltage equals exactly 12.0V with sleep command (type=2).",State Transition
REQ-005,CC Voltage Cable Check,"System shall output test_status=4 vehicle_state=30 when CC电压值 is in range [0.1V, 3.9V], indicating invalid cable contact resistance.",Safety
REQ-006,CP Amplitude Interference Check,"System shall output test_status=4 vehicle_state=30 when CP幅值 is in range [9.1V, 12.9V], indicating CP signal conflict or protocol anomaly.",Safety
REQ-007,Supply Voltage Overvoltage Check,"System shall output test_status=4 vehicle_state=30 when 供电电压 is in range [9.1V, 15.9V], indicating unexpected external supply or overvoltage.",Safety
REQ-008,Network Wake Conflict Check,"System shall output test_status=4 vehicle_state=30 when 网络唤醒报文使能状态=1 conflicts with CC2 wake protocol. Normal state is 0 (disabled).",Safety
REQ-009,READY Flag Consistency,"When vehicle_state=170 system shall set ready_flag=1. When vehicle_state=30 system shall set ready_flag=0. These two fields must always be consistent.",State Control
REQ-010,Test Duration Compliance,"Each single-signal test shall complete within 120 seconds. Based on real HIL data, actual_duration averages approximately 100 seconds.",Timing
```

---

### 2.6 仿真器目录结构

```
vcu_simulator/
├── main.py           FastAPI 入口（端口 8001）
├── simulator.py      5信号判定逻辑（VCUSimulator 类）
├── models.py         Pydantic 请求/响应模型
├── constants.py      信号边界常量（来自5个真实数据库分析）
└── requirements.txt  fastapi, uvicorn, pydantic
```

---

## 三、AutoTestDesign Tool — FR 逐条实现方案

### FR 1.0 — Input/Parsing（需求输入）✅ 必须实现

**要求**：能从 CSV、纯文本、直接表单输入等多种来源导入软件需求

#### 后端

新增 `backend/api/routers/requirements.py`：
```
POST /api/requirements/import/csv     上传 CSV 文件（multipart/form-data）
POST /api/requirements/import/text    粘贴纯文本（按行解析）
POST /api/requirements/import/form    表单直接输入（JSON body）
GET  /api/requirements                获取需求列表
GET  /api/requirements/{id}           获取单条需求
PUT  /api/requirements/{id}           更新需求（Interactive Review）
DELETE /api/requirements/{id}         删除需求
```

新增 `backend/api/services/requirement_service.py`：
- CSV：`pandas.read_csv()` → 按列映射到 Requirement 模型
- 文本：按行分割，正则识别 `REQ-\d+` 编号
- 直接输入：JSON 直接反序列化
- 持久化：存储到 `data/requirements/` 目录下的 JSON 文件

**VCU 仿真器的 6 条预定义需求**（提供 CSV 模板）：

```csv
ID,Title,Description,Category
REQ-001,CC2 Voltage Input Range,"System shall accept CC2 wake-up voltage in range [4.9V, 7.7V]. Values at 7.8V are boundary cases. Values outside [4.9V, 7.8V] shall result in test_status=4 with vehicle_state=30.",Input Validation
REQ-002,READY Flag Activation,"System shall set READY flag to 1 when VEHICLE_STATUS exceeds 170. Flag must be set within 10ms.",State Control
REQ-003,READY Flag Deactivation,"System shall clear READY flag to 0 when VEHICLE_STATUS drops below 30. Tolerance: ±5 units.",State Control
REQ-004,Wake State Duration,"System shall maintain wake state for at least 100ms before transitioning to sleep.",Timing
REQ-005,Sleep Transition Voltage,"System shall transition to sleep mode when cc2_voltage reaches 12.0V steady state for 50ms.",State Transition
REQ-006,Anomaly Detection,"System shall detect and report anomaly types: state_follow_mismatch / error / stuck / ready_flag_mismatch.",Safety
```

#### 前端

新增 `RequirementInput.tsx`：
- Tab 1：CSV 文件拖拽上传，预览解析结果再确认导入
- Tab 2：文本框粘贴原始需求，显示自动识别出的条目
- Tab 3：表单逐字段填写
- 下方：已导入需求表格，每行支持内联编辑（Interactive Review）

---

### FR 1.1 — Requirement Structuring（需求结构化）✅ 必须实现

**要求**：解析并 tokenize 原始文本，识别 Input Fields、Data Ranges、Conditions、Expected Actions

#### 解析器设计

新增 `backend/api/services/requirement_parser.py`，基于正则规则识别四类结构：

```python
class RequirementParser:
    # Input Fields：识别名词性技术术语（电压、状态、标志位等）
    FIELD_PATTERNS = [r'\b(CC2[_\s]voltage|vehicle[_\s]status|READY[_\s]flag|cc2_voltage)\b']

    # Data Ranges：识别数值范围表达式
    RANGE_PATTERNS = [
        r'(\d+\.?\d*)\s*V?\s+to\s+(\d+\.?\d*)\s*V',       # "4.8V to 7.8V"
        r'(?:exceeds|above|greater\s+than)\s+(\d+)',        # "exceeds 170"
        r'(?:below|less\s+than|drops\s+below)\s+(\d+)',     # "drops below 30"
        r'(?:reaches|equals?)\s+(\d+\.?\d*)\s*V',          # "reaches 12.0V"
    ]

    # Conditions：识别触发条件
    CONDITION_KEYWORDS = ['when', 'if', 'while', 'during', 'after', 'before', 'until']

    # Expected Actions：识别 shall/must/will + 动词
    ACTION_PATTERN = r'(?:shall|must|will)\s+([a-z][a-z\s]+?)(?:\.|,|$)'
```

**REQ-001 解析结果示例**：
```json
{
  "requirement_id": "REQ-001",
  "input_fields": ["cc2_voltage"],
  "data_ranges": [
    {"field": "cc2_voltage", "min": 4.9, "max": 7.7, "unit": "V", "type": "inclusive",
     "boundary_note": "7.8V is grey zone (FAIL in majority of real test records)"}

  ],
  "conditions": ["wake-up mode active"],
  "expected_actions": [
    "accept voltage input and maintain wake state",
    "trigger error state if value is out of range"
  ]
}
```

**REQ-002 解析结果示例**：
```json
{
  "requirement_id": "REQ-002",
  "input_fields": ["vehicle_status", "ready_flag"],
  "data_ranges": [
    {"field": "vehicle_status", "min": 170, "max": 255, "type": "lower_bound"}
  ],
  "conditions": ["system in WAKING or WAKE state"],
  "expected_actions": ["set READY flag to 1 within 10ms"]
}
```

#### API 端点
```
POST /api/requirements/{id}/parse   触发解析（返回解析结果）
GET  /api/requirements/{id}/parsed  获取已解析的结构
PUT  /api/requirements/{id}/parsed  手动修改解析结果（Interactive Review）
```

#### 前端展示

在 `RequirementInput.tsx` 的需求详情区展示四栏卡片：
- **Input Fields**：字段名标签列表（可增删）
- **Data Ranges**：范围可视化（进度条形式），双击可编辑 min/max
- **Conditions**：触发条件列表（可编辑）
- **Expected Actions**：预期动作列表（可编辑）

---

### FR 2.0 — Risk Analysis & Prioritization（风险分析）✅ 必须实现

**要求**：为每条需求分配 Risk Score 和 Test Priority（High / Medium / Low）

#### 风险评分算法（5 维度加权）

| 维度 | 权重 | 评分说明 |
|-----|------|---------|
| Criticality | 35% | Safety=10, State Transition=8, State Control=7, Input=6, Timing=4 |
| Boundary Sensitivity | 25% | 有精确数值边界=10，有范围但无精确值=6，无边界=2 |
| Complexity | 20% | 条件数 × 2 + 范围数 × 2（上限 10） |
| State Impact | 15% | 影响多状态=10，影响单状态=6，不影响状态=2 |
| Testability | 5% | 直接可测=10（反向：越难测风险越低） |

优先级映射：Score ≥ 7.0 → **High**，4.0~6.9 → **Medium**，< 4.0 → **Low**

**VCU 6 条需求的预期评分**：

| ID | Criticality | Boundary | Complexity | State | Testability | **Score** | **Priority** |
|----|------------|---------|-----------|-------|------------|---------|------------|
| REQ-001 | 6 (Input) | 10 (精确 4.9/7.7，灰色 7.8) | 4 | 6 | 10 | **7.35** | **High** |
| REQ-002 | 7 (State) | 10 (精确 170) | 6 | 10 | 10 | **8.30** | **High** |
| REQ-003 | 7 (State) | 8 (精确 30 ±5) | 6 | 10 | 10 | **8.05** | **High** |
| REQ-004 | 4 (Timing) | 6 (100ms) | 2 | 4 | 8 | **4.50** | **Medium** |
| REQ-005 | 8 (Transition) | 10 (精确 12.0V) | 4 | 10 | 10 | **8.70** | **High** |
| REQ-006 | 10 (Safety) | 4 (无精确范围) | 8 | 8 | 8 | **7.80** | **High** |

#### API 端点
```
POST /api/risk-analysis/analyze/{req_id}   分析单条需求
POST /api/risk-analysis/analyze-all        批量分析
GET  /api/risk-analysis/report             风险报告
PUT  /api/risk-analysis/{req_id}/override  手动覆盖（Interactive Review）
```

#### 前端：`RiskAnalysis.tsx`
- 顶部：风险矩阵热力图（X=Boundary Sensitivity，Y=Criticality）
- 需求列表：每行显示彩色优先级徽章 + Score + 各维度分项
- 可点击任意需求 → 弹窗手动调整各维度分值（Interactive Review）
- 批量分析按钮（调用 `/analyze-all`）

---

### FR 3.0 — Black-Box Test Design + Execution（黑盒测试设计与执行）✅ 必须实现

**要求**：自动生成至少 3 种 ISO 29119-4 黑盒测试技术的用例，并能执行

本 FR 分为**两个子步骤**：

```
步骤 A（设计）：根据解析后的需求，生成结构化测试用例（含预期结果）
步骤 B（执行）：将测试用例作为请求发送给 VCU 仿真器 API，比对响应
```

#### 3.1 等价划分（Equivalence Partitioning）

针对 **5 个输入信号**，分别划分等价类。每个信号独立测试，每次请求只传一个信号。

**所有信号的 EP 测试用例**：

| 用例 ID | 信号名 | 等价类 | 测试值 | 预期 test_status | 预期 vehicle_state | 预期 ready_flag | 覆盖需求 |
|--------|-------|-------|-------|----------------|------------------|----------------|---------|
| EP-CC2-V1 | CC2电压 | Valid（正常唤醒） | 6.30 V | 1 (PASS) | 170 | 1 | REQ-001 |
| EP-CC2-I1 | CC2电压 | Invalid-Low（低于下界） | 3.00 V | 4 (FAIL) | **30** | 0 | REQ-002 |
| EP-CC2-I2 | CC2电压 | Invalid-High（高于上界） | 9.00 V | 4 (FAIL) | **30** | 0 | REQ-003 |
| EP-CC2-S1 | CC2电压 | Sleep trigger | 12.00 V | 3 (SLEEP) | 30 | 0 | REQ-004 |
| EP-CC-V1 | CC电压值 | Valid（正常接线） | 12.00 V | 1 (PASS) | 170 | 1 | REQ-005 |
| EP-CC-I1 | CC电压值 | Invalid（接触不良） | 2.00 V | 4 (FAIL) | 30 | 0 | REQ-005 |
| EP-CP-V1 | CP幅值 | Valid（待机） | 0.00 V | 1 (PASS) | 170 | 1 | REQ-006 |
| EP-CP-I1 | CP幅值 | Invalid（协议冲突） | 11.00 V | 4 (FAIL) | 30 | 0 | REQ-006 |
| EP-SV-V1 | 供电电压 | Valid（无外部供电） | 0.00 V | 1 (PASS) | 170 | 1 | REQ-007 |
| EP-SV-I1 | 供电电压 | Invalid（过压） | 12.50 V | 4 (FAIL) | 30 | 0 | REQ-007 |
| EP-NW-V1 | 网络唤醒报文使能状态 | Valid（未使能） | 0 | 1 (PASS) | 170 | 1 | REQ-008 |
| EP-NW-I1 | 网络唤醒报文使能状态 | Invalid（冲突使能） | 1 | 4 (FAIL) | 30 | 0 | REQ-008 |

> EP 共 12 条测试用例，覆盖 5 个信号 × 有效/无效等价类

#### 3.2 边界值分析（Boundary Value Analysis）

对有连续值域的 4 个信号（除网络唤醒外）各做 5~7 点 BVA。

**CC2电压 BVA**（最重要，7点边界，δ=0.1V）：

| 用例 ID | 边界类型 | 测试值 | 预期 test_status | 预期 vehicle_state | 说明 |
|--------|---------|-------|----------------|------------------|-----|
| BVA-CC2-1 | just_below_min | 4.70 V | 4 (FAIL) | 30 | 低于规格下界 4.8V |
| BVA-CC2-2 | exact_min | **4.80 V** | 1 (PASS) | 170 | 规格下界（db_2确认PASS） |
| BVA-CC2-3 | just_above_min | 4.90 V | 1 (PASS) | 170 | 5个DB均确认PASS |
| BVA-CC2-4 | nominal | 6.30 V | 1 (PASS) | 170 | 中间稳定值 |
| BVA-CC2-5 | just_below_max | 7.70 V | 1 (PASS) | 170 | 所有DB确认最高稳定PASS值 |
| BVA-CC2-6 | exact_boundary | **7.80 V** | 4 (FAIL) | 30 | 灰色边界，多数FAIL |
| BVA-CC2-7 | just_above_max | 7.90 V | 4 (FAIL) | 30 | 明确越界 |

**CC电压值 BVA**（失效区间 [0.1, 3.9]V）：

| 用例 ID | 边界类型 | 测试值 | 预期 test_status | 预期 vehicle_state |
|--------|---------|-------|----------------|------------------|
| BVA-CC-1 | just_below_fail | 0.00 V | 1 (PASS) | 170 |
| BVA-CC-2 | exact_fail_min | **0.10 V** | 4 (FAIL) | 30 |
| BVA-CC-3 | mid_fail | 2.00 V | 4 (FAIL) | 30 |
| BVA-CC-4 | exact_fail_max | **3.90 V** | 4 (FAIL) | 30 |
| BVA-CC-5 | just_above_fail | 4.00 V | 1 (PASS) | 170 |

**CP幅值 BVA**（失效区间 [9.1, 12.9]V）：

| 用例 ID | 边界类型 | 测试值 | 预期 test_status | 预期 vehicle_state |
|--------|---------|-------|----------------|------------------|
| BVA-CP-1 | normal_idle | 0.00 V | 1 (PASS) | 170 |
| BVA-CP-2 | just_below_fail | 9.00 V | 1 (PASS) | 170 |
| BVA-CP-3 | exact_fail_min | **9.10 V** | 4 (FAIL) | 30 |
| BVA-CP-4 | mid_fail | 11.00 V | 4 (FAIL) | 30 |
| BVA-CP-5 | exact_fail_max | **12.90 V** | 4 (FAIL) | 30 |
| BVA-CP-6 | just_above_fail | 13.00 V | 1 (PASS) | 170 |

**供电电压 BVA**（失效区间 [9.1, 15.9]V）：

| 用例 ID | 边界类型 | 测试值 | 预期 test_status | 预期 vehicle_state |
|--------|---------|-------|----------------|------------------|
| BVA-SV-1 | normal | 0.00 V | 1 (PASS) | 170 |
| BVA-SV-2 | just_below_fail | 9.00 V | 1 (PASS) | 170 |
| BVA-SV-3 | exact_fail_min | **9.10 V** | 4 (FAIL) | 30 |
| BVA-SV-4 | mid_fail | 12.50 V | 4 (FAIL) | 30 |
| BVA-SV-5 | exact_fail_max | **15.90 V** | 4 (FAIL) | 30 |
| BVA-SV-6 | just_above_fail | 16.00 V | 1 (PASS) | 170 |

> BVA 共 24 条用例，重点覆盖每个信号的失效区间上下边界

#### 3.3 决策表（Decision Tables）

决策表测试**多信号组合**对 VCU 状态的影响，是 5 个独立信号之外最重要的补充。

**决策表：信号有效性 × 预期输出**（条件：各信号是否在有效区间）

| 规则 | CC2电压 | CC电压值 | CP幅值 | 供电电压 | 网络唤醒 | → test_status | → vehicle_state | 覆盖需求 |
|-----|--------|---------|-------|---------|---------|--------------|----------------|---------|
| DT-R1 | Valid [4.8,7.7] | Valid | Valid | Valid | 0 | **1 (PASS)** | **170** | REQ-001~009 |
| DT-R2 | **Invalid** <4.8V | Valid | Valid | Valid | 0 | **4 (FAIL)** | **30** | REQ-002 |
| DT-R3 | **Invalid** >7.8V | Valid | Valid | Valid | 0 | **4 (FAIL)** | **30** | REQ-003 |
| DT-R4 | Valid | **Invalid** [0.1,3.9]V | Valid | Valid | 0 | **4 (FAIL)** | **30** | REQ-005 |
| DT-R5 | Valid | Valid | **Invalid** [9.1,12.9]V | Valid | 0 | **4 (FAIL)** | **30** | REQ-006 |
| DT-R6 | Valid | Valid | Valid | **Invalid** [9.1,15.9]V | 0 | **4 (FAIL)** | **30** | REQ-007 |
| DT-R7 | Valid | Valid | Valid | Valid | **1** | **4 (FAIL)** | **30** | REQ-008 |
| DT-R8 | 12.0V（Sleep） | 12.0V | 0.0V | 0.0V | 0 | **3 (SLEEP)** | **30** | REQ-004 |

> 决策表反映了真实测试策略（strategy=1）的核心思想：一个信号异常就会导致整体 FAIL

#### 3.4 五种信号的测试数据生成原理

> **重要设计依据**：对 5 个真实 BAIC VCU 数据库（共 9615 条记录）的分析表明，各信号在真实测试中的取值方式存在本质差异。AutoTestDesign 工具根据这一差异，为每种信号选择最合适的生成策略，而不是对所有信号一律使用同一方法。

---

##### 信号 1：CC2电压 — EP + BVA + GAN 序列补充

**数据特征**：
- strategy=0（正常唤醒测试）：CC2 电压以 0.1V 步长在 [4.9, 7.7]V 区间均匀扫描，每个值重复 10~15 次
- strategy=1（越界异常测试）：以 0.1V 步长向下扫描至 4.1V，向上扫描至 8.0V

**为什么用 EP + BVA（主方法）**：
CC2 电压存在明确的 PASS 区间 [4.8, 7.7]V、两个无效区间（低越界 / 高越界）以及一个精确的休眠触发值 12.0V。等价类划分直接对应这四个区间；7.8V 灰色边界（真实数据中多数 FAIL）正是边界值分析最有价值的地方。EP+BVA 能以最少的用例数获得最高的区间覆盖率。

**为什么补充 GAN 序列测试（辅助方法）**：

EP/BVA 生成的是**离散单值**，每条测试只发送一个 CC2 值，这对应真实测试中的单次触发。但 VCU 在真实台架测试中是对**电压时间序列**做响应的：电压从 7.5V 缓慢爬升越过 7.7V 是一种场景，从 5V 快速跳变到 7.8V 是另一种场景，两者对 VCU 状态机的冲击不同。

现有 Conv1D 条件 GAN 模型经过真实车辆数据（`train_voltages.npy`）训练，能够生成符合真实物理规律的 CC2 **电压时序序列**（每条序列 8 个时间步）。这些序列覆盖了 EP/BVA 单值测试无法模拟的**动态边界穿越场景**：

```
GAN 生成示例（含边界穿越的异常序列）：
  [5.2, 6.1, 7.3, 7.6, 7.7, 7.8, 8.1, 9.2]  ← 电压缓慢越过上界
  [4.9, 4.8, 4.7, 4.6, 4.5, 4.3, 4.1, 3.8]  ← 电压缓慢跌破下界
  [6.5, 7.7, 7.8, 7.7, 7.8, 7.7, 7.8, 7.9]  ← 在灰色边界7.7/7.8V反复抖动
```

GAN 调用方式（复用现有接口）：
```python
POST /api/gan/generate
{
  "condition": {
    "anomaly_flag": 1,        # 1=希望生成含越界的序列，0=正常唤醒序列
    "vehicle_status_norm": 0.9  # 整车状态归一化值
  },
  "n_samples": 20
}
# 返回 20 条 8 步电压序列，每条拆分为 8 个单独测试用例发给仿真器
```

**GAN 测试用例执行方式**：将序列中每个时间步的 CC2 值作为一条独立的 `signal_name=CC2电压` 请求发给仿真器，记录序列中状态是否在预期位置发生转变。

---

##### 信号 2：CC电压值 — EP + BVA（仅失效区间）

**数据特征**：
- 真实测试（strategy=1）：以 0.1V 步长在 [0.1, 3.9]V 区间**均匀线性扫描**，共 38~39 个不同值，全部 FAIL
- 正常唤醒测试（strategy=0）中不独立测试此信号（背景值约 12.0V 不干扰 CC2 唤醒）

**物理含义**：CC（Control Connection）触点电压反映充电枪连接线阻状态。0.1~3.9V 代表线阻过低（接触不良/短路）。正常无枪或休眠态时 CC 电压约 12V。

**为什么只用 EP + BVA，不用 GAN**：
- 失效区间 [0.1, 3.9]V 是**简单连续范围**，线性均匀扫描已覆盖完整，GAN 无法提供额外信息
- 此信号没有"动态序列"的物理含义——每次测试注入一个固定的 CC 线阻值，不存在时序变化
- 关注点在**边界精确性**（0.1V / 3.9V / 4.0V 三个边界点），BVA 完整覆盖

**生成逻辑**（工具内部）：
```python
class CCVoltageGenerator:
    FAIL_MIN, FAIL_MAX = 0.1, 3.9
    DELTA = 0.1

    def generate_ep(self):
        return [
            TestCase(signal="CC电压值", value=12.0,  expected=PASS),  # 有效类
            TestCase(signal="CC电压值", value=2.0,   expected=FAIL),  # 失效类中值
        ]

    def generate_bva(self):
        return [
            TestCase(signal="CC电压值", value=0.0,              expected=PASS),  # just_below_fail
            TestCase(signal="CC电压值", value=self.FAIL_MIN,    expected=FAIL),  # exact_fail_min
            TestCase(signal="CC电压值", value=self.FAIL_MIN+0.1,expected=FAIL),
            TestCase(signal="CC电压值", value=self.FAIL_MAX,    expected=FAIL),  # exact_fail_max
            TestCase(signal="CC电压值", value=self.FAIL_MAX+0.1,expected=PASS),  # just_above_fail
        ]
```

---

##### 信号 3：CP幅值 — EP + BVA（仅失效区间）

**数据特征**：
- 真实测试：以 0.1V 步长在 [9.1, 12.9]V 区间线性扫描，全部 FAIL
- 正常背景值：0.0V（无 CP 信号，VCU 待机状态）

**物理含义**：CP（Control Pilot）是 IEC 61851 AC 充电协议的导引信号，正常幅值 12V（无充电）或 9V（充电中、用 PWM 占空比指示电流上限）。9.1~12.9V 范围内该信号出现表示协议错误或异常干扰，VCU 拒绝唤醒。

**为什么只用 EP + BVA**：
- 原理与 CC电压值 相同：简单连续失效区间，无时序意义
- 失效边界 9.1V 和 12.9V 是精确的 BVA 重点

---

##### 信号 4：供电电压 — EP + BVA（仅失效区间，仅 db.db 存在）

**数据特征**：
- 真实测试（仅在 db.db 中出现）：以 0.1V 步长在 [9.1, 15.9]V 区间线性扫描，全部 FAIL
- db_2.db 中供电电压恒为 0.0V，未作为独立测试信号

**物理含义**：外部交流供电电压。正常情况（CC2 唤醒时）供电电压应为 0V（无外部供电接入）。9.1~15.9V 表示异常的外部电源接入，可能来自供电设备故障或测试环境异常，VCU 应拒绝唤醒以保护安全。

**为什么只用 EP + BVA**：原理同上，失效区间为连续线性范围，边界 9.1V 和 15.9V 是 BVA 重点。

---

##### 信号 5：网络唤醒报文使能状态 — 仅 EP（穷举，2 个值）

**数据特征**：
- 取值只有 0 和 1 两种（二值信号）
- 真实测试：值=1 时全部 FAIL（176/177 条，1 条数据噪声）

**物理含义**：该信号控制是否允许通过 CAN 网络报文触发 VCU 远程唤醒。值=1（使能）与 CC2 充电唤醒协议同时存在时产生冲突，VCU 无法正确判断唤醒源，导致 FAIL。

**为什么只用 EP**：
- 只有 2 个可能值，EP 穷举即为完整覆盖
- BVA 对二值信号无意义（没有连续边界）
- GAN 对二值信号无意义

---

##### 各信号生成策略汇总

| 信号 | EP | BVA | GAN | 原因 |
|-----|:--:|:---:|:---:|-----|
| CC2电压 | ✅ | ✅ | ✅ | 唯一有连续 PASS/FAIL 两侧区间 + 时序意义的信号 |
| CC电压值 | ✅ | ✅ | ❌ | 纯失效区间，线性连续，无时序意义 |
| CP幅值 | ✅ | ✅ | ❌ | 同上 |
| 供电电压 | ✅ | ✅ | ❌ | 同上 |
| 网络唤醒报文使能状态 | ✅ | ❌ | ❌ | 二值信号，EP穷举即完整覆盖 |

**GAN 的明确角色定位**：
> GAN 不是"为所有信号生成测试值"的通用工具，而是专门为 **CC2 电压的动态时序场景**服务的 AI 组件。它弥补了 EP/BVA 单值测试无法覆盖的**连续变化过程中的边界穿越行为**，这是真实 HIL 台架测试中最难用规则枚举的测试场景。

---

#### 3.5 执行流程

每条测试用例（无论由 EP / BVA / 决策表 / GAN 生成）都以相同格式发给仿真器执行：

```python
# ---- EP 用例执行示例（CC电压值 = 2.0V）----
POST http://localhost:8001/simulate
{
  "signal_name": "CC电压值",
  "value": 2.0,
  "data_type": "float"
}
# 返回
{
  "test_status": 4,
  "vehicle_state": 30,
  "vehicle_mode": 2,
  "ready_flag": 0,
  "detail": "CC电压值=2.0V ∈ [0.1,3.9]V → 接触不良 FAIL"
}
# Test Oracle 判断
expected = {"test_status": 4, "vehicle_state": 30, "ready_flag": 0}
actual   = {"test_status": 4, "vehicle_state": 30, "ready_flag": 0}
result   = PASS ✅   # 仿真器行为与预期一致


# ---- BVA 用例执行示例（CC2电压 = 7.80V 灰色边界）----
POST http://localhost:8001/simulate
{
  "signal_name": "CC2电压",
  "value": 7.80,
  "data_type": "float"
}
# 返回
{
  "test_status": 4,
  "vehicle_state": 30,
  "vehicle_mode": 2,
  "ready_flag": 0,
  "detail": "CC2电压=7.8V 在灰色边界7.8V → FAIL"
}
# Test Oracle 判断
expected = {"test_status": 4, "vehicle_state": 30, "ready_flag": 0}
result   = PASS ✅


# ---- GAN 序列执行示例（8步序列，逐步发送）----
gan_sequence = [5.2, 6.1, 7.3, 7.6, 7.7, 7.8, 8.1, 9.2]  # GAN 生成

results = []
for step, v in enumerate(gan_sequence):
    resp = POST /simulate {"signal_name": "CC2电压", "value": v}
    results.append({"step": step, "value": v, "state": resp["vehicle_state"]})

# 分析：第5步(7.7V) → state=170 PASS，第6步(7.8V) → state=30 FAIL
# 检验：状态转变是否发生在预期的边界位置
boundary_crossing_at_step = next(i for i,r in enumerate(results) if r["state"]==30)
assert boundary_crossing_at_step >= 4, "状态转变位置早于预期（仿真器边界逻辑有误）"


# ---- 休眠测试执行（固定5信号）----
POST http://localhost:8001/simulate/sleep
{
  "cc2_voltage": 12.0,
  "cc_voltage": 12.0,
  "cp_amplitude": 0.0,
  "supply_voltage": 0.0,
  "network_wake_enable": 0.0
}
# 返回
{
  "test_status": 3,
  "vehicle_state": 30,
  "vehicle_mode": 2,
  "ready_flag": 0,
  "detail": "CC2=12.0V 固定休眠命令 → SLEEP"
}
result = PASS ✅
```

#### API 端点
```
POST /api/test-design/generate/ep               生成 EP 用例
POST /api/test-design/generate/bva              生成 BVA 用例（支持自定义 delta）
POST /api/test-design/generate/decision-table   生成决策表用例
POST /api/test-design/generate/gan              调用 GAN 生成补充序列
POST /api/test-design/generate/all              全部技术
GET  /api/test-design/test-cases                获取所有用例
PUT  /api/test-design/test-cases/{id}           修改用例（Interactive Review）
DELETE /api/test-design/test-cases/{id}         删除用例
POST /api/test-design/test-cases                手动新增用例
POST /api/test-design/execute/{id}              执行单条用例（调用仿真器）
POST /api/test-design/execute-all               批量执行所有用例
GET  /api/test-design/results                   获取执行结果汇总
```

#### 前端：`TestCaseDesign.tsx`
- 顶部：选择需求（多选）+ 选择技术（EP / BVA / Decision Table / GAN / All）+ BVA delta 参数
- 中部：测试用例表格（ID / 技术 / 输入参数 / 预期结果 / 执行状态 / 实际结果）
  - 每行可内联编辑（Interactive Review）
  - 可手动增删行
- 底部：执行区域
  - "执行所有用例"按钮 → 逐条调用仿真器 API → 实时更新状态（PASS/FAIL/ERROR）
  - 执行进度条

---

### FR 4.0 — White-Box Test Modeling（白盒测试建模）⭐ 加分项

**要求**：建模系统行为（状态转换图），生成最优测试序列

#### VCU 状态机定义

```json
{
  "states": ["SLEEP", "WAKING", "WAKE", "ERROR"],
  "initial_state": "SLEEP",
  "transitions": [
    {"id": "T1", "from": "SLEEP",  "to": "WAKING", "trigger": "cc2_in_range",    "condition": "4.8 ≤ V ≤ 7.8"},
    {"id": "T2", "from": "WAKING", "to": "WAKE",   "trigger": "status_high",     "condition": "vehicle_status > 170"},
    {"id": "T3", "from": "WAKE",   "to": "SLEEP",  "trigger": "sleep_voltage",   "condition": "V == 12.0"},
    {"id": "T4", "from": "WAKING", "to": "ERROR",  "trigger": "voltage_invalid", "condition": "V < 4.8 or V > 7.8"},
    {"id": "T5", "from": "WAKE",   "to": "ERROR",  "trigger": "status_mismatch", "condition": "status_mismatch detected"},
    {"id": "T6", "from": "ERROR",  "to": "SLEEP",  "trigger": "reset",           "condition": "reset signal"}
  ]
}
```

**覆盖目标**：
- **All States**：4 条测试序列覆盖 SLEEP / WAKING / WAKE / ERROR
- **All Transitions**：6 条序列覆盖 T1~T6 每条转换至少一次

生成的测试序列可直接在 FR 3.0 执行引擎中串行调用仿真器 `/simulate` 接口。

---

### FR 5.0 — Test Oracle Generation（测试预言）⭐ 加分项

**要求**：为给定需求和测试数据综合 Expected Result

在本系统中，FR 5.0 的 Test Oracle 有两层含义：

**层 1 — 静态 Oracle（测试用例设计时）**：
根据 FR 1.1 解析的数据范围，自动推导预期结果填入测试用例（FR 3.0 用例生成时已完成）

**层 2 — 动态 Oracle（测试执行时）**：
将仿真器 API 返回的实际结果与测试用例中的预期结果对比，判断 PASS / FAIL

```python
class TestOracle:
    def verify(self, test_case: TestCase, simulator_response: dict) -> OracleResult:
        checks = []
        # 检查状态
        if test_case.expected_state:
            checks.append(simulator_response["state"] == test_case.expected_state)
        # 检查 READY 标志位
        if test_case.expected_ready_flag is not None:
            checks.append(simulator_response["ready_flag"] == test_case.expected_ready_flag)
        # 检查异常类型
        if test_case.expected_anomaly:
            checks.append(simulator_response["anomaly_type"] == test_case.expected_anomaly)
        # 检查响应时间（NFR）
        if test_case.max_response_ms:
            checks.append(simulator_response["response_time_ms"] <= test_case.max_response_ms)
        
        passed = all(checks)
        return OracleResult(
            verdict="PASS" if passed else "FAIL",
            expected=test_case.to_expected_dict(),
            actual=simulator_response,
            mismatch_fields=[...] if not passed else []
        )
```

---

### FR 6.0 — Output & Export（输出与导出）✅ 必须实现

**要求**：生成 Test Cases、Test Suites、Risk Scores，支持 JSON 或 Excel/CSV

#### 导出 JSON 结构

```json
{
  "tool": "AutoTestDesign v1.0",
  "target_application": "VCU Wake-Sleep Behavior Simulator",
  "simulator_endpoint": "http://localhost:8001/simulate",
  "generated_at": "2026-05-13T10:00:00",
  "summary": {
    "total_requirements": 6,
    "high_priority": 5,
    "medium_priority": 1,
    "total_test_cases": 28,
    "executed": 28,
    "passed": 25,
    "failed": 3
  },
  "requirements": [...],
  "risk_report": [
    {"id": "REQ-001", "risk_score": 7.35, "priority": "High"}
  ],
  "test_suites": [
    {
      "suite_id": "TS-BVA-001",
      "technique": "Boundary Value Analysis",
      "requirement_ref": "REQ-001",
      "test_cases": [
        {
          "id": "BVA-001-2",
          "input": {"cc2_voltage": 4.80, "vehicle_status": 180},
          "expected": {"state": "WAKING", "ready_flag": 0, "anomaly_type": "normal"},
          "actual": {"state": "WAKING", "ready_flag": 0, "anomaly_type": "normal"},
          "verdict": "PASS",
          "response_time_ms": 3.2
        }
      ]
    }
  ],
  "traceability_matrix": {
    "REQ-001": ["EP-001-V1", "EP-001-I1", "EP-001-I2", "BVA-001-1", ..., "BVA-001-7"],
    "REQ-002": ["DT-R1", "DT-R3"],
    ...
  }
}
```

#### 导出 Excel（多 Sheet）

| Sheet | 内容 |
|-------|------|
| Requirements | 需求列表（6列：ID/Title/Description/Category/Risk Score/Priority） |
| Risk Analysis | 风险详情（各维度分 + 总分 + Priority + Rationale） |
| Test Cases - EP | EP 用例（含执行结果） |
| Test Cases - BVA | BVA 用例（含执行结果） |
| Test Cases - DT | 决策表用例（含执行结果） |
| Test Cases - GAN | GAN 生成用例（含执行结果） |
| Traceability Matrix | 需求×用例矩阵（√ 表示覆盖） |
| Execution Summary | 汇总统计（Pass/Fail 数量、覆盖率） |

#### API 端点
```
GET /api/export/json    下载 JSON（application/json）
GET /api/export/csv     下载 CSV（text/csv）
GET /api/export/excel   下载 Excel（.xlsx）
```

---

### FR 7.0 — Test Suite Optimization（测试套件优化）⭐ 加分项

**要求**：基于风险或覆盖效率对测试套件进行优先化或最小化

实现两种策略：

**策略 1：Risk-Based Prioritization（风险优先排序）**
按关联需求的 Risk Score 降序排列所有测试用例，确保高风险用例优先执行。

**策略 2：Coverage-Based Minimization（最小化）**
贪心算法：保证覆盖率不降低的前提下，去除与其他用例覆盖项完全重叠的冗余用例。

```
POST /api/optimize/prioritize    返回按风险排序的用例列表
POST /api/optimize/minimize      返回最小化后的用例子集及其覆盖率对比
```

---

### Interactive Review — 贯穿全流程 ✅ 必须实现

Assignment 要求工具必须支持设计者在整个流程中**交互式地审阅、修订和更改**设计项。

| 阶段 | 可修改内容 | 实现方式 |
|-----|---------|---------|
| 需求输入 | 任意需求字段 | 内联编辑表格 |
| 需求解析 | Input Fields / Ranges / Conditions / Actions | 四栏可编辑卡片 |
| 风险分析 | 各维度分值、最终优先级 | 滑块+下拉弹窗 |
| 测试用例设计 | 输入参数、预期结果 | 内联编辑，可增删行 |
| BVA 参数 | delta 值、边界点数量 | 参数面板，修改后重新生成 |
| 执行配置 | 仿真器地址、超时时间 | 配置页面 |
| 导出范围 | 选择导出哪些需求/用例 | 勾选框 |

**"Mainly" 完整流程对应**：

```
1. Concept              → 首页定义目标（VCU Wake-Sleep Simulator）
2. Coverage Item ID     → FR 1.1 解析出 Input Fields 和 Conditions → 用户可增删
3. Coverage Strategy    → FR 2.0 风险分析确定优先技术 → 用户可调整
4. Test Cases           → FR 3.0 生成用例 → 用户可编辑 → 与需求自动关联
5. Prompt Design        → 展示 BVA delta / EP 分区策略等参数 → 用户可调整后重生成
6. Results Analysis     → FR 5.0 执行后显示 PASS/FAIL + 覆盖度报告
7. Improvement          → 发现未覆盖项 → 系统建议新用例 → 用户确认添加
```

---

## 四、代码修改清单

### 4.1 新增：VCU 仿真器（全新目录）

```
vcu_simulator/                 ★ 全新（目标应用）
├── main.py                    FastAPI 服务入口（端口 8001）
├── state_machine.py           VCU 状态机逻辑（引用 configs/ 常量）
├── models.py                  请求/响应 Pydantic 模型
└── requirements.txt           fastapi, uvicorn, pydantic
```

### 4.2 后端新增/修改

```
backend/
├── api/
│   ├── routers/
│   │   ├── requirements.py        ★ 新增（FR 1.0/1.1）
│   │   ├── risk_analysis.py       ★ 新增（FR 2.0）
│   │   ├── test_design.py         ★ 新增（FR 3.0，含执行调用）
│   │   ├── export.py              ★ 新增（FR 6.0）
│   │   ├── state_machine.py       ★ 新增（FR 4.0，加分）
│   │   └── optimizer.py           ★ 新增（FR 7.0，加分）
│   ├── services/
│   │   ├── requirement_service.py ★ 新增（需求 CRUD）
│   │   ├── requirement_parser.py  ★ 新增（FR 1.1 解析逻辑）
│   │   ├── risk_service.py        ★ 新增（FR 2.0 评分算法）
│   │   ├── test_design_service.py ★ 新增（EP/BVA/决策表生成）
│   │   ├── simulator_client.py    ★ 新增（调用仿真器 API 的 HTTP 客户端）
│   │   ├── oracle_service.py      ★ 新增（FR 5.0 判定逻辑）
│   │   ├── export_service.py      ★ 新增（FR 6.0 JSON/CSV/Excel）
│   │   ├── state_machine_service.py ★ 新增（FR 4.0，加分）
│   │   └── optimizer_service.py   ★ 新增（FR 7.0，加分）
│   ├── models/
│   │   └── schemas.py             ✏ 扩展（新增 FR 相关模型）
│   └── main.py                    ✏ 注册新路由
├── data/
│   ├── requirements/              ★ 新建（运行时生成）
│   ├── risk_analysis/             ★ 新建（运行时生成）
│   └── test_cases/                ★ 新建（运行时生成）
└── requirements.txt               ✏ 增加 openpyxl, python-multipart
```

新增的关键 `simulator_client.py`：
```python
import httpx
from typing import Optional

class SimulatorClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def simulate(self, cc2_voltage: float, vehicle_status: int,
                       current_state: str = "SLEEP",
                       duration_ms: int = 100) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/simulate",
                json={"cc2_voltage": cc2_voltage,
                      "vehicle_status": vehicle_status,
                      "current_state": current_state,
                      "duration_ms": duration_ms}
            )
            resp.raise_for_status()
            return resp.json()

    async def simulate_batch(self, test_cases: list) -> list:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/simulate/batch",
                json=test_cases
            )
            return resp.json()
```

### 4.3 前端新增/修改

```
frontend/src/
├── components/
│   ├── RequirementInput.tsx   ★ 新增（FR 1.0/1.1）
│   ├── RiskAnalysis.tsx       ★ 新增（FR 2.0）
│   ├── TestCaseDesign.tsx     ★ 新增（FR 3.0 + 执行）
│   ├── StateMachineEditor.tsx ★ 新增（FR 4.0，加分）
│   ├── ExportCenter.tsx       ★ 新增（FR 6.0）
│   └── Sidebar.tsx            ✏ 新增导航项
├── services/
│   └── api.ts                 ✏ 新增 requirementAPI、riskAPI、testDesignAPI 等
└── App.tsx                    ✏ 新增视图 case
```

Sidebar 新导航结构：
```
需求管理（RequirementInput）   ← 新增
风险分析（RiskAnalysis）       ← 新增
测试设计（TestCaseDesign）     ← 新增（含执行功能）
测试监控（TestMonitoring）     ← 保留
结果分析（ResultAnalysis）     ← 保留
导出中心（ExportCenter）       ← 新增
报告中心（ReportCenter）       ← 保留
系统设置（SystemSettings）     ← 保留
```

---

## 五、项目结构（最终）

```
softwaretest-vcu-fuzzy-test-system/
├── vcu_simulator/          目标应用（VCU 行为仿真器，端口 8001）
│   ├── main.py
│   ├── state_machine.py
│   ├── models.py
│   └── requirements.txt
├── backend/                AutoTestDesign Tool 后端（端口 8000）
│   ├── api/
│   ├── configs/
│   ├── nn/（GAN 模型）
│   ├── data/
│   ├── run_server.py
│   └── requirements.txt
├── frontend/               AutoTestDesign Tool 前端（端口 3000）
│   └── src/
├── tests/                  pytest 测试脚本
│   ├── test_vcu_simulator.py    ← 对仿真器的自动化测试（Artifact 4）
│   ├── test_api_routes.py
│   └── test_e2e.py
├── docs/
│   └── DESIGN_PLAN.md
├── setup.sh
└── README.md
```

---

## 六、四大交付物设计

### Artifact 1 — AutoTestDesign Tool（20%）

**交付物**：源代码 + README + 视频演示（5~8 分钟）

**视频脚本**：
1. 展示系统架构（工具 + 仿真器两个服务均已启动）（30s）
2. 导入 VCU 需求 CSV，查看解析结果（FR 1.0/1.1）（1min）
3. 手动修改 REQ-001 的一个 Data Range（Interactive Review）（30s）
4. 执行风险分析，调整 REQ-006 的优先级（FR 2.0 + Interactive Review）（1min）
5. 生成 BVA + 决策表测试用例，编辑一条用例（FR 3.0 + Interactive Review）（1.5min）
6. 点击"执行所有用例" → 实时显示 PASS/FAIL（FR 5.0）（1min）
7. 导出 Excel，打开展示追踪矩阵（FR 6.0）（30s）
8. 可选：展示状态机图 / 优化功能（FR 4.0/7.0）（1min）

### Artifact 2 — Risk Analysis Report（10%）

**针对 VCU 仿真器（目标应用）的风险分析报告**，结构：
1. 目标应用概述（VCU 仿真器的功能、接口、背景）
2. 测试范围与边界（6 条需求的测试边界）
3. 风险评估方法（5 维度算法详述）
4. 风险分析结果（表格 + 风险矩阵热力图）
5. 测试优先级建议（基于 Risk Score 排序的测试执行顺序）

### Artifact 3 — Test Plan（40%）

7 个必须覆盖的章节：

| 章节 | 内容要点 |
|-----|---------|
| **Project Scope** | 用 AutoTestDesign 工具对 VCU 行为仿真器进行系统性软件测试 |
| **Test Items** | 仿真器的 4 个核心功能（电压处理/状态控制/睡眠转换/异常检测）+ NFR（响应时间 <10ms） |
| **High-level Test Suite Design** | 6 套测试套件（见下表） |
| **Schedule** | 4 周计划（需求分析/用例设计/脚本开发/执行分析） |
| **Organization Chart** | Test Lead + 3 个 Tester 职责划分 |
| **Testing Framework** | pytest（执行）+ httpx（调用仿真器 API）+ AutoTestDesign Tool（用例设计） |
| **Cost Estimation** | 手动 vs 工具辅助对比（预计节省 69%工作量） |

**High-level Test Suite Design**：

| 套件 | 技术 | 需求 | 优先级 |
|-----|------|------|-------|
| TS-01：电压边界测试 | BVA | REQ-001, REQ-005 | High |
| TS-02：状态等价划分 | EP | REQ-001, REQ-002, REQ-003 | High |
| TS-03：多条件状态决策 | Decision Table | REQ-002, REQ-003, REQ-006 | High |
| TS-04：状态机序列测试 | State Transition | REQ-004, REQ-005 | Medium |
| TS-05：智能模糊补充 | GAN-based | REQ-006 | High |
| TS-06：NFR 性能测试 | Boundary Value | REQ-002, REQ-004 | Medium |

### Artifact 4 — Detailed Test Design（30%）

选取 **REQ-001（CC2 电压输入范围）** 作为详细设计模块。

#### Test Case Design（由 AutoTestDesign 工具生成）

完整 10 条用例（3 EP + 7 BVA），见 FR 3.0 节的表格。

#### Test Tool Implementation（pytest 脚本）

覆盖全部 5 个输入信号，使用真实字段结构：

```python
# tests/test_vcu_simulator.py
import pytest
import httpx

SIMULATOR_URL = "http://localhost:8001"

@pytest.fixture(autouse=True)
def reset_simulator():
    httpx.post(f"{SIMULATOR_URL}/reset")

# ===========================================================
# 参数化：(signal_name, value, exp_status, exp_state, exp_ready, tc_id)
# ===========================================================
@pytest.mark.parametrize(
    "signal_name, value, exp_status, exp_state, exp_ready, tc_id",
    [
        # ===== EP：CC2电压（REQ-001/002/003/004）=====
        ("CC2电压",  6.30,  1, 170, 1, "EP-CC2-V1"),   # 有效等价类
        ("CC2电压",  3.00,  4,  30, 0, "EP-CC2-I1"),   # 无效低 → state=30（5DB全部35条确认）
        ("CC2电压",  9.00,  4,  30, 0, "EP-CC2-I2"),   # 无效高 → state=30（37/38条确认）
        ("CC2电压", 12.00,  3,  30, 0, "EP-CC2-S1"),   # 休眠触发

        # ===== EP：CC电压值（REQ-005）=====
        ("CC电压值", 12.00, 1, 170, 1, "EP-CC-V1"),   # 有效（正常接线电压）
        ("CC电压值",  2.00, 4,  30, 0, "EP-CC-I1"),   # 无效（接触不良，[0.1,3.9]V）

        # ===== EP：CP幅值（REQ-006）=====
        ("CP幅值",   0.00,  1, 170, 1, "EP-CP-V1"),   # 有效（待机，无CP信号）
        ("CP幅值",  11.00,  4,  30, 0, "EP-CP-I1"),   # 无效（协议冲突，[9.1,12.9]V）

        # ===== EP：供电电压（REQ-007）=====
        ("供电电压",  0.00, 1, 170, 1, "EP-SV-V1"),   # 有效（无外部供电）
        ("供电电压", 12.50, 4,  30, 0, "EP-SV-I1"),   # 无效（意外过压，[9.1,15.9]V）

        # ===== EP：网络唤醒报文使能状态（REQ-008）=====
        ("网络唤醒报文使能状态", 0.0, 1, 170, 1, "EP-NW-V1"),  # 有效（未使能）
        ("网络唤醒报文使能状态", 1.0, 4,  30, 0, "EP-NW-I1"),  # 无效（冲突使能）

        # ===== BVA：CC2电压 7点边界 =====
        ("CC2电压", 4.70, 4,  30, 0, "BVA-CC2-1"),  # just_below_min
        ("CC2电压", 4.80, 1, 170, 1, "BVA-CC2-2"),  # exact_min（db_2确认）
        ("CC2电压", 4.90, 1, 170, 1, "BVA-CC2-3"),  # just_above_min
        ("CC2电压", 6.30, 1, 170, 1, "BVA-CC2-4"),  # nominal
        ("CC2电压", 7.70, 1, 170, 1, "BVA-CC2-5"),  # just_below_max
        ("CC2电压", 7.80, 4,  30, 0, "BVA-CC2-6"),  # exact_boundary（灰色FAIL）
        ("CC2电压", 7.90, 4,  30, 0, "BVA-CC2-7"),  # just_above_max

        # ===== BVA：CC电压值（失效区间[0.1,3.9]V）=====
        ("CC电压值", 0.00, 1, 170, 1, "BVA-CC-1"),  # just_below_fail
        ("CC电压值", 0.10, 4,  30, 0, "BVA-CC-2"),  # exact_fail_min
        ("CC电压值", 2.00, 4,  30, 0, "BVA-CC-3"),  # mid_fail
        ("CC电压值", 3.90, 4,  30, 0, "BVA-CC-4"),  # exact_fail_max
        ("CC电压值", 4.00, 1, 170, 1, "BVA-CC-5"),  # just_above_fail

        # ===== BVA：CP幅值（失效区间[9.1,12.9]V）=====
        ("CP幅值",  0.00, 1, 170, 1, "BVA-CP-1"),  # normal_idle
        ("CP幅值",  9.00, 1, 170, 1, "BVA-CP-2"),  # just_below_fail
        ("CP幅值",  9.10, 4,  30, 0, "BVA-CP-3"),  # exact_fail_min
        ("CP幅值", 11.00, 4,  30, 0, "BVA-CP-4"),  # mid_fail
        ("CP幅值", 12.90, 4,  30, 0, "BVA-CP-5"),  # exact_fail_max
        ("CP幅值", 13.00, 1, 170, 1, "BVA-CP-6"),  # just_above_fail

        # ===== BVA：供电电压（失效区间[9.1,15.9]V）=====
        ("供电电压",  0.00, 1, 170, 1, "BVA-SV-1"),
        ("供电电压",  9.00, 1, 170, 1, "BVA-SV-2"),
        ("供电电压",  9.10, 4,  30, 0, "BVA-SV-3"),
        ("供电电压", 12.50, 4,  30, 0, "BVA-SV-4"),
        ("供电电压", 15.90, 4,  30, 0, "BVA-SV-5"),
        ("供电电压", 16.00, 1, 170, 1, "BVA-SV-6"),
    ]
)
def test_vcu_single_signal(signal_name, value, exp_status, exp_state, exp_ready, tc_id):
    resp = httpx.post(f"{SIMULATOR_URL}/simulate",
                      json={"signal_name": signal_name, "value": value,
                            "data_type": "float"},
                      timeout=10.0)
    assert resp.status_code == 200, f"[{tc_id}] HTTP {resp.status_code}"
    data = resp.json()

    assert data["test_status"] == exp_status, (
        f"[{tc_id}] {signal_name}={value}: "
        f"expected test_status={exp_status}, got {data['test_status']} | {data.get('detail')}"
    )
    assert data["vehicle_state"] == exp_state, (
        f"[{tc_id}] {signal_name}={value}: "
        f"expected vehicle_state={exp_state}, got {data['vehicle_state']}"
    )
    assert data["ready_flag"] == exp_ready, (
        f"[{tc_id}] {signal_name}={value}: "
        f"expected ready_flag={exp_ready}, got {data['ready_flag']}"
    )
    # REQ-009: ready_flag 与 vehicle_state 必须一致
    assert (data["vehicle_state"] == 170) == (data["ready_flag"] == 1), \
        f"[{tc_id}] READY flag / vehicle_state inconsistency: {data}"


def test_sleep_command():
    """休眠测试（type=2，固定5信号，REQ-004）"""
    resp = httpx.post(f"{SIMULATOR_URL}/simulate/sleep",
                      json={"cc2_voltage": 12.0, "cc_voltage": 12.0,
                            "cp_amplitude": 0.0, "supply_voltage": 0.0,
                            "network_wake_enable": 0.0},
                      timeout=10.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["test_status"] == 3,     f"Expected SLEEP status=3, got {data['test_status']}"
    assert data["vehicle_state"] == 30,  f"Expected state=30, got {data['vehicle_state']}"
    assert data["vehicle_mode"] == 2,    f"Expected mode=2, got {data['vehicle_mode']}"
    assert data["ready_flag"] == 0,      f"Expected ready=0, got {data['ready_flag']}"
```

#### Test Result Analysis

执行 `pytest tests/test_vcu_simulator.py -v` 后填写：
- 通过率：X/10
- 发现缺陷：（如边界值精度问题、状态转换时序问题）
- 追踪矩阵：10 条用例 → 覆盖 REQ-001 的全部 Data Ranges 和 Conditions
- 改进：依据 FAIL 用例添加新的覆盖项（体现"improvement with evidence"）

---

## 七、与评分点的对应

| 评分维度 | 占比 | 我们如何拿分 |
|---------|-----|-----------|
| **Understanding of Concepts** | 10% | 正确引用 ISO 29119-4（EP/BVA/Decision Table）；风险分析引用 ISTQB Risk-Based Testing；需求结构化体现 Coverage Item Identification；Test Oracle 体现预言问题认知 |
| **Coherence of Design & Implementation** | 20% | 端到端流程连贯（需求→解析→风险→用例→执行→导出）；工具与目标应用职责清晰分离；每个 FR 都有对应的前端页面 + 后端 API；追踪矩阵贯穿始终 |
| **Coverage & Effectiveness** | 40% | FR 1.0/1.1/2.0/3.0/6.0 全部实现；FR 4.0/5.0/7.0 加分实现；测试用例实际在仿真器上执行并有 PASS/FAIL 结果；GAN 提供 AI 补充测试 |
| **In-depth Analysis** | 20% | 工具可推广性（VCU 只是示例，任何有数值边界的系统都适用）；三种技术适用场景对比；第一轮执行后增加新用例的改进证据；手动 vs 工具的定量对比 |
| **Presentation** | 10% | 15 分钟脚本：工具 Demo（5min）+ 仿真器测试结果（5min）+ Q&A（5min） |

---

## 八、实施顺序建议

### 阶段 1：目标应用（先建，后续所有演示都依赖它）

1. `vcu_simulator/state_machine.py` — VCU 状态机逻辑（~60行）
2. `vcu_simulator/models.py` — 请求/响应模型（~30行）
3. `vcu_simulator/main.py` — FastAPI 服务（~40行）
4. 验证：`curl -X POST localhost:8001/simulate -d '{"cc2_voltage":6.3,"vehicle_status":180}'`

### 阶段 2：后端核心 FR

5. `schemas.py` 扩展 — 新增 Requirement / ParsedRequirement / RiskResult / TestCase 模型
6. `requirement_parser.py` — 正则解析逻辑
7. `requirement_service.py` + `routers/requirements.py`
8. `risk_service.py` + `routers/risk_analysis.py`
9. `test_design_service.py` + `simulator_client.py` + `oracle_service.py` + `routers/test_design.py`
10. `export_service.py` + `routers/export.py`
11. `main.py` 注册新路由

### 阶段 3：前端新增页面

12. `RequirementInput.tsx` — 导入 + 解析展示 + 内联编辑
13. `RiskAnalysis.tsx` — 矩阵图 + 分值调整
14. `TestCaseDesign.tsx` — 用例表格 + 执行进度
15. `ExportCenter.tsx` — 格式选择 + 下载
16. 修改 `Sidebar.tsx` + `App.tsx` + `api.ts`

### 阶段 4：加分项（时间允许）

17. FR 4.0 状态机（react-flow 可视化）
18. FR 7.0 优化（风险排序 + 最小化）

### 阶段 5：文档与演示

19. Artifact 2（Risk Analysis Report，~5h）
20. Artifact 3（Test Plan，~8h）
21. Artifact 4（Detailed Test Design，~4h）
22. 录制视频演示（~2h）
