# Artifact 4 文档大纲：Detailed Test Design and Execution Document

> 文档用途：提交 Assignment 2 的第 4 项交付物，即“针对自选目标应用一个主要特性/模块的详细测试设计与执行文档”。
>
> 写作对象：使用 AutoTestDesign 工具，对独立的 VCU Wake-Sleep Behavior Simulator 的核心决策模块进行测试设计与执行分析。
>
> 注意边界：AutoTestDesign 是测试设计工具；VCU Simulator 是 target application。本文档不能写成测试 AutoTestDesign 工具本身。

---

## 0. Cover Page

需要填写：

| Field | Content |
|---|---|
| Course | Software Testing |
| Assignment | Assignment 2 Final Project |
| Artifact | Detailed Test Design and Execution Document |
| Team ID | [INSERT TEAM ID] |
| Team Members | [INSERT NAMES AND STUDENT IDS] |
| Author of this document | [INSERT YOUR NAME] |
| Target Application | VCU Wake-Sleep Behavior Simulator |
| Selected Module | Wake-Sleep Decision Module |
| Tool Used | AutoTestDesign |
| Date | [INSERT DATE] |
| Version | v1.0 |

需要测试同学提供：最终小组 ID、成员姓名、学号、工具版本、仿真器版本、代码 commit hash。

---

## 1. Introduction

### 1.1 Purpose

本文档说明如何使用 AutoTestDesign 工具，对 VCU Wake-Sleep Behavior Simulator 的核心决策模块完成详细测试设计、测试脚本实现、测试执行和结果分析。

必须体现的评分点：

- 使用 AutoTestDesign 工具生成测试用例。
- 选定 target application 的一个主要 feature/module。
- 使用多种黑盒测试技术。
- 使用白盒测试技术。
- 提供测试执行证据和结果分析。
- 展示人工 tester 对 coverage items、strategies、test cases 的交互式审查与改进。

### 1.2 Target Application and Selected Module

| Item | Description |
|---|---|
| Target Application | VCU Wake-Sleep Behavior Simulator |
| Service Type | FastAPI service |
| Typical Port | 8001 |
| Selected Module | Wake-Sleep Decision Module |
| Main Input Signal | CC2 voltage |
| Supporting Signals | CC voltage, CP amplitude, power supply voltage, network wake-up |
| Output Oracle Fields | test_status, vehicle_state, vehicle_mode, ready_flag |
| Main Endpoints | POST /simulate, POST /simulate/sleep |

需要插入：

- [INSERT SCREENSHOT: VCU Simulator Swagger/OpenAPI page]
- [INSERT SCREENSHOT: POST /simulate API example]
- [INSERT SCREENSHOT: POST /simulate/sleep API example]

需要测试同学提供：接口文档截图、Swagger 截图、Postman/curl/API 调用样例。

### 1.3 Scope

#### In Scope

- CC2 voltage wake-up decision.
- CC2 lower and upper boundary behavior.
- Invalid wake-up rejection.
- Sleep transition behavior.
- Auxiliary signal abnormality handling.
- ready_flag consistency with vehicle_state.
- API-level execution through pytest/httpx.
- Traceability from requirement to risk, coverage item, test case, and result.

#### Out of Scope

- Real HIL bench execution.
- dSPACE SCALEXIO connection.
- ASAM XCP physical communication.
- CAN physical layer validation.
- 1kHz physical sampling validation.
- 20ms hardware emergency stop validation.
- Real vehicle road testing.

说明口径：这些工业级能力来自项目背景和未来扩展；本次 Assignment 2 的执行对象是 SIL-level simulator。

---

## 2. Test Basis

### 2.1 Requirement Sources

| Source | Usage in This Document | Evidence Needed |
|---|---|---|
| Assignment 2 Updated | Determines artifact requirements and scoring criteria | [Already available] |
| VCU simulator specification | Defines input ranges and oracle rules | [INSERT FILE NAME / SCREENSHOT] |
| Risk Analysis Report | Supplies requirement risks and priorities | [INSERT RISK TABLE] |
| AutoTestDesign exported test cases | Supplies generated test cases | [INSERT CSV/JSON/Excel EXPORT] |
| pytest execution outputs | Supplies actual execution evidence | [INSERT TERMINAL OUTPUT / REPORT] |

