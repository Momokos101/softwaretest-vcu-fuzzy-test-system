# Member 2 Tool Developer Deliverables

> Purpose: This document collects the materials owned by Member 2 for the final project package, including the tool explanation, demo script, Testing Framework and Rationale, Cost Estimation, and AI-driven positioning.

---

## 1. Tool Scope

Member 2 is responsible for the AutoTestDesign tool implementation. The tool is applied to a separate target application: the VCU wake-sleep behavior simulator in `vcu_simulator/`.

The implemented workflow is:

```text
Requirement Import -> Requirement Structuring -> Risk Analysis -> Test Case Generation
-> Simulator Execution -> Oracle Comparison -> Export
```

The tool implements the mandatory functional requirements:

| Requirement | Implementation |
|---|---|
| FR 1.0 Input / Parsing | CSV upload, pasted plain text, and direct form input. |
| FR 1.1 Requirement Structuring | Regex-based extraction of Input Fields, Data Ranges, Conditions, and Expected Actions. |
| FR 2.0 Risk Analysis & Prioritization | Five-dimension risk scoring with High / Medium / Low priority. |
| FR 3.0 Black-Box Test Design | Equivalence Partitioning, Boundary Value Analysis, and Decision Table generation. |
| FR 5.0 Test Oracle Generation | Expected `test_status` and `vehicle_state` are generated for each test case and compared with actual simulator output. |
| FR 6.0 Output & Export | JSON, CSV, and Excel export with requirements, risk scores, test cases, execution results, and traceability matrix. |

FR 4.0 and FR 7.0 are not claimed as completed in the current tool. They can be discussed as future improvements or optional extensions.

---

## 2. Demo CSV

The demo CSV is included in:

```text
docs/demo_vcu_requirements.csv
```

Use this file in the demo step "Upload VCU requirements CSV". It contains 10 VCU wake-sleep requirements derived from the simulator specification.

Expected upload behavior:

- The tool imports 10 requirements.
- For `REQ-001`, parsing should identify:
  - Input Field: `CC2电压`
  - Data Range: `4.8` to `7.7`
  - Condition: `CC2 voltage is 4.8V to 7.7V`
  - Expected Action: wake / `vehicle_state=170`

If the parser misses or imperfectly extracts a field, use the Interactive Review section to edit the parsed result manually. This is intentional and demonstrates the required designer participation.

---

## 3. Demo Script

Recommended demo length: about 5 to 6 minutes.

| Time | Action | Evidence Shown |
|---|---|---|
| 0:00-0:30 | Show two terminals: VCU simulator on port 8001 and AutoTestDesign backend on port 8000. | Confirms separate tool and target application. |
| 0:30-1:20 | Open `需求管理`, upload `docs/demo_vcu_requirements.csv`, and parse `REQ-001`. | Demonstrates FR 1.0 and FR 1.1. |
| 1:20-1:50 | Expand parsed result and manually edit one Data Range or Action field. | Demonstrates Interactive Review. |
| 1:50-2:40 | Open `风险分析`, analyze the requirement, then adjust one risk dimension. | Demonstrates FR 2.0 and human review. |
| 2:40-4:20 | Open `测试设计`, select the requirement, choose `ALL`, set BVA delta to `0.1`, generate cases, edit one case, and execute all cases. | Demonstrates FR 3.0 and FR 5.0. |
| 4:20-5:10 | Point out the separate columns `VCU输出` and `用例判定`. | Shows actual simulator behavior vs oracle result. |
| 5:10-5:50 | Open `导出中心`, export Excel, and show multiple sheets. | Demonstrates FR 6.0 and traceability. |

Important explanation during the demo:

```text
The table's "用例判定" means whether actual output matches expected output.
For invalid inputs, the VCU may output FAIL, and the test case can still be judged as passed
because FAIL was the expected result.
```

---

## 4. Testing Framework and Rationale

The testing framework for executing the generated tests against the target application is based on HTTP-level integration testing. The VCU simulator is implemented as a FastAPI service on port 8001, and the AutoTestDesign backend calls it through `httpx`. This is appropriate because the target application exposes stable REST endpoints (`/simulate`, `/simulate/sleep`, and `/simulate/batch`) and does not require a browser or physical hardware interface for execution. HTTP-level execution keeps the framework lightweight, repeatable, and easy to automate in CI or during a classroom demo.

