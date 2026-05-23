# Risk Analysis Report
## VCU Behavior Simulator V2

**Document Type**: Artifact 2 — Risk Analysis Report
**Target Application**: VCU Behavior Simulator V2
**Standard Basis**: ISO 9126 quality characteristics, risk-based testing, IEEE 829 style test planning
**Date**: 2026-05

---

## Chapter 1: Target Application Overview

The target application is a Software-in-the-Loop VCU behavior simulator. It models the wake, initialization, run, sleep, protection, CAN communication, diagnostic, and power-monitoring behavior of a vehicle control unit.

The simulator is not the AutoTestDesign Tool itself. It is the System Under Test. The tool sends HTTP test inputs to the simulator and compares actual outputs with generated test oracles. This separation allows the project to demonstrate a complete testing workflow:

```text
Requirements -> Risk Analysis -> Test Design -> Test Execution -> Result Analysis -> Export
```

The simulator exposes a FastAPI service on port `8001`.

| Endpoint | Purpose |
|----------|---------|
| `POST /simulate` | Main V2 execution interface |
| `POST /simulate/sleep` | Compatibility/demo sleep shortcut |
| `POST /simulate/batch` | Batch execution |
| `POST /reset` | Reset state machine and optionally clear DTC |
| `GET /state` | Query current VCU state |
| `GET/PUT /config` | Query/update thresholds |
| `GET /dtc` | Query diagnostic trouble codes |
| `GET /performance` | Query duration statistics |

`/simulate` is the formal interface for requirement coverage. `/simulate/sleep` is a convenience interface and is not used as formal evidence for h1/h2/h3 sleep-condition coverage.

---

## Chapter 2: Test Scope and Boundaries

### 2.1 In Scope

The V2 simulator contains five functional modules:

| Module | Function | Main Requirements |
|--------|----------|-------------------|
| Module A | Power state management | REQ-001~014 |
| Module B | Signal guard | REQ-015~017 |
| Module C | CAN communication management | REQ-018~019 |
| Module D | DTC management | REQ-020~022 |
| Module E | Power monitoring | REQ-023~024 |

The main state model is:

```text
state09 -> state10 -> state11
state11 -> state09
state10 -> stuck fault
any wake input + overvoltage -> fault_protection
any wake input + undervoltage -> undervoltage_shutdown
```

### 2.2 Out of Scope

- Physical CAN bus arbitration and bit-level timing
- Real ADC sampling and hardware noise
- Firmware flashing, secure boot, HSM, encryption, or UDS session control
- Multi-VCU network topology
- Real battery management system internals

These boundaries are important because the project evaluates software testing design, not hardware validation.

---

## Chapter 3: Requirements List

