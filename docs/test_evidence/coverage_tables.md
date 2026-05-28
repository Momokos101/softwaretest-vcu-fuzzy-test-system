# Coverage 分析三张表（Step 4.3 — Artifact 4 §11）

> **范围**：仅 Module A（REQ-001~014）。数据由脚本从 `09_test_cases_reviewed.json` + `execution_details.json` + `coverage_analysis.md` 重算。
> 三张表对应 Artifact 4 §11.1 Requirement Coverage / §11.2 Coverage Item Coverage / §11.3 Branch Coverage。

---

## 11.1 Requirement Coverage（需求覆盖）

> REQ ↔ 用例追溯来自 `10_traceability_matrix.csv`；Result 来自真实执行。**14/14 需求全覆盖，96/96 全 PASS。**

| 需求组 | REQ | 技术 | 用例数 | Passed | Status |
|---|---|---|---|---|---|
| 7 路唤醒 | REQ-001~007 | EP + BVA + ST | **57** | 57 | ✅ Covered |
| 休眠条件 | REQ-008~011 | EP + BVA + DT + ST | **24** | 24 | ✅ Covered |
| 卡死缺陷 | REQ-012 | SC + ST | **6** | 6 | ✅ Covered（**DEF-001 复现确认**：state10 + DTC_001 + 41s）|
| 输出一致性 | REQ-013 | EP + DT + ST | **4** | 4 | ✅ Covered |
| 时序合规 | REQ-014 | BVA | **5** | 5 | ✅ Covered |
| | | **合计** | **96** | **96** | **14/14 需求** |

### 逐需求明细（含 RPN 风险序）
| REQ | RPN | 用例数 | Passed | 技术 |
|---|---|---|---|---|
| REQ-012 | 1 | 6 | 6 | SC, ST |
| REQ-001 | 2 | 10 | 10 | EP, BVA, ST |
| REQ-008 | 2 | 5 | 5 | EP, DT, ST |
| REQ-009 | 2 | 3 | 3 | EP, DT, ST |
| REQ-010 | 2 | 6 | 6 | EP, DT, ST |
| REQ-011 | 2 | 10 | 10 | EP, BVA, DT, ST |
| REQ-003 | 4 | 7 | 7 | EP, BVA, ST |
| REQ-002 | 6 | 8 | 8 | EP, BVA, ST |
| REQ-004 | 6 | 7 | 7 | EP, BVA, ST |
| REQ-005 | 6 | 7 | 7 | EP, BVA, ST |
| REQ-007 | 6 | 8 | 8 | EP, BVA, ST |
| REQ-014 | 6 | 5 | 5 | BVA |
| REQ-013 | 8 | 4 | 4 | EP, DT, ST |
| REQ-006 | 9 | 10 | 10 | EP, BVA, ST |

**Requirement Coverage = 14/14 = 100%**，每条需求均由 ≥1 黑盒技术覆盖，核心状态机需求另有白盒 ST 覆盖。

---

## 11.2 Coverage Item Coverage（测试覆盖项覆盖）

> Module A 规范级测试条件（Coverage Items）来自 `coverage_items.json`，共 **22 项**。下表按 `(需求 + 技术)` 把每个 CI 映射到覆盖它的设计用例数（同一 (req,technique) 的多个 CI 由该组用例共同覆盖）。

