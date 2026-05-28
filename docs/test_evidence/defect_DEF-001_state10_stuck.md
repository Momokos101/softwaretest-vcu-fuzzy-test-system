# 缺陷报告 DEF-001 — state10 卡死（连续快速唤醒-休眠循环）

> **Artifact 4 §10.3 核心证据：通过 Module A 测试发现并复现的真实工程缺陷。**
> 本报告按课件 `Workshop/Chap5Congfig Anatomy of a Perfect Bug Report.docx`「完美缺陷报告」三阶段方法组织：
> **Phase 1 Investigation（人工主导：Reproduce / Isolate / Generalize / Compare）→ Phase 2 Synthesis（技术摘要 + 影响）→ Phase 3 Polish（结构化字段）**。
> 所有「Actual」数据取自真实执行 `docs/test_evidence/pytest_output/execution_details.json`（REQ-012 6 条），非手填。

---

## Phase 1 — Investigation（人工主导）

> 用 REQ-012 的 6 条用例（1 条 ST + 5 条 SC 边界）做双维度隔离。每条都有真实 VCU 输出。

### Reproduce（可复现性）
固定序列：`reset()` → 连续 3 次（间隔 0.5s）`(唤醒→休眠)` → 第 4 次唤醒。
- 用例 `778cc8ad`（ST，cycles=3, interval=0.5s）→ **稳定复现**：`vehicle_state=10, result_type=error, active_dtcs=['DTC_001'], actual_duration=41.0, power_alarm_flag=1`。
- 复现率 **100%**（确定性，无并发/时序抖动依赖）。

### Isolate（隔离触发条件）—— 双维度边界分析
| 用例 | cycles | interval | 是否触发卡死 | VCU 实际 vehicle_state / duration |
|---|---|---|---|---|
| `b696660e` (SC) | 2 | 0.9s | ❌ 不触发 | state11 / 14.7s（正常唤醒）|
| `0cfe2431` (SC) | 3 | 0.9s | ✅ 触发 | **state10 / 41s + DTC_001** |
| `a4c9c942` (SC) | 4 | 0.9s | ✅ 触发 | **state10 / 41s + DTC_001** |
| `778cc8ad` (ST) | 3 | 0.5s | ✅ 触发 | **state10 / 41s + DTC_001** |
| `6448e10b` (SC) | 3 | **1.0s（边界）** | ❌ 不触发 | state11 / 14.7s |
| `c315d930` (SC) | 3 | 1.1s | ❌ 不触发 | state11 / 14.7s |

**隔离结论**：当且仅当 **循环次数 ≥ 3 且相邻循环间隔 < 1.0s** 时触发卡死。两个边界都被钉死：
- **次数边界**：2 不触发 / 3 触发（阈值 = `rapid_cycle_threshold = 3`）。
- **间隔边界**：0.9s 触发 / **1.0s 不触发** / 1.1s 不触发（阈值 = `rapid_cycle_interval_s = 1.0`，判定为 `间隔 ≥ 1.0s 即重置计数`，故 1.0s 恰好不触发）。

### Generalize（普遍性）
触发与「用哪一路唤醒信号」无关——卡死判定在 `_handle_wake` 中，位于 7 路唤醒源检测之后，对供电/CAN/CP/CC/CC2/口盖/门板任一唤醒路径都成立。即任何能把 VCU 唤醒的信号，在快速循环 ≥3 次后都会导致 state10。

### Compare（与正常行为对比）
| | 正常唤醒（无快速循环）| 卡死（快速循环 ≥3）|
|---|---|---|
| vehicle_state | 11（state11）| **10（state10）** |
| result_type | expected | **error** |
| actual_duration | 14.7s（type1 nominal）| **41s（= stuck_est_time×2+1 = 20×2+1）** |
| active_dtcs | [] | **['DTC_001']** |
| power_alarm_flag | 0 | **1** |
| 恢复 | 自动 | **需 `reset()` 才能回 state09，否则永久卡死** |

---

## Phase 2 — Synthesis（技术摘要 + 影响）

**技术摘要**：`simulator.py` 的 `_handle_wake()`（L164-176）在检测到近期累计 ≥3 次「间隔<1s 的快速唤醒-休眠循环」后，把整车状态置为 `STATE_INIT`（state10）而非 `STATE_RUN`（state11），上报 `DTC_001`、置 `power_alarm_flag=1`，并把唤醒耗时拉到 41s（估计时间的 2 倍 +1）。该状态在 Module A 内为**吸收态**，只能靠 `reset()` 恢复。

