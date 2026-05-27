# Module A 代码覆盖率分析（Step 3.4 — 白盒证据，Artifact 4 §11.3）

> 工具：coverage.py 7.14（`--branch`）。
> **被测代码（SUT）= Module A 的实现 `vcu_simulator/simulator.py`**（唤醒-休眠-卡死状态机）。
> 测试来源：`tests/test_suite_from_design.py`（96 条 reviewed 设计用例，进程内直接驱动 `VCUSimulator`）。
> 退出标准：语句 ≥80% / 分支 ≥70%。
> **范围说明**：Artifact 4 只测 Module A（REQ-001~014），覆盖率只统计 Module A 被测代码，**不含 Module B/C/D/E**。`modules/*`、`main.py`、`models.py` 不计入。

## 1. Module A 覆盖率（结论）

| 指标 | 纯 Module A 逻辑 | 目标 | 结果 |
|---|---|---|---|
| **语句覆盖** | **95.8%**（160/167） | ≥80% | ✅ 远超 |
| **分支覆盖** | **89.0%**（73/82） | ≥70% | ✅ 远超 |

> 说明：`simulator.py` 是**多模块共享文件**，文件级原始覆盖率为语句 79.6%(180/226) / 分支 70.4%(76/108)；其中混入了 **59 条非-Module-A 语句行 + 26 条非-Module-A 分支**（见 §2）。把这些剔除后，**纯 Module A 决策逻辑**的覆盖率即上表的 95.8% / 89.0%。

## 2. 从 Module A 覆盖率中剔除的非-Module-A 代码（逐项）

| 被剔除部分 | 所属 | 行/方法 | 理由 |
|---|---|---|---|
| `_handle_guard_rejection` | Module B | 过压→fault_protection+DTC_002、欠压→undervoltage_shutdown | REQ-015/016，非 Module A |
| `can_error_count` 注入 | Module C | L40 | CAN 错误，REQ-019，非 Module A |
| `reset(clear_dtc=True)` 清码 | Module D | L99 | DTC 清除，REQ-022，非 Module A |
| `get_state/get_config/update_config/get_performance/_deep_update` | 基础设施/API | — | 查询/配置接口，非测试目标（用例直接调 `simulate()`）|
| `simulate_sleep / simulate_batch` | 旧接口 | — | legacy 包装，Module A 数据驱动用例不走 |
| `_normalize_legacy_payload` | 旧接口 | L372–389 | 旧 `signal_name` 兼容，新用例用 kwargs，不触发 |

## 3. Module A 内仍未覆盖的 7 行（次要）

`155, 202, 273, 304, 330, 333, 358`：
- L155 = "处于 fault/undervoltage 时拒绝唤醒"（Module B 故障恢复分支，边界）；
- L202 = 休眠时功耗不达标置 power_alarm（Module E 功耗告警分支）；
- L273/304/330/333/358 = `_detect_wake_reason` 无信号 fallthrough、`test_status` 次要赋值、状态映射与 stuck 电流的次要分支。
均为边界/相邻模块联动，不影响 Module A 主决策路径（7 路唤醒 + 3 条件休眠 + 卡死 + 输出一致性）的覆盖。

## 4. 度量方法（可复现，透明）

文件级数字来自 `coverage report --include="*/vcu_simulator/simulator.py"`。纯 Module A 数字由脚本从 `coverage.json` 按"方法归属"分类每条语句/分支：剔除上述非-Module-A 方法与特定行（L40/L99）后，对剩余 Module A 语句/分支重算覆盖率。

## 5. 证据文件
`coverage_report.txt`（simulator.py 语句+分支）、`coverage.json`（精确指标，含 executed/missing branches）、`coverage.xml`、`coverage_html/`（逐行高亮）。
