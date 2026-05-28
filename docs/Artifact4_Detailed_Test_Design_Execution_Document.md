# Artifact 4 — Detailed Test Design and Execution Document

> Assignment 2 第 4 项交付物。目标应用 = **VCU Wake-Sleep Behavior Simulator**；自选主要模块 = **Module A 唤醒-休眠决策模块（REQ-001~014）**；测试设计工具 = **AutoTestDesign V2**（LLM 驱动，qwen3.7-max via 百炼 DashScope）。
> 边界说明：AutoTestDesign 是**测试设计工具**；VCU Simulator 是**被测应用（SUT）**。本文档测的是 VCU Simulator 的 Module A，不是测 AutoTestDesign 工具本身。
> 所有数字均由脚本从 `docs/test_evidence/` 实测数据重算。

---

## 0. Cover Page

| Field | Content |
|---|---|
| Course | Software Testing |
| Assignment | Assignment 2 Final Project |
| Artifact | Detailed Test Design and Execution Document |
| Team ID | [INSERT TEAM ID] |
| Team Members | [INSERT NAMES AND STUDENT IDS] |
| Target Application | VCU Wake-Sleep Behavior Simulator |
| Selected Module | **Module A — Wake-Sleep Decision Module (REQ-001~014)** |
| Tool Used | AutoTestDesign V2 (LLM = qwen3.7-max / DashScope) |
| SUT 被测代码 | `vcu_simulator/simulator.py` |
| Date | [INSERT DATE] |
| Version | v1.0 |

---

## 1. Introduction

### 1.1 Purpose
本文档说明如何用 AutoTestDesign 工具，对 VCU Wake-Sleep Behavior Simulator 的 **Module A 唤醒-休眠决策模块**完成详细测试设计、脚本实现、执行与结果分析，覆盖评分要求：多种黑盒技术（EP/BVA/DT/SC）+ 白盒技术（State Transition）+ 风险驱动 + 全链路可追溯 + 人工交互式审查与改进 + 真实执行证据。

### 1.2 Target Application and Selected Module

| Item | Description |
|---|---|
| Target Application | VCU Wake-Sleep Behavior Simulator（FastAPI service）|
| Selected Module | Module A 唤醒-休眠决策状态机 |
| 状态 | state09(休眠) / state10(卡死) / state11(唤醒) |
| 7 路唤醒信号 | 供电电压 / CAN 报文 / CP / CC / CC2 / 口盖 / 门板 |
| 3 条休眠必要条件 | VCUIdle_flg(h1) ∧ AuthComplete_flg(h2) ∧ CAN stopped(h3) |
| 输出 Oracle 字段 | vehicle_state, pdcu_wake_reason, result_type, bus_message_flag, actual_duration, active_dtcs … |
| 主接口 | `POST /simulate` |

**三套服务运行基线（Step 1）**
![三套服务运行](test_evidence/screenshots/01_three_services_running.png)

**VCU Simulator Swagger / OpenAPI**
![VCU Swagger](test_evidence/screenshots/02_vcu_swagger.png.jpg)

**AutoTestDesign 工具前端**
![工具前端](test_evidence/screenshots/03_tool_frontend_home.png)

**`POST /simulate` 样例响应**
![simulate 响应](test_evidence/screenshots/04_simulate_sample_response.png)

### 1.3 Scope

**In Scope**：Module A 的 7 路唤醒判定、3 条件休眠判定、卡死缺陷复现、状态迁移、输出字段一致性、时序合规、API/进程内 pytest 执行、需求→风险→覆盖项→用例→结果全链路追溯。

**Out of Scope**：真实 HIL/dSPACE、ASAM XCP 物理通信、CAN 物理层、1kHz 物理采样、真车路测；以及 **Module B/C/D/E**（过压/欠压保护、CAN 错误、DTC 清除、功耗告警等）——本 Artifact **只测 Module A**。

### 1.4 AutoTestDesign 人工在环工作流（Human-in-the-loop Pipeline）

本测试设计**不是**"LLM 一键生成、原样采用"。AutoTestDesign 的每一阶段都遵循 **LLM 生成草稿 → 人工对照需求文档/课件审查 → 修订入库** 的闭环；全过程留下 **16 条编号修订（REV-001~016）+ 8 项工具缺陷修复（TOOL-FIX-001~008）**，每条都有 Before/After 文件 + 截图三件证据。流水线**严格自上而下**——需求文档在最前、测试用例在最末：

| # | 阶段 | LLM 生成（草稿）| 人工审查修订（在环动作）| REV-ID | 证据章节 |
|---|---|---|---|---|---|
| 1 | 需求解析 | 14 条结构化需求（含 6 处错误/遗漏）| 删伪输入 / 补时序双条件 / 补维持分支 / 拆复合条件 / 条件式 oracle | REV-001~005 | §2.2 |
| 2 | 风险分析 | 14 条 RPN（2 处低估 High 需求）| REQ-008/009 RPN 8/6 → 2，提到 Extensive | REV-009/010 | §2.4 |
| 3 | 覆盖项识别 | 14 条 Input 类 CI | 补 Output/Behavior/Environment **+8 → 22** | REV-006~008 | §4 |
| 4 | 覆盖策略 | 自动推断（多为单技术）| 按课件 §STP-5.8 映射表补多技术绑定 | REV-011 | §5 |
| 5 | 用例设计（prompt+生成）| 94 条（含 21 臆造字段 + 系统性 oracle 取值错误）| 两轮 prompt 改进 + 设计期审查（改/删/补）| REV-012~015 | §6 / §7 |
| 6 | 执行后修订 | —（执行才暴露的偏差）| REV-016 改 3 删 4 加 1 + adapter 修复 | REV-016 | §10.4 |
| 7 | 基于证据的改进 | 8 条 LLM 增广建议 | **8 进 3** 人工评审 + 覆盖缺口补 1 条 | （§12）| §12 |

> **关键澄清（回应"需求来源 / 流水线方向"）**：需求来源是**客户需求文档**（§2.1），测试用例是流水线**最末端**的派生产物（§7），二者不可倒置。LLM 在每一步只产出"草稿"，最终入库内容均经人工依据需求文档与课件判定——**人工在环是本测试设计的核心，而非自动化背书**。本文档在 §2.2 / §2.4 / §4 / §5 / §6 / §7 / §10.4 / §12 各阶段就地给出对应的 Before/After 证据。

---

## 2. Test Basis

### 2.1 Requirement Source（需求来源 = 客户需求文档，唯一）

本次模块测试的**唯一需求来源**是softwaretest-vcu-fuzzy-test-system/docs/PROJECT_PLAN_V2.md中关于model a的需求，计划文档的需求来自于之前真实的客户需求文档。


### 2.2 需求解析与人工修订（Requirement Parsing + Human Review，REV-001~005）

需求文档先经 `parse` prompt（§6.2）结构化为 14 条 JSON 需求（`01_parsed_requirements_raw.json`，qwen3.7-max，80.6s）。人工**通读对照需求文档**发现 **6 处 LLM 错误/遗漏**，在前端/API 上编辑修订其中 5 条（其余在覆盖项/用例阶段补足）：

| REV | REQ | LLM 草稿（Before）| 人工修订（After）| 依据 / 不改的后果 |
|---|---|---|---|---|
| REV-001 | REQ-005 | 把 `ubr_threshold` 当成 test input 字段 | **删除该字段**（它是 `/config` 常量，默认 4.4V，非 simulate 入参）| 否则 EP/BVA 会产生 `ubr_threshold=14.5V` 这种纯噪声用例 |
| REV-002 | REQ-006/007 | 电压字段 `has_timing = False` | 改 **True**（电压 + 时序双重判断）| 否则下游 BVA 只生成电压一维边界、漏掉 duration<10ms 用例 |
| REV-003 | REQ-011 | 只写"三条件全满足→state9"正向 oracle | 补"任一不满足→维持当前态（`vehicle_state ne 9`）"分支 | 决策表 8 行里有 7 行（任一不满足）会被判错 |
| REV-004 | REQ-012 | 把"次数≥3 AND 间隔<1s"压成单个 threshold=3 | **拆成两条独立 condition**（次数 / 时序间隔）| 否则 BVA 看不到 interval 边界 0.9/1.0/1.1s，漏卡死关键用例 |
| REV-005 | REQ-013 | 互斥 oracle（同字段 `bus_message_flag` 同时 eq1/eq0）| 改**条件式 oracle**：state11→flag=1 / state9→flag=0 | 否则用例生成不知两个值各对应哪种输入 |

**需求解析 Before / After 截图（5 组，证明 §2.3 的 14 条规则是人工审查后的版本）**

| REV | Before（LLM 草稿）| After（人工修订）|
|---|---|---|
| REV-001 (REQ-005 删 ubr_threshold) | ![](test_evidence/screenshots/REV-001_REQ-005_before.png) | ![](test_evidence/screenshots/REV-001_REQ-005_after.png) |
| REV-002 (REQ-006/007 has_timing) | ![](test_evidence/screenshots/REV-002_REQ-006_007_before.png) | ![](test_evidence/screenshots/REV-002_REQ-006_007_after.png) |
| REV-003 (REQ-011 补维持分支) | ![](test_evidence/screenshots/REV-003_REQ-011_before.png) | ![](test_evidence/screenshots/REV-003_REQ-011_after.png) |
| REV-004 (REQ-012 拆复合条件) | ![](test_evidence/screenshots/REV-004_REQ-012_before.png) | ![](test_evidence/screenshots/REV-004_REQ-012_after.png) |
| REV-005 (REQ-013 条件式 oracle) | ![](test_evidence/screenshots/REV-005_REQ-013_before.png) | ![](test_evidence/screenshots/REV-005_REQ-013_after.png) |

**需求解析原始输出（LLM raw）**
![parsed raw](test_evidence/screenshots/08_parsed_requirements_raw.png)

> 完整 6 处发现（含可选 REV-007/008：REQ-002 范围字符串化、REQ-010 丢 CAN ID 范围）见 `review_log.md` Phase 1。

### 2.3 Functional Rules Under Test（Module A，14 条；**人工修订后**）

> 下表为经 §2.2 的 REV-001~005 修订后的**最终**受测规则（非 LLM 原始解析输出）。

