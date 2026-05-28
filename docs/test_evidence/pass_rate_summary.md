# 通过率汇总（Step 4.1 — Artifact 4 §10.1 / §10.2）

> **范围**：只统计 Module A（REQ-001~014）的 96 条 reviewed 设计用例。
> **数据来源**：`docs/test_evidence/pytest_output/execution_details.json`（每条用例 VCU 实际输出 + oracle 比对）与 `design_suite.xml`（JUnit）。
> **执行命令**：`python -m pytest tests/test_suite_from_design.py`（实测 **96 passed in 12.53s**）。
> 本表所有数字均由脚本从执行结果重算，非手填。

---

## 1. 按测试技术（§10.1）

| 技术 | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| EP（等价类）| 27 | 27 | 0 | 100% |
| BVA（边界值）| 33 | 33 | 0 | 100% |
| DT（决策表）| 13 | 13 | 0 | 100% |
| ST（状态迁移，白盒 FR4.0）| 18 | 18 | 0 | 100% |
| SC（场景）| 5 | 5 | 0 | 100% |
| **合计** | **96** | **96** | **0** | **100%** |

> 集成测试 `tests/test_integration_http.py` 另 **11/11 通过**（API 端到端，0.60s），不计入上面 96 条设计用例。

## 2. 按需求 + 风险等级（§10.2，风险驱动执行顺序）

> RPN 取自 `risk_analysis.json`（**RPN 越小风险越高，先测**）。执行顺序在 `test_suite_from_design.py` 中按 RPN 升序排（REQ-012 卡死缺陷 RPN=1 最先跑）。

| REQ | RPN | 唤醒/休眠语义 | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|---|---|
| REQ-012 | 1 | 连续快速循环 → state10 卡死（缺陷 DEF-001）| 6 | 6 | 0 | 100% |
| REQ-001 | 2 | 供电电压唤醒 | 10 | 10 | 0 | 100% |
| REQ-008 | 2 | 休眠条件 h1（VCUIdle）| 5 | 5 | 0 | 100% |
| REQ-009 | 2 | 休眠条件 h2（AuthComplete）| 3 | 3 | 0 | 100% |
| REQ-010 | 2 | 休眠条件 h3（CAN stopped）| 6 | 6 | 0 | 100% |
| REQ-011 | 2 | 休眠 h1∧h2∧h3 联合判定 | 10 | 10 | 0 | 100% |
| REQ-003 | 4 | CP 信号唤醒 | 7 | 7 | 0 | 100% |
| REQ-002 | 6 | CAN 报文唤醒 | 8 | 8 | 0 | 100% |
| REQ-004 | 6 | CC 信号唤醒 | 7 | 7 | 0 | 100% |
| REQ-005 | 6 | CC2 信号唤醒 | 7 | 7 | 0 | 100% |
| REQ-007 | 6 | 门板信号唤醒 | 8 | 8 | 0 | 100% |
| REQ-014 | 6 | 唤醒/休眠时长（type1≈14.7s / type2≈42s）| 5 | 5 | 0 | 100% |
| REQ-013 | 8 | 状态输出一致性（bus_message_flag 等）| 4 | 4 | 0 | 100% |
| REQ-006 | 9 | 口盖信号唤醒 | 10 | 10 | 0 | 100% |
| | | **合计（14 条需求全覆盖）** | **96** | **96** | **0** | **100%** |

### 风险等级门槛（仅 Module A）
| 风险带 | 对应需求 | 门槛 | 实测 | 结论 |
|---|---|---|---|---|
| RPN ≤ 5（High）| REQ-001/003/008/009/010/011/012 | **100% 必过** | 47/47 = 100% | ✅ 达成 |
| RPN 6~10（Medium）| REQ-002/004/005/006/007/013/014 | ≥ 95% | 49/49 = 100% | ✅ 达成 |

## 3. 正向 / 负向构成（关键：通过 ≠ 仿真器全 success）

| 类别 | 数量 | 含义 | 通过即代表 |
|---|---|---|---|
| **正向**（Positive）| **49** | 期望 VCU **成功唤醒（vehicle_state=11）或成功休眠（=9）**，result_type=expected | VCU 在合法输入下正确进入目标状态 |
| **负向**（Negative）| **47** | 期望 VCU **报错/拒绝/维持/卡死**（result_type=error 46 条 + 卡死 state10 无显式 result_type 1 条）| VCU 在非法/边界/缺陷输入下**正确报错或暴露缺陷** |
| **合计** | **96** | | |

> **设计意图**：负向用例占 49%，目的正是「找出 VCU 报错/卡死之处」。它们 **PASS 的语义 = VCU 按预期报错/拒绝/卡死**，而非「VCU 返回 success」。
> 例：REQ-012 的卡死用例 PASS = 成功复现 `vehicle_state=10 + DTC_001 + actual_duration=41s` 缺陷（见 `defect_DEF-001_state10_stuck.md`）；CP=8V 负向用例 PASS = VCU 正确拒绝唤醒并维持 state09。
> **不追求「全 success」**：若某用例失败且确属 VCU 缺陷（非 oracle 错误），按 §10.3 写缺陷报告，**不硬改用例使其变绿**。本轮无遗留失败——所有 oracle 缺陷已在执行期审查 REV-016 修正（见 `review_log.md` Phase 6）。

## 4. 证据文件
- `pytest_output/design_suite.xml`（JUnit，96 testcase 逐条 pass/fail）
- `pytest_output/design_suite.txt`（pytest 控制台输出，`96 passed`）
- `pytest_output/design_suite_report.html`（pytest-html 自包含报告）
- `pytest_output/execution_details.json`（96 条逐条：input / expected / VCU actual_output / mismatches）
- 前端「Results」页（`AutoTestDesignV2.tsx`）可展开查看每条用例 VCU 实际输出。