| # | REQ | 技术 | 覆盖用例数 | Coverage Item 标题 | Status |
|---|---|---|---|---|---|
| 1 | REQ-001 | BVA | 4 | 硬线供电唤醒边界值测试 | ✅ |
| 2 | REQ-001 | EP | 5 | vehicle_state 唤醒/休眠 oracle 一致性 | ✅ |
| 3 | REQ-001 | EP | 5 | pdcu_wake_reason 来源编码 oracle | ✅ |
| 4 | REQ-001 | EP | 5 | VCU 仿真器 v1.0 SIL 环境基线 | ✅ |
| 5 | REQ-001 | ST | 1 | 正常唤醒序列 state09→state11 | ✅ |
| 6 | REQ-002 | BVA | 4 | CAN 网络唤醒报文 ID 边界测试 | ✅ |
| 7 | REQ-003 | BVA | 3 | CP 信号唤醒电压边界测试 | ✅ |
| 8 | REQ-004 | BVA | 3 | CC 信号唤醒电压边界测试 | ✅ |
| 9 | REQ-005 | BVA | 3 | CC2 信号唤醒电压边界测试 | ✅ |
| 10 | REQ-006 | BVA | 6 | 口盖信号唤醒电压与时间边界测试 | ✅ |
| 11 | REQ-007 | BVA | 3 | 门板信号唤醒电压与时间边界测试 | ✅ |
| 12 | REQ-008 | EP | 2 | 休眠条件 h1 状态等价类测试 | ✅ |
| 13 | REQ-009 | EP | 1 | 休眠条件 h2 状态等价类测试 | ✅ |
| 14 | REQ-010 | EP | 2 | 休眠条件 h3 CAN 总线空闲状态测试 | ✅ |
| 15 | REQ-011 | DT | 8 | 三条件组合休眠判定表测试 | ✅ |
| 16 | REQ-012 | SC | 5 | 快速唤醒休眠循环卡死缺陷场景测试 | ✅ |
| 17 | REQ-012 | SC | 5 | active_dtcs 卡死时包含 DTC_001 | ✅ |
| 18 | REQ-012 | SC | 5 | 卡死序列：连续 3 次快速循环触发 state10 | ✅ |
| 19 | REQ-013 | DT | 1 | bus_message_flag 与 vehicle_state 一致性 | ✅ |
| 20 | REQ-013 | ST | 1 | 电源状态与总线报文标志位状态转换 | ✅ |
| 21 | REQ-014 | BVA | 5 | 响应时序合规性边界值测试 | ✅ |
| 22 | REQ-014 | BVA | 5 | actual_duration 时序边界 oracle | ✅ |

**Coverage Item Coverage = 22/22 = 100%**；技术覆盖 **EP / BVA / DT / ST / SC 五种齐全**（黑盒 EP/BVA/DT/SC + 白盒 ST），满足 Assignment 2「多种黑盒 + 白盒」要求。

### ⚠ 追溯链小缺口（已知，诚实披露）
- 22 个 canonical CI 中，**21 个**可由用例的 `coverage_item_id`（UUID）直接 join；其余 **1 个**（#17 REQ-012「DTC_001」CI）在 v3 regenerate 时丢失了 UUID 链，但**功能上仍被 REQ-012 的卡死用例覆盖**（每条都断言 `active_dtcs contains DTC_001`），故按 (req+技术) 映射为已覆盖。
- 另有 **16 条** v3-regenerated 用例的 `coverage_item_id` 是占位串（`EP-REQ-002` / `ST-REQ-005` / `N/A` / 空），非 canonical UUID。
- **影响评估**：不影响覆盖结论（22/22 仍成立，按 req+技术可验证），仅为**追溯字段卫生问题**。建议后续在 AutoTestDesign 生成阶段强制 CI UUID 回填（记为流程改进项）。

---

## 11.3 Branch Coverage（白盒，被测代码 `vcu_simulator/simulator.py`）

> 工具：coverage.py 7.14（`--branch`）。测试来源：`tests/test_suite_from_design.py`（96 条进程内驱动 VCUSimulator）。详见 `coverage_analysis.md`。

| 指标 | 纯 Module A 逻辑 | 目标（Chap5 MTP 退出准则）| 结果 |
|---|---|---|---|
| 语句覆盖 | **95.8%**（160/167）| ≥ 80% | ✅ 远超 |
| 分支覆盖 | **89.0%**（73/82）| ≥ 70% | ✅ 远超 |

> `simulator.py` 是多模块共享文件，文件级原始覆盖率为语句 79.6% / 分支 70.4%；剔除 59 条非-Module-A 语句 + 26 条非-Module-A 分支（Module B 过压/欠压、Module C CAN 错误、Module D 清码、基础设施 getter、legacy 接口）后，纯 Module A 决策逻辑即 95.8% / 89.0%。剔除明细与可复现度量法见 `coverage_analysis.md`。

---

## 证据文件
- `10_traceability_matrix.csv`（REQ ↔ CI ↔ 用例 ↔ Result 追溯，含 Design Case UUID）
- `09_test_cases_reviewed.json`（96 条设计用例）+ `_state_snapshot/coverage_items.json`（22 canonical CI）
- `pytest_output/execution_details.json` / `design_suite.xml`（逐条 PASS/FAIL）
- `coverage_analysis.md` + `pytest_output/coverage.json` / `coverage_html/`（分支覆盖逐行）