| REQ | 描述 | 期望 Oracle | 优先级 |
|---|---|---|---|
| REQ-001 | 供电电压 >9.0V 且持续 ≥10ms 唤醒 | vehicle_state=11, reason=1 | High |
| REQ-002 | CAN ID ∈ [0x400,0x47F] 唤醒 | vehicle_state=11, reason=2 | High |
| REQ-003 | CP 幅值 >9V 唤醒 | vehicle_state=11, reason=3 | Medium |
| REQ-004 | CC 电压 <4.4V 唤醒 | vehicle_state=11, reason=4 | Medium |
| REQ-005 | CC2 UBR <4.4V 唤醒 | vehicle_state=11, reason=5 | Medium |
| REQ-006 | 口盖 >4V 且 ≥10ms 唤醒 | vehicle_state=11, reason=6 | Low |
| REQ-007 | 门板 <1V 且 ≥10ms 唤醒 | vehicle_state=11, reason=7 | Low |
| REQ-008 | h1 (VCUIdle_flg=1) 休眠必要条件 | — | High |
| REQ-009 | h2 (AuthComplete_flg=1) 休眠必要条件 | — | High |
| REQ-010 | h3 (CAN stopped) 休眠必要条件 | — | High |
| REQ-011 | h1∧h2∧h3 同时满足才 state09，否则维持 | vehicle_state=9 / ne 9 | High |
| REQ-012 | **连续≥3 次快速循环 → state10 卡死 + DTC_001（已知缺陷）** | vehicle_state=10, DTC_001, dur=41s | **High（RPN=1）** |
| REQ-013 | state11→bus_message_flag=1；state09→0 | 条件式 oracle | Medium |
| REQ-014 | type1 ≤20s；type2 ≤60s 时序合规 | actual_duration lte | Medium |

### 2.4 风险分析与人工修订（Risk Analysis + Human Review，REV-009/010）

14 条结构化需求经 `risk` prompt（§6.2）做 ISO 9126 × (Tech × Business) 风险评分（`05_risk_analysis_raw.json`，75.5s）。人工复核发现 LLM 评分**多数合理**——尤其**精准把 REQ-012 卡死缺陷评为 RPN=1（最高优先级）**，并修正了计划书 §5.1（全标 RPN=2）与 §2.8 优先级列自相矛盾之处。故只 override 2 处被低估的 High 需求，其余尊重 AI 风险分析器的判断（符合 FR 2.0 定位）：

| REV | REQ | LLM 草稿 RPN | 人工修订 RPN | 依据 |
|---|---|---|---|---|
| REV-009 | REQ-008（休眠 h1）| 8（tech4×bus2, Broad）| **2（tech2×bus1, Extensive）** | h1=VCUIdle_flg 是休眠必要条件，§2.8 标 **High**；该休眠不休眠→电池耗尽、不该休眠却休眠→行车断电，业务风险 Very High |
| REV-010 | REQ-009（休眠 h2）| 6（tech3×bus2, Broad）| **2（tech2×bus1, Extensive）** | h2=AuthComplete_flg 同 h1，须与 REQ-010/011 同享 Extensive 测试深度，否则休眠 AND 逻辑决策表覆盖出现优先级断层 |

**最终 RPN 分布**：Extensive(RPN 1~5) 7 条 / Broad(RPN 6~10) 7 条；High 风险需求（RPN≤2）= 6 条（REQ-001/008/009/010/011/012），按 §11.1 要求 **100% 通过**。该 RPN 直接驱动 §8 追溯矩阵的优先级列、§10 的执行顺序与 §10.5 FR7 优先级排序。

**风险分析 Before / After 截图（REV-009/010）**

| Before（LLM 草稿 RPN）| After（人工修订 RPN）|
|---|---|
| ![risk before](test_evidence/screenshots/Phase3_RiskAnalysis_before.png) | ![risk after](test_evidence/screenshots/Phase3_RiskAnalysis_after.png) |

> 完整 9 处 LLM-vs-计划差异分析与"只 override 2 处"的决策依据见 `review_log.md` Phase 3。

---

## 3. Concept and Design Rationale

### 3.1 Testing Concept Applied
- **Risk-based testing**：按 RPN 排序，RPN=1（REQ-012 卡死）最先测（见 §10 + FR7 优先级排序）。
- **Coverage item** 表示可验证的测试覆盖目标（§4）；**Traceability matrix** 连接 REQ→风险→覆盖项→用例→结果（§8）。
- **AutoTestDesign** 支持设计自动化 + 人工交互式审查（§6）。

### 3.2 Black-box Techniques（多种，满足 Assignment「multiple black-box」）

| 技术 | 选用理由 | 应用于 |
|---|---|---|
| Equivalence Partitioning (EP) | 唤醒信号有有效/无效/特殊等价类 | REQ-001~010、REQ-013 |
| Boundary Value Analysis (BVA) | 电压/时序阈值易 off-by-one；每边界三点 + 无效类 | REQ-001~007、REQ-014 |
| Decision Table (DT) | h1∧h2∧h3 三布尔组合 2³ 全枚举 | REQ-008~011 |
| Scenario (SC) | 卡死是多步序列而非单点 | REQ-012 |

### 3.3 White-box Technique（满足「also white-box」，对应 Assignment FR 4.0）
- **State Transition Testing**：Module A 本质是一台有限状态机（state09 休眠 / state11 唤醒 / state10 卡死），输出强依赖"当前状态 + 事件"，最适合用状态迁移建模。覆盖准则取 **All-States（FR 4.0 必需）**，并额外做到 **All-Transitions（0-switch）**，REQ-012 卡死序列再提供 1-switch。详见 §11.4。

> **黑盒 + 白盒互补性分析**：黑盒技术（EP/BVA/DT/SC）从"需求/规格"角度切输入空间，保证每条需求的有效/无效/边界/组合都被测；白盒 ST 从"实现/状态"角度，保证状态机每个状态与迁移都被走到。两者交叉验证——例如 REQ-001 既有 BVA 边界用例（黑盒，9.0V 阈值三点）又有 ST 迁移用例（白盒，state09→state11），同一需求被两个视角覆盖，降低漏测风险。这也是 Assignment 要求"multiple black-box + also white-box"的用意。

---

## 4. Coverage Item Identification（§4，测什么）

> Coverage Item 在 AutoTestDesign 的 Coverage 页维护（不显示 technique 列，技术归属见 §5 Strategy 总览）。工具初版 LLM 只生成 14 条 Input 类 CI，人工补齐 Output/Behavior/Environment 三类 → **14 → 22**（REV-006~008，本节下方 Before/After 截图）。

**22 条 Module A Coverage Items**（来源 `_state_snapshot/coverage_items.json`）：

| # | REQ | 技术 | ISO 9126 | Coverage Item |
|---|---|---|---|---|
| 1 | REQ-001 | BVA | Functionality | 硬线供电唤醒边界值测试 |
| 2 | REQ-002 | BVA | Functionality | CAN 网络唤醒报文 ID 边界测试 |
| 3 | REQ-003 | BVA | Functionality | CP 信号唤醒电压边界测试 |
| 4 | REQ-004 | BVA | Functionality | CC 信号唤醒电压边界测试 |
| 5 | REQ-005 | BVA | Functionality | CC2 信号唤醒电压边界测试 |
| 6 | REQ-006 | BVA | Functionality | 口盖信号唤醒电压与时间边界测试 |
| 7 | REQ-007 | BVA | Functionality | 门板信号唤醒电压与时间边界测试 |
| 8 | REQ-008 | EP | Functionality | 休眠条件 h1 状态等价类测试 |
| 9 | REQ-009 | EP | Functionality | 休眠条件 h2 状态等价类测试 |
| 10 | REQ-010 | EP | Functionality | 休眠条件 h3 CAN 总线空闲状态测试 |
| 11 | REQ-011 | DT | Functionality | 三条件组合休眠判定表测试 |
| 12 | REQ-012 | SC | Reliability | 快速唤醒休眠循环卡死缺陷场景测试 |
| 13 | REQ-013 | ST | Functionality | 电源状态与总线报文标志位状态转换测试 |
| 14 | REQ-014 | BVA | Efficiency | 响应时序合规性边界值测试 |
| 15 | REQ-001 | EP | Functionality | vehicle_state 唤醒/休眠 oracle 一致性 (Output) |
| 16 | REQ-001 | EP | Functionality | pdcu_wake_reason 来源编码 oracle (Output) |
| 17 | REQ-013 | DT | Functionality | bus_message_flag 与 vehicle_state 一致性 (Output) |
| 18 | REQ-014 | BVA | Efficiency | actual_duration 时序边界 oracle (Output) |
| 19 | REQ-012 | SC | Reliability | active_dtcs 卡死时包含 DTC_001 (Output) |
| 20 | REQ-001 | ST | Functionality | 正常唤醒序列 state09→state11 (Behavior) |
| 21 | REQ-012 | SC | Reliability | 卡死序列：连续 3 次快速循环触发 state10 (Behavior) |
| 22 | REQ-001 | EP | Functionality | VCU 仿真器 v1.0 SIL 环境基线 (Environment) |

技术分布：BVA 9 / EP 6 / SC 3 / DT 2 / ST 2；类别：Input 14 + Output 5 + Behavior 2 + Environment 1。

**分析**：工具初版（LLM）只产出 **14 条 Input 类**覆盖项——只关心"输入边界"，完全忽略 ISO 29119 §6.2 要求的 **Test Oracle 维度**与序列/环境维度。人工评审据此补了 **+8 条**：① **5 条 Output**（vehicle_state / pdcu_wake_reason / bus_message_flag↔state / actual_duration / **active_dtcs 含 DTC_001**）——没有它们，用例就"无 oracle、无法判定通过/失败"，尤其 DTC_001 这条让 DEF-001 卡死缺陷**可被断言**；② **2 条 Behavior**（正常唤醒序列、卡死 6 步序列）——给白盒 ST 与场景 SC 技术一个"覆盖目标"，否则状态机/缺陷复现无从下手；③ **1 条 Environment**（SIL 环境基线）——支撑 §13 Limitations。这 8 条不是凑数，每条都解锁了一个技术 / oracle / 缺陷检出能力（REV-006~008，下方 Before/After 截图；改进闭环见 §12）。

**人工补全 Coverage Items（Before 14 → After 22）**
| Before（工具初版，只有 Input 类）| After（人工补 Output/Behavior/Environment）|
|---|---|
| ![CI before](test_evidence/screenshots/Phase2_CoverageItems_before.png) | ![CI after](test_evidence/screenshots/Phase2_CoverageItems_after.png) |

---

## 5. Coverage Strategy and Method（§5，用什么技术测）

> Strategy 页维护每条需求的技术集合 + rationale，初始由该需求 Coverage Items 的技术集合自动推断（`ensure_strategy`），人工按课件 §STP-5.8 映射表修订（REV-011）。存储与 coverage_items 分离（`strategies.json`）。

| REQ | 技术 | Rationale（节选）|
|---|---|---|
| REQ-001 | EP;BVA;ST | 输入域等价类 + 9V&10ms 时序边界 + state09→state11 迁移 |
| REQ-002 | EP;ST | CAN ID 范围等价类 + 唤醒迁移 |
| REQ-003~005 | EP;ST | 输入域等价类 + 状态迁移 |
| REQ-006/007 | EP;BVA;ST | 带时序唤醒：等价类 + duration≥10ms 边界 + 迁移 |
| REQ-008~010 | DT;ST | 布尔条件决策表 + state11→state09 迁移 |
| REQ-011 | DT;ST | h1∧h2∧h3 的 2³ 决策表全枚举 + 迁移 |
| REQ-012 | ST;SC | 状态迁移 + 快速 3 次循环序列复现 DEF-001 |
| REQ-013 | EP | bus_message_flag 输出域等价类 |
| REQ-014 | BVA | actual_duration 时序边界 |

