# VCU 模糊测试系统 — 完整项目计划 V2

> 基于北汽原始需求文档（0319/0324/0331）+ 研究生学长 bq_new 代码 + Assignment 2 要求  
> 更新日期：2026-05-21

---

## 一、项目定位与整体架构

### 1.1 两个系统，职责明确

```
┌─────────────────────────────────────────────────────────────┐
│                  AutoTestDesign Tool（我们的工具）             │
│                                                             │
│  需求导入 → 风险分析 → 用例生成 → 执行 → Oracle判断 → 导出    │
│  FR1.0    FR2.0    FR3.0/4.0  FR5.0   FR5.0       FR6.0    │
│                                                             │
│  变异策略（FR7.0）：基于 bq_new DataVariation 实现           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP POST /simulate
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              VCU 行为仿真器（被测目标应用）                    │
│                                                             │
│  状态机：state09（休眠）→ state10（初始化）→ state11（运行）  │
│  7路唤醒触发（w1-w7）+ 3路休眠条件（h1-h3）                  │
│  已知缺陷：快速上下电序列触发 state10 卡死                    │
│                                                             │
│  输出：vehicle_state / vehicle_mode / power_current /       │
│        bus_message_flag / pdcu_wake_reason / actual_duration│
└─────────────────────────────────────────────────────────────┘
```

### 1.2 为什么这样设计

1. **真实 bug 来源**：北汽原始需求文档（0319）明确记录了 state10 卡死缺陷，这是真实工程问题，不是为了作业人为构造的
2. **7路唤醒 + 3路休眠**：直接来自北汽需求文档，每路信号有独立的电压阈值和时序要求，天然适合 EP/BVA
3. **决策表的天然场景**：休眠需要 h1 AND h2 AND h3 同时满足，3个二值条件 = 8种组合，教科书级决策表
4. **输出有 5 个字段**：测试 Oracle 不再是单一 PASS/FAIL，而是 5 个字段同时校验，深度远超旧方案
5. **result_type 三分类**：expected / error / stuck，来自学长代码的 assert 结构，支撑白盒三条路径覆盖

---

## 二、VCU 行为仿真器设计

### 2.1 状态机

```
                    ┌─────────────────┐
                    │  state09 (休眠)  │◄──────────────────┐
                    └────────┬────────┘                   │
                             │ 任意唤醒触发满足（w1-w7之一）  │
                             ↓                            │
                    ┌─────────────────┐          h1 AND h2 AND h3
                    │ state10 (初始化)│                   │
                    └────────┬────────┘                   │
                             │ 初始化完成                  │
              ⚠ 已知缺陷：     ↓                            │
              快速连续上下电   ┌─────────────────┐           │
              导致卡死在此  → │ state11 (正常运行)│──────────┘
                             └─────────────────┘

卡死触发条件：连续3次以上唤醒-休眠循环，相邻间隔 < 1s
卡死表现：state 停留在 10，actual_duration > est_time × 2
```

### 2.2 输入信号定义（来自北汽原始文档）

#### 唤醒触发条件（Type 1，单信号，任一满足即唤醒）

| 编号 | 信号名 | 触发条件 | 是否有时序要求 |
|------|--------|---------|--------------|
| w1 | 供电电压 | voltage > 9.0V 且 duration ≥ 10ms | **是** |
| w2 | CAN 网络报文 | can_msg ∈ [0x400, 0x47F] | 否 |
| w3 | CP 信号 | cp_voltage > 9.0V | 否 |
| w4 | CC 信号 | cc_voltage < 4.4V | 否 |
| w5 | CC2 信号 | cc2_voltage < ubr_threshold | 否 |
| w6 | 口盖信号 | hood_voltage > 4.0V 且 duration ≥ 10ms | **是** |
| w7 | 门板信号 | door_voltage < 1.0V 且 duration ≥ 10ms | **是** |

#### 时序判断逻辑说明

w1/w6/w7 有持续时间要求，仿真器对这三路信号采用**双条件判断**，客户端在请求体中通过 `duration`（单位 ms）字段传入持续时间：