| ID | Module | Title | Summary |
|----|--------|-------|---------|
| REQ-001 | A | Supply voltage wake | `supply_voltage > 9V` and `duration_ms >= 10` wakes VCU |
| REQ-002 | A/C | CAN wake | CAN ID `[0x400,0x47F]` wakes VCU |
| REQ-003 | A | CP wake | `cp_voltage > 9V` wakes VCU |
| REQ-004 | A | CC wake | `cc_voltage < 4.4V` wakes VCU |
| REQ-005 | A | CC2 wake | `cc2_voltage < ubr_threshold` wakes VCU |
| REQ-006 | A | Hood wake | `hood_voltage > 4V` and `duration_ms >= 10` wakes VCU |
| REQ-007 | A | Door wake | `door_voltage < 1V` and `duration_ms >= 10` wakes VCU |
| REQ-008 | A | Sleep h1 | `VCUIdle_flg=1` is necessary for sleep |
| REQ-009 | A | Sleep h2 | `AuthComplete_flg=1` is necessary for sleep |
| REQ-010 | A/C | Sleep h3 | CAN stop is necessary for sleep |
| REQ-011 | A | Sleep conjunction | h1 AND h2 AND h3 are required for `state09` |
| REQ-012 | A/D | state10 stuck | Rapid wake-sleep cycles trigger stuck state and DTC_001 |
| REQ-013 | A | Output consistency | `bus_message_flag` follows state |
| REQ-014 | A | Duration compliance | type1 <= 20s, type2 <= 60s |
| REQ-015 | B | Overvoltage protection | `supply_voltage > 16V` enters `fault_protection` |
| REQ-016 | B | Undervoltage shutdown | `supply_voltage < 6V` enters `undervoltage_shutdown` |
| REQ-017 | B | Debounce | timing signals under 5ms are rejected |
| REQ-018 | C | CAN ID filter | only `[0x400,0x47F]` is accepted |
| REQ-019 | C | CAN bus_off | `error_counter > 255` sets `bus_off_flag=1` |
| REQ-020 | D | DTC creation | DTC_001/002/003 are generated for stuck/overvoltage/undervoltage |
| REQ-021 | D | DTC query | `/dtc` returns code, status, count, timestamp |
| REQ-022 | D | DTC clear | `/reset?clear_dtc=true` clears DTC status |
| REQ-023 | E | Power alarm | high current in state11 triggers alarm |
| REQ-024 | E | Sleep power compliance | state09 current must be <= 0.01A |

---

## Chapter 4: Risk Assessment Method

This report uses the Chapter 4 risk framework:

- **Technical Risk**: probability that the implementation is wrong or fragile.
- **Business Risk**: impact of failure on safety, reliability, or test credibility.
- **RPN**: `Technical Risk x Business Risk`, where lower values indicate higher priority.

| RPN Range | Test Depth |
|-----------|------------|
| 1-5 | Extensive |
| 6-10 | Broad |
| 11-15 | Cursory |
| 16-25 | Opportunity |

The quality categories follow ISO 9126:

| ISO 9126 Characteristic | Simulator Focus |
|-------------------------|-----------------|
| Functionality | correct wake/sleep/CAN/DTC behavior |
| Reliability | stuck detection and recovery behavior |
| Efficiency | duration and power-current constraints |
| Maintainability | clear DTC and API observability |
| Portability | HTTP service usable by tool backend |

---

## Chapter 5: Quality Risk Summary

| QR-ID | Quality Risk | ISO 9126 | Tech Risk | Bus Risk | RPN | Depth | Trace |
|-------|--------------|----------|-----------|----------|-----|-------|-------|
| QR-1.1 | wake threshold or timing boundary wrong | Functionality/Accuracy | 2 | 2 | 4 | Extensive | REQ-001/006/007 |
| QR-1.2 | sleep enters with missing h1/h2/h3 | Functionality/Suitability | 2 | 2 | 4 | Extensive | REQ-008~011 |
| QR-1.3 | state10 stuck fault not detected | Reliability/Maturity | 1 | 1 | 1 | Extensive | REQ-012/020 |
| QR-1.4 | output flags inconsistent with state | Functionality/Accuracy | 3 | 2 | 6 | Broad | REQ-013 |
| QR-1.5 | duration constraint not enforced | Efficiency/Time Behaviour | 3 | 2 | 6 | Broad | REQ-014 |
| QR-2.1 | overvoltage/undervoltage guard missing | Reliability/Maturity | 2 | 1 | 2 | Extensive | REQ-015/016 |
| QR-2.2 | debounce accepts transient noise | Reliability/Maturity | 3 | 2 | 6 | Broad | REQ-017 |
| QR-3.1 | CAN ID range boundary wrong | Functionality/Interoperability | 3 | 2 | 6 | Broad | REQ-018 |
| QR-3.2 | bus_off not triggered/reset correctly | Reliability/Fault Tolerance | 3 | 2 | 6 | Broad | REQ-019 |
| QR-4.1 | DTC not generated for high-risk faults | Maintainability/Analysability | 2 | 2 | 4 | Extensive | REQ-020 |
| QR-4.2 | DTC query or clear lifecycle wrong | Maintainability/Analysability | 4 | 3 | 12 | Cursory | REQ-021/022 |
| QR-5.1 | high power current alarm missing | Efficiency/Resource Utilisation | 3 | 2 | 6 | Broad | REQ-023 |
| QR-5.2 | sleep power rule not checked | Efficiency/Resource Utilisation | 4 | 2 | 8 | Broad | REQ-024 |