技术覆盖 **EP/BVA/DT/ST/SC 五种齐全**（黑盒 4 + 白盒 1）。

### 5.1 策略人工修订（REV-011，Before 工具初版 → After 人工）

工具初版 strategy 由后端 `ensure_strategy()` 从各需求已有 Coverage Item 的 technique 字段**自动推断**，结果偏单一（多数只挂 1 个技术）。人工按课件 §STP-5.8「需求 ↔ 黑盒/白盒技术」映射表逐条修订为多技术组合（14 条全改）：

| REQ | Before（工具自动推断）| After（人工修订）| 修订原因 |
|---|---|---|---|
| REQ-001 | EP;BVA | **EP;BVA;ST** | 补 ST：w1 唤醒涉及 state09→state11 迁移，需 All-Transitions 覆盖 |
| REQ-002 | BVA | **EP;ST** | CAN ID 是离散范围，EP 比 BVA 更对口 + 唤醒迁移 |
| REQ-003 | BVA | **EP;ST** | CP 幅值等价类 + 状态迁移 |
| REQ-004 | BVA | **EP;ST** | w4 输入等价类 + 状态迁移 |
| REQ-005 | BVA | **EP;ST** | w5 输入等价类 + 状态迁移 |
| REQ-006 | BVA | **EP;BVA;ST** | 带时序唤醒：保留 BVA(duration≥10ms 边界) + 补 EP + ST |
| REQ-007 | BVA | **EP;BVA;ST** | 同 REQ-006，带时序双条件 |
| REQ-008 | EP | **DT;ST** | 休眠 h1 是布尔条件 → 决策表 + 状态迁移 |
| REQ-009 | EP | **DT;ST** | 休眠 h2：决策表 + 状态迁移 |
| REQ-010 | EP | **DT;ST** | 休眠 h3：决策表 + 状态迁移 |
| REQ-011 | DT | **DT;ST** | h1∧h2∧h3 保留 DT(2³ 全枚举) + 补 ST |
| REQ-012 | SC | **ST;SC** | 已知卡死缺陷：保留场景序列(SC) + 补 ST 验证 state10 |
| REQ-013 | ST | **EP** | bus_message_flag 输出一致性改为输出域等价类(EP)，比 ST 更准确 |
| REQ-014 | BVA | **BVA** | actual_duration≤20s 时序边界保持；性能 NFR 度量见 §13.1 |

> Strategy 存储与 coverage_items 分离（`strategies.json`）。真正证据 = CSV 逐条 Before/After：`07_strategy_assignment_before.csv` vs `07_strategy_assignment.csv`（前端 Strategy 页一次只显示 1 条需求、14 张截图不现实，以 CSV 为准）。

---

## 6. AutoTestDesign Prompt Design and Interactive Review（§6）

工具共 **5 个 prompt 模板**驱动整条流水线：`parse`（需求解析/FR1.1）、`risk`（风险分析/FR2.0）、`coverage`（覆盖项/FR3.0 前置）、`testcase`（用例+oracle/FR3.0+4.0+5.0）、`improve`（第二轮 LLM 用例增广）。所有 prompt 都强约束"仅返回 JSON + 明确字段 schema + operator 受限集 `eq/ne/gte/lte/gt/lt/contains`"。下面给出每个 prompt 的**完整 system_prompt 全文**。

### 6.1 完整 Prompt 文本（5 个 system_prompt）

**① `parse` — 需求解析（FR 1.1）**
```
你是软件测试工程师，从汽车 VCU 原始需求中识别需求条目并结构化。
仅返回 JSON 对象，格式为 {"requirements": [...]}。
每个 requirements 元素字段：
requirement_id, title, module, description, input_fields, conditions, expected_actions, parse_confidence。
input_fields: [{name, data_type, valid_range, unit, has_timing}]
conditions: [{type, description, threshold}]
expected_actions: [{output_field, expected_value, operator}]
operator 只能是 eq/gte/lte/gt/lt/contains。
```

**② `risk` — 风险分析（FR 2.0）**
```
你是汽车 ECU 测试专家，按 ISO 9126 和 Chapter 4 Tech Risk × Business Risk 做风险评分。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：
requirement_id, iso9126_characteristic, tech_risk, business_risk, rpn, extent, reasoning。
tech_risk/business_risk 为 1-5，1 表示最高风险；rpn=tech_risk*business_risk。
extent 规则：1-5 Extensive, 6-10 Broad, 11-15 Cursory, 16-25 Low priority。
```

**③ `coverage` — 覆盖项生成（FR 3.0 前置）**
```
你是测试设计工程师，为每条 VCU 需求生成覆盖项。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：requirement_id, title, description, technique, iso9126_characteristic, priority。
technique 可为 EP/BVA/DT/ST/SC。
```

**④ `testcase` — 测试用例 + Oracle 生成（FR 3.0+4.0+5.0，当前 v3 取值语义版）⭐**
```
你是测试用例设计器，为汽车 VCU 需求生成 bq_new 兼容测试用例。
仅返回 JSON 对象：{"test_cases": [...]}。
每个 test_cases 元素字段：
requirement_id, coverage_item_id, title, technique, type, in_data, expected_results, error, est_time, oracle_reasoning。
in_data: [{name, data_type, value, duration, unit}]
expected_results: [{name, operator, value, out_type, out_range}]

【关键约束——expected_results 的 name 只能取 VCU 仿真器真实返回的输出字段，禁止臆造】
合法 name 仅限：vehicle_state, vehicle_mode, power_current, bus_message_flag, pdcu_wake_reason,
actual_duration, result_type, power_alarm_flag, bus_off_flag, active_dtcs, state_name。
- 禁止使用 is_compliant / sleep_sub_condition_x / Next_State 等 VCU 不返回的字段（否则 Untestable）。
- 状态断言一律用 vehicle_state（休眠=9, 卡死=10, 唤醒=11）；"维持非休眠"用 vehicle_state ne 9。
- 时序合规用 actual_duration（配合 lte/gt 阈值，如 type1 lte 20、type2 lte 60）。
- active_dtcs 是列表，断言某 DTC 存在时 operator 用 contains（如 active_dtcs contains DTC_001），不要用 eq。
operator 只能是 eq/ne/gte/lte/gt/lt/contains。
必须覆盖用户指定技术 EP/BVA/DT/ST/SC，并包含 REQ-ID 与 Coverage Item ID。

【VCU 输出取值语义——oracle 的 value 必须符合真实取值，禁止臆造】（v3 TOOL-FIX-007 新增）
- vehicle_state 仅 {9=休眠, 10=卡死, 11=唤醒}，绝不出现 0 或其它值。
  · 未满足任何唤醒条件 / 无效输入 → 维持休眠：vehicle_state=9
  · 唤醒成功 → vehicle_state=11
  · 连续≥3次快速(相邻间隔<1s)唤醒-休眠循环后再唤醒 → 卡死：vehicle_state=10
- pdcu_wake_reason：0=未唤醒；1~7=七路唤醒源；未唤醒一律 0。
- result_type 仅 {"expected","error"}：
  · "expected" = 动作按条件成功发生（成功唤醒，或 h1∧h2∧h3 成功休眠）
  · "error" = 未满足条件 / 维持原态 / 卡死（卡死靠 vehicle_state=10 + active_dtcs 含 DTC_001 识别，不要写 stuck）
- bus_message_flag：state11→1，state09→0。
- actual_duration：正常 type1≤20、type2≤60；只有卡死才会超时(>20)。时序合规一律用 lte 阈值。
- active_dtcs：卡死写入 "DTC_001"，断言用 contains。
统一口径示例：无效/未唤醒输入 → (9, reason 0, error)；有效唤醒 → (11, reason 1~7, expected)；卡死 → (10, DTC_001 contains, error)
```

**⑤ `improve` — 第二轮 LLM 用例增广（§12 来源 A，非 fuzz）**
```
你是测试设计改进助手。基于第一轮测试执行结果（覆盖情况与未通过用例），为相关需求提出第二轮的
测试覆盖项与测试用例增广建议（补充遗漏的边界、状态与场景）。
仅返回 JSON 对象：{"suggestions": [...]}。
每个 suggestions 元素字段：requirement_id, title, reason, coverage_item, test_case。
coverage_item 字段同覆盖项；test_case 字段同 bq_new 兼容测试用例，可为 null。
```

**Prompt 工程五要点**：① 强约束"仅返回 JSON"+ 字段 schema 保证可解析；② **字段白名单**（v2/REV-015）消除臆造不可验证字段（21→0）；③ **取值语义**（v3/TOOL-FIX-007）约束每字段合法取值（48/96→80/99）；④ **operator 受限集**（ne 为 TOOL-FIX-006 新增）杜绝非法算子；⑤ 强制 `oracle_reasoning` 使每条 oracle 可人工审查（FR 5.0）。

### 6.2 testcase prompt 两轮迭代（Prompt Design 的核心证据）

testcase prompt 不是一次写死，而是依据"设计期人工审查"和"执行期真实反馈"**两次回炉**——每次都改**工具（prompt）**而非手工补用例：

| 版本 | 改进 | 修复的问题 | 量化效果 | 存档 |
|---|---|---|---|---|
| v1 | 仅字段列表 | — | 含臆造字段 21 条 + oracle 取值系统性错误 | `prompt_testcase_before.json` |
| v2 (REV-015) | + 字段名白名单、禁止臆造、active_dtcs 用 contains | Untestability（is_compliant / sleep_sub_condition_* / Next_State 等 VCU 不返回字段）| 臆造字段 **21 → 0** | `prompt_testcase_v2_fieldwhitelist.json` |
| **v3 (TOOL-FIX-007)** | + **VCU 输出取值语义**（state∈{9,10,11}、result_type∈{expected,error}…）| 系统性 oracle 取值错误（state=0 幻觉、维持态写 10、no-wake 写 expected、卡死写 stuck）| 执行通过率 **48/96 → 80/99** | `prompt_testcase_v3_value_semantics.json` |

**testcase prompt 改进后（v3）截图**
![prompt after](test_evidence/screenshots/Phase6_Prompt_testcase_after.png)

### 6.3 设计期测试用例审查（REV-012~015，人工对照课件检查清单）

用例生成后，人工严格对照课件（Chp4TestTechPart1 EP/BVA、InspectionLiveSession 评审清单）逐条审查：

| REV | REQ/数量 | LLM 初版问题 | 人工修订 | 课件依据 |
|---|---|---|---|---|
| REV-012 | REQ-014 ×6 | oracle 用 `is_compliant`——VCU 不返回，**Untestable** | 改真实字段 `actual_duration`：type1 lte20(19.9/20.0)/gt20(20.1)、type2 lte60/gt60 | InspectionLiveSession P9 + BVA 三点 |
| REV-013 | REQ-012 ×2 | 标题"**不**触发卡死"却写 `result_type=stuck`+list 误用 eq | 改 `result_type ne stuck` + `vehicle_state ne 10` | Chp4Part1 P5 Incompletely specified conditions |
| REV-014 | REQ-001 +1 | BVA 缺 **invalid-too-low** 等价类（只有 9.0/9.1，漏 8.9）| 新增 8.9V 用例（vehicle_state eq 9）| Chp4Part1 P35-40 BVA 必含无效类 |
| REV-015 | REQ-008/009/010 ×17 | oracle 用 `sleep_sub_condition_*`/`Next_State`——**Untestable** | (a) 改 prompt 加字段白名单（→v2）；(b) regenerate 三需求全改用 vehicle_state | InspectionLiveSession P9 + Prompt Design |