| 值条件 | 时序条件 | 判断结果 | result_type |
|--------|---------|---------|------------|
| 满足 | duration ≥ 阈值 | 唤醒成功 | expected |
| 满足 | duration < 阈值 | 时序不足，唤醒失败 | error（时序无效类） |
| 不满足 | 任意 | 值不足，唤醒失败 | error（值无效类） |

w2/w3/w4/w5 没有时序要求，仿真器只检查信号值，`duration` 字段传了也忽略。

这个双条件设计的测试价值：BVA 可以同时在**电压轴**和**时序轴**做边界值分析，产生两个独立的边界点集合（见 Suite B）。

#### 休眠触发条件（Type 2，多信号，必须同时满足）

| 编号 | 信号名 | 触发条件 |
|------|--------|---------|
| h1 | VCUIdle_flg | VCUO_bDIAG_VCUIdle_flg = 1 |
| h2 | AuthComplete_flg | VCUO_bDIAG_AuthComplete_flg = 1 |
| h3 | CAN 停发 | CAN 0x400~0x47F 停止发送 |

### 2.3 输出信号定义（来自 bq_new result_judge.py）

| 字段名 | 类型 | 正常运行值 | 休眠值 | 卡死值 |
|--------|------|-----------|--------|--------|
| vehicle_state | int | 11 | 9 | 10 |
| vehicle_mode | int | 2 | 2 | 2 |
| power_current | float | ≤ 0.05A | ≤ 0.01A | > 0.2A |
| bus_message_flag | int | 1 | 0 | 0 |
| pdcu_wake_reason | int | 1-7（对应w1-w7） | 0 | 0 |
| actual_duration | float | ≤ est_time | ≤ est_time | > est_time × 2 |

### 2.4 结果类型定义（来自 bq_new result_judge.py `_compare_results`）

| result_type | strategy 返回值 | 含义 | 判断逻辑 |
|-------------|----------------|------|---------|
| `expected` | 0 | 正常，全部字段匹配预期 | 所有字段满足 expected_results |
| `error` | 1 或 2 | 异常，状态未正确跳转 | 某字段匹配 error\[0\]（error_type=1）的条件 |
| `stuck` | 3（-3）| 卡死，state10 无法跳出 | 字段匹配 error\[1\]（error_type=2）且 actual_duration > est_time×2 |
| `new_state` | 1 或 2 | 发现未知新状态 | 输出不匹配以上三种任何预期，触发变异进入下一轮 |

> **说明**：`strategy` 是 Tool 内部的决策值，决定下一步对该用例做何种变异操作：
> - strategy=0：正常通过，继续下一条
> - strategy=1：触发单参数变异（螺旋滑动窗口取邻近值）
> - strategy=2：触发多参数变异（多信号同时随机偏移）
> - strategy=3：触发重复执行变异（对卡死用例重复 N 次）
> - strategy=-1：平台错误，停止测试

### 2.5 API 接口设计

```
POST /simulate          执行一条测试用例（type1 或 type2）
POST /reset             复位 VCU 状态到 state09
GET  /state             查询当前 VCU 状态
GET  /config            查询所有信号阈值
PUT  /config            修改信号阈值（支持非功能测试）
```

**POST /simulate 请求体**：

```json
{
  "type": 1,
  "in_data": [
    {
      "name": "供电电压",
      "data_type": "float",
      "value": "9.3",
      "duration": 15
    }
  ],
  "est_time": 20
}
```

**POST /simulate 响应体**：

```json
{
  "vehicle_state": 11,
  "vehicle_mode": 2,
  "power_current": 0.042,
  "bus_message_flag": 1,
  "pdcu_wake_reason": 1,
  "actual_duration": 14.7,
  "result_type": "expected",
  "detail": "供电电压=9.3V > 9V，持续15ms ≥ 10ms，硬线唤醒成功，state09→state10→state11"
}
```

**Type 2 休眠测试请求体**：

```json
{
  "type": 2,
  "in_data": [
    {"name": "VCUIdle_flg",       "data_type": "int", "value": "1"},
    {"name": "AuthComplete_flg",  "data_type": "int", "value": "1"},
    {"name": "CAN_stop",          "data_type": "int", "value": "1"}
  ],
  "est_time": 60
}
```