需要测试同学提供：最终使用的需求基线文件、AutoTestDesign 导出的需求结构化结果、用例导出文件、pytest 报告。

### 2.2 Functional Rules Under Test

建议以 10 条 REQ 作为基线。具体文本以测试同学和代码仓库的最终版本为准。

| Requirement ID | Requirement Description | Expected Oracle | Priority | Evidence Source |
|---|---|---|---|---|
| REQ-001 | CC2 lower boundary wake-up behavior | CC2 = 4.8V should PASS, vehicle_state = 170 | High | [TBD] |
| REQ-002 | CC2 upper boundary wake-up behavior | 7.7V PASS, 7.8V FAIL | High | [TBD] |
| REQ-003 | CC2 out-of-range failure behavior | Out-of-range should FAIL, vehicle_state = 30 | High | [TBD] |
| REQ-004 | Sleep transition behavior | /simulate/sleep returns SLEEP | High | [TBD] |
| REQ-005 | CC voltage abnormal behavior | Abnormal CC range should FAIL | Medium | [TBD] |
| REQ-006 | CP amplitude abnormal behavior | Abnormal CP range should FAIL | Medium | [TBD] |
| REQ-007 | Power supply abnormal behavior | Abnormal power supply range should FAIL | Medium | [TBD] |
| REQ-008 | Network wake-up conflict behavior | network_wakeup = 1 should FAIL | Medium | [TBD] |
| REQ-009 | ready_flag consistency | ready_flag should match wake/fail/sleep state | High | [TBD] |
| REQ-010 | Response structure and weak timing stability | Required response fields exist and response is stable | Low/Medium | [TBD] |

需要测试同学确认：REQ 编号、REQ 原文、优先级、oracle 字段和接口路径。

---

## 3. Concept and Design Rationale

本节对应评分中的 Concept Understanding 和 Coherence of Design & Implementation。

### 3.1 Testing Concept Applied

写作要点：

- 本文采用 risk-based testing 思路，优先测试高风险需求。
- 用 coverage item 表示可验证的测试覆盖目标。
- 用 traceability matrix 连接 requirement、risk、coverage item、test case、execution result。
- 用 AutoTestDesign 支持测试设计自动化与人工交互式审查。

### 3.2 Black-box Techniques

| Technique | Reason for Selection | Applied Area |
|---|---|---|
| Equivalence Partitioning | 输入信号具有明显有效类、无效类、特殊类 | CC2, CC, CP, power supply, network wake-up |
| Boundary Value Analysis | 电压区间边界容易出现 off-by-one 或阈值错误 | CC2 lower/upper boundary, CC/CP/power boundary |
| Decision Table Testing | 多信号组合和 sleep/fail/pass 规则可表示为条件-动作表 | Valid wake-up, auxiliary abnormality, sleep request |

### 3.3 White-box Techniques

| Technique | Reason for Selection | Evidence Needed |
|---|---|---|
| State Transition Testing | VCU output logic can be modeled as Sleep/Idle, Wake Success, Wake Failure, Sleep Confirmed states | [INSERT STATE DIAGRAM OR TABLE] |
| Branch Coverage or Code Coverage | Simulator has deterministic rule branches for PASS/FAIL/SLEEP | [INSERT COVERAGE.PY REPORT IF AVAILABLE] |

如果测试同学没有代码覆盖率报告，则正文写 State Transition Testing 作为主白盒技术，Branch Coverage 放到限制与改进建议中。

### 3.4 GAN Sequence as Complementary Testing

说明：

- EP/BVA 覆盖静态单点输入。
- GAN sequence 覆盖 CC2 电压连续变化、边界穿越和渐变越界。
- GAN 测试不改变 oracle；oracle 仍以仿真器契约为准。
- GAN 用例用于补充 Coverage & Effectiveness，不替代 ISO 29119-4 黑盒技术。

需要插入：

- [INSERT SCREENSHOT: GAN-generated CC2 sequence in AutoTestDesign]
- [INSERT TABLE: GAN sequence test cases and expected transition points]

---

## 4. Coverage Item Identification

本节是全文核心。必须写清“测什么”。

### 4.1 Input Coverage Items