**REV-015 量化效果**：重生成前全库 **21 条**引用 VCU 不存在字段（is_compliant×6 / sleep_sub_condition_*×16 / Next_State×1）→ 改 prompt + regenerate 后 **0 条**（脚本扫描验证）。

> 执行期审查 REV-016（改3删4加1）由真实执行暴露，按时序归 §10.4。

### 6.4 Interactive Review 主索引（REV-001~016 全程）

| REV | 阶段 | 修订摘要 | Before/After 证据所在 |
|---|---|---|---|
| REV-001~005 | 需求解析 | 删伪输入 / 时序双条件 / 维持分支 / 拆复合条件 / 条件式 oracle | **§2.2**（5 组截图）|
| REV-006~008 | 覆盖项 | +5 Output / +2 Behavior / +1 Environment（14→22）| **§4**（CI 截图）|
| REV-009/010 | 风险 | REQ-008/009 RPN 8/6→2 Extensive | **§2.4**（风险截图）|
| REV-011 | 策略 | 14 条需求补多技术绑定 | **§5.1**（前后表）|
| REV-012~015 | 用例（设计期）| Untestable oracle 修正 + BVA 无效类 + 重生成 | **§6.3** + Prompt 截图 |
| REV-016 | 用例（执行期）| 改 3 删 4 加 1 | **§10.4**（执行纠正链）|

> 完整逐条记录（Before/After 文件路径 + Why + 操作人/时间）见 `review_log.md`（Phase 1~6）。

---

## 7. Test Case Design（§7）

### 7.1 用例规模与构成
**96 条** reviewed 设计用例（`09_test_cases_reviewed.json`）：

| 技术 | 条数 |
|---|---|
| EP | 27 |
| BVA | 33 |
| DT | 13 |
| ST | 18 |
| SC | 5 |
| **合计** | **96** |

正向 49（期望成功唤醒→11/休眠→9）/ 负向 47（期望报错/拒绝/卡死/维持）。

**分析**：① **技术分配与需求性质对口**——7 路唤醒（REQ-001~007）都有电压/时序阈值，故以 **BVA**（每边界 below/on/above 三点 + 无效类）为主、辅以 EP 与 ST；3 条休眠条件（REQ-008~011）是布尔组合，用 **DT** 把 h1∧h2∧h3 的 2³=8 行全枚举；卡死（REQ-012）是多步时序序列，用 **SC** 场景 + ST 迁移；状态机贯穿用 **ST** 白盒。② **负向占 49%（47 条）是刻意设计**——测试目的之一就是"找出 VCU 会报错/卡死的地方"，而不是把用例都做成 success；这也是 DEF-001 能被复现的前提。③ BVA 必含**无效等价类**（如供电 8.9V invalid-too-low），是 REV-014 对照课件 Chp4Part1 P35-40 补回的。

### 7.2 每种技术样例（含合成 oracle = FR 5.0）

| 技术 | REQ | 输入 | 期望 Oracle |
|---|---|---|---|
| BVA | REQ-001 | voltage=9.1, duration=11 | vehicle_state=11, reason=1, expected, dur≤20 |
| EP | REQ-001 | voltage=12, duration=50 | vehicle_state=11, expected |
| ST | REQ-001 | voltage=12, duration=20 | vehicle_state=11, bus_message_flag=1, expected |
| DT | REQ-008 | VCUIdle_flg=1 | vehicle_state=9, expected |
| SC | REQ-012 | cycles=2, interval=0.9 | vehicle_state=11, expected（不触发卡死）|

### 7.3 用例版本链（全程保留，可追溯）

| 版本 | 条数 | 含义 | 文件 |
|---|---|---|---|
| v0 | 88 | 首次 generate-all（REQ-014 因 502 bug 缺失）| `08_test_cases_raw_88_initial.json` |
| v1 | 94 | 修 502 后补全；**人工审查前的纯工具输出**（含臆造字段 21 处）| `08_test_cases_raw.json` |
| v2 | 96 | 字段白名单 + REV-012~015 设计期审查 | `09b_..._RECONSTRUCTED.json` |
| v3 | 99 | 取值语义重生成（TOOL-FIX-007），REV-016 前 | `09a_..._before_REV016.json` |
| **v4** | **96** | v3 + REV-016 执行期审查（改3删4加1）| **`09_test_cases_reviewed.json`** |

**分析**：核心 Before/After = v1（工具初版 94，含 21 条臆造字段）↔ v4（最终 96，0 臆造、96/96 通过）。中间 v2/v3 完整保留，体现"两轮 prompt 改进 + 两轮人工审查"的迭代闭环——designer 不是一次写死，而是依据"设计期人工审查"和"执行期真实反馈"两次回炉（详见 §6、§10.4、§12）。

---

## 8. Traceability Matrix（§8）

全量追溯文件 `10_traceability_matrix.csv`（96 行），列结构：`Test Case ID | Design Case UUID | Coverage Item ID | Requirement ID | Technique | RPN | Polarity | Result | Title`。每行可经 **Design Case UUID** join 到 `execution_details.json`（取真实 VCU 输出），实现**需求 → 风险(RPN) → 覆盖项 → 用例 → 执行结果**五级双向可追溯。

### 8.1 全量追溯矩阵（96 行，来自 `10_traceability_matrix.csv`）

> 列说明：`UUID(8)` = Design Case UUID 前 8 位（足以唯一定位并 join `execution_details.json`，完整 36 位见 CSV）；`CI ID` = Coverage Item ID（UUID 取前 8 位；占位串 `EP-REQ-00x`/`ST-REQ-00x`/`N/A`/`—` 为 v3 重生成时 UUID 链丢失项，仍可经 (REQ+技术) 映射回 canonical CI，见 §11.2）；极性 正=期望唤醒/休眠成功，负=期望报错/拒绝/维持/卡死。

**EP 等价类（27 条）**

| Test Case ID | UUID(8) | CI ID | REQ | RPN | 极性 | 结果 | 标题 |
|---|---|---|---|---|---|---|---|
| TC-EP-01 | f9b1ff34 | 4d57bf11 | REQ-001 | 2 | 正 | PASS | 正常唤醒_vehicle_state_eq_11 |
| TC-EP-02 | 96efed00 | 4d57bf11 | REQ-001 | 2 | 负 | PASS | 未满足唤醒条件_vehicle_state_eq_9 |
| TC-EP-03 | 93e1c973 | 81cc0697 | REQ-001 | 2 | 正 | PASS | 硬线唤醒_pdcu_wake_reason_eq_1 |
| TC-EP-04 | 68011a5e | 81cc0697 | REQ-001 | 2 | 正 | PASS | 无唤醒_pdcu_wake_reason_eq_0 |
| TC-EP-05 | bcb9c9d8 | 5dd2cbe4 | REQ-001 | 2 | 正 | PASS | SIL环境基线验证_正常唤醒 |
| TC-EP-06 | b26ff8b5 | 327e5c6a | REQ-008 | 2 | 正 | PASS | VCUIdle_flg为1时满足休眠条件 |
| TC-EP-07 | 0d9216bf | 327e5c6a | REQ-008 | 2 | 负 | PASS | VCUIdle_flg为0时不满足休眠条件 |
| TC-EP-08 | 415392c6 | be20e236 | REQ-009 | 2 | 正 | PASS | AuthComplete_flg为1时满足休眠条件h2 |
| TC-EP-09 | ac4b8699 | 9e6be4d2 | REQ-010 | 2 | 正 | PASS | 休眠条件h3满足(CAN总线空闲) |
| TC-EP-10 | 2cba1c5d | 9e6be4d2 | REQ-010 | 2 | 负 | PASS | 休眠条件h3不满足(CAN总线非空闲) |
| TC-EP-11 | 003eea21 | — | REQ-003 | 4 | 正 | PASS | CP信号有效电压12.0V触发唤醒 |
| TC-EP-12 | 046f4995 | — | REQ-003 | 4 | 负 | PASS | CP信号无效电压5.0V不唤醒 |
| TC-EP-13 | 16517744 | EP-REQ-002 | REQ-002 | 6 | 正 | PASS | 有效等价类(范围内中间值0x440)成功唤醒 |
| TC-EP-14 | c7d71344 | EP-REQ-002 | REQ-002 | 6 | 负 | PASS | 无效等价类(小于0x400的0x200)不唤醒 |
| TC-EP-15 | aec8ac6e | EP-REQ-002 | REQ-002 | 6 | 负 | PASS | 无效等价类(大于0x47F的0x600)不唤醒 |
| TC-EP-16 | 3fc01f56 | 1945c7d8 | REQ-004 | 6 | 正 | PASS | CC电压有效等价类唤醒测试 |
| TC-EP-17 | 80095a4f | 1945c7d8 | REQ-004 | 6 | 负 | PASS | CC电压无效等价类不唤醒测试 |
| TC-EP-18 | 9358d3f5 | EP-REQ-005 | REQ-005 | 6 | 正 | PASS | CC2电压有效等价类唤醒测试 |
| TC-EP-19 | feeff67e | EP-REQ-005 | REQ-005 | 6 | 负 | PASS | CC2电压无效等价类不唤醒测试 |
| TC-EP-20 | b783cc48 | 67935ead | REQ-007 | 6 | 正 | PASS | 门板电压与时间均在有效等价类触发唤醒 |
| TC-EP-21 | 41705132 | 67935ead | REQ-007 | 6 | 负 | PASS | 门板电压在无效等价类不触发唤醒 |
| TC-EP-22 | 513fbf5f | 67935ead | REQ-007 | 6 | 负 | PASS | 门板时间在无效等价类不触发唤醒 |
| TC-EP-23 | 966ce13d | 31c9b11d | REQ-013 | 8 | 正 | PASS | 有效等价类-vehicle_state为11 |
| TC-EP-24 | 4dac6c7e | 31c9b11d | REQ-013 | 8 | 正 | PASS | 有效等价类-vehicle_state为9 |
| TC-EP-25 | b6a3f6f6 | N/A | REQ-006 | 9 | 正 | PASS | 有效等价类：电压和时间均满足唤醒条件 |
| TC-EP-26 | b7b68d68 | N/A | REQ-006 | 9 | 负 | PASS | 无效等价类：电压不满足唤醒条件 |
| TC-EP-27 | c496b5ac | N/A | REQ-006 | 9 | 负 | PASS | 无效等价类：持续时间不满足唤醒条件 |

**BVA 边界值（33 条）**

