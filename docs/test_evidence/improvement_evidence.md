# 基于证据的改进 — Improvement with Evidence（Artifact 4 §12）

> **范围更正（重要）**：Assignment 2「Mainly」内容清单里，**#7 基于证据的改进**排在 **#6 结果分析**之后，特指**测试用例真正在 VCU 上跑完、拿到执行/覆盖证据之后，新增的有效覆盖项与测试用例**。
> 因此本节**只**收录**基于第一轮执行/覆盖证据**的改进，两类来源：(A) `/api/improve` 第二轮 LLM 用例增广 → 人工评审挑选 → 加入套件 → 重跑 VCU；(B) 依据覆盖分析定位的未覆盖分支 → 针对性新增用例 → 重跑验证覆盖提升。
> 设计期的改进（不属于本节）已归位到下表对应板块。

## §0 内容归属表（把设计期 / 结果分析 / FR7 内容放回正确板块）

| 内容 | 发生时机 | 正确归属板块 | 证据文件 |
|---|---|---|---|
| **+8 Coverage Items**（5 Output / 2 Behavior / 1 Environment，14→22）| LLM 生成覆盖项后**立即人工补**，**未跑模拟器** | **§4 覆盖项识别（人工交互评审）** | `review_log.md` Phase 2（REV-006~008）、`coverage_tables.md` |
| **需求结构化修订**（REV-001~005：ubr_threshold、has_timing、维持分支…）| 设计期需求审查 | **§2/§4 + 提示设计交互** | `review_log.md` Phase 1 |
| **风险评分校正**（REV-009/010）| 设计期风险审查 | **§3 风险分析** | `review_log.md` Phase 3 |
| **策略技术绑定**（REV-011）| 设计期 | **§5 覆盖策略与方法** | `review_log.md` Phase 4 |
| **Prompt 迭代 + 用例重生成**（REV-012~015、TOOL-FIX-007 取值语义、用例 v1→v4 版本链）| 改 prompt 重生成，**重生成前那版未跑**（一眼有问题直接改提示词）| **§6 提示设计 + 测试用例人工交互（版本链）** | `review_log.md` Phase 5、`prompts_used.md`、版本链 5 个 json |
| **执行纠正链 48→80→92→96**（oracle 取值纠正、harness 修复、REV-016 改/删）| 跑完之后，但属**纠正/删除**，非"新增有效用例" | **§10 结果分析（执行质量）** | `review_log.md` Phase 6、`pass_rate_summary.md` |
| **FR7.0 最小化 96 vs 65 对比**（65/65 通过、覆盖 95.8/89.0→~94.6/86.6、耗时 -55%）| 跑完之后的套件优化对比 | **§10 结果分析（设计用例↔覆盖/策略映射，展示 FR7 功能点）** | `fr7_optimization.md` §2b、`coverage_min65.json` |
| **工具自身缺陷修复 TOOL-FIX-001~006/008**（前端编辑器、CRUD、幂等、持久化、error 归一、ne 算子、pytest 执行引擎）| 全程 | **§9 工具实现 / Improvement 加分** | `review_log.md` 附录 |

> 说明：上述都是有价值的改进证据，但**按 Assignment 的时序语义不属于"基于证据的改进（新增有效用例）"**，故归位到各自板块；本节只保留下面 §1 的真·执行后增广。

---

## §1 第二轮 LLM 用例增广（本节核心 — 执行后、基于证据的新增有效用例）

> 闭环：**第一轮执行（96/96）→ 调 `/api/improve`（LLM，improve prompt，把执行后的全部用例作上下文）→ 8 条增广建议 → 人工评审挑选（不全信 LLM）→ 加入套件 → 重新跑 VCU → 有效性分析**。
> 证据文件：`improve_round2_suggestions.json`（8 条原始建议）、`improve_round2_accepted.json`（3 条采纳，含人工修正）、`tests/test_improve_round2.py`、`pytest_output/improve_round2_execution.json`。

### 1.1 LLM 增广建议（`/api/improve`，qwen3.7-max，67s，8 条）
工具把第一轮执行后的 96 条用例作为上下文喂给 LLM，返回 8 条第二轮建议（新覆盖项 + 新用例），目标是补充第一轮**按单信号设计**所遗漏的组合/并发/极端场景。

### 1.2 人工评审挑选（不全信 LLM —— designer interactive validation）
逐条对照 `vcu_simulator/simulator.py` 真实行为核查，**8 进 3（采纳率 37.5%），其中 2 条还修正了 LLM 写错的 oracle**：

