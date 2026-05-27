# FR 5.0 — Test Oracle Generation 证据

> Assignment 2 §1.1 FR 5.0（可选加分项）："The system can help synthesize the **Expected Result** for a given requirement and specific test data."
> 即：给定需求 + 具体测试数据，工具能合成**预期结果（test oracle）**。

## 1. 实现方式

AutoTestDesign 的 oracle 合成**内置在测试用例生成流程**（FR 3.0/4.0 同一次 LLM 调用）中。每条由工具生成的 TestCase 都带两个 oracle 字段：

- `expected_results`: 结构化 oracle，形如 `{name, operator, value}`（operator ∈ eq/ne/gte/lte/gt/lt/contains），对照 VCU 仿真器真实输出字段判定通过/失败。
- `oracle_reasoning`: 自然语言推导依据，说明该预期结果如何从"需求 + 该条测试数据"推导而来。
- `error` (`List[BqErrorOracle]`): 异常/错误型 oracle 载体。

判定逻辑在 `backend/api/services/simulator_client.py::_compare_expected / _matches`，按 operator 比对 VCU 实际响应字段与 expected_results。

## 2. 覆盖率统计（实测）

| 指标 | 数值 |
|---|---|
| 测试用例总数 | 96 |
| 含 `expected_results`（结构化 oracle）的用例 | 96 / 96 |
| 含 `oracle_reasoning`（推导依据）的用例 | 96 / 96 |
| 按技术分布 | {'BVA': 32, 'EP': 25, 'ST': 18, 'DT': 16, 'SC': 5} |

→ **100% 用例均带工具合成的 oracle**（expected_results + oracle_reasoning）。

## 3. 代表性 oracle 合成样例（每种技术 1 条，体现"从需求+数据推导"）

- **[REQ-001 / BVA]** BVA: 电压9.1V且持续10ms触发唤醒
  - 输入(test data): voltage=9.1; duration_ms=10
  - 合成 oracle (expected_results): `vehicle_state eq 11`; `pdcu_wake_reason eq 1`; `result_type eq expected`
  - oracle_reasoning: 电压9.1V > 9.0V，持续时间10ms >= 10ms，满足唤醒条件，处于边界有效值。
- **[REQ-001 / EP]** EP: 正常唤醒 vehicle_state 输出 11
  - 输入(test data): voltage=12.0; duration_ms=50
  - 合成 oracle (expected_results): `vehicle_state eq 11`
  - oracle_reasoning: 输入属于有效等价类（voltage>9, duration>=10），预期 vehicle_state 迁移至唤醒状态 11。
- **[REQ-001 / ST]** ST: 正常唤醒序列 state09->state10->state11
  - 输入(test data): voltage=12.0; duration_ms=50
  - 合成 oracle (expected_results): `vehicle_state eq 11`
  - oracle_reasoning: 验证状态机从休眠(09)经准备(10)最终到达唤醒(11)的完整迁移路径，最终状态应为11。
- **[REQ-011 / DT]** DT-条件全满足进入休眠
  - 输入(test data): h1=1; h2=1; h3=1
  - 合成 oracle (expected_results): `vehicle_state eq 9`
  - oracle_reasoning: h1, h2, h3全为True，满足三条件同时休眠，VCU进入state09。
- **[REQ-012 / SC]** 连续3次快速唤醒休眠循环(间隔0.9s)触发卡死
  - 输入(test data): consecutive_wake_sleep_cycles=3; interval=0.9
  - 合成 oracle (expected_results): `vehicle_state eq 10`; `result_type eq stuck`; `active_dtcs contains DTC_001`
  - oracle_reasoning: 满足连续>=3次且间隔<1.0s的条件，应触发state10卡死并上报DTC_001。

## 4. 诚实说明（边界与限制）

1. **打包式实现**：oracle 与测试数据在同一次 LLM 调用中一起生成，没有"只喂 test data 现场单独回 oracle"的独立端点。FR 5.0 能力完全具备且可演示；若需"纯 oracle 生成"独立演示，可加一个端点（非必须）。
2. **oracle 质量需人工把关**：工具初版 oracle 存在缺陷（曾臆造 VCU 不返回的字段、卡死场景逻辑反转），已由人工审查 REV-012~015 修正——见 `review_log.md` Phase 5。这正是 Assignment "Mainly" 段强调的 designer 交互式验证 oracle 有效性，属加分点。

## 5. 证据文件

- `FR5_oracle_samples.csv`：全 96 条用例的 (test data → expected_results → oracle_reasoning) 明细
- `09_test_cases_reviewed.json`：完整用例（含 oracle 字段）
- `prompt_testcase_after.json`：生成 oracle 的 testcase prompt