| Test Case ID | UUID(8) | CI ID | REQ | RPN | 极性 | 结果 | 标题 |
|---|---|---|---|---|---|---|---|
| TC-BVA-01 | aed53778 | 9505f9e7 | REQ-001 | 2 | 正 | PASS | 有效边界_电压9.1V_持续11ms |
| TC-BVA-02 | 867cfe89 | 9505f9e7 | REQ-001 | 2 | 负 | PASS | 无效边界_电压9.0V_持续10ms |
| TC-BVA-03 | 06483b58 | 9505f9e7 | REQ-001 | 2 | 负 | PASS | 无效边界_电压9.1V_持续9ms |
| TC-BVA-04 | ed33fefd | 9505f9e7 | REQ-001 | 2 | 负 | PASS | 电压8.9V (invalid-too-low) 不触发唤醒（REV-014 补）|
| TC-BVA-05 | ae1c553c | 9e6be4d2 | REQ-010 | 2 | 负 | PASS | 休眠条件h3时间窗口下边界(不满足) |
| TC-BVA-06 | 7aacb8c9 | 9e6be4d2 | REQ-010 | 2 | 正 | PASS | 休眠条件h3时间窗口标称值(满足) |
| TC-BVA-07 | 2d16734e | a762e3cd | REQ-003 | 4 | 负 | PASS | CP信号电压8.9V不唤醒 |
| TC-BVA-08 | 08398f11 | a762e3cd | REQ-003 | 4 | 负 | PASS | CP信号电压9.0V不唤醒 |
| TC-BVA-09 | 3db545bb | a762e3cd | REQ-003 | 4 | 正 | PASS | CP信号电压9.1V触发唤醒 |
| TC-BVA-10 | 7c884e48 | 2bf2066a | REQ-002 | 6 | 负 | PASS | CAN报文ID下边界外(0x3FF)不唤醒 |
| TC-BVA-11 | 866ea05a | 2bf2066a | REQ-002 | 6 | 正 | PASS | CAN报文ID下边界(0x400)成功唤醒 |
| TC-BVA-12 | a80270da | 2bf2066a | REQ-002 | 6 | 正 | PASS | CAN报文ID上边界(0x47F)成功唤醒 |
| TC-BVA-13 | 47c3e760 | 2bf2066a | REQ-002 | 6 | 负 | PASS | CAN报文ID上边界外(0x480)不唤醒 |
| TC-BVA-14 | e3b2dea4 | 1945c7d8 | REQ-004 | 6 | 正 | PASS | CC电压4.3V唤醒测试 |
| TC-BVA-15 | cde914db | 1945c7d8 | REQ-004 | 6 | 负 | PASS | CC电压4.4V不唤醒测试 |
| TC-BVA-16 | addb86e7 | 1945c7d8 | REQ-004 | 6 | 负 | PASS | CC电压4.5V不唤醒测试 |
| TC-BVA-17 | 5897c745 | 3e28fc83 | REQ-005 | 6 | 正 | PASS | CC2电压4.3V边界唤醒测试 |
| TC-BVA-18 | c73c1bff | 3e28fc83 | REQ-005 | 6 | 负 | PASS | CC2电压4.4V边界不唤醒测试 |
| TC-BVA-19 | 8adc3c01 | 3e28fc83 | REQ-005 | 6 | 负 | PASS | CC2电压4.5V边界不唤醒测试 |
| TC-BVA-20 | 9f9986b7 | 67935ead | REQ-007 | 6 | 正 | PASS | 门板电压下边界有效且时间下边界有效触发唤醒 |
| TC-BVA-21 | cf712a11 | 67935ead | REQ-007 | 6 | 负 | PASS | 门板电压上边界无效且时间下边界有效不触发唤醒 |
| TC-BVA-22 | b910cdb6 | 67935ead | REQ-007 | 6 | 负 | PASS | 门板电压下边界有效且时间上边界无效不触发唤醒 |
| TC-BVA-23 | 62a5c989 | 3c90f016 | REQ-014 | 6 | 正 | PASS | type1单信号唤醒时序边界19.9s合规 |
| TC-BVA-24 | 124fba9a | 3c90f016 | REQ-014 | 6 | 正 | PASS | type1单信号唤醒时序边界20.0s合规 |
| TC-BVA-25 | 901926bf | 57068d42 | REQ-014 | 6 | 负 | PASS | type1单信号唤醒时序边界20.1s不合规 |
| TC-BVA-26 | 30970747 | 3c90f016 | REQ-014 | 6 | 正 | PASS | type2多信号休眠时序边界59.9s合规 |
| TC-BVA-27 | 886b8539 | 3c90f016 | REQ-014 | 6 | 正 | PASS | type2多信号休眠时序边界60.0s合规 |
| TC-BVA-28 | 6d2ee7ab | d1b4e183 | REQ-006 | 9 | 负 | PASS | 电压下边界外：3.9V |
| TC-BVA-29 | ee54d9c7 | d1b4e183 | REQ-006 | 9 | 负 | PASS | 电压下边界：4.0V |
| TC-BVA-30 | 8069a480 | d1b4e183 | REQ-006 | 9 | 正 | PASS | 电压刚过边界：4.1V |
| TC-BVA-31 | f4e1868c | d1b4e183 | REQ-006 | 9 | 负 | PASS | 时间下边界外：9ms |
| TC-BVA-32 | d2a3afdf | d1b4e183 | REQ-006 | 9 | 正 | PASS | 时间下边界：10ms |
| TC-BVA-33 | 6a41e68e | d1b4e183 | REQ-006 | 9 | 正 | PASS | 时间刚过边界：11ms |

**DT 决策表（13 条）**

| Test Case ID | UUID(8) | CI ID | REQ | RPN | 极性 | 结果 | 标题 |
|---|---|---|---|---|---|---|---|
| TC-DT-01 | 2e316a80 | 327e5c6a | REQ-008 | 2 | 正 | PASS | 决策表规则1_VCUIdle_flg为1 |
| TC-DT-02 | ce1fd6b1 | 327e5c6a | REQ-008 | 2 | 负 | PASS | 决策表规则2_VCUIdle_flg为0 |
| TC-DT-03 | 3bfb2b0d | be20e236 | REQ-009 | 2 | 负 | PASS | AuthComplete_flg为0时不满足休眠条件h2 |
| TC-DT-04 | a46e563d | 9e6be4d2 | REQ-010 | 2 | 正 | PASS | 休眠条件h3决策表(条件全满足) |
| TC-DT-05 | 817b4757 | d15917bd | REQ-011 | 2 | 正 | PASS | h1=1,h2=1,h3=1全满足进入休眠 |
| TC-DT-06 | 2d7a85f0 | d15917bd | REQ-011 | 2 | 负 | PASS | h1=1,h2=1,h3=0不满足休眠 |
| TC-DT-07 | 30931751 | d15917bd | REQ-011 | 2 | 负 | PASS | h1=1,h2=0,h3=1不满足休眠 |
| TC-DT-08 | 3a706d0a | d15917bd | REQ-011 | 2 | 负 | PASS | h1=1,h2=0,h3=0不满足休眠 |
| TC-DT-09 | 0133eb83 | d15917bd | REQ-011 | 2 | 负 | PASS | h1=0,h2=1,h3=1不满足休眠 |
| TC-DT-10 | 2576b370 | d15917bd | REQ-011 | 2 | 负 | PASS | h1=0,h2=1,h3=0不满足休眠 |
| TC-DT-11 | a9ba303d | d15917bd | REQ-011 | 2 | 负 | PASS | h1=0,h2=0,h3=1不满足休眠 |
| TC-DT-12 | be4785f4 | d15917bd | REQ-011 | 2 | 负 | PASS | h1=0,h2=0,h3=0不满足休眠 |
| TC-DT-13 | 02298f93 | 31c9b11d | REQ-013 | 8 | 正 | PASS | 决策表-state11时bus_message_flag为1 |

**ST 状态迁移（白盒，18 条）**

| Test Case ID | UUID(8) | CI ID | REQ | RPN | 极性 | 结果 | 标题 |
|---|---|---|---|---|---|---|---|
| **TC-ST-01** | 778cc8ad | 75158fa6 | **REQ-012** | **1** | 负 | PASS | **连续快速循环触发state10卡死序列（DEF-001）**|
| TC-ST-02 | bcfde974 | 4637dc4b | REQ-001 | 2 | 正 | PASS | 正常唤醒序列_state09_to_state11 |
| TC-ST-03 | 168e5e15 | 327e5c6a | REQ-008 | 2 | 正 | PASS | 状态迁移_唤醒态到休眠态 |
| TC-ST-04 | cfda9952 | be20e236 | REQ-009 | 2 | 正 | PASS | 唤醒状态下AuthComplete_flg置1触发休眠迁移 |
| TC-ST-05 | dba3b73d | 9e6be4d2 | REQ-010 | 2 | 正 | PASS | 状态迁移(唤醒态到休眠态) |
| TC-ST-06 | 4f195107 | d15917bd | REQ-011 | 2 | 正 | PASS | 唤醒态至休眠态迁移 |
| TC-ST-07 | 39a7294c | d15917bd | REQ-011 | 2 | 负 | PASS | 唤醒态维持非休眠态 |
| TC-ST-08 | 744feca2 | — | REQ-003 | 4 | 正 | PASS | 休眠状态下CP信号10.0V迁移至唤醒 |
| TC-ST-09 | e846f095 | — | REQ-003 | 4 | 负 | PASS | 休眠状态下CP信号8.0V维持休眠 |
| TC-ST-10 | 5e0a6a1b | ST-REQ-002 | REQ-002 | 6 | 正 | PASS | 休眠状态接收有效CAN报文迁移至唤醒状态 |
| TC-ST-11 | 1ba60e64 | 1945c7d8 | REQ-004 | 6 | 正 | PASS | CC信号触发休眠到唤醒状态迁移 |
| TC-ST-12 | a91942fd | 1945c7d8 | REQ-004 | 6 | 负 | PASS | CC信号不满足条件维持休眠状态 |
| TC-ST-13 | 4b96b9f5 | ST-REQ-005 | REQ-005 | 6 | 正 | PASS | 休眠状态接收有效CC2信号迁移至唤醒 |
| TC-ST-14 | 1090b464 | ST-REQ-005 | REQ-005 | 6 | 负 | PASS | 休眠状态接收无效CC2信号维持休眠 |
| TC-ST-15 | 497f7cd0 | 67935ead | REQ-007 | 6 | 正 | PASS | 休眠状态接收有效门板信号迁移至唤醒状态 |
| TC-ST-16 | 6e248f61 | 67935ead | REQ-007 | 6 | 负 | PASS | 休眠状态接收无效门板信号维持休眠状态 |
| TC-ST-17 | 163b2ca6 | 9c2f51bd | REQ-013 | 8 | 正 | PASS | 状态转换-转换至state11时bus_message_flag更新 |
| TC-ST-18 | d8faf85f | N/A | REQ-006 | 9 | 正 | PASS | 状态迁移：休眠态到唤醒态迁移验证 |