| Coverage Item ID | Signal | Coverage Item | Technique | Requirement ID | Risk Priority |
|---|---|---|---|---|---|
| CI-CC2-EP-01 | CC2 | Valid wake-up partition [4.8, 7.7] | EP | REQ-001/REQ-002 | High |
| CI-CC2-EP-02 | CC2 | Invalid low partition < 4.8 | EP | REQ-003 | High |
| CI-CC2-EP-03 | CC2 | Invalid high partition >= 7.8 | EP | REQ-003 | High |
| CI-CC2-BVA-01 | CC2 | Just below lower boundary 4.7V | BVA | REQ-001 | High |
| CI-CC2-BVA-02 | CC2 | Lower boundary 4.8V | BVA | REQ-001 | High |
| CI-CC2-BVA-03 | CC2 | Just above lower boundary 4.9V | BVA | REQ-001 | High |
| CI-CC2-BVA-04 | CC2 | Just below upper valid boundary 7.6V | BVA | REQ-002 | High |
| CI-CC2-BVA-05 | CC2 | Upper valid boundary 7.7V | BVA | REQ-002 | High |
| CI-CC2-BVA-06 | CC2 | Gray fail boundary 7.8V | BVA | REQ-002/REQ-003 | High |
| CI-CC2-BVA-07 | CC2 | Just above fail boundary 7.9V | BVA | REQ-003 | High |
| CI-SLEEP-01 | Five-signal combo | Sleep transition combination | Decision Table / State | REQ-004 | High |
| CI-READY-01 | Output | ready_flag consistency for PASS | Oracle Coverage | REQ-009 | High |
| CI-READY-02 | Output | ready_flag consistency for FAIL | Oracle Coverage | REQ-009 | High |
| CI-READY-03 | Output | ready_flag consistency for SLEEP | Oracle Coverage | REQ-009 | High |

需要测试同学提供：AutoTestDesign 识别出的 coverage items 原始导出文件，人工修改后的 coverage items 文件。

### 4.2 Output Oracle Coverage Items

| Output Field | PASS Expected Value | FAIL Expected Value | SLEEP Expected Value | Validation Method |
|---|---|---|---|---|
| test_status | 1 | 4 | 3 | pytest assertion |
| vehicle_state | 170 | 30 | 30 | pytest assertion |
| vehicle_mode | 5 | 2 | 2 | pytest assertion |
| ready_flag | 1 | 0 | 0 | pytest assertion |

需要测试同学确认：输出字段名称是否完全一致，是否存在 status/message/detail 等额外字段。

### 4.3 State Coverage Items

| State ID | State Name | Oracle Condition | Covered By Test Case |
|---|---|---|---|
| S0 | Sleep / Idle | vehicle_state = 30, vehicle_mode = 2 | [TBD] |
| S1 | Wake Success | test_status = 1, vehicle_state = 170, ready_flag = 1 | [TBD] |
| S2 | Wake Failure | test_status = 4, vehicle_state = 30, ready_flag = 0 | [TBD] |
| S3 | Sleep Confirmed | test_status = 3, vehicle_state = 30, vehicle_mode = 2 | [TBD] |

需要插入：

- [INSERT FIGURE: State transition diagram]
- [INSERT TABLE: state coverage result]

---

## 5. Coverage Strategy and Method

### 5.1 EP Strategy

| Signal | Valid Partition | Invalid / Special Partition | Representative Values | Expected Result |
|---|---|---|---|---|
| CC2 | [4.8, 7.7] | <4.8, >=7.8 | 6.3, 3.0, 9.0 | PASS / FAIL |
| CC | Normal high voltage | [0.1, 3.9] abnormal | 12.0, 2.0 | PASS / FAIL |
| CP | 0V standby | [9.1, 12.9] abnormal | 0, 11.0 | PASS / FAIL |
| Power Supply | 0V normal | [9.1, 15.9] abnormal | 0, 12.5 | PASS / FAIL |
| Network Wake-up | 0 normal | 1 conflict | 0, 1 | PASS / FAIL |

需要测试同学确认：每个信号名称在 API 请求体中的实际字段名。

### 5.2 BVA Strategy