| # | REQ | 建议 | 评审结论 |
|---|---|---|---|
| 3 | REQ-011 | 休眠条件全满足 + 同时来唤醒信号 | ✅ 采纳，**人工改 oracle**：LLM 写 state11(唤醒赢)，实际 `simulate()` 先判 `_has_sleep_inputs`→**休眠优先 state9** |
| 5 | REQ-004 | CC 与 CC2 同时满足唤醒 | ✅ 采纳，**人工改 oracle**：LLM 写 `reason in [4,5,6]`(操作符不支持)，实际 `_detect_wake_reason` CC 先于 CC2→**reason 4** |
| 8 | REQ-006 | 口盖超长时序 5000ms | ✅ 采纳（原样，LLM oracle 正确）|
| 1 | REQ-001 | 电压跌落致防抖重置 | ❌ 拒：SUT 未建模防抖重置，无法送 voltage_profile |
| 2 | REQ-002 | CAN Bus-Off 下唤醒 | ❌ 拒：Module C 越界 + 臆造 DTC_CAN_BUS_OFF |
| 4 | REQ-012 | state10 卡死后唤醒屏蔽 | ❌ 弃：与 DEF-001 重叠、setup 复杂 |
| 6 | REQ-014 | NM 报文刷新休眠计时器 | ❌ 拒：SUT 无 NM keep-awake 机制 |
| 7 | REQ-009 | 认证超时降级 | ❌ 拒：臆造 state 12 + DTC_AUTH_TIMEOUT |

> **关键价值**：5 条因「SUT 未建模 / 越界 Module C / 臆造 DTC 与状态」被拒；2 条 oracle 被人工纠正——充分体现"LLM 不能全信，需人工 + 领域知识验证"。

### 1.3 加入套件后重新执行 VCU（4/4 通过）
本节最终采纳 **4 条新增用例（两类来源）**，由 `tests/test_improve_round2.py` 驱动 VCU：

| 用例 | 来源 | 输入 | VCU 实际输出 | 通过 | 价值 |
|---|---|---|---|---|---|
| r2-001 (REQ-011/SC) | LLM | h1=h2=h3=1, voltage=12 | vehicle_state=**9**, reason=0, expected | ✅ | 休眠优先于唤醒（并发）|
| r2-002 (REQ-004/SC) | LLM | cc=2.0, cc2=2.0 | vehicle_state=11, pdcu_wake_reason=**4**, expected | ✅ | CC 优先于 CC2（多源并发）|
| r2-003 (REQ-006/BVA) | LLM | hood=4.1, dur=5000 | vehicle_state=11, reason=6, expected | ✅ | 超长时序无溢出（鲁棒）|
| **r2-004 (REQ-001/EP)** | **覆盖缺口驱动** | 无任何唤醒信号 | vehicle_state=**9**, reason=0, error | ✅ | **覆盖 L273（之前未覆盖的 fallthrough）** |

LLM 三条的 VCU 实测与**人工修正后**的 oracle 完全一致（state9 / reason4 / reason6），反证 LLM 原 oracle（state11 / in[4,5,6]）是错的。

### 1.4 有效性分析（诚实：分来源、双维度度量）

**来源 A — LLM 增广（3 条，r2-001~003）**
| 维度 | 结果 |
|---|---|
| 通过 | 3/3 |
| 捕获 LLM oracle 错误 | 2/3（人工拦下并修正）|
| 组合/优先级覆盖 | **+3 条新条件**（休眠>唤醒、CC>CC2、极端时序）|
| 分支覆盖 | **+0**（76.65%→76.65%）—— 诚实：优先级是"判定顺序"行为，走已覆盖路径，分支覆盖对其不敏感 |

**来源 B — 覆盖缺口驱动（1 条，r2-004）**
| 维度 | 结果 |
|---|---|
| 触发证据 | `coverage_analysis.md`：96 条基线下 simulator.py **L273 未覆盖** |
| 新增用例 | 「无任何有效唤醒信号 → 维持 state9 报错」（7 路唤醒需求的负向等价类）|
| **分支覆盖（可量化提升）** | 语句 180→**181**、分支 76→**77**；文件级 76.65%→**77.25%**；**纯 Module A 95.8%→96.4% / 89.0%→90.2%** |
| 新覆盖的行 | **恰为 L273**（脚本 diff 确认）|

**结论（基于证据的改进）**：第二轮改进有**两类有效来源**——
1. **LLM 增广**：采纳率 37.5%（8→3），新增 3 条**组合/优先级**用例（分支覆盖看不见但属真实规格行为），并经人工评审拦下 5 条越界/臆造、修正 2 条错误 oracle；
2. **覆盖缺口驱动**：依据第一轮覆盖分析（L273 未覆盖）新增 1 条用例，**可量化地把分支覆盖 +1（纯 Module A 89.0%→90.2%）**。

合计 **4 条新增有效用例、4/4 通过**。**核心认知**：分支覆盖必要但不充分——组合/优先级盲区靠 LLM 增广提示（需人工把关），代码路径盲区靠覆盖分析定位；两类证据互补，才构成完整的"基于证据的改进"。

---

## 证据文件
- `review_log.md`（REV-001~016 + TOOL-FIX-001~008 全量记录，按 Phase 1~6 时序归类）
- `coverage_tables.md`（覆盖项 14→22 before/after，属 §4）
- `prompts_used.md` + 用例版本链 5 个 json（属 §6）
- `pass_rate_summary.md` + `fr7_optimization.md`（属 §10 结果分析）
- 本节增广证据：`improve_round2_suggestions.json`、新增用例的 `execution_details` 与覆盖对比（生成后补）