### 2.6 卡死缺陷仿真实现逻辑

```python
class VCUSimulator:
    def __init__(self):
        self.state = 9           # 初始 state09
        self._wake_history = []  # 记录最近唤醒时间戳

    def simulate(self, test_data):
        # 检测快速上下电序列 → 触发 stuck
        now = time.time()
        self._wake_history = [t for t in self._wake_history if now - t < 5.0]
        if len(self._wake_history) >= 3:
            intervals = [self._wake_history[i+1] - self._wake_history[i]
                        for i in range(len(self._wake_history)-1)]
            if all(iv < 1.0 for iv in intervals):
                self.state = 10
                return {
                    "vehicle_state": 10,
                    "actual_duration": test_data["est_time"] * 3,
                    "result_type": "stuck",
                    "detail": "检测到快速连续上下电序列，state10 卡死，无法完成初始化"
                }
        # 正常判断逻辑 ...
```

### 2.7 需求列表（14条）

| REQ-ID | 标题 | 描述 | 风险 |
|--------|------|------|------|
| REQ-001 | 硬线供电唤醒 w1 | 供电电压 > 9V 持续 ≥ 10ms 时，VCU 从 state09 进入 state10→11，pdcu_wake_reason=1 | High |
| REQ-002 | CAN 网络唤醒 w2 | CAN 总线收到 0x400~0x47F 报文时唤醒，pdcu_wake_reason=2 | High |
| REQ-003 | CP 信号唤醒 w3 | CP 幅值 > 9V 上升沿触发唤醒，pdcu_wake_reason=3 | Medium |
| REQ-004 | CC 信号唤醒 w4 | CC 电压下降至 < 4.4V 触发唤醒，pdcu_wake_reason=4 | Medium |
| REQ-005 | CC2 信号唤醒 w5 | CC2 UBR 电压下降沿触发唤醒，pdcu_wake_reason=5 | Medium |
| REQ-006 | 口盖信号唤醒 w6 | 口盖电压 > 4V 持续 ≥ 10ms 触发唤醒，pdcu_wake_reason=6 | Low |
| REQ-007 | 门板信号唤醒 w7 | 门板电压 < 1V 持续 ≥ 10ms 触发唤醒，pdcu_wake_reason=7 | Low |
| REQ-008 | 休眠条件 h1 | VCUIdle_flg=1 是进入休眠的必要条件之一 | High |
| REQ-009 | 休眠条件 h2 | AuthComplete_flg=1 是进入休眠的必要条件之一 | High |
| REQ-010 | 休眠条件 h3 | CAN 0x400~0x47F 停发是进入休眠的必要条件之一 | High |
| REQ-011 | 三条件同时满足才休眠 | h1 AND h2 AND h3 同时满足时 VCU 进入 state09，任一不满足则维持当前状态 | High |
| REQ-012 | 卡死缺陷检测 | 连续3次以上快速唤醒-休眠循环（间隔<1s）导致 state 卡死在 10，actual_duration 超时 | High |
| REQ-013 | 输出字段一致性 | vehicle_state=11 时 bus_message_flag 必须=1；vehicle_state=9 时 bus_message_flag 必须=0 | Medium |
| REQ-014 | 响应时序合规 | type1 测试 actual_duration ≤ 20s；type2 测试 actual_duration ≤ 60s | Medium |

---

## 三、AutoTestDesign Tool 设计

### 3.1 功能需求覆盖

| FR | 功能 | 实现说明 |
|----|------|---------|
| FR 1.0 | Input/Parsing | 从 CSV 导入 REQ-001~014，字段：ID/Title/Input/Condition/Expected |
| FR 1.1 | Requirement Structuring | 解析 Input Fields（信号名/类型/范围）、Conditions（阈值/持续时间）、Expected Actions（5字段预期值） |
| FR 2.0 | Risk Analysis | 按安全影响×缺陷概率打分，High/Medium/Low 三级 |
| FR 3.0 | Black-Box Test Design | EP + BVA + 决策表 + 状态转移 四种技术 |
| FR 4.0 | White-Box Test Modeling | state09/10/11 状态机建模，All-States + All-Transitions 覆盖 ★加分 |
| FR 5.0 | Test Oracle Generation | LLM 合成 5 个输出字段的预期值 ★加分 |
| FR 6.0 | Output & Export | 导出 JSON（bq_new 格式）/ CSV / Excel，含需求-用例追溯矩阵 |
| FR 7.0 | Test Suite Optimization | 基于 bq_new DataVariation 的三种变异策略（单参数/多参数/重复执行）★加分 |