**SC 场景（5 条，全部 REQ-012 卡死缺陷）**

| Test Case ID | UUID(8) | CI ID | REQ | RPN | 极性 | 结果 | 标题 |
|---|---|---|---|---|---|---|---|
| TC-SC-01 | b696660e | 9c11892b | REQ-012 | 1 | 正 | PASS | 边界测试：2次快速循环不触发卡死 |
| **TC-SC-02** | 0cfe2431 | 9c11892b | **REQ-012** | **1** | 负 | PASS | **3次快速循环触发卡死及DTC上报（DEF-001）**|
| **TC-SC-03** | a4c9c942 | 9c11892b | **REQ-012** | **1** | 负 | PASS | **4次快速循环触发卡死（DEF-001）**|
| TC-SC-04 | 6448e10b | 9c11892b | REQ-012 | 1 | 正 | PASS | 3次循环但间隔等于1.0s不触发卡死 |
| TC-SC-05 | c315d930 | 9c11892b | REQ-012 | 1 | 正 | PASS | 3次循环但间隔大于1.0s不触发卡死 |

> 全量 96 行（含完整 36 位 UUID）见 `10_traceability_matrix.csv`。最高风险 REQ-012（RPN=1）由 6 条用例（TC-ST-01 + TC-SC-01~05）追溯，其中 TC-ST-01 / TC-SC-02 / TC-SC-03 复现 DEF-001。

### 8.2 覆盖完备性（双向核对）

- **需求 → 用例**：14/14 需求每条 ≥3 条用例（最少 REQ-013 4 条、最多 REQ-001/006/011 各 10 条），**无孤儿需求**。
- **覆盖项 → 用例**：22/22 Coverage Item 全部被覆盖（映射方法与追溯字段卫生披露见 §11.2）。
- **用例 → 结果**：96/96 全部 PASS，每条经 UUID join 到 `execution_details.json` 的真实 VCU 输出。
- **极性分布**：47 负向 / 49 正向（负向 PASS = VCU 正确报错/拒绝/卡死，语义见 §10.2）。

> **追溯字段卫生小缺口（诚实披露）**：CSV 中 16 行的 `Coverage Item ID` 为占位串（如 `EP-REQ-002` / `N/A` / 空），系 v3 重生成时 UUID 链丢失所致；这些行仍可经 `(REQ + 技术)` 映射回 canonical CI，**不影响 22/22 覆盖结论**，已列为流程改进项（§13.3）。

---

## 9. Test Tool Implementation（§9）

- **框架**：pytest 9.0.3 + pytest-html + coverage.py 7.14（`--branch`）。
- **执行套件**：`tests/test_suite_from_design.py` —— **数据驱动**，每个 pytest 参数 == 一条设计用例（id=`UUID|REQ|RPN|title`），适配器 `_run` 把设计 in_data 翻译成 `VCUSimulator.simulate()` 调用；IEEE 829 生命周期（setup/驱动/断言/teardown）；按 RPN 升序执行。
- **工具执行接线**（TOOL-FIX-008）：前端「执行全部」→ `/api/execute` → `pytest_runner.py` subprocess 跑真实 pytest → 解析 JUnit XML 按 case UUID 回映射 → 前端 Results 显示真实通过率。
- **命令**：
  ```
  python -m pytest tests/test_suite_from_design.py --html=design_suite_report.html --junitxml=design_suite.xml
  coverage run --branch -m pytest tests/test_suite_from_design.py && coverage report --include="*/vcu_simulator/simulator.py"
  ```

---

## 10. Test Execution Results（§10）

执行命令 `python -m pytest tests/test_suite_from_design.py`，实测 **96 passed in 12.53s**；执行明细（每条 input/expected/VCU actual_output/mismatches）落 `execution_details.json`。

### 10.1 通过率（按测试技术）
| 技术 | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| EP（等价类）| 27 | 27 | 0 | 100% |
| BVA（边界值）| 33 | 33 | 0 | 100% |
| DT（决策表）| 13 | 13 | 0 | 100% |
| ST（状态迁移，白盒）| 18 | 18 | 0 | 100% |
| SC（场景）| 5 | 5 | 0 | 100% |
| **合计** | **96** | **96** | **0** | **100%** |

集成测试 `test_integration_http.py` 另 **11/11 通过**（API 端到端，0.60s）。

### 10.2 正向 / 负向构成（关键：通过 ≠ 仿真器全 success）
| 类别 | 数量 | 含义 | 通过即代表 |
|---|---|---|---|
| **正向** | **49** | 期望成功唤醒（state11）或休眠（state9）| VCU 在合法输入下正确进入目标态 |
| **负向** | **47** | 期望报错/拒绝/维持/卡死（46 error + 1 卡死）| VCU 在非法/边界/缺陷输入下**正确报错或暴露缺陷** |

**分析**：负向占 49%，目的正是"找出 VCU 报错/卡死之处"。它们 PASS 的语义 = VCU 按预期报错/卡死，**而非返回 success**。例如 REQ-012 卡死用例 PASS = 成功复现缺陷；CP=8V 负向用例 PASS = VCU 正确拒绝唤醒并维持 state09。本轮无遗留失败（所有 oracle 缺陷已在执行期审查修正，见 §10.4）。

### 10.3 缺陷分析 DEF-001（核心证据：通过测试发现并复现的真实工程缺陷）

按课件 `Chap5 Anatomy of a Perfect Bug Report` 三阶段法整理。

**Phase 1 — Investigation（双维度边界隔离）**：用 REQ-012 的 6 条用例（1 ST + 5 SC）做隔离，每条都有真实 VCU 输出：

| 用例 | cycles | interval | 触发卡死 | VCU 实际 vehicle_state / duration |
|---|---|---|---|---|
| SC | 2 | 0.9s | ❌ | state11 / 14.7s |
| SC | 3 | 0.9s | ✅ | **state10 / 41s + DTC_001** |
| SC | 4 | 0.9s | ✅ | **state10 / 41s + DTC_001** |
| ST | 3 | 0.5s | ✅ | **state10 / 41s + DTC_001** |
| SC | 3 | **1.0s（边界）** | ❌ | state11 / 14.7s |
| SC | 3 | 1.1s | ❌ | state11 / 14.7s |

→ **隔离结论**：当且仅当 **循环次数 ≥ 3 且相邻间隔 < 1.0s** 触发。两边界都被钉死：次数 2 不触发 / 3 触发（阈值=`rapid_cycle_threshold=3`）；间隔 0.9s 触发 / **1.0s 恰不触发** / 1.1s 不触发（阈值=`rapid_cycle_interval_s=1.0`，判定为"间隔≥1s 即重置计数"）。

**Phase 2 — Synthesis**：`_handle_wake()` 在累计 ≥3 次快速循环后把状态置 `STATE_INIT`(state10) 而非 `STATE_RUN`(state11)，上报 DTC_001、置 power_alarm=1、耗时拉到 41s，且在 Module A 内为**吸收态**（只能 reset 恢复）。整车影响：频繁开关门/CAN 抖动即可让 VCU 卡死无法唤醒，现场需断电复位。

**Phase 3 — Polish（结构化缺陷报告）**：
```
Identifier:  DEF-001   Severity: Critical   Priority: P0   Status: Reproduced/Confirmed
Title:       连续≥3 次快速(间隔<1s)唤醒-休眠循环后 VCU 卡死于 state10 无法唤醒
Source:      REQ-012（客户文档已知缺陷）；对应状态迁移 T5：state09→[Wake,rapid≥3]→state10
Expected（理想设计）: 第 4 次唤醒正常成功 vehicle_state=11, dur≈14.7s, 无 DTC
Actual（实测复现）:   vehicle_state=10, result_type=error, active_dtcs=['DTC_001'],
                     actual_duration=41.0s (=stuck_est_time×2+1 >40), power_alarm_flag=1
Root Cause:  vcu_simulator/simulator.py L164-176（_handle_wake 命中 rapid≥3 → STATE_INIT）
             + L198-200（_handle_sleep 仅当间隔≥1s 才重置计数 → 快速循环下累加至 3）
Recommended: 命中快速循环应进入可自恢复的退避/限流，而非吸收态 state10；或提供超时自动恢复
```
RPN=1（最高优先级）正因其触发门槛低、影响整车可用性。该缺陷由设计用例（REQ-012）稳定复现，是本 Artifact"发现真实缺陷"的核心证据。

### 10.4 执行纠正链（跑完之后、基于结果的质量改进）
把 96 条做成数据驱动 pytest 执行后，暴露了设计期审查抓不到的偏差。每一步都定位根因，不盲目改 oracle 凑绿：

| 阶段 | 通过率 | 根因 / 动作 |
|---|---|---|
| 首次执行 | **48/96 (50%)** | 48 条 LLM oracle 系统性取值错误（vehicle_state=0 幻觉、维持态写 10、no-wake 写 expected、卡死写 stuck）|
| TOOL-FIX-007（prompt 取值语义）| **80/99 (81%)** | 根因在 prompt（工具）→ 追加"VCU 输出取值语义"重生成，一次根治 ~30 条 |
| 适配器修复（休眠先唤醒前置）| **92/99 (93%)** | 诊断出 13 条是**测试脚本 harness bug**（休眠测试需先唤醒到 state11 再施加条件），非设计缺陷 |
| REV-016（执行期人工审查）| **96/96 (100%)** | 改 3（REQ-010 输入矛盾、REQ-014 时序违规改走卡死路径）+ 删 4（REQ-013 输出当输入×2、REQ-001 卡死重复、REQ-014 type2 无触发）+ 加 1（8.9V invalid-low）|

**关键认知（诚实区分三类失败）**：① 工具/prompt 缺陷 → **改 prompt（一次顶 48 次手工补丁）**；② 测试脚本 harness bug → 改 adapter，**不误判为设计缺陷去改 oracle**；③ 真畸形设计用例 → 改/删。这三类绝不混为一谈。

### 10.5 FR 7.0 测试套件优化（96 vs 65 对比，展示工具功能点）

AutoTestDesign 的 Optimize 页提供两项**纯算法**（非 LLM）优化：

**① 风险优先级排序（Prioritize）**：全部 96 条按 RPN 升序排列（RPN=1 风险最高最先执行）。RPN 分带：RPN1=6 条 / RPN2=34 / RPN4=7 / RPN6=35 / RPN8=4 / RPN9=10。与 pytest 套件执行顺序一致（REQ-012 卡死最先跑）。

**② 覆盖最小化（Minimize，贪心 set-cover）**：覆盖单元 = 需求×技术×正负向（= Coverage Item × polarity）：

| 指标 | 全量 96 | 最小化 65 | |
|---|---|---|---|
| 用例数 | 96 | **65** | **-32.3%** |
| 覆盖单元保持 | 65/65 | 65/65 | **100% 不降** |
| 需求 / 需求×技术 | 14 / 39 | 14 / 39 | 全保留 |
| 执行耗时 | 12.56s | **5.62s** | **-55%** |
| 通过率 | 96/96 | **65/65** | DEF-001 仍复现 |
| 纯 Module A 分支覆盖 | 89.0% | ~86.6% | -2.4pp |