| Boundary | Values to Test | Expected Results | Requirement |
|---|---|---|---|
| CC2 lower boundary 4.8V | 4.7, 4.8, 4.9 | FAIL, PASS, PASS | REQ-001 |
| CC2 upper boundary 7.7/7.8V | 7.6, 7.7, 7.8, 7.9 | PASS, PASS, FAIL, FAIL | REQ-002/REQ-003 |
| CC abnormal lower region | [TBD] | [TBD] | REQ-005 |
| CP abnormal region | [TBD] | [TBD] | REQ-006 |
| Power abnormal region | [TBD] | [TBD] | REQ-007 |

需要测试同学提供：最终实际执行的 BVA 值。如果工具生成与人工修改后不同，要保留两个版本。

### 5.3 Decision Table Strategy

| Rule ID | CC2 Valid | CC Normal | CP Normal | Power Normal | Network Normal | Sleep Request | Expected Action |
|---|---|---|---|---|---|---|---|
| DT-01 | Y | Y | Y | Y | Y | N | PASS |
| DT-02 | N | - | - | - | - | N | FAIL |
| DT-03 | Y | N | Y | Y | Y | N | FAIL |
| DT-04 | Y | Y | N | Y | Y | N | FAIL |
| DT-05 | Y | Y | Y | N | Y | N | FAIL |
| DT-06 | Y | Y | Y | Y | N | N | FAIL |
| DT-07 | - | - | - | - | - | Y | SLEEP |

需要测试同学提供：AutoTestDesign 生成的决策表原始版本、人工审查后版本、每条规则对应测试用例 ID。

### 5.4 White-box State Transition Strategy

| Transition ID | Start State | Event / Input | Expected End State | Test Case ID |
|---|---|---|---|---|
| T1 | S0 Sleep / Idle | Valid CC2 wake-up signal | S1 Wake Success | [TBD] |
| T2 | S0 Sleep / Idle | Invalid CC2 signal | S2 Wake Failure | [TBD] |
| T3 | S1 Wake Success | Sleep endpoint or sleep combination | S3 Sleep Confirmed | [TBD] |
| T4 | S0 Sleep / Idle | Valid CC2 + abnormal auxiliary signal | S2 Wake Failure | [TBD] |

需要测试同学提供：状态机图、状态转换覆盖表、是否执行了全部 transition。

### 5.5 GAN Sequence Strategy

| Sequence ID | CC2 Sequence | Coverage Purpose | Expected Result |
|---|---|---|---|
| GAN-SEQ-01 | [INSERT SEQUENCE] | Gradual crossing from valid to invalid high range | [TBD] |
| GAN-SEQ-02 | [INSERT SEQUENCE] | Boundary oscillation near 7.7/7.8 | [TBD] |
| GAN-SEQ-03 | [INSERT SEQUENCE] | Gradual recovery into valid range | [TBD] |

需要测试同学提供：GAN 生成的实际序列、执行方式、是否作为单步循环执行、结果如何判断。

---

## 6. AutoTestDesign Prompt Design and Interactive Review

本节必须体现“工具不是一次性生成结果，human tester 会参与审查和修订”。

### 6.1 Prompt for Requirement Structuring

```text
[INSERT ACTUAL PROMPT USED IN AUTOTESTDESIGN]
```

需要测试同学提供：真实 prompt 文本或 prompt 配置文件。

### 6.2 Prompt for Test Case Generation

```text
Generate test cases for the VCU Wake-Sleep Decision Module.
Use Equivalence Partitioning, Boundary Value Analysis, Decision Table Testing, and State Transition Testing.
Input signals include CC2 voltage, CC voltage, CP amplitude, power supply voltage, and network wake-up.
Expected outputs include test_status, vehicle_state, vehicle_mode, and ready_flag.
Return structured test cases with requirement ID, risk ID, coverage item ID, technique, input data, expected output, and priority.
```

最终文本以测试同学真实使用版本为准。

### 6.3 Initial Tool Output Summary

| Output Type | Count | Export File | Screenshot |
|---|---:|---|---|
| Parsed requirements | [TBD] | [TBD] | [TBD] |
| Risk-scored requirements | [TBD] | [TBD] | [TBD] |
| Coverage items | [TBD] | [TBD] | [TBD] |
| Generated test cases | [TBD] | [TBD] | [TBD] |
| Selected test cases for execution | [TBD] | [TBD] | [TBD] |

### 6.4 Interactive Review and Revision Record

