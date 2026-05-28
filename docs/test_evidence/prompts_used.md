# Prompts Used — AutoTestDesign 工具实际使用的 LLM Prompt

> Artifact 4 §6 Prompt Design 证据。LLM = 百炼 DashScope（OpenAI 兼容模式），model=qwen，结构化 JSON 输出。
> 工具共 5 个 prompt 模板：`parse`（需求解析/FR1.1）、`risk`（风险分析/FR2.0）、`coverage`（覆盖项/FR3.0前置）、`testcase`（用例+oracle生成/FR3.0+4.0+5.0）、`improve`（第二轮 LLM 用例增广建议）。
> 每个 prompt 以"system_prompt + user_prompt 模板 + 真实输入→输出样例"呈现，体现"prompt 决定输出质量"。

---

## 1. `parse` — 需求解析（FR 1.1 Requirement Structuring）

### system_prompt
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

### user_prompt（模板）
```
原始需求文本：
{raw_text}
```

**输入→输出样例（REQ-001）**
- 输入 raw_text：`供电电压 voltage > 9.0V 持续 duration ≥ 10ms 时唤醒 VCU。`
- 输出结构化（节选）：
  - input_fields: `[{"name": "voltage", "data_type": "float", "valid_range": {"expression": "0-36"}, "unit": "V", "has_timing": false}, {"name": "duration_ms", "data_type": "integer", "valid_range": {"expression": "0-10000"}, "unit": "ms", "has_timing": true}]`
  - conditions: `[{"type": "threshold", "description": "voltage > 9.0V", "threshold": 9.0}, {"type": "timing", "description": "duration_ms >= 10", "threshold": 10}]`
  - expected_actions: `[{"output_field": "vehicle_state", "expected_value": 11, "operator": "eq"}, {"output_field": "pdcu_wake_reason", "expected_value": 1, "operator": "eq"}, {"output_field": "result_type", "expected_value": "expected", "operator": "eq"}]`

---

## 2. `risk` — 风险分析（FR 2.0 Risk Analysis & Prioritization）

### system_prompt
```
你是汽车 ECU 测试专家，按 ISO 9126 和 Chapter 4 Tech Risk × Business Risk 做风险评分。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：
requirement_id, iso9126_characteristic, tech_risk, business_risk, rpn, extent, reasoning。
tech_risk/business_risk 为 1-5，1 表示最高风险；rpn=tech_risk*business_risk。
extent 规则：1-5 Extensive, 6-10 Broad, 11-15 Cursory, 16-25 Low priority。
```

### user_prompt（模板）
```
结构化需求 JSON：
{requirements_json}
```

**输入→输出样例（REQ-012 卡死缺陷，最高优先级）**
- 输入：REQ-012 结构化需求（state10 卡死检测）
- 输出 oracle：tech_risk=`1`, business_risk=`1`, rpn=`1`, extent=`Extensive`, iso9126=`Reliability`
  - reasoning（节选）：Tech=1: 涉及极端时序、异常状态恢复及故障注入，极易触发底层死锁；Biz=1: 已知致命缺陷，VCU 卡死将导致车辆直接抛锚，业务风险最高。

---

## 3. `coverage` — 覆盖项生成（FR 3.0 前置：Coverage Item Identification）

### system_prompt
```
你是测试设计工程师，为每条 VCU 需求生成覆盖项。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：requirement_id, title, description, technique, iso9126_characteristic, priority。
technique 可为 EP/BVA/DT/ST/SC。
```

### user_prompt（模板）
```
结构化需求 JSON：
{requirements_json}
```

**输入→输出样例（REQ-001 生成的覆盖项）**
- `BVA` | 硬线供电唤醒边界值测试 — 验证供电电压在9.0V边界（8.9V, 9.0V, 9.1V）及持续时间在10ms边界（9ms, 1
- `EP` | vehicle_state 唤醒/休眠 oracle 一致性 — 验证 vehicle_state 在唤醒 (=11)、休眠 (=9)、卡死 (=10) 三种情况下输
- `EP` | pdcu_wake_reason 来源编码 oracle — 验证 pdcu_wake_reason 在 7 路唤醒源 (=1~7) 和无唤醒 (=0) 情况下正
- `ST` | 正常唤醒序列 state09→state10→state11 — 完整 3 步状态迁移序列覆盖 All-Transitions 中 T1 路径

---

## 4. `testcase` — 测试用例 + Oracle 生成（FR 3.0 + 4.0 + 5.0）⭐