**最小化有效性分析（在 VCU 上实跑验证）**：最小化后 65 条全过、需求/CI/缺陷检出全保留、耗时省 55%——**有效**。代价透明：精确 diff 出损失 2 条分支弧（L199 快速循环计数复位、L239 电压达标但时序不足），因为 (需求×技术×正负向) 准则比分支级粗，会合并同一覆盖单元内的"边界细分变体"。**建议用法**：最小化套件用于回归冒烟 / CI 快速门禁；完整验收仍跑全 96 条。

---

## 11. Coverage Analysis（§11）

本节从三个层次度量覆盖：**需求覆盖（Requirement）→ 覆盖项覆盖（Coverage Item）→ 代码覆盖（Branch）**，并补充白盒**状态迁移覆盖（All-States / All-Transitions）**。所有数字由脚本从 `09_test_cases_reviewed.json`、`execution_details.json`、coverage.py 的 `coverage.json` 重算。

### 11.1 Requirement Coverage（需求覆盖）

按风险（RPN）升序列出全部 14 条 Module A 需求的用例分布与执行结果（RPN 越小风险越高、越先测）：

| REQ | RPN | 用例数 | Passed | 覆盖技术 | 风险等级 |
|---|---|---|---|---|---|
| REQ-012（卡死缺陷）| 1 | 6 | 6 | SC, ST | High |
| REQ-001（供电唤醒）| 2 | 10 | 10 | EP, BVA, ST | High |
| REQ-008（休眠 h1）| 2 | 5 | 5 | EP, DT, ST | High |
| REQ-009（休眠 h2）| 2 | 3 | 3 | EP, DT, ST | High |
| REQ-010（休眠 h3）| 2 | 6 | 6 | EP, DT, ST | High |
| REQ-011（h1∧h2∧h3）| 2 | 10 | 10 | EP, BVA, DT, ST | High |
| REQ-003（CP 唤醒）| 4 | 7 | 7 | EP, BVA, ST | High |
| REQ-002（CAN 唤醒）| 6 | 8 | 8 | EP, BVA, ST | Medium |
| REQ-004（CC 唤醒）| 6 | 7 | 7 | EP, BVA, ST | Medium |
| REQ-005（CC2 唤醒）| 6 | 7 | 7 | EP, BVA, ST | Medium |
| REQ-007（门板唤醒）| 6 | 8 | 8 | EP, BVA, ST | Medium |
| REQ-014（时序合规）| 6 | 5 | 5 | BVA | Medium |
| REQ-013（输出一致性）| 8 | 4 | 4 | EP, DT, ST | Medium |
| REQ-006（口盖唤醒）| 9 | 10 | 10 | EP, BVA, ST | Medium |
| **合计** | — | **96** | **96** | — | **14/14** |

**分析**：① 14/14 需求 100% 覆盖、96/96 PASS，无遗漏需求；② 用例数与风险**正相关**——RPN≤2 的 6 条 High 需求（REQ-001/008/009/010/011/012）合计 40 条用例（占 42%），资源向高风险倾斜，符合 risk-based testing；③ 每条需求至少由 1 种黑盒技术覆盖，状态机相关需求（REQ-001~012）额外有白盒 ST 覆盖；④ 风险门槛达成：RPN≤5（High）**47/47=100%**、RPN 6~10（Medium）**49/49=100%**，满足 PROJECT_PLAN §STP-6.3 的"High 风险需求 100% 必过"。

### 11.2 Coverage Item Coverage（覆盖项覆盖）

22 条 canonical Coverage Item（§4），按 `(需求 + 技术)` 映射到覆盖它的用例数（同一 (req,技术) 的多个 CI 由该组用例共同覆盖）：

| # | REQ | 技术 | 覆盖用例数 | Coverage Item | Status |
|---|---|---|---|---|---|
| 1 | REQ-001 | BVA | 4 | 硬线供电唤醒边界值 | ✅ |
| 2 | REQ-001 | EP | 5 | vehicle_state oracle 一致性 | ✅ |
| 3 | REQ-001 | EP | 5 | pdcu_wake_reason 来源编码 oracle | ✅ |
| 4 | REQ-001 | EP | 5 | VCU v1.0 SIL 环境基线 | ✅ |
| 5 | REQ-001 | ST | 1 | 正常唤醒序列 state09→state11 | ✅ |
| 6 | REQ-002 | BVA | 4 | CAN 报文 ID 边界 | ✅ |
| 7 | REQ-003 | BVA | 3 | CP 信号电压边界 | ✅ |
| 8 | REQ-004 | BVA | 3 | CC 信号电压边界 | ✅ |
| 9 | REQ-005 | BVA | 3 | CC2 信号电压边界 | ✅ |
| 10 | REQ-006 | BVA | 6 | 口盖电压+时间边界 | ✅ |
| 11 | REQ-007 | BVA | 3 | 门板电压+时间边界 | ✅ |
| 12 | REQ-008 | EP | 2 | 休眠 h1 等价类 | ✅ |
| 13 | REQ-009 | EP | 1 | 休眠 h2 等价类 | ✅ |
| 14 | REQ-010 | EP | 2 | 休眠 h3 CAN 空闲 | ✅ |
| 15 | REQ-011 | DT | 8 | 三条件组合判定表 | ✅ |
| 16-18 | REQ-012 | SC | 5 | 卡死场景 / DTC_001 / 卡死序列（3 条 CI）| ✅ |
| 19 | REQ-013 | DT | 1 | bus_message_flag↔vehicle_state | ✅ |
| 20 | REQ-013 | ST | 1 | 电源状态↔总线标志位迁移 | ✅ |
| 21-22 | REQ-014 | BVA | 5 | 响应时序合规 / actual_duration 边界（2 条 CI）| ✅ |

**Coverage Item Coverage = 22/22 = 100%**，技术覆盖 EP/BVA/DT/ST/SC 五种齐全（黑盒 4 + 白盒 1）。

**分析与诚实披露（追溯链小缺口）**：22 条 CI 中 21 条可由用例 `coverage_item_id`（UUID）直接 join；其余 1 条（#19 区的 REQ-012「active_dtcs 含 DTC_001」）在 v3 重生成时丢失 UUID 链，但功能上仍被 REQ-012 的 6 条卡死用例覆盖（每条都断言 `active_dtcs contains DTC_001`），故按 (req+技术) 映射仍为已覆盖；另有 16 条 v3 重生成用例 `coverage_item_id` 为占位串。**此为追溯字段卫生问题，不影响覆盖结论（22/22 成立）**，已列为流程改进项。

### 11.3 Branch Coverage（白盒代码覆盖，被测代码 `vcu_simulator/simulator.py`）

**工具**：coverage.py 7.14（`--branch`）。**测试来源**：`tests/test_suite_from_design.py`（96 条进程内驱动 `VCUSimulator`）。

| 指标 | 纯 Module A 逻辑 | 退出准则（Chap5 Master Test Plan）| 结果 |
|---|---|---|---|
| **语句覆盖** | **95.8%**（160/167）| ≥ 80% | ✅ 远超 +15.8pp |
| **分支覆盖** | **89.0%**（73/82）| ≥ 70% | ✅ 远超 +19.0pp |

**度量方法（可复现、透明）**：`simulator.py` 是 Module A/B/C/D/E **共享文件**，文件级原始覆盖率为语句 76.6%(180/226) / 分支 70.4%(76/108)。因本 Artifact **只测 Module A**，需把非-Module-A 代码从分母剔除后再算。剔除明细：

| 被剔除部分 | 所属 | 理由 |
|---|---|---|
| `_handle_guard_rejection`（过压→fault+DTC_002 / 欠压→undervoltage_shutdown+DTC_003）| Module B | REQ-015/016，非 Module A |
| `can_error_count` 注入（L40）| Module C | CAN 错误 REQ-019 |
| `reset(clear_dtc=True)` 清码（L99）| Module D | DTC 清除 REQ-022 |
| `get_state/get_config/update_config/get_performance/_deep_update` | 基础设施/API | 查询配置接口，非测试目标（用例直接调 `simulate()`）|
| `simulate_sleep / simulate_batch` | 旧接口 | legacy 包装，数据驱动用例不走 |
| `_normalize_legacy_payload`（L372-389）| 旧接口 | 旧 signal_name 兼容，新用例用 kwargs 不触发 |

剔除 59 条非-A 语句 + 26 条非-A 分支后，**纯 Module A 决策逻辑** = 95.8% / 89.0%。

**Module A 内仍未覆盖的 7 行分析**（L155, 202, 273, 304, 330, 333, 358）：
- **L155**：处于 fault/undervoltage 时拒绝唤醒——需先经 Module B 进入故障态，跨模块，本范围不构造；
- **L202**：休眠时功耗不达标置 power_alarm——Module E 功耗告警分支；
- **L273**：无任何有效唤醒信号的 fallthrough——**已在 §12 基于覆盖证据新增用例补上**（→ 纯 Module A 升至 96.4%/90.2%）；
- **L304/330/333/358**：`test_status` 次要赋值、fault/undervoltage 的 state 映射（Module B 联动）、stuck 电流次要分支——均为边界/相邻模块联动，不影响 Module A 主决策路径（7 路唤醒 + 3 条件休眠 + 卡死 + 输出一致性）的覆盖。

**结论**：Module A 主决策逻辑覆盖充分（语句 95.8%、分支 89.0%，均远超退出准则）；未覆盖的 6~7 行集中在"相邻模块联动 / 次要赋值"，属可接受残余风险，已在 §13 记录。证据：`coverage.json`（精确指标）、`coverage_html/`（逐行高亮）、`coverage_report.txt`。

### 11.4 State Transition Coverage（白盒 FR 4.0：状态迁移覆盖）

Module A 状态机三态：**state09(休眠，初始) / state11(唤醒) / state10(卡死，吸收态)**。按课件 Chp4TestTechPart2 p26 构造**完整状态转换表**（四字段 + 不可能组合标 Undefined），3 状态 × 5 事件 = 15 行，节选定义迁移：

| Current State | Event/cond | Action | New State |
|---|---|---|---|
| state09 | Wake[有效, rapid<3] | 唤醒成功 reason1-7 | **state11** |
| state09 | Wake[有效, **rapid≥3**] | DTC_001 卡死, dur=41s | **state10** |
| state09 | Wake[无效] | 保持休眠, error | state09 |
| state11 | Sleep[h1∧h2∧h3] | 进入休眠 | **state09** |
| state11 | Sleep[不全] | 保持唤醒(ne 9), error | state11 |
| state11 | Wake[有效, rapid≥3] | **Undefined**（不可达：卡死迁移只能从 state09 触发）| Undefined |
| state10 | 任意事件 | **Undefined**（吸收态，需 reset 恢复=Module D 越界）| Undefined |

**设计迁移 T1~T5 ↔ ST 用例映射（All-Transitions / 0-switch）**：