| Review Item | Initial Tool Output | Human Tester Revision | Reason | Evidence |
|---|---|---|---|---|
| CC2 lower boundary | [TBD] | Added / confirmed 4.8V PASS | Real HIL data shows 4.8V wake success | [SCREENSHOT] |
| CC2 upper boundary | [TBD] | Treated 7.8V as gray fail boundary | Avoid ambiguity with 7.7 max valid | [SCREENSHOT] |
| Sleep behavior | [TBD] | Separated /simulate/sleep from CC2=12 single-point test | Sleep is a five-signal fixed combination | [SCREENSHOT] |
| db_15 configuration risk | [TBD] | Added residual risk note | 8.1V PASS exists in one batch | [SCREENSHOT] |
| ready_flag consistency | [TBD] | Added oracle coverage item | Output consistency risk | [SCREENSHOT] |

需要测试同学提供：编辑前、编辑后截图；导出前、导出后文件；修改原因说明。

---

## 7. Test Case Design

### 7.1 Test Case Naming Convention

建议格式：

```text
TC-[TECHNIQUE]-[MODULE]-[NUMBER]
Example: TC-BVA-CC2-001
```

### 7.2 Test Case Specification Template

| Field | Description |
|---|---|
| Test Case ID | Unique ID |
| Requirement ID | Linked requirement |
| Risk ID | Linked risk |
| Coverage Item ID | Linked coverage item |
| Technique | EP / BVA / Decision Table / State Transition / GAN |
| Priority | High / Medium / Low |
| Preconditions | Simulator running, endpoint available |
| Input Data | Request body |
| Expected Result | Oracle fields |
| Actual Result | Filled after execution |
| Status | Pass / Fail / Blocked |
| Evidence | Log / screenshot / report row |

### 7.3 EP Test Cases

| Test Case ID | Requirement | Coverage Item | Input | Expected Result | Actual Result | Status | Evidence |
|---|---|---|---|---|---|---|---|
| TC-EP-CC2-001 | REQ-001 | CI-CC2-EP-01 | CC2=6.3 | PASS, state=170, mode=5, ready=1 | [TBD] | [TBD] | [TBD] |
| TC-EP-CC2-002 | REQ-003 | CI-CC2-EP-02 | CC2=3.0 | FAIL, state=30, mode=2, ready=0 | [TBD] | [TBD] | [TBD] |
| TC-EP-CC2-003 | REQ-003 | CI-CC2-EP-03 | CC2=9.0 | FAIL, state=30, mode=2, ready=0 | [TBD] | [TBD] | [TBD] |
| TC-EP-NET-001 | REQ-008 | [TBD] | network_wakeup=1 | FAIL | [TBD] | [TBD] | [TBD] |

### 7.4 BVA Test Cases

| Test Case ID | Requirement | Boundary | Input | Expected Result | Actual Result | Status | Evidence |
|---|---|---|---|---|---|---|---|
| TC-BVA-CC2-001 | REQ-001 | just below min | CC2=4.7 | FAIL | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-002 | REQ-001 | min valid | CC2=4.8 | PASS | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-003 | REQ-001 | just above min | CC2=4.9 | PASS | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-004 | REQ-002 | just below max | CC2=7.6 | PASS | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-005 | REQ-002 | max valid | CC2=7.7 | PASS | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-006 | REQ-003 | gray fail boundary | CC2=7.8 | FAIL | [TBD] | [TBD] | [TBD] |
| TC-BVA-CC2-007 | REQ-003 | above fail boundary | CC2=7.9 | FAIL | [TBD] | [TBD] | [TBD] |

### 7.5 Decision Table Test Cases

| Test Case ID | Rule ID | Input Combination | Expected Action | Actual Result | Status | Evidence |
|---|---|---|---|---|---|---|
| TC-DT-001 | DT-01 | All normal, CC2 valid | PASS | [TBD] | [TBD] | [TBD] |
| TC-DT-002 | DT-02 | CC2 invalid high | FAIL | [TBD] | [TBD] | [TBD] |
| TC-DT-003 | DT-03 | CC2 valid + CC abnormal | FAIL | [TBD] | [TBD] | [TBD] |
| TC-DT-004 | DT-04 | CC2 valid + CP abnormal | FAIL | [TBD] | [TBD] | [TBD] |
| TC-DT-005 | DT-05 | CC2 valid + Power abnormal | FAIL | [TBD] | [TBD] | [TBD] |
| TC-DT-006 | DT-06 | CC2 valid + Network conflict | FAIL | [TBD] | [TBD] | [TBD] |
| TC-DT-007 | DT-07 | Sleep request | SLEEP | [TBD] | [TBD] | [TBD] |