> 注：此 prompt 经过 **两轮迭代改进**（Interactive Review 第 5 步 Prompt Design 的核心证据），当前为 **v3（取值语义版）**。每一轮改进都由"执行/审查发现问题 → 改 prompt（工具）→ 重生成"驱动，而非人工逐条改用例。

**Prompt 演进史（v1 → v2 → v3）：**

| 版本 | 改进内容 | 修复的问题 | 量化效果 | 存档 |
|---|---|---|---|---|
| v1 原始 | 仅字段列表 | — | 初版（含臆造字段 21 条、oracle 取值系统性错误）| `prompt_testcase_before.json` |
| v2 (REV-015) | + 字段名白名单、禁止臆造、active_dtcs 用 contains | Untestability：21 条用例引用 VCU 不存在字段（is_compliant / sleep_sub_condition_* / Next_State）| 臆造字段 21→0 | `prompt_testcase_v2_fieldwhitelist.json` |
| **v3 (TOOL-FIX-007)** | + **VCU 输出取值语义**（state/result_type/reason/duration 合法取值与判定口径）| 系统性 oracle 取值错误：vehicle_state=0 幻觉、维持态写成 10、no-wake 写 expected、卡死写 stuck | 执行通过率 **48/96 → 80/99** | `prompt_testcase_v3_value_semantics.json` |

### system_prompt（v3 当前版）
```
你是测试用例设计器，为汽车 VCU 需求生成 bq_new 兼容测试用例。
仅返回 JSON 对象：{"test_cases": [...]}。
每个 test_cases 元素字段：
requirement_id, coverage_item_id, title, technique, type, in_data, expected_results, error, est_time, oracle_reasoning。
in_data: [{name, data_type, value, duration, unit}]
expected_results: [{name, operator, value, out_type, out_range}]

【关键约束——expected_results 的 name 只能取 VCU 仿真器真实返回的输出字段，禁止臆造】
合法 name 仅限：vehicle_state, vehicle_mode, power_current, bus_message_flag, pdcu_wake_reason, actual_duration, result_type, power_alarm_flag, bus_off_flag, active_dtcs, state_name。
- 禁止使用 is_compliant / sleep_sub_condition_x / Next_State 等 VCU 不返回的字段（否则 oracle 无法验证 = Untestable）。
- 休眠/唤醒/卡死等状态断言一律用 vehicle_state（休眠=9, 卡死=10, 唤醒=11）；"维持非休眠"用 vehicle_state ne 9。
- 时序合规用 actual_duration（配合 lte/gt 阈值，如 type1 lte 20、type2 lte 60）。
- active_dtcs 是列表，断言某 DTC 存在时 operator 用 contains（如 active_dtcs contains DTC_001），不要用 eq。

operator 只能是 eq/ne/gte/lte/gt/lt/contains。
必须覆盖用户指定技术 EP/BVA/DT/ST/SC，并包含 REQ-ID 与 Coverage Item ID。

【VCU 输出取值语义——oracle 的 value 必须符合真实取值，禁止臆造】（v3 TOOL-FIX-007 新增）
- vehicle_state 仅 {9=休眠state09, 10=卡死state10, 11=唤醒state11}，绝不出现 0 或其它值。
  · 未满足任何唤醒条件 / 无效输入 → 维持休眠：vehicle_state=9
  · 唤醒成功 → vehicle_state=11
  · 连续≥3次快速(相邻间隔<1s)唤醒-休眠循环后再唤醒 → 卡死：vehicle_state=10
- pdcu_wake_reason：0=未唤醒；1~7=七路唤醒源；仅成功唤醒时非0，未唤醒一律 0。
- result_type 仅 {"expected","error"}：
  · "expected" = 动作按条件成功发生（成功唤醒，或 h1∧h2∧h3 成功休眠）
  · "error" = 未满足条件 / 维持原态 / 卡死（卡死时 result_type 也是 "error"，靠 vehicle_state=10 + active_dtcs 含 DTC_001 识别，不要写 stuck）
- bus_message_flag：state11→1，state09→0。
- actual_duration：正常 type1≤20、type2≤60；只有卡死才会超时(>20)。时序合规一律用 lte 阈值，不要给正常操作设 gt 阈值（正常操作产生不了超时）。
- active_dtcs：卡死写入 "DTC_001"，断言用 contains（不要用 eq）。
统一口径示例：无效/未唤醒输入 → (9, reason 0, error)；有效唤醒 → (11, reason 1~7, expected)；卡死复现 → (10, DTC_001 contains, error)
```

### user_prompt（模板）
```
需求、覆盖项、策略 JSON：
{design_context_json}
```

