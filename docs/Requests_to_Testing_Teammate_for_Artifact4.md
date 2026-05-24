# 给负责测试同学的资料需求清单

> 目的：我负责撰写 Assignment 2 的 Artifact 4：Detailed Test Design and Execution Document。这个文档需要基于你运行 AutoTestDesign 工具和 VCU Simulator 的实际证据来写。由于我不直接运行工具，需要你提供可引用、可截图、可复查的测试资料包。
>
> 核心要求：请保留“工具生成初版”和“人工审查修改后版本”两套材料。老师要求体现 human tester 的 interactive review，因此只给最终结果不够。

---

## 1. 请先确认测试对象和版本

### 1.1 系统版本信息

请提供以下信息：

| Item | Please Fill |
|---|---|
| AutoTestDesign frontend URL / port | [e.g., http://localhost:3000] |
| AutoTestDesign backend URL / port | [e.g., http://localhost:8000] |
| VCU Simulator URL / port | [e.g., http://localhost:8001] |
| Git branch | [TBD] |
| Git commit hash | [TBD] |
| Test date and time | [TBD] |
| OS | [TBD] |
| Python version | [TBD] |
| pytest version | [TBD] |
| httpx / requests version | [TBD] |

需要截图：

- [ ] 三个服务启动成功的终端截图。
- [ ] VCU Simulator Swagger/OpenAPI 页面截图。
- [ ] AutoTestDesign 前端首页或功能页截图。

### 1.2 API 基线确认

请确认并提供以下接口信息：

| Endpoint | Confirmed? | Request Example | Response Example |
|---|---|---|---|
| POST /simulate | [Y/N] | [Provide JSON] | [Provide JSON] |
| POST /simulate/sleep | [Y/N] | [Provide JSON] | [Provide JSON] |
| Any GAN sequence execution endpoint | [Y/N] | [Provide JSON] | [Provide JSON] |

需要文件或截图：

- [ ] Swagger 截图：POST /simulate。
- [ ] Swagger 截图：POST /simulate/sleep。
- [ ] 至少一个 PASS 响应样例。
- [ ] 至少一个 FAIL 响应样例。
- [ ] 至少一个 SLEEP 响应样例。

---

## 2. 请提供最终需求基线

我需要在文档中引用 REQ-001 到 REQ-010，所以请提供最终版需求表。

### 2.1 需求表

请提供 CSV / Excel / Markdown 表格，字段如下：

| Requirement ID | Requirement Text | Input Signal | Range / Condition | Expected Action | Expected Output Fields | Priority |
|---|---|---|---|---|---|---|
| REQ-001 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

最低需要包含：

- [ ] CC2 lower boundary rule。
- [ ] CC2 upper boundary rule。
- [ ] CC2 out-of-range failure rule。
- [ ] Sleep transition rule。
- [ ] CC voltage abnormal rule。
- [ ] CP amplitude abnormal rule。
- [ ] Power supply abnormal rule。
- [ ] Network wake-up conflict rule。
- [ ] ready_flag consistency rule。
- [ ] Response structure / timing stability rule。

### 2.2 请明确这些关键 oracle

请确认：

| Scenario | test_status | vehicle_state | vehicle_mode | ready_flag |
|---|---:|---:|---:|---:|
| PASS wake-up | [Expected] | [Expected] | [Expected] | [Expected] |
| FAIL rejection | [Expected] | [Expected] | [Expected] | [Expected] |
| SLEEP transition | [Expected] | [Expected] | [Expected] | [Expected] |

重点确认：

- [ ] CC2=4.8V 是否按 PASS。
- [ ] CC2=7.7V 是否按 PASS。
- [ ] CC2=7.8V 是否按 FAIL。
- [ ] CC2=12.0V 在 /simulate 中是什么结果。
- [ ] /simulate/sleep 的固定五路组合是什么。
- [ ] ready_flag 与 vehicle_state 的一致性规则。

---

## 3. 请导出 AutoTestDesign 工具生成材料

### 3.1 需求输入与结构化解析证据

请提供：

- [ ] 需求导入页面截图。
- [ ] 导入的原始需求文件，CSV / TXT / JSON 均可。
- [ ] 结构化解析结果截图。
- [ ] 结构化解析导出文件。

导出文件最好包含这些字段：

| Requirement ID | Input Fields | Data Ranges | Conditions | Expected Actions | Expected Outputs |
|---|---|---|---|---|---|

### 3.2 风险分析证据

请提供：

- [ ] 风险评分页面截图。
- [ ] 风险矩阵图截图。
- [ ] 风险分析导出文件。

风险表需要包含：

| Requirement ID | Risk ID | Likelihood | Impact | Risk Score | Priority | Rationale |
|---|---|---:|---:|---:|---|---|

如果工具使用 5 维风险评分，请提供每个维度的分数和权重。

### 3.3 Coverage items 证据

请提供：

- [ ] AutoTestDesign 初始识别出的 coverage items。
- [ ] 人工审查修改后的 coverage items。
- [ ] 两者对比说明。

表格字段建议：

| Coverage Item ID | Requirement ID | Signal | Coverage Item | Technique | Priority | Review Status |
|---|---|---|---|---|---|---|

重点覆盖项必须有：

- [ ] CC2 valid partition。
- [ ] CC2 invalid low partition。
- [ ] CC2 invalid high partition。
- [ ] CC2=4.7 / 4.8 / 4.9。
- [ ] CC2=7.6 / 7.7 / 7.8 / 7.9。
- [ ] Sleep transition。
- [ ] ready_flag PASS/FAIL/SLEEP consistency。
- [ ] CC / CP / Power / Network auxiliary abnormality。
- [ ] GAN CC2 dynamic sequence coverage。

### 3.4 测试用例生成证据

请提供 AutoTestDesign 导出的测试用例文件：

- [ ] JSON。
- [ ] CSV。
- [ ] Excel。如果没有 Excel，CSV 可以。

测试用例字段最好包含：

| Test Case ID | Requirement ID | Risk ID | Coverage Item ID | Technique | Input Data | Expected Result | Priority | Review Status |
|---|---|---|---|---|---|---|---|---|

请同时提供：

- [ ] 工具生成初版测试用例截图。
- [ ] 人工修改后测试用例截图。
- [ ] 最终执行用例列表。

---

## 4. 请保留 Interactive Review 证据

老师明确要求工具体现 human tester 的参与。请不要只给最终表格。

### 4.1 需要截图的交互式修改过程

请至少提供 5 组“前后对比”证据：

| Review Evidence ID | Screenshot Before | Screenshot After | What Changed | Why Changed |
|---|---|---|---|---|
| REV-001 | [file] | [file] | Added / confirmed CC2=4.8 PASS case | Real data indicates wake success |
| REV-002 | [file] | [file] | Added 7.8 gray fail boundary | Clarify upper boundary |
| REV-003 | [file] | [file] | Separated /simulate/sleep from CC2=12 | Avoid sleep oracle ambiguity |
| REV-004 | [file] | [file] | Added ready_flag consistency check | Output oracle completeness |
| REV-005 | [file] | [file] | Added db_15 config risk note | Batch/configuration variant |

如果工具界面不能直接显示前后对比，请提供：

- [ ] 修改前导出文件。
- [ ] 修改后导出文件。
- [ ] 简短文字说明。
- [ ] 截图证明该工具支持编辑。

### 4.2 人工审查说明

请写一个 200-300 字说明，回答：

1. 工具初版输出遗漏了什么？
2. 人工 tester 修改了哪些 coverage items、strategies、test cases？
3. 修改后新增了哪些有效测试用例？
4. 这些修改怎样提升覆盖度？

---

## 5. 请提供 Prompt 记录

我需要写 Prompt Design 章节。请提供工具实际使用的 prompt。

### 5.1 Prompt 文件或文本

请提供：

- [ ] Requirement structuring prompt。
- [ ] Risk analysis prompt。
- [ ] Test case generation prompt。
- [ ] Test oracle generation prompt，如果有。
- [ ] Test suite optimization prompt，如果有。

每个 prompt 请说明：

| Prompt Name | Used For | Input | Output | File / Screenshot |
|---|---|---|---|---|

### 5.2 Prompt 输出样例

每类 prompt 至少给一个输出样例：

- [ ] 结构化需求样例。
- [ ] 风险评分样例。
- [ ] 测试用例样例。
- [ ] traceability 样例。

---

## 6. 请提供具体执行用例清单

### 6.1 用例数量汇总

请填写：

| Technique | Generated by Tool | Selected for Execution | Executed | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|---:|---:|
| EP | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| BVA | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Decision Table | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| State Transition | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| GAN Sequence | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### 6.2 必须覆盖的最小测试集

请确保至少执行或给出未执行原因：

#### EP

- [ ] CC2=6.3V → PASS。
- [ ] CC2=3.0V → FAIL。
- [ ] CC2=9.0V → FAIL。
- [ ] CC abnormal value，如 2.0V → FAIL。
- [ ] CP abnormal value，如 11.0V → FAIL。
- [ ] Power abnormal value，如 12.5V → FAIL。
- [ ] Network wake-up=1 → FAIL。

#### BVA

- [ ] CC2=4.7V → FAIL。
- [ ] CC2=4.8V → PASS。
- [ ] CC2=4.9V → PASS。
- [ ] CC2=7.6V → PASS。
- [ ] CC2=7.7V → PASS。
- [ ] CC2=7.8V → FAIL。
- [ ] CC2=7.9V → FAIL。

#### Decision Table

- [ ] All normal → PASS。
- [ ] CC2 invalid → FAIL。
- [ ] CC2 valid + CC abnormal → FAIL。
- [ ] CC2 valid + CP abnormal → FAIL。
- [ ] CC2 valid + Power abnormal → FAIL。
- [ ] CC2 valid + Network conflict → FAIL。
- [ ] Sleep request → SLEEP。

#### White-box State Transition

- [ ] Sleep/Idle → Wake Success。
- [ ] Sleep/Idle → Wake Failure。
- [ ] Wake Success → Sleep Confirmed。
- [ ] Sleep/Idle → Failure caused by auxiliary signal abnormality。

#### GAN Sequence

- [ ] 一组从有效区间渐变到 7.8V 以上的序列。
- [ ] 一组围绕 7.7/7.8 边界振荡的序列。
- [ ] 一组接近 4.8V 下界的序列。

---

## 7. 请提供 pytest 脚本与执行证据

### 7.1 测试脚本

请提供：

- [ ] tests 目录结构截图。
- [ ] 主要 pytest 文件。
- [ ] 参数化测试代码片段。
- [ ] 测试数据文件。

建议文件：

```text
tests/
  test_vcu_wake_sleep.py
  test_cc2_bva.py
  test_decision_table.py
  test_sleep_endpoint.py
  data/
    generated_test_cases.csv
    traceability_matrix.csv
```

### 7.2 运行命令

请提供真实命令，例如：

```bash
pytest tests/test_vcu_wake_sleep.py -v
```

如果有 coverage：

```bash
coverage run -m pytest tests/test_vcu_wake_sleep.py -v
coverage report -m
```

### 7.3 执行结果

请提供：

- [ ] 终端运行截图。
- [ ] pytest 完整文本输出。
- [ ] pytest-html 报告，如有。
- [ ] JUnit XML 报告，如有。
- [ ] 失败用例的 request/response 日志，如有。
- [ ] 全部通过时的 summary 截图。

请输出一个汇总表：

| Metric | Value |
|---|---:|
| Total executed | [TBD] |
| Passed | [TBD] |
| Failed | [TBD] |
| Skipped | [TBD] |
| Pass rate | [TBD]% |
| Execution time | [TBD] |

---

## 8. 请提供覆盖率相关数据

### 8.1 Requirement Coverage

| Requirement ID | Test Cases Covering It | Result | Coverage Status |
|---|---|---|---|
| REQ-001 | [TBD] | [TBD] | Covered / Partial / Not Covered |

### 8.2 Coverage Item Coverage

| Coverage Type | Total Items | Covered Items | Coverage Rate |
|---|---:|---:|---:|
| EP coverage items | [TBD] | [TBD] | [TBD]% |
| BVA coverage items | [TBD] | [TBD] | [TBD]% |
| Decision table rules | [TBD] | [TBD] | [TBD]% |
| State transition items | [TBD] | [TBD] | [TBD]% |
| Output oracle items | [TBD] | [TBD] | [TBD]% |

### 8.3 Code / Branch Coverage

如果可以运行 coverage.py，请提供：

- [ ] coverage report 终端截图。
- [ ] coverage html 页面截图。
- [ ] coverage.xml 或 .coverage 文件。

表格：

| File | Statement Coverage | Branch Coverage | Missing Lines |
|---|---:|---:|---|
| vcu_simulator/[file].py | [TBD]% | [TBD]% | [TBD] |

如果无法提供代码覆盖率，请说明原因。我会在文档中把白盒技术写成 state transition testing，并把 branch coverage 作为 future improvement。

---

## 9. 如果发现缺陷，请保留 defect evidence

如果有失败用例，请不要只说“失败了”。需要保留缺陷报告信息。

| Defect ID | Failed Test Case | Severity | Priority | Expected | Actual | Steps to Reproduce | Evidence |
|---|---|---|---|---|---|---|---|
| DEF-001 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

每个缺陷至少要给：

- [ ] request body。
- [ ] response body。
- [ ] pytest assertion failure。
- [ ] server log，如有。
- [ ] 复现命令。

如果没有发现缺陷，请提供全通过证据，并说明执行范围。

---