The tool uses a staged data flow. First, FR 1.0 imports requirements from CSV, plain text, or form input. FR 1.1 then structures each requirement into input fields, data ranges, conditions, and expected actions. FR 2.0 assigns each requirement a risk score using five weighted dimensions: criticality, boundary sensitivity, complexity, state impact, and testability. FR 3.0 uses the structured requirement and known VCU signal rules to generate Equivalence Partitioning, Boundary Value Analysis, and Decision Table test cases. During execution, FR 5.0 compares the generated expected result with the actual VCU simulator response. Finally, FR 6.0 exports requirements, risk scores, test cases, execution results, and the traceability matrix to JSON, CSV, or Excel.

Interactive Review is implemented through editable UI controls connected to PUT APIs. The tester can revise raw requirements, parsed structures, risk scores, and generated test cases before executing or exporting them. This design ensures that the tool supports human tester participation rather than acting as an opaque automatic generator.

---

## 5. Cost Estimation

The following estimate compares manual VCU test design work with tool-assisted work for the same requirement set.

| Activity | Manual Effort | Tool-Assisted Effort | Saving |
|---|---:|---:|---:|
| Requirement parsing | 6h | 1h | 83% |
| Risk assessment | 5h | 1h | 80% |
| EP/BVA test case design | 20h | 3h | 85% |
| Decision Table design | 8h | 2h | 75% |
| Test execution and result recording | 10h | 2h | 80% |
| Export and traceability preparation | 4h | 0.5h | 88% |
| **Total** | **53h** | **9.5h** | **82%** |

The largest saving comes from systematic test case generation and automatic result recording. Manual testing still remains necessary for reviewing parsed requirements, validating risk scores, and confirming that generated test cases match the intended coverage strategy.

---

## 6. AI-Driven Positioning

The tool is AI-driven through the integration of the existing GAN-based VCU test data generation component in the repository. The standard EP/BVA/Decision Table generator provides deterministic and explainable baseline coverage, while the GAN component can generate additional VCU signal inputs learned from historical VCU data, especially CC2 voltage patterns.

The project therefore uses a hybrid design:

- Rule-based methods provide traceable and auditable test design artifacts.
- The GAN component provides AI-assisted supplementary test data for input diversity and boundary-transition exploration.
- Human testers remain in the loop through interactive review and manual correction.

This positioning is safer than claiming that every part of the tool is AI-generated. It also matches software testing practice: deterministic techniques are used where standards require explainable coverage, and AI is used where it adds value by increasing input diversity.

Suggested presentation wording:

```text
Our AutoTestDesign tool combines explainable rule-based test design with an AI-driven GAN component.
The rule-based part guarantees traceable EP, BVA, and Decision Table cases.
The GAN component supplements these cases by generating additional VCU signal patterns learned from historical data.
```

---

## 7. Non-Functional Requirement Notes

| NFR | Evidence |
|---|---|
| Performance | Requirement parsing, risk scoring, and test case generation are deterministic in-memory operations and complete quickly for the 10-requirement demo CSV. |
| Usability | The frontend provides dedicated pages for requirements, risk analysis, test design, and export. The test result table separates actual VCU output from test case verdict to avoid ambiguity. |
| Security | The tool is designed for local classroom/demo use. File upload is limited to CSV requirement import. |
| Maintainability | Backend logic is separated into routers, services, and Pydantic schemas. Frontend pages are separated by feature area. |

---

## 8. Known Limitations and Improvement Plan

| Limitation | Improvement |
|---|---|
| FR 4.0 white-box state transition modeling is not fully implemented in the tool UI. | Add a state-machine editor and all-states/all-transitions sequence generator. |
| FR 7.0 optimization is not fully implemented as a separate feature. | Add risk-based sorting and duplicate/minimal-suite reduction. |
| Requirement parsing is regex-based, so unusual wording may need manual correction. | Add an LLM-assisted parser or configurable parsing templates. |
| Data is currently stored in memory for the AutoTestDesign demo flow. | Persist requirements, risks, and test cases to SQLite. |