### 3.2 Interactive Review 流程（Assignment "Mainly" 要求）

```
① Concept 导入
   └─ 导入 REQ-001~014，解析 Input Fields / Conditions / Expected Actions

② Coverage Item 识别
   └─ 工具自动识别：等价类边界、时序阈值、状态节点、决策表条件

③ Coverage Strategy 选择
   ├─ w1-w7 单信号 → EP + BVA（电压边界 + 时序边界）
   ├─ h1-h3 多信号 → 决策表（8种组合）
   ├─ state09/10/11 → 状态转移测试（All-Transitions）
   └─ 卡死序列 → 序列测试 + 重复执行变异
   （每步支持人工修改）

④ Test Cases + Traceability
   └─ 生成用例，每条附 REQ-ID，含 expected/error/stuck 三种预期

⑤ Prompt Design / Oracle 合成
   └─ LLM 根据需求描述+输入值合成 5 个输出字段的预期值

⑥ Results Analysis
   └─ 执行后统计 expected/error/stuck 比例，映射 Coverage Item 覆盖率

⑦ Improvement with Evidence
   └─ 对 error/stuck 用例触发 DataVariation，生成邻近值变异用例
```

### 3.3 测试用例 JSON 格式（与 bq_new 兼容）

```json
{
  "type": 1,
  "in_data": [
    {
      "name": "供电电压",
      "data_type": "float",
      "value": "9.3",
      "duration": 15
    }
  ],
  "expected_results": [
    {"name": "整车State状态",      "out_type": 1, "out_range": 2, "value": 11},
    {"name": "总线报文发送标志位",  "out_type": 1, "out_range": 2, "value": 1},
    {"name": "PDCU唤醒原因",       "out_type": 1, "out_range": 2, "value": 1},
    {"name": "整车模式",           "out_type": 1, "out_range": 2, "value": 2},
    {"name": "功耗电流",           "out_type": 1, "out_range": 3, "value": 0.05}
  ],
  "error": [
    {
      "error_type": 1,
      "out_data": [
        {"name": "整车State状态", "out_type": 1, "out_range": 2, "value": 10}
      ]
    },
    {
      "error_type": 2,
      "out_data": [
        {"name": "整车State状态",  "out_type": 1, "out_range": 2, "value": 10},
        {"name": "actual_duration","out_type": 1, "out_range": 1, "value": 40}
      ]
    }
  ],
  "est_time": 20
}
```

> **out_range 取值说明**（来自 bq_new data_init.py 注释）：
> - `out_range=1`：大于等于（≥）
> - `out_range=2`：等于（=）
> - `out_range=3`：小于等于（≤）
> - `out_type=1`：阈值类型（当前仅支持此类型）
```

### 3.4 测试执行轮询机制（来自 bq_new result_judge.py）

Tool 调用 VCU 仿真器的执行流程**不是单次请求-响应**，而是一个轮询循环：

```
POST /reset                          ← 每条用例执行前先复位

POST /send（发送输入信号）             ← 学长代码 send_api()

循环轮询（每隔 read_interval 秒，最多等 est_time 秒）：
    GET /read（读取5个输出信号）        ← 学长代码 read_api()
    _compare_results()
        ├─ 匹配 expected_results？  → 返回 strategy=0，记录 actual_duration，退出循环
        ├─ 匹配 error[0]？         → 返回 strategy=1/2，记录，退出循环
        ├─ 匹配 error[1](stuck)？  → 返回 strategy=3，记录，退出循环
        └─ 都不匹配？              → 继续等待，直到 est_time 超时
                                      超时后视为 new_state，记录，触发变异

