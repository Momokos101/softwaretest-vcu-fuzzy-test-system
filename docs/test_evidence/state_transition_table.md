# Module A 状态转换表 + All-States / All-Transitions 覆盖（Step 3.5 — 白盒证据，Artifact 4 §11 / FR 4.0）

> **被测代码（SUT）= Module A 实现 `vcu_simulator/simulator.py`** 的唤醒-休眠-卡死状态机。
> **方法依据**：
> - 课件 `Chp4TestTechPart2 (1).pdf` p18–31：Finite-State Models（p18）、State-Transition Diagram（p19）、Deriving Tests / State-Transition Cover（p20）、**Example: State Transition Table（p26，四字段：Current State | Event/cond | Action | New State）**、Row Cover（p27）、N-1 Switch Cover / 0-switch·1-switch（p29–31）。
> - `Omninet System Requirement_V1.0.pdf` 第 070-050 项「Kiosk State-Transition Table」（字段：State / Event / Condition / Next State / Action）的工程实例结构。
> - `Assignment 2` **FR 4.0 White-Box Test Modeling = State Transition Diagram + 覆盖准则**；本 Artifact 4 取覆盖准则 **All-States（必需）**，并额外做到 **All-Transitions（0-switch）**。
> **范围**：只建模 Module A 三态（REQ-001~014）。过压/欠压保护、CAN 错误、DTC 清除等迁移属 **Module B/C/D**，不在本 Artifact 4 范围（见 §6）。

---

## 1. 状态清单（Finite-State Model，课件 p18）

| 状态 | `state_name` | `vehicle_state` | 含义 | 类型 | 代码锚点 |
|---|---|---|---|---|---|
| **S9** | `state09` | 9 | 休眠态（低功耗，bus_message_flag=0）| **初始态**（构造/`reset()` 后）| `simulator.py:32,94,196` |
| **S11** | `state11` | 11 | 唤醒/运行态（bus_message_flag=1，ready）| 正常工作态 | `simulator.py:179` |
| **S10** | `state10` | 10 | 卡死态（DTC_001，actual_duration=41s，power_alarm=1）| **故障吸收态**（缺陷 DEF-001）| `simulator.py:165` |

> 说明：`state10` 在 Module A 范围内是**吸收态**——一旦进入只能靠 `reset()` 恢复，而 `reset()` 含清码逻辑属 Module D，不在本范围内建模。

## 2. 事件/条件字母表（Event/cond alphabet）

| 记号 | 事件/条件 | 判定（代码锚点）|
|---|---|---|
| `Wake[有效, rapid<3]` | 7 路唤醒信号任一**值+时序**满足，且近期快速循环计数 <3 | `_detect_wake_reason` 返回 reason 1~7（`simulator.py:230-273`）+ `_handle_wake` 计数判断（L164）|
| `Wake[有效, rapid≥3]` | 唤醒信号有效，但**连续 ≥3 次快速(间隔<1s)唤醒-休眠循环**已累计 | `len(_rapid_sleep_timestamps) >= rapid_cycle_threshold(3)`（`simulator.py:164`）|
| `Wake[无效]` | 唤醒信号**值或时序不满足**（如 cp=8V≤9V、door 时序不足）| `_detect_wake_reason` 返回 `(0, ...)`（`simulator.py:238-271`）|
| `Sleep[全满足]` | 休眠握手 `h1 ∧ h2 ∧ h3` 同时为真 | `_handle_sleep` 全真分支（`simulator.py:195`）|
| `Sleep[不全]` | `h1/h2/h3` 中至少一个为假 | `_handle_sleep` missing 分支（`simulator.py:214-228`）|

> 其中 h1=`VCUO_bDIAG_VCUIdle_flg`、h2=`VCUO_bDIAG_AuthComplete_flg`、h3=`can_stopped`。

## 3. 状态转换图（State-Transition Diagram，课件 p19 文字版）

