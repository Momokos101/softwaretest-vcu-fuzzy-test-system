# Prompt and Rule Design Notes

This project uses a hybrid AutoTestDesign approach:

- deterministic parsing and test design rules for traceability;
- GAN-based AI test data generation for supplementary VCU signal inputs;
- human interactive review at each major design step.

The current implementation does not rely on a live LLM API during the demo. The "prompt design" artifact is documented as reusable design prompts and rule templates that guided requirement structuring, risk analysis, test case generation, and result analysis.

---

## 1. Requirement Structuring Prompt Template

```text
Given a raw software requirement for the VCU wake-sleep simulator,
extract the following fields:

1. Input Fields: signal names or system variables used as inputs.
2. Data Ranges: numerical ranges or threshold values with units.
3. Conditions: clauses introduced by when, if, while, during, 当, 如果, 若, 在.
4. Expected Actions: expected VCU behavior, output status, state, mode, or ready flag.

Return the result as structured JSON:
{
  "input_fields": [],
  "data_ranges": {},
  "conditions": [],
  "actions": []
}
```

Implementation mapping:

- `input_fields` are extracted by VCU signal aliases such as `CC2电压`, `CC电压值`, `CP幅值`, `供电电压`, and `网络唤醒报文使能状态`.
- `data_ranges` use regular expressions for forms such as `4.8V to 7.7V`, `[4.8, 7.7]V`, `below 4.8V`, and `exceeds 7.8V`.
- `conditions` and `actions` use keyword-based patterns in English and Chinese.
- The tester can edit all extracted fields in the UI before risk analysis or test generation.

---

## 2. Risk Analysis Prompt Template

```text
Given a structured requirement, score it on five 0-10 risk dimensions:

- Criticality: safety or business impact if the behavior fails.
- Boundary Sensitivity: likelihood of boundary-related failures.
- Complexity: number of conditions, inputs, and interactions.
- State Impact: whether it affects VCU state, mode, or READY flag.
- Testability: how clearly the expected behavior can be tested.

Calculate:
score = criticality * 0.35
      + boundary_sensitivity * 0.25
      + complexity * 0.20
      + state_impact * 0.15
      + testability * 0.05

Priority:
High if score >= 7.0
Medium if score >= 4.0
Low otherwise
```

Implementation mapping:

- The backend applies the formula deterministically.
- The frontend allows the tester to adjust each dimension manually.
- Adjusted values are recalculated and stored as the final reviewed risk score.

---

## 3. Black-Box Test Design Prompt Template

```text
Given a structured VCU requirement and selected test techniques,
generate black-box test cases using:

1. Equivalence Partitioning:
   - one representative valid class value;
   - one invalid-low class value;
   - one invalid-high class value.

2. Boundary Value Analysis:
   - lower boundary - delta;
   - lower boundary;
   - lower boundary + delta;
   - midpoint;
   - upper boundary;
   - upper boundary + delta;
   - upper boundary + 2 * delta.

3. Decision Table:
   - map major signal conditions to expected VCU output decisions.

For each test case, include:
requirement_id, technique, signal_name, test_value,
expected_result, expected_status, expected_vehicle_state.
```

Implementation mapping:

- For CC2 voltage `[4.8V, 7.7V]`, BVA with `delta=0.1` generates:

```text
4.7, 4.8, 4.9, 6.3, 7.7, 7.8, 7.9
```

- Expected results are generated from the VCU simulator rules.
- The tester can edit signal name, test value, and expected result before execution.

---

## 4. Test Oracle Prompt Template

```text
For a generated VCU test case, synthesize the expected result:

If expected_result is PASS:
  expected_status = 1
  expected_vehicle_state = 170

If expected_result is FAIL:
  expected_status = 4
  expected_vehicle_state = 30

If expected_result is SLEEP:
  expected_status = 3
  expected_vehicle_state = 30

After executing the test case, compare actual test_status and vehicle_state
with the expected values. The test case verdict is PASS only if both match.
```

Implementation mapping:

- The backend calls `/simulate`, `/simulate/sleep`, or `/simulate/batch`.
- The UI separates:
  - `VCU输出`: actual simulator output (`PASS`, `FAIL`, `SLEEP`);
  - `用例判定`: whether actual output matched expected output.

---

## 5. AI / GAN Supplementary Test Data Prompt

```text
Use the trained GAN component to generate supplementary VCU signal data,
especially CC2 voltage patterns near wake-sleep boundaries.
Compare these generated inputs with traditional EP/BVA test cases.
Use the AI-generated inputs to improve input diversity and explore dynamic
boundary transition behavior.
```

Implementation positioning:

- EP/BVA/Decision Table cases provide standards-based baseline coverage.
- GAN-generated cases provide AI-assisted additional input diversity.
- Human review remains required before including generated cases in final reports.

---

## 6. Result Analysis Prompt Template

```text
Given executed test cases, summarize:

1. Requirement coverage: which requirements have linked test cases.
2. Technique coverage: EP, BVA, Decision Table case counts.
3. VCU behavior: counts of actual PASS, FAIL, and SLEEP outputs.
4. Oracle verdict: counts of passed and failed test case verdicts.
5. Evidence-based improvement: identify missing boundaries or conditions
   and add new coverage items or test cases if needed.
```

Implementation mapping:

- Export includes requirements, risk results, test cases, execution results, and traceability matrix.
- The tester can use the exported Excel workbook as evidence for the Detailed Test Design and Execution Document.