### 7.6 White-box State Transition Test Cases

| Test Case ID | Transition | Input Event | Expected State Transition | Actual Result | Status | Evidence |
|---|---|---|---|---|---|---|
| TC-ST-001 | T1 | Valid CC2 | S0 → S1 | [TBD] | [TBD] | [TBD] |
| TC-ST-002 | T2 | Invalid CC2 | S0 → S2 | [TBD] | [TBD] | [TBD] |
| TC-ST-003 | T3 | Sleep endpoint | S1 → S3 | [TBD] | [TBD] | [TBD] |
| TC-ST-004 | T4 | Auxiliary abnormality | S0 → S2 | [TBD] | [TBD] | [TBD] |

### 7.7 GAN Sequence Test Cases

| Test Case ID | Sequence | Purpose | Expected Observation | Actual Observation | Status | Evidence |
|---|---|---|---|---|---|---|
| TC-GAN-001 | [TBD] | Crossing upper boundary | State changes from PASS to FAIL at boundary | [TBD] | [TBD] | [TBD] |
| TC-GAN-002 | [TBD] | Boundary oscillation | No incorrect PASS beyond fail boundary | [TBD] | [TBD] | [TBD] |
| TC-GAN-003 | [TBD] | Lower boundary approach | PASS begins at 4.8V | [TBD] | [TBD] | [TBD] |

---

## 8. Traceability Matrix

| Requirement ID | Risk ID | Coverage Item ID | Technique | Test Case ID | Priority | Execution Status | Evidence |
|---|---|---|---|---|---|---|---|
| REQ-001 | RISK-[TBD] | CI-CC2-BVA-02 | BVA | TC-BVA-CC2-002 | High | [TBD] | [TBD] |
| REQ-002 | RISK-[TBD] | CI-CC2-BVA-05 | BVA | TC-BVA-CC2-005 | High | [TBD] | [TBD] |
| REQ-003 | RISK-[TBD] | CI-CC2-EP-03 | EP | TC-EP-CC2-003 | High | [TBD] | [TBD] |
| REQ-004 | RISK-[TBD] | CI-SLEEP-01 | DT / State | TC-DT-007 / TC-ST-003 | High | [TBD] | [TBD] |
| REQ-009 | RISK-[TBD] | CI-READY-01/02/03 | Oracle Coverage | Multiple | High | [TBD] | [TBD] |

需要测试同学提供：AutoTestDesign 导出的 traceability matrix，或至少测试用例表中包含 requirement_id、coverage_item_id、technique、result。

---

## 9. Test Tool Implementation

### 9.1 Selected Framework

建议写 PyTest + httpx/requests：

| Item | Selected Tool | Rationale |
|---|---|---|
| Test framework | pytest | Supports parameterized API tests and clear assertions |
| HTTP client | httpx or requests | Suitable for FastAPI endpoint testing |
| Report | pytest terminal output / pytest-html / JUnit XML | Produces execution evidence |
| Coverage | coverage.py | Optional, supports branch/statement coverage |
| Data format | JSON/CSV/Excel exported from AutoTestDesign | Maintains traceability |

### 9.2 Test Environment

| Environment Item | Value |
|---|---|
| OS | [TBD] |
| Python version | [TBD] |
| pytest version | [TBD] |
| VCU Simulator host | [TBD] |
| VCU Simulator port | 8001 |
| AutoTestDesign backend port | 8000 |
| AutoTestDesign frontend port | 3000 |
| Git commit hash | [TBD] |
| Test date/time | [TBD] |

需要测试同学提供：运行环境截图、pip freeze 或 requirements.txt、服务启动截图。

### 9.3 Test Script Structure

```text
[INSERT PROJECT TEST SCRIPT TREE]
example:
tests/
  test_vcu_wake_sleep.py
  test_cc2_bva.py
  test_decision_table.py
  test_sleep_endpoint.py
  data/
    generated_test_cases.csv
    traceability_matrix.csv
```