**整车/客户影响**：用户/网络在短时间内反复触发唤醒-休眠（如频繁开关门、CAN 报文抖动）即可让 VCU 卡死，**整车无法正常唤醒进入工作态**，并伴随诊断码 DTC_001 与功耗告警；现场只能通过断电复位恢复，属影响可用性的高严重度缺陷。

---

## Phase 3 — Polish（结构化缺陷报告）

```
Identifier:   DEF-001  （课件式全编号：VCU-DEF-2026-05-27-001）
Title:        连续 ≥3 次快速(间隔<1s)唤醒-休眠循环后，VCU 卡死于 state10 无法唤醒
Severity:     Critical（整车无法唤醒，需断电复位）
Priority:     P0
Status:       Reproduced / Confirmed（设计已知缺陷，本测试复现确认）
Source:       REQ-012（客户需求文档，已知卡死缺陷）
Module:       Module A（唤醒-休眠状态机）；对应状态迁移 T5：state09 →[Wake,rapid≥3]→ state10
Environment:  vcu_simulator/simulator.py；config: rapid_cycle_threshold=3,
              rapid_cycle_interval_s=1.0s, stuck_est_time=20s
Linked Tests: tests/test_suite_from_design.py 中 REQ-012 的 6 条用例
              （ST×1 卡死序列 + SC×5 双维度边界），全部 PASS = 全部按预期复现/不复现

Description:
  当 VCU 在 <1s 间隔内连续完成 3 次及以上「唤醒→休眠」循环后，下一次唤醒不再进入
  正常工作态 state11，而是卡死于 state10，上报 DTC_001 并触发功耗告警，且无法自动恢复。

Steps to Reproduce（= 适配器 _run 对 REQ-012 的执行序列，tests/test_suite_from_design.py:122-131）:
  1. sim.reset()                                        → VCU 回 state09（休眠）
  2. 循环 3 次（相邻间隔 < 1s，如 0.5s 或 0.9s）：
       sim.simulate(supply_voltage=9.3, duration_ms=15)                                  → 唤醒到 state11
       sim.simulate(VCUO_bDIAG_VCUIdle_flg=1, VCUO_bDIAG_AuthComplete_flg=1, can_stopped=True) → 快速休眠回 state09
  3. 第 4 次 sim.simulate(supply_voltage=9.3, duration_ms=15)                              → 触发卡死

Expected Result（按理想设计应当）:
  第 4 次唤醒正常成功：vehicle_state=11, result_type=expected, actual_duration≈14.7s,
  无 DTC，无功耗告警（快速循环不应使 VCU 永久不可用）。

Actual Result（实测复现，execution_details.json）:
  vehicle_state    = 10        （STATE_INIT / state10 卡死）
  result_type      = "error"
  active_dtcs      = ["DTC_001"]
  actual_duration  = 41.0 s    （= stuck_est_time×2 + 1 = 20×2+1，> 估计时间 2 倍）
  power_alarm_flag = 1
  恢复             = 需 reset()，否则永久卡死

Root Cause（代码定位）:
  vcu_simulator/simulator.py
    - L164-176 _handle_wake(): if len(_rapid_sleep_timestamps) >= rapid_cycle_threshold(3):
                                self.state = STATE_INIT(state10); log DTC_001; power_alarm=1;
                                actual_duration = stuck_est_time*2 + 1
    - L198-200 _handle_sleep(): 仅当相邻休眠间隔 >= rapid_cycle_interval_s(1.0s) 才重置计数，
                                否则持续累加 → 快速循环下计数达 3。

Impact:
  整车无法唤醒进入工作态；现场需断电复位；伴随 DTC_001 与功耗告警。
  触发门槛低（间隔<1s 的 3 次循环即可），属高发可用性风险——故风险分析 RPN=1（最高优先级，最先测）。

Recommended Action（建议，非本次测试范围）:
  在 _handle_wake 命中快速循环时，应进入可自恢复的退避/限流逻辑（而非吸收态 state10），
  或在 reset 之外提供超时自动恢复路径，避免现场断电复位。
```

---

## 证据文件
- `docs/test_evidence/pytest_output/execution_details.json` —— REQ-012 6 条用例逐条 input/expected/**VCU actual_output**/mismatches（Actual 数据来源）。
- `docs/test_evidence/pytest_output/design_suite.txt` / `design_suite.xml` —— pytest 通过记录（6/6 按预期复现/不复现）。
- `docs/test_evidence/09_test_cases_reviewed.json` —— REQ-012 用例设计（technique=ST/SC）。
- `docs/test_evidence/state_transition_table.md` —— 迁移 T5（state09→state10）的状态机定位。
- 复现代码：`tests/test_suite_from_design.py` `_run()` REQ-012 分支（L122-131）。