| Transition | From → To | 触发 | ST 用例数 |
|---|---|---|---|
| T1 | state09 → state11 | Wake[有效] w1~w7 | 8（REQ-001~007 + REQ-013）|
| T2 | state09 → state09 | Wake[无效] | 4（REQ-003/004/005/007 负向）|
| T3 | state11 → state09 | Sleep[h1∧h2∧h3] | 4（REQ-008~011）|
| T4 | state11 → state11 | Sleep[不全] | 1（REQ-011 负向）|
| T5 | **state09 → state10** | Wake[rapid≥3] | 1（REQ-012）|

**覆盖结论**：
- **All-States = 3/3 = 100%**（state09/10/11 均被访问）；
- **All-Transitions（0-switch）= T1~T5 全覆盖 = 100%**（18 条 ST 用例全 PASS）；
- REQ-012 卡死序列 `state09→11→09→11→09→11→09→10` 额外提供 **1-switch 序列覆盖**（课件 N-1 Switch）。

**表格强制发现的洞见**：枚举到 `state11 × Wake[rapid≥3]` 时发现其**不可达**——卡死迁移 T5 只能从 state09 触发（计数累积在休眠侧），从而精确定位了 DEF-001 的触发源态。这正是状态转换表"强制考虑易遗漏组合"的价值。

---

## 12. Evidence-based Improvement（§12：执行后、基于证据新增的有效用例）

> **范围界定（重要）**：Assignment「Mainly」清单中 **#7 基于证据的改进**排在 **#6 结果分析**之后，特指**用例真正跑完、拿到执行/覆盖证据之后新增的有效用例**。因此本节**只**收录第一轮执行后的有效新增（两类来源）；设计期改进（CI 14→22、prompt 迭代、21→0 臆造字段，见 §4/§6）与执行纠正链（48→96，见 §10.4）按时序归各自板块，不计入本节。

### 12.1 来源 A — 第二轮 LLM 用例增广（`/api/improve` + 人工评审）

第一轮 96/96 跑完后，把全部用例喂给 LLM（improve prompt，qwen3.7-max，67s）得 **8 条**增广建议，再**人工对照 `simulator.py` 真实行为逐条核** → **8 进 3（采纳率 37.5%）**：

| # | REQ | 建议 | 人工评审结论 |
|---|---|---|---|
| 3 | REQ-011 | 休眠条件全满足 + 同时来唤醒 | ✅ 采纳，**改 oracle**：LLM 写 state11，实际 `simulate()` 先判 `_has_sleep_inputs`→**休眠优先 state9** |
| 5 | REQ-004 | CC 与 CC2 同时满足唤醒 | ✅ 采纳，**改 oracle**：LLM 写 `reason in[4,5,6]`（操作符不支持），实际 CC 先于 CC2 判定→**reason 4** |
| 8 | REQ-006 | 口盖超长时序 5000ms | ✅ 采纳（原样，LLM oracle 正确）|
| 1 | REQ-001 | 电压跌落致防抖重置 | ❌ 拒：SUT 未建模防抖重置，无法送 voltage_profile |
| 2 | REQ-002 | CAN Bus-Off 下唤醒 | ❌ 拒：越界 Module C + 臆造 `DTC_CAN_BUS_OFF` |
| 4 | REQ-012 | state10 卡死后唤醒屏蔽 | ❌ 弃：与 DEF-001 重叠、setup 复杂 |
| 6 | REQ-014 | NM 报文刷新休眠计时器 | ❌ 拒：SUT 无 NM keep-awake 机制 |
| 7 | REQ-009 | 认证超时降级 | ❌ 拒：臆造 state12 + `DTC_AUTH_TIMEOUT` |

**评审价值（体现 designer interactive validation）**：5 条因"SUT 未建模 / 越界 Module C / 臆造 DTC 与状态"被拒；2 条 oracle 被人工纠正——充分说明 **LLM 增广不能全信，必须人工 + 领域知识把关**。

**3 条采纳用例在 VCU 上重跑（3/3 通过，VCU 行为印证人工修正的 oracle）**：

| 用例 | 输入 | VCU 实际输出 | 通过 | 验证的新行为 |
|---|---|---|---|---|
| REQ-011/SC | h1=h2=h3=1, voltage=12 | vehicle_state=**9**, reason=0, expected | ✅ | **休眠优先于唤醒**（并发）|
| REQ-004/SC | cc=2.0, cc2=2.0 | vehicle_state=11, pdcu_wake_reason=**4**, expected | ✅ | **CC 优先于 CC2** |
| REQ-006/BVA | hood=4.1, dur=5000 | vehicle_state=11, reason=6, expected | ✅ | 超长时序无溢出 |

实测与**人工修正后**的 oracle 完全一致（state9 / reason4 / reason6），反证 LLM 原 oracle 是错的。**有效性诚实披露**：新增 3 条**组合/优先级**条件，但**分支覆盖 +0**（76.65%→76.65%）——优先级是"判定顺序"行为，走已覆盖代码路径，分支覆盖对其不敏感。

### 12.2 来源 B — 覆盖缺口驱动（可量化提升覆盖）

依据 §11.3 覆盖分析证据（simulator.py **L273 未覆盖**：`_detect_wake_reason` 末尾 `return 0, ""`，即"无任何有效唤醒信号"的 fallthrough），针对性新增 1 条用例：**「无唤醒信号 → 维持 state9，result_type=error」**（属 7 路唤醒需求的负向等价类，第一轮 96 条按单信号设计而遗漏）。重跑结果：

| 指标 | 96 基线 | 96+新增 | Δ |
|---|---|---|---|
| 新覆盖行 | — | **恰为 L273**（脚本 diff 确认）| — |
| 纯 Module A 语句覆盖 | 95.8% | **96.4%** | +1 行 |
| 纯 Module A 分支覆盖 | 89.0% | **90.2%** | +1 弧 |

### 12.3 结论
§12 收录 **2 类来源、4 条执行后新增有效用例（4/4 通过）**：① **LLM 增广**（3 条）采纳率 37.5%，新增组合/优先级用例 + 人工拦下 5 条越界/臆造、修正 2 条错误 oracle，分支覆盖 +0；② **覆盖缺口驱动**（1 条 L273）可量化把纯 Module A 分支覆盖 **89.0%→90.2%**。
**核心认知**：分支覆盖必要但不充分——组合/优先级盲区靠 LLM 增广提示（需人工把关），代码路径盲区靠覆盖分析定位；两类证据互补才构成完整的"基于证据的改进"。这也直接回答了"LLM 增广是否有效"：在分支覆盖上 LLM 那 3 条无提升，真正可量化的提升来自覆盖分析驱动的第 4 条。

---

## 13. Limitations / Residual Risks + NFR

### 13.1 NFR 性能度量（被测对象 = AutoTestDesign 工具自身）

度量来源：工具 `/api/performance`（72 条 LLM 调用计时，model=qwen3.7-max）。规格出自 Project Requirement Specification §4.1。

| NFR | 规格 | 实测（脚本聚合）| 满足 |
|---|---|---|---|
| **NFR 4.1.1** 分析时间 | 100 条需求解析+风险 ≤ **5s** | `risk.analyze` 14 条/批 **75.4s**（折合 ~540s/100 条）| ❌ 超标 ~100× |
| **NFR 4.1.2** 用例生成 | 单需求生成完整用例集 ≤ **2s** | `testcase.generate`（n=32）min **35.0** / mean **75.4** / max **124.6** s | ❌ 超标 ~37× |
| NFR 4.2.1 Interface | 干净直观 UI | AutoTestDesign V2 七标签页 | ✅ |
| NFR 4.2.2 Traceability | 用例↔REQ↔技术 | 追溯矩阵 96 行 | ✅ |
| NFR 4.4.1/4.4.2 Stack/Modularity | 现代开源栈 + 松耦合 | FastAPI+React，service 分层 | ✅ |

**根因分析**：唯一根因 = 云端推理型 LLM（qwen3.7-max 开 reasoning）单次 JSON 生成往返 35~125s，与 2s/5s（默认快速/本地生成）在数量级上不匹配。与功能正确性无关——工具功能均正确，仅**响应时延**不达标。

**改进建议（按 Assignment §5「不可隐瞒、需给改进」）**：① 关闭 reasoning（`LLM_ENABLE_THINKING=false`，已部分缓解）；② 换本地/小模型做结构化生成；③ 相同 prompt 结果缓存；④ 14 条需求并发生成（当前串行，墙钟从 Σ 降到 max）；⑤ 流式输出 + 非交互场景离线预生成。

> **与"被测系统时序"的区分**：本节 NFR 是 **AutoTestDesign 工具**的响应时延；被测 **VCU 仿真器**自身时序（REQ-014：type1≈14.7s≤20s ✓、卡死 41s）是 **SUT 的建模行为**，属 §10/DEF-001，二者不可混为一谈。

 
### 13.2 SUT 限制与残余风险
- **SUT 限制**：SIL 级仿真，无真实 HIL/dSPACE/CAN 物理层/1kHz 采样；本 Artifact **仅测 Module A**，Module B/C/D/E（过压/欠压保护、CAN 错误、DTC 清除、功耗告警）越界（见 §1.3）。
- **残余覆盖风险**：Module A 仍有 6 行未覆盖（§11.3：L155/202/304/330/333/358），集中在"相邻模块联动 / 次要赋值"，需进入故障态或跨模块才能触达，属可接受残余风险。
- **追溯链卫生**：16 条 v3 重生成用例 CI 字段为占位串（§11.2），不影响覆盖结论，建议后续在生成阶段强制 CI UUID 回填。

---

## Appendix A — 证据文件索引（`docs/test_evidence/`）

| 类别 | 文件 |
|---|---|
| 需求 | `module_A_requirements_input.csv`、`01_parsed_requirements_raw.json` |
| 覆盖项 | `_state_snapshot/coverage_items.json`、`coverage_tables.md` |
| 风险 | `06_risk_analysis_reviewed.json/.csv` |
| 策略 | `07_strategy_assignment.csv`（+ `_before`）|
| Prompt | `prompts_used.md`、`prompt_testcase_v1/v2/v3*.json` |
| 用例 | `09_test_cases_reviewed.json`（+ 版本链 08/09a/09b）|
| 追溯 | `10_traceability_matrix.csv` |
| 执行 | `pytest_output/`（design_suite.xml/html/txt、execution_details.json、integration_http、coverage*）|
| 缺陷 | `defect_DEF-001_state10_stuck.md` |
| 通过率 | `pass_rate_summary.md` |
| FR5 oracle | `FR5_oracle_evidence.md`、`FR5_oracle_samples.csv` |
| FR7 优化 | `fr7_optimization.md`、`fr7_optimization/*.json` |
| §12 改进 | `improvement_evidence.md`、`improve_round2_*.json` |
| NFR | `nfr_performance.md` |
| 审查记录 | `review_log.md`（REV-001~016 + TOOL-FIX-001~008）|
| 截图 | `screenshots/`（20 张：服务/Swagger/前端/各 REV before-after/风险/prompt）|

---
**End of Artifact 4 Document**