```
        Wake[有效,rapid<3] / 唤醒成功(reason1-7),expected,14.7s
        ┌────────────────────────────────────────────────┐
        │                                                  ▼
   ●──▶[S9 state09]                                   [S11 state11]
   初始   ▲   │  ▲                                    │   │   ▲
        │   │  │ Wake[无效]/error (自环)               │   │   │ Wake[有效]/幂等 (自环)
        │   │  └──────────────────────────────────────┘   │   └──(repeat wake)
        │   │   Sleep[不全]/error,状态不变 (自环)            │
        │   │                                              │ Sleep[全满足]/进入休眠
        │   └──────────────────────────────────────────────┘ expected,42s
        │   Sleep[全满足]/维持休眠,计数++ (自环)
        │
        │ Wake[有效,rapid≥3] / DTC_001,卡死,error,41s,alarm=1   ← 缺陷 DEF-001
        ▼
   [S10 state10]  （吸收态：需 reset() 恢复，reset 属 Module D，越界）
```

- `●` = 初始态指示符（课件 p19 Initial state indicator）→ 进入 S9。
- 标注格式 `事件[条件] / 动作`（课件 p19 Event[Condition]/Action）。

## 4. 完整状态转换表（Example: State Transition Table，课件 p26）

> 构造法（p26 原文）：列出所有状态 × 所有事件/条件组合，每行四字段 **Current State | Event/cond | Action | New State**；依状态图填充能到达的行，**其余组合标记 Undefined**。表格的价值正是「强制考虑容易被遗漏的(状态×事件)对」。
> 共 3 状态 × 5 事件 = **15 行**。

| # | Current State | Event/cond | Action | New State |
|---|---|---|---|---|
| 1 | state09 | Wake[有效, rapid<3] | 检测唤醒源(reason 1~7)，Module B 校验通过，唤醒成功；result=expected，dur=14.7s | **state11** |
| 2 | state09 | Wake[有效, rapid≥3] | 检测到连续快速循环，记录 **DTC_001**，power_alarm=1；result=error，**actual_duration=41s(>40)** | **state10** |
| 3 | state09 | Wake[无效] | 不满足任何唤醒条件，保持休眠；result=error | state09 |
| 4 | state09 | Sleep[全满足] | h1∧h2∧h3 满足，维持休眠并追加快速循环时间戳；result=expected，dur=42s | state09 |
| 5 | state09 | Sleep[不全] | 缺少 ≥1 个 h 条件，状态保持不变；result=error | state09 |
| 6 | state11 | Wake[有效, rapid<3] | 已处于唤醒态，幂等再次唤醒；result=expected | state11 |
| 7 | state11 | Wake[有效, rapid≥3] | **Undefined** —— 不可达：rapid≥3 仅能在 state09 经 3 次循环后累计；其下一次唤醒即转入 state10，系统无法在 rapid≥3 的同时停留于 state11 | **Undefined** |
| 8 | state11 | Wake[无效] | 唤醒条件无效；result=error，保持唤醒 | state11 |
| 9 | state11 | Sleep[全满足] | h1∧h2∧h3 满足，进入休眠；result=expected，dur=42s | **state09** |
| 10 | state11 | Sleep[不全] | 缺少 ≥1 个 h；result=error，保持唤醒（vehicle_state ne 9）| state11 |
| 11 | state10 | Wake[有效, rapid<3] | **Undefined** —— 吸收态，需 `reset()` 恢复（Module D，越界）| **Undefined** |
| 12 | state10 | Wake[有效, rapid≥3] | **Undefined**（同上）| **Undefined** |
| 13 | state10 | Wake[无效] | **Undefined**（同上）| **Undefined** |
| 14 | state10 | Sleep[全满足] | **Undefined**（同上）| **Undefined** |
| 15 | state10 | Sleep[不全] | **Undefined**（同上）| **Undefined** |

> **表格强制发现的「遗漏组合」洞见**（课件 p26 的核心价值）：
> - **第 7 行**：列举 `state11 × Wake[rapid≥3]` 时发现它**不可达**——澄清了缺陷 DEF-001 的精确触发路径是 **state09 →(Wake,rapid≥3)→ state10**（卡死迁移源态是 state09，不是 state11；详见 §5 T5）。
> - **第 11~15 行**：state10 对任何事件都 Undefined，证明它是 Module A 内的**吸收态**，恢复依赖越界的 `reset()`。

## 5. 设计迁移 T1~T5 与 ST 用例映射（All-Transitions / 0-switch，课件 p20）

> 起止规则（p20 step1）：测试从初始态 **state09** 出发，止于任一已定义态。
> 下表 5 条为状态图中**已定义且经设计的迁移**（对应 §4 表的第 1/2/3/9/10 行）；自环行 4/6/8 为已定义但属次要（幂等/维持），不单列设计迁移。