Highest priority risk: **QR-1.3 state10 stuck fault not detected**. This is based on a real engineering defect scenario and directly affects reliability and power consumption.

---

## Chapter 6: Test Suite Prioritization

| Suite | Technique | Reason | Risk Coverage |
|-------|-----------|--------|---------------|
| Suite A Wake EP | Equivalence Partitioning | valid/invalid wake classes | QR-1.1 |
| Suite B Wake BVA | Boundary Value Analysis | 9V, 10ms, 4V, 1V boundaries | QR-1.1 |
| Suite C Sleep Decision Table | Decision Table | h1/h2/h3 combinations | QR-1.2 |
| Suite D State Transition | State Transition Testing | all states and transitions | QR-1.2/1.3 |
| Suite E Stuck Scenario | Scenario + Sequence | rapid wake-sleep reproduction | QR-1.3 |
| Suite F Signal Guard | EP + BVA | 6V, 16V, 5ms boundaries | QR-2.1/2.2 |
| Suite G CAN | EP + BVA + Decision Table | CAN ID and bus_off states | QR-3.1/3.2 |
| Suite H DTC | State/lifecycle testing | active -> cleared lifecycle | QR-4.1/4.2 |
| Suite I Power | BVA | current and duration thresholds | QR-5.1/5.2 |
| Suite J Performance | Performance Testing | `actual_duration` limits | QR-1.5 |

This suite design intentionally mixes black-box and white-box techniques:

- EP and BVA for numeric boundaries
- Decision tables for logical combinations
- State transition testing for VCU state coverage
- Scenario testing for the known stuck defect
- Performance testing for non-functional timing requirements

---

## Chapter 7: Exit Criteria and Current Evidence

### 7.1 Exit Criteria

| Level | Criteria |
|-------|----------|
| Component | Module B/C/D/E unit paths pass |
| Integration | `/simulate`, `/state`, `/dtc`, `/config`, `/performance` callable |
| System | High-risk requirements pass; stuck fault reproducible with DTC evidence |
| Regression | Existing backend simulator client does not break |

### 7.2 Current Evidence

Current local verification:

```text
vcu_simulator/.venv/bin/python -m unittest tests/test_vcu_simulator_v2.py
Ran 15 tests
OK
```

Additional checks reported by integration verification:

- Simulator pytest set: 15 passed, 7 subtests passed
- API routes + simulator: 18 passed, 3 warnings, 7 subtests passed
- BAIC adapter unit test passed after proxy environment removal
- Backend E2E script completed for health, test plans, test tasks, reports, and error handling
- FastAPI key endpoints manually checked: `/health`, `/simulate`, `/reset`, `/config`, `/simulate/sleep`

Known unrelated limitation:

- GAN generation returns 500 when `model_weights/vcu` is missing. This is outside VCU simulator V2 scope.

---

## Appendix: Interface Contract Note

`/simulate/sleep` is a compatibility/demo shortcut. It internally creates the V2 sleep condition h1/h2/h3 and is useful for quick demonstrations. It must not be counted as formal evidence for REQ-008 through REQ-011.

Formal sleep-condition coverage must use `/simulate` with:

```json
{
  "VCUO_bDIAG_VCUIdle_flg": 1,
  "VCUO_bDIAG_AuthComplete_flg": 1,
  "can_stopped": true
}
```

This is an intentional interface-contract decision and should be documented in the test plan traceability matrix.