actual_duration = 从发送信号到轮询到匹配结果的耗时（毫秒）
```

> **关键设计**：`actual_duration` 不是 API 响应时间，而是 VCU 完成状态转移所需的真实时间。  
> 每10次 strategy=0 的正常结果后，Tool 还会分析最近10次 actual_duration 趋势（`db.analyze_durations()`），若持续升高则触发变异——对应模糊测试文档中"基于时间的反馈"。

### 3.5 两轮模糊测试反馈机制（来自 bq_new process_control.py）

这是模糊测试区别于普通测试的核心，学长代码 `ProcessCtrl.run()` 实现了两轮循环：

```
第一轮（round=1）：
  ① 从 JSON 文件加载初始用例
  ② DataVariation 生成变异数据池（单参数/多参数/MIX 模式）
  ③ 逐条执行，结果存入数据库
  ④ 发现 new_state 或 stuck → 记录到数据库，标记 strategy

第二轮（round=2）：
  ① 从数据库查询第一轮发现的新状态记录（get_new_status_by_round）
  ② 针对这些记录重新生成变异用例（based_new_state_fuzz）
  ③ 再次执行，验证是否能稳定复现或找到更多边界
```

**体现在 Assignment "Improvement with Evidence" 要求**：

| 第一轮发现 | 第二轮动作 | 对应 Assignment 要求 |
|-----------|----------|-------------------|
| new_state（未知状态） | 围绕该输入值做单/多参数变异 | 新增 Coverage Item |
| stuck（卡死） | 重复执行该序列 × N 次确认 | 改进测试用例，提供缺陷证据 |
| actual_duration 趋势上升 | 触发变异，寻找极端输入 | 非功能测试深入分析 |

---

## 四、测试计划（Test Plan，40% 交付物）

### 4.1 Project Scope

使用 AutoTestDesign Tool 对 VCU 行为仿真器的**唤醒（7路）、休眠（3条件组合）、状态转移（state09/10/11）及已知卡死缺陷**进行系统性测试。  
覆盖 14 条需求，重点验证 High 风险项（REQ-001/002/011/012）。  
测试输出结果分四类（expected/error/stuck/new_state），白盒覆盖 All-Transitions，采用两轮模糊测试反馈机制，第二轮基于第一轮新状态发现结果生成变异用例。

### 4.2 Test Items

| 模块 | 需求范围 | 测试目标 |
|------|---------|---------|
| 唤醒功能（7路信号） | REQ-001~007 | 各信号有效/无效/边界值下的 state 跳转和 pdcu_wake_reason |
| 休眠功能（3条件） | REQ-008~011 | h1/h2/h3 各种布尔组合下是否正确进入 state09 |
| 卡死缺陷 | REQ-012 | 快速上下电序列触发 stuck，actual_duration 超时 |
| 输出一致性 | REQ-013 | 5个输出字段互相不矛盾 |
| 响应时序 | REQ-014 | type1 ≤ 20s，type2 ≤ 60s |

### 4.3 High-Level Test Suite Design

| 套件 | 覆盖需求 | 测试技术 | 用例数 | Oracle |
|------|---------|---------|--------|--------|
| Suite A：唤醒 EP | REQ-001~007 | 等价类划分（有效类/无效类/时序无效类） | 21 | 5字段 |
| Suite B：唤醒 BVA | REQ-001/006/007 | 边界值分析（电压边界 + 时序边界） | 18 | 5字段 |
| Suite C：休眠决策表 | REQ-008~011 | 决策表（h1×h2×h3 全8组合） | 8 | vehicle_state=09 |
| Suite D：状态转移 | REQ-001~012 | 状态转移测试（All-Transitions，5条路径） | 15 | state 序列 |
| Suite E：卡死缺陷 | REQ-012 | 序列测试 + 变异重复执行 | 10 | result_type=stuck |
| Suite F：非功能时序 | REQ-014 | 性能测试（actual_duration 监控） | 10 | duration ≤ 阈值 |
| **合计** | REQ-001~014 | EP/BVA/决策表/状态转移/序列测试 | **82** | |

### 4.4 等价类划分（Suite A，以 w1 供电电压为例）

| 等价类 | 范围 | 代表值 | 预期 result_type |
|--------|------|--------|-----------------|
| 有效类（电压+时序均满足） | voltage > 9V AND duration ≥ 10ms | 9.3V, 15ms | expected |
| 无效类1（电压不满足） | voltage ≤ 9V | 8.9V, 15ms | error |
| 无效类2（时序不满足） | voltage > 9V AND duration < 10ms | 9.3V, 8ms | error |
| 无效类3（电压时序均不满足） | voltage ≤ 9V AND duration < 10ms | 8.5V, 5ms | error |

### 4.5 边界值分析（Suite B，以 w1 供电电压为例）

| 边界维度 | 边界点 | 测试值 | 预期 |
|---------|--------|--------|------|
| 电压下边界 | 9.0V | 8.9V / 9.0V / 9.1V | error / error / expected |
| 时序下边界 | 10ms | 9ms / 10ms / 11ms | error / expected / expected |
| 电压×时序双边界 | 9.0V, 10ms | 9.0V+10ms / 9.1V+9ms | error / error |

### 4.6 决策表（Suite C，REQ-011 休眠条件）

| 组合编号 | h1 (VCUIdle_flg) | h2 (AuthComplete_flg) | h3 (CAN停发) | 预期结果 | result_type |
|---------|-----------------|----------------------|-------------|---------|------------|
| C-001 | 0 | 0 | 0 | 不休眠，维持 state11 | error |
| C-002 | 1 | 0 | 0 | 不休眠 | error |
| C-003 | 0 | 1 | 0 | 不休眠 | error |
| C-004 | 0 | 0 | 1 | 不休眠 | error |
| C-005 | 1 | 1 | 0 | 不休眠 | error |
| C-006 | 1 | 0 | 1 | 不休眠 | error |
| C-007 | 0 | 1 | 1 | 不休眠 | error |
| **C-008** | **1** | **1** | **1** | **休眠 state09，bus_flag=0** | **expected** |

### 4.7 状态转移测试（Suite D，All-Transitions）

| 路径编号 | 前置状态 | 输入 | 后置状态 | 覆盖目标 |
|---------|---------|------|---------|---------|
| T-001 | state09 | w1 有效（9.3V, 15ms） | state11 | 正常唤醒路径 |
| T-002 | state11 | h1+h2+h3 全满足 | state09 | 正常休眠路径 |
| T-003 | state11 | h1+h2（缺 h3） | state11（维持） | 休眠条件不足路径 |
| T-004 | state09 | w1 无效（8.5V） | state09（维持） | 唤醒失败路径 |
| T-005 | state09 | 连续3次 w1 间隔<1s | state10（卡死） | 卡死缺陷路径 |

### 4.8 白盒覆盖目标

| 覆盖准则 | 目标 | 对应 Suite |
|---------|------|-----------|
| All-States | 覆盖 state09 / state10 / state11 | Suite D |
| All-Transitions | 覆盖全部 5 条状态转移路径（含卡死） | Suite D + E |
| Branch Coverage | 7路唤醒 × 有效/无效 = 14条分支 | Suite A |
| Stuck Path | 卡死触发序列专项覆盖 | Suite E |

### 4.9 Testing Framework & Rationale

- **执行框架**：pytest + httpx，向 FastAPI 仿真器发 HTTP 请求
- **选择理由**：轻量、脚本化、可 CI 集成，与 FastAPI 接口天然适配
- **执行流程**：`POST /reset` → `POST /simulate` → 校验 5 字段 + actual_duration + result_type → 存库 → 报告
- **测试脚本结构**（参考 bq_new 学长代码）：

```python
def test_wake_w1_valid():
    """REQ-001：供电电压有效，期望正常唤醒"""
    client.post("/reset")
    resp = client.post("/simulate", json={
        "type": 1,
        "in_data": [{"name": "供电电压", "value": "9.3", "duration": 15}],
        "est_time": 20
    })
    data = resp.json()
    assert data["vehicle_state"] == 11
    assert data["bus_message_flag"] == 1
    assert data["pdcu_wake_reason"] == 1
    assert data["power_current"] <= 0.05
    assert data["actual_duration"] <= 20
    assert data["result_type"] == "expected"
