# Baseline Reference — NOT Artifact 4 Evidence

这个目录下的所有 pytest 报告 / coverage 报告是 **2026-05-24 在拿到 AutoTestDesign LLM API key 之前**，
直接跑仓库里既有的 `tests/test_suite_*.py` 产生的，**仅用于验证 VCU 仿真器（SUT）本身可运行**。

**严禁**把这些文件作为 Artifact 4 §10 Test Execution Results 的合法证据，理由：

> Assignment 2 第 4 项 Test Case Design 明确要求 *"Design test cases for the selected feature/module **using the AutoTestDesign tool**"*。
> 直接复用预先存在的 pytest 脚本绕过了 AutoTestDesign 工具，违反了"工具生成 + Interactive Review"的核心评分项。

## 后续正确处理

1. 拿到 LLM API key 后跑 AutoTestDesign Step 2.2~2.6（7 步 Interactive Review）。
2. 工具导出 `09_test_cases_reviewed.json` 作为正式用例集。
3. 把这份 JSON 中的用例对照 / 修订 `tests/test_suite_*.py`，确保 input/expected 和工具产出一致；每条 test 方法 docstring 首行加 `TC-X-NNN | CI-... | REQ-NNN` 三联追溯。
4. 才能重新跑 pytest，新的输出落到 `docs/test_evidence/pytest_output/` 作为合法证据。
5. 同时在 Artifact 4 §10.4 Improvement 里写明：本目录的 baseline run 帮助提前发现了 SUT 是否健康，避免后续 LLM 生成用例时把"工具 bug"误判为"SUT 缺陷"。

## 本目录内容（baseline 跑出来的客观事实）

- Suite A (既有 21 条): 21 passed
- Suite B (既有 24 条): 24 passed
- Suite C (既有 8 条): 8 passed
- Suite D (既有 15 条): 15 passed
- Suite E (既有 10 条): 10 passed
- Integration HTTP: 11 skipped (VCU 仿真器 HTTP 服务未启动)
- coverage: simulator.py Statement 81% / Branch ~94%

> 这些数字说明 SUT 是 healthy 的，AutoTestDesign 后续生成的用例如果跑出 FAIL，更可能是用例本身问题或 LLM 幻觉，而不是 SUT 缺陷（REQ-012 卡死除外，那是已知的）。