需要测试同学提供：测试脚本目录截图或文件列表。

### 9.4 Example Test Script

```python
# [INSERT ACTUAL PYTEST CODE SNIPPET]
```

需要测试同学提供：真实 pytest 代码，不需要全量代码时至少提供核心参数化测试片段。

### 9.5 Execution Command

```bash
# [INSERT ACTUAL COMMAND]
pytest tests/test_vcu_wake_sleep.py -v
```

如果有覆盖率：

```bash
coverage run -m pytest tests/test_vcu_wake_sleep.py -v
coverage report -m
```

需要测试同学提供：真实执行命令、终端输出截图、报告文件。

---

## 10. Test Execution Results

### 10.1 Execution Summary

| Metric | Value |
|---|---:|
| Total test cases generated by AutoTestDesign | [TBD] |
| Total test cases selected for execution | [TBD] |
| Total test cases executed | [TBD] |
| Passed | [TBD] |
| Failed | [TBD] |
| Blocked / Skipped | [TBD] |
| Pass rate | [TBD]% |
| Execution time | [TBD] seconds |

需要插入：

- [INSERT SCREENSHOT: pytest summary]
- [INSERT SCREENSHOT: detailed pytest output]
- [INSERT FILE: pytest_result.txt / html report]

### 10.2 Result by Technique

| Technique | Generated | Executed | Passed | Failed | Coverage Achieved |
|---|---:|---:|---:|---:|---:|
| EP | [TBD] | [TBD] | [TBD] | [TBD] | [TBD]% |
| BVA | [TBD] | [TBD] | [TBD] | [TBD] | [TBD]% |
| Decision Table | [TBD] | [TBD] | [TBD] | [TBD] | [TBD]% |
| State Transition | [TBD] | [TBD] | [TBD] | [TBD] | [TBD]% |
| GAN Sequence | [TBD] | [TBD] | [TBD] | [TBD] | [TBD]% |

### 10.3 Failed Test Analysis

如果有 failed cases，必须写 defect-style 分析。