```

### 4.10 Organization Chart（分工）

| 成员 | 负责交付物 |
|------|----------|
| （填写） | VCU 仿真器开发（state机器 + 7路唤醒 + 3路休眠 + stuck仿真） |
| （填写） | AutoTestDesign Tool（需求导入 + 决策表生成器 + 状态转移生成器） |
| （填写） | 测试用例 JSON 文件（82条，含 expected/error/stuck 三种预期） |
| （填写） | 风险分析报告 + 测试计划文档 |
| （填写） | 详细测试设计与执行文档 + 测试结果分析 |

### 4.11 Cost Estimation

| 方式 | 工作量估算 |
|------|----------|
| 手工测试 82 条 × 10 min/条 | ~14 人时 |
| AutoTestDesign Tool 自动执行 | < 10 分钟 |
| 节省比例 | ~98% |
| 变异用例额外覆盖 | +N条（DataVariation 自动生成） |

---

## 五、风险分析（Risk Analysis Report）

### 5.1 需求风险评分

| REQ-ID | 安全影响 | 缺陷概率 | 风险等级 | 测试优先级 |
|--------|---------|---------|---------|----------|
| REQ-001 | 高（主要唤醒路径） | 中 | **High** | P1 |
| REQ-002 | 高（网络依赖） | 中 | **High** | P1 |
| REQ-011 | 高（唯一进入休眠路径） | 低 | **High** | P1 |
| REQ-012 | 极高（已知真实 bug） | 高 | **High** | P1 |
| REQ-003~005 | 中（辅助唤醒） | 低 | **Medium** | P2 |
| REQ-013 | 中（系统一致性） | 低 | **Medium** | P2 |
| REQ-014 | 中（响应时间） | 中 | **Medium** | P2 |
| REQ-006~010 | 低 | 低 | **Low** | P3 |

### 5.2 已知缺陷分析（REQ-012）

- **来源**：北汽原始需求文档（0319.pdf p.3）明确记录
- **缺陷描述**：N61AB_C01HBT 项目，PDCU 在频繁上下电过程中偶发 state 卡死在 state10，控制器不休眠，功耗电流始终 > 200mA
- **触发条件**：连续快速上下电（频率 > 1次/秒，持续3次以上）
- **根因**：控制器底层在频繁上下电过程中卡死在某一死循环中无法跳出
- **测试策略**：Suite E 专项设计快速循环序列，监控 actual_duration 超时和 vehicle_state 不跳转

---

## 六、开发工作量与时间安排

| 模块 | 主要工作 | 估计天数 |
|------|---------|---------|
| VCU 仿真器 | state机器 + 7路唤醒逻辑 + 3路休眠判断 + stuck检测 + FastAPI | 3天 |
| AutoTestDesign Tool 增强 | 新需求格式 + 决策表生成器 + 状态转移生成器 + 变异策略接口 | 3天 |
| 测试用例 JSON 文件 | 82条用例，含三种预期结构 | 2天 |
| pytest 测试脚本 | 6个 suite 的执行脚本 + 结果分析 | 1天 |
| 文档写作 | 风险报告 + 测试计划 + 详细设计文档 | 3天 |
| **合计** | | **12天** |

---

## 七、关键资料来源

| 资料 | 用于 |
|------|------|
| 客户提供的待测试的demo：模糊测试技术开发需求0319.pdf | 7路唤醒触发条件定义、已知 bug（state10卡死）描述 |
| 模糊测试技术方案细化0324.pdf | 模糊测试框架（M^N输入空间）、Δt反馈机制、新状态反馈机制 |
| 模糊测试技术方案细化0331-输入输出改2(1).pptx | 输入输出清单、测试平台接口对接方式 |
| bq_new/app/services/data_init.py | 测试用例 JSON 文件格式（type1/type2，in_put/out_put/error/stuck） |
| bq_new/app/services/data_variation.py | 三种变异策略（单参数/多参数/重复执行） |
| bq_new/app/services/result_judge.py | 结果判断逻辑（expected/error/stuck 三分类）、5个输出字段 |
| bq_new/app/services/bq_api.py | API 接口格式（send/read/reset），100+信号列表 |