**输入→输出样例（REQ-001 BVA，含合成 oracle = FR 5.0）**
- 输入 design context：REQ-001 结构化需求 + 覆盖项 + 策略(EP/BVA/ST)
- 输出用例：BVA: 电压9.1V且持续10ms触发唤醒
  - in_data: `[{"name": "voltage", "value": 9.1}, {"name": "duration_ms", "value": 10}]`
  - expected_results(oracle): `[{"name": "vehicle_state", "op": "eq", "value": 11}, {"name": "pdcu_wake_reason", "op": "eq", "value": 1}, {"name": "result_type", "op": "eq", "value": "expected"}]`
  - oracle_reasoning: 电压9.1V > 9.0V，持续时间10ms >= 10ms，满足唤醒条件，处于边界有效值。

---

## 5. `improve` — 第二轮 LLM 用例增广建议（PROJECT_PLAN_V2 §3.9 反馈机制；非 fuzz）

### system_prompt（当前版）
```
你是测试设计改进助手。基于第一轮测试执行结果（覆盖情况与未通过用例），为相关需求提出第二轮的测试覆盖项与测试用例增广建议（补充遗漏的边界、状态与场景）。
仅返回 JSON 对象：{"suggestions": [...]}。
每个 suggestions 元素字段：
requirement_id, title, reason, coverage_item, test_case。
coverage_item 字段同覆盖项；test_case 字段同 bq_new 兼容测试用例，可为 null。
```

### user_prompt（模板）
```
执行结果上下文 JSON：
{execution_context_json}
```

**真实输入→输出样例（Artifact 4 §12 已执行）**：第一轮 96/96 跑完后调用，LLM 返 8 条建议（qwen3.7-max，67s）→ 人工评审 8 进 3（其中 2 条纠正 LLM 写错的 oracle）→ 加入后 VCU 重跑 3/3 通过。详见 `improve_round2_suggestions.json`（8 条原始）、`improve_round2_accepted.json`（3 条采纳）、`improvement_evidence.md` §1。
**术语澄清**：此功能是"LLM 第二轮用例增广"（结构化、有 oracle、需人工评审），**不是 fuzz**（无随机/变异输入）；Assignment 2 亦无 fuzz 相关 FR。FR 7.0 的"测试套件优化（优先级排序/最小化）"是另一独立、纯算法功能，见 `fr7_optimization.md`。

---

## 6. Prompt 工程要点（写进 Artifact 4 §6）

1. **强约束输出格式**：所有 prompt 都要求"仅返回 JSON 对象"+ 明确字段 schema，保证可解析。
2. **field 白名单（v2 / REV-015）**：testcase prompt 限定 oracle 字段只能取 VCU 真实输出字段，消除"臆造不可验证字段"——把 Untestable oracle 从 21 条降到 0 条。
3. **取值语义（v3 / TOOL-FIX-007）**：进一步约束每个输出字段的合法取值与判定口径（state∈{9,10,11}、result_type∈{expected,error}、no-wake→9/0/error 等）——把执行通过率从 48/96 提到 80/99。这是 **prompt 第二轮改进**，由"执行 96 条用例暴露系统性 oracle 取值错误"驱动。
4. **operator 受限集**：eq/ne/gte/lte/gt/lt/contains（ne 为 TOOL-FIX-006 新增），避免 LLM 产出非法算子。
5. **oracle_reasoning 强制**：要求每条用例附推导依据，使 oracle 可人工审查（FR 5.0 + interactive review）。

**两轮 prompt 改进 + 两轮人工测试数据修订（Interactive Review 完整闭环，写进 Artifact 4 §6 + §12）：**

| 轮次 | Prompt 改进 | 人工用例修订 | 触发来源 |
|---|---|---|---|
| 第 1 轮（设计期）| v2 字段白名单（REV-015）| REV-012~015：oracle 字段/逻辑修正 + 重生成 REQ-008/009/010 | 人工对照课件审查（Untestability / 条件不完整 / BVA 无效类）|
| 第 2 轮（执行期）| **v3 取值语义（TOOL-FIX-007）** | **REV-016**：执行 96 条暴露问题后，改 3 删 4 加 1（8.9V invalid-low）+ adapter 修复 | 数据驱动 pytest 执行（48/96→80/99→92/99→96/96）|

> 说明：testcase prompt 的两轮改进对应 Step 2.6 Prompt Design 的迭代本质——designer 不是一次写死 prompt，而是依据"设计期人工审查"和"执行期真实反馈"两次回炉，每次都改**工具（prompt）**而非手工补用例。详见 `review_log.md` Phase 5（设计期）与 Phase 6（执行期）。