| Failed Test ID | Expected | Actual | Severity | Possible Cause | Follow-up Action |
|---|---|---|---|---|---|
| [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

如果没有 failed cases，写：

- No functional failure was observed in the selected execution set.
- Residual risks remain in untested real-HIL timing, physical CAN behavior, and configuration variants such as db_15 upper boundary extension.

需要测试同学提供：失败用例的请求体、响应体、日志、复现步骤；若无失败，提供全通过证据。

---

## 11. Coverage Analysis

### 11.1 Requirement Coverage

| Requirement ID | Covered by Test Cases | Passed | Coverage Status |
|---|---:|---:|---|
| REQ-001 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-002 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-003 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-004 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-005 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-006 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-007 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-008 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-009 | [TBD] | [TBD] | Covered / Partial / Not Covered |
| REQ-010 | [TBD] | [TBD] | Covered / Partial / Not Covered |

### 11.2 Coverage Item Coverage

| Coverage Type | Total Items | Covered Items | Coverage Rate |
|---|---:|---:|---:|
| EP coverage items | [TBD] | [TBD] | [TBD]% |
| BVA coverage items | [TBD] | [TBD] | [TBD]% |
| Decision table rules | [TBD] | [TBD] | [TBD]% |
| State transition coverage items | [TBD] | [TBD] | [TBD]% |
| Output oracle coverage items | [TBD] | [TBD] | [TBD]% |

### 11.3 Code / Branch Coverage

如果测试同学能提供 coverage.py：

| File | Statement Coverage | Branch Coverage | Missing Lines |
|---|---:|---:|---|
| vcu_simulator/[TBD].py | [TBD]% | [TBD]% | [TBD] |

如果没有：

> Code-level branch coverage was not collected in this execution. Instead, white-box coverage is represented by state transition coverage over the simulator’s exposed behavior model. Branch coverage measurement using coverage.py is listed as a future improvement.

---

## 12. Evidence-based Improvement

此节必须写，直接对应作业“基于证据的改进”。

### 12.1 Initial Gaps Found after Tool Generation

| Gap ID | Initial Gap | Evidence | Impact |
|---|---|---|---|
| GAP-001 | [TBD: e.g., missing CC2=4.8 PASS boundary] | [TBD] | Boundary coverage incomplete |
| GAP-002 | [TBD: e.g., sleep treated as normal CC2=12 FAIL] | [TBD] | Sleep oracle ambiguity |
| GAP-003 | [TBD: missing ready_flag consistency oracle] | [TBD] | Output consistency risk |

### 12.2 Human Review Actions

| Review Action ID | Action | Reason | Resulting New Coverage / Test Case |
|---|---|---|---|
| REV-001 | Added CC2=4.8V boundary PASS case | Real data indicates hardware wake success | TC-BVA-CC2-002 |
| REV-002 | Added 7.8V gray fail boundary case | Clarifies upper boundary | TC-BVA-CC2-006 |
| REV-003 | Separated sleep endpoint test | Avoids mixing sleep with normal FAIL | TC-DT-007 / TC-ST-003 |
| REV-004 | Added ready_flag oracle checks to all PASS/FAIL/SLEEP cases | Ensures output consistency | Multiple cases |
| REV-005 | Added db_15 config risk note | 8.1V PASS batch difference remains | Residual risk entry |

### 12.3 Before-and-after Comparison

| Metric | Before Review | After Review | Improvement |
|---|---:|---:|---|
| Coverage items | [TBD] | [TBD] | [TBD] |
| Test cases | [TBD] | [TBD] | [TBD] |
| BVA cases | [TBD] | [TBD] | [TBD] |
| Decision table rules | [TBD] | [TBD] | [TBD] |
| Oracle fields checked | [TBD] | [TBD] | [TBD] |

需要测试同学提供：交互式修改前后截图、导出文件差异、人工修改说明。

---

## 13. Limitations and Residual Risks

建议写：

| Limitation | Impact | Mitigation / Future Work |
|---|---|---|
| Simulator is deterministic SIL, not real HIL | Cannot validate physical timing and hardware safety | Future HIL integration |
| CAN physical layer not tested | Cannot detect bus-level communication issues | Add CAN/HIL tests later |
| db_15 upper boundary variant not used as default oracle | Version/configuration risk remains | Add configuration-based oracle |
| GAN sequence oracle is simplified | Dynamic transition behavior may require more precise state timing | Add time-series oracle later |
| Code branch coverage may be unavailable | White-box evidence weaker | Add coverage.py report |

---

## 14. Conclusion

结论需要包含：

- AutoTestDesign successfully supported structured test design for the selected VCU module.
- EP, BVA, Decision Table, State Transition, and GAN sequence together covered static, boundary, combinational, state-based, and dynamic scenarios.
- Traceability was maintained from requirements to risks, coverage items, test cases, and execution results.
- Human interactive review improved coverage by adding or correcting boundary, sleep, and oracle consistency cases.
- Remaining risks are mainly real-HIL timing, physical communication, and configuration-variant behavior.

---

## Appendix A. Prompt Records

需要插入：

- [INSERT PROMPT FOR REQUIREMENT STRUCTURING]
- [INSERT PROMPT FOR RISK ANALYSIS]
- [INSERT PROMPT FOR TEST CASE GENERATION]
- [INSERT PROMPT FOR TEST SUITE OPTIMIZATION IF USED]

---

## Appendix B. Exported Artifacts

需要列出：

| File Name | Description | Provided by |
|---|---|---|
| [TBD].json | Structured requirements | Testing teammate |
| [TBD].csv | Risk score table | Testing teammate |
| [TBD].xlsx | Test case export | Testing teammate |
| [TBD].csv | Traceability matrix | Testing teammate |
| [TBD].txt | pytest terminal result | Testing teammate |
| [TBD].html | pytest report | Testing teammate |

---

## Appendix C. Raw Execution Evidence

需要插入或引用：

- [INSERT SCREENSHOT: Services running]
- [INSERT SCREENSHOT: Swagger API]
- [INSERT SCREENSHOT: AutoTestDesign requirement input]
- [INSERT SCREENSHOT: AutoTestDesign risk analysis]
- [INSERT SCREENSHOT: AutoTestDesign generated cases]
- [INSERT SCREENSHOT: Interactive review before/after]
- [INSERT SCREENSHOT: Export center]
- [INSERT SCREENSHOT: pytest command]
- [INSERT SCREENSHOT: pytest summary]
- [INSERT SCREENSHOT: coverage report if available]