| Transition | From → To | Event/cond（§4 行）| Covered By（18 条 ST 用例）| 数量 |
|---|---|---|---|---|
| **T1** | state09 → state11 | Wake[有效,rapid<3]，w1~w7 任一（§4 行1）| REQ-001(供电) / 002(CAN) / 003(CP) / 004(CC) / 005(CC2) / 006(口盖) / 007(门板) 唤醒正向 + REQ-013(进入 state11 输出一致性) | 8 |
| **T2** | state09 → state09 | Wake[无效]（§4 行3，自环）| REQ-003(CP 8V) / 004(CC 6V) / 005(CC2 5V) / 007(门板 2V) 负向 | 4 |
| **T3** | state11 → state09 | Sleep[全满足]（§4 行9）| REQ-008(h1) / 009(h2) / 010(h3) / 011(h1∧h2∧h3) 休眠正向 | 4 |
| **T4** | state11 → state11 | Sleep[不全]（§4 行10，自环）| REQ-011(h1=h2=h3=0，vehicle_state ne 9) 负向 | 1 |
| **T5** | **state09 → state10** | Wake[有效,**rapid≥3**]（§4 行2，缺陷迁移）| REQ-012(连续 3 次 interval<1s 循环后唤醒 → DTC_001) | 1 |
| | | | **合计** | **18** |

> **T5 源态精确性说明**：REQ-012 适配器执行 `(唤醒→休眠)×3` 后，状态停在 **state09** 且快速循环计数=3；随后**第 4 次唤醒**从 state09 触发卡死（`simulator.py:164-176`，此时 `self.state == STATE_SLEEP`）。故 T5 的迁移源态是 **state09**（与 §4 第 7 行的不可达性分析一致）。

## 6. 覆盖结论

### 6.1 All-States（FR 4.0 必需准则）
| 状态 | 是否被访问 | 证据 |
|---|---|---|
| state09 | ✅ | 初始态 + T1/T2 源态、T3 目标态 |
| state11 | ✅ | T1 目标态 + T3/T4 源态 |
| state10 | ✅ | T5 目标态（REQ-012 卡死复现）|

**All-States 覆盖率 = 3/3 = 100%** ✅

### 6.2 All-Transitions（0-switch，超出必需准则的加强）
设计迁移 T1~T5 每条均有 ≥1 条 Module A 用例覆盖：**5/5 = 100%** ✅

### 6.3 N-1 Switch / 1-switch 加强（课件 p29–31）
REQ-012（778cc8ad）执行的是一条**迁移序列**而非单次迁移：

```
state09 →T1→ state11 →T3→ state09 →T1→ state11 →T3→ state09 →T1→ state11 →T3→ state09 →T5→ state10
```

该序列把迁移对 **[T1;T3]（唤醒→休眠往返）** 连续遍历 3 次，并最终触达 **[T3-上下文; T5]** 卡死对，**提供了关键迁移对的 1-switch 覆盖**，超出 0-switch 单迁移覆盖，对应课件 p29–31 的 N-1 Switch Coverage。

## 7. 越界声明（不纳入 Module A 状态图与覆盖）

| 越界迁移 | 所属模块 | 触发 | 理由 |
|---|---|---|---|
| → fault_protection（过压 >16V，DTC_002）| Module B | `_handle_guard_rejection` overvoltage（`simulator.py:132-136`）| REQ-015/016，非 Module A |
| → undervoltage_shutdown（欠压 <6V，DTC_003）| Module B | `_handle_guard_rejection` undervoltage（`simulator.py:137-140`）| REQ-015/016，非 Module A |
| bus_off（CAN 错误注入）| Module C | `can_manager.report_error`（`simulator.py:39-40`）| REQ-019，非 Module A |
| state10/fault → 恢复（reset 清码）| Module D | `reset(clear_dtc=True)`（`simulator.py:93-99`）| REQ-022，非 Module A |

## 8. 证据文件
- 本表 `state_transition_table.md`（状态图 + 完整转换表 + 迁移映射 + 覆盖结论）。
- ST 用例原始定义：`docs/test_evidence/09_test_cases_reviewed.json`（technique=="ST" 的 18 条）。
- 执行结果：`docs/test_evidence/pytest_output/execution_details.json`（每条 ST 用例的 VCU 实际输出 + oracle 比对）。
- 可执行实现：`tests/test_suite_from_design.py::TestSuiteST_StateTransition`。
