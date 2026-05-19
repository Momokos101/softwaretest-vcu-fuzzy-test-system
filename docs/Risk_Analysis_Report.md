# Risk Analysis Report
## VCU Wake-Sleep Control Module — Behavior Simulator

**Document Type**: Artifact 2 — Risk Analysis Report  
**Target Application**: VCU (Vehicle Control Unit) Wake-Sleep Control Module Simulator  
**Data Basis**: 5 real BAIC VCU HIL test databases (db_10 / db_11 / db_15 / db / db_2), **9615 records total**  
**Date**: 2026-05  

---

## Chapter 1: Target Application Overview

### 1.1 What is the VCU Wake-Sleep Control Module?

VCU (Vehicle Control Unit，整车控制器) is the central control brain of an electric vehicle. The Wake-Sleep Control Module is one of its most critical sub-functions: it monitors charging port signals and decides when the vehicle should **wake up** (activate charging mode) and when it should **go to sleep** (enter low-power standby).

In plain terms: every time a charging gun is plugged in, the VCU checks a set of electrical signals to determine whether the connection is safe and valid. If it is, the vehicle wakes up and begins charging. If the signals are abnormal — for example, if the charging cable has a fault, or there is a protocol conflict — the VCU refuses to wake up and returns a failure state. This prevents faulty charging from damaging the battery or posing a safety risk.

### 1.2 Position in the EV Charging System

```
Charging Station (EVSE)
        │
        │  CC2 voltage (~6V)     ← Main wake signal
        │  CC voltage            ← Cable contact check
        │  CP pilot signal       ← AC protocol handshake
        ▼
  Charging Port Connector
        │
        ▼
  VCU Wake-Sleep Module   ←──── Supply Voltage (abnormal external power check)
        │                 ←──── Network Wake Enable (CAN remote wake check)
        │
        ├── PASS  → vehicle_state=170, mode=5, ready_flag=1 (charging proceeds)
        ├── SLEEP → vehicle_state=30,  mode=2, ready_flag=0 (normal sleep)
        └── FAIL  → vehicle_state=30,  mode=2, ready_flag=0 (fault detected)
```

### 1.3 Why Use a Software Simulator Instead of Real Hardware

Using a Software-In-the-Loop (SIL) simulator instead of a physical HIL test bench is standard industry practice for the following reasons:

1. **Cost and availability**: Physical VCU test benches (HIL rigs) cost tens of thousands of dollars and require lab facilities. A software simulator provides full functional coverage at zero hardware cost.
2. **Safety**: Sending fault signals (e.g., overvoltage, protocol conflicts) to real hardware risks damaging expensive components. A simulator accepts any input safely.
3. **Repeatability**: Software behavior is 100% deterministic; test results never vary due to environmental factors like temperature or connector wear.
4. **Industry precedent**: The automotive industry mandates SIL testing before HIL testing in development workflows (e.g., ISO 26262 V-model). Our simulator reflects this standard approach.
5. **Data authenticity**: All boundary values in the simulator are derived from 9615 real HIL test records, making the simulator faithfully representative of the real system's behavior.

### 1.4 Simulator API Design

The simulator is an independent FastAPI service on **port 8001**, accepting HTTP requests. This decouples the test tool from the target application, enabling independent development and clear interface contracts.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/simulate` | POST | Single-signal test (main interface) |
| `/simulate/sleep` | POST | Sleep test (fixed 5-signal combination) |
| `/simulate/batch` | POST | Batch test (array input) |
| `/health` | GET | Service health check |
| `/signals` | GET | Signal boundary reference |
| `/reset` | POST | State machine reset |

**Request format** (single-signal test):
```json
{"signal_name": "CC2电压", "value": 6.3, "data_type": "float"}
```

**Response format**:
```json
{
  "test_status": 1,       "vehicle_state": 170,
  "vehicle_mode": 5,      "ready_flag": 1,
  "bms_wake_cmd": 1,      "mcu_wake_cmd": 1,
  "battery_voltage": 12.92, "actual_duration": 100.4,
  "detail": "CC2电压=6.3V ∈ [4.8,7.7]V → 正常唤醒 vehicle_state=170"
}
```

---

## Chapter 2: Test Scope and Boundaries

### 2.1 In Scope: 5 Input Signals

| Signal | Physical Meaning | Valid Range (PASS) | Invalid Range (FAIL) |
|--------|-----------------|-------------------|---------------------|
| **CC2电压** | AC charging wake-up voltage | [4.8V, 7.7V] | <4.8V or >7.8V |
| **CC电压值** | Charging gun cable contact voltage | >4.0V | [0.1V, 3.9V] |
| **CP幅值** | AC protocol pilot signal amplitude | 0.0V (standby) | [9.1V, 12.9V] |
| **供电电压** | External AC supply voltage | 0.0V (none) | [9.1V, 15.9V] |
| **网络唤醒报文使能状态** | Network remote wake enable flag | 0 (disabled) | 1 (conflict) |

Three test scenarios are modeled:
- **Strategy 0** (normal wake): Single valid CC2 voltage signal → PASS
- **Strategy 1** (fault injection): Single invalid signal → FAIL
- **Strategy -3** (sleep test): Fixed 5-signal combination → SLEEP

### 2.2 Out of Scope

- VCU internal firmware logic (state machine transitions beyond wake/sleep)
- CAN bus physical layer (bit timing, arbitration)
- Multi-signal simultaneous injection (other than the defined sleep combination)
- Hardware-layer faults (transient noise states vehicle_state=12/46)
- Battery management system (BMS) internal logic

---

## Chapter 3: Requirements List

The following 10 requirements are derived from analysis of 5 real BAIC VCU HIL test databases. Each requirement corresponds to a testable behavior of the VCU simulator.

| ID | Title | Description | Category |
|----|-------|-------------|----------|
| REQ-001 | CC2 Wake Voltage Valid Range | System shall accept CC2 voltage in [4.8V, 7.7V] as valid wake-up signal and output vehicle_state=170, vehicle_mode=5, ready_flag=1. Value 7.8V is a boundary case observed to FAIL in majority of real tests. | Input Validation |
| REQ-002 | CC2 Voltage Below Valid Range | System shall output test_status=4, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage is below 4.8V. All 35 real test records with CC2 < 4.8V confirm vehicle_state=30. | Input Validation |
| REQ-003 | CC2 Voltage Above Valid Range | System shall output test_status=4, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage exceeds 7.8V (excluding sleep trigger 12.0V). Real data: 37/38 records confirm state=30. | Input Validation |
| REQ-004 | Sleep Trigger Voltage | System shall output test_status=3, vehicle_state=30, vehicle_mode=2, ready_flag=0 when CC2 voltage equals 12.0V with sleep command (type=2). | State Transition |
| REQ-005 | CC Voltage Cable Check | System shall output test_status=4, vehicle_state=30 when CC电压值 is in range [0.1V, 3.9V], indicating invalid cable contact resistance. | Safety |
| REQ-006 | CP Amplitude Interference Check | System shall output test_status=4, vehicle_state=30 when CP幅值 is in range [9.1V, 12.9V], indicating CP signal conflict or protocol anomaly. | Safety |
| REQ-007 | Supply Voltage Overvoltage Check | System shall output test_status=4, vehicle_state=30 when 供电电压 is in range [9.1V, 15.9V], indicating unexpected external supply or overvoltage. | Safety |
| REQ-008 | Network Wake Conflict Check | System shall output test_status=4, vehicle_state=30 when 网络唤醒报文使能状态=1 conflicts with CC2 wake protocol. Normal state is 0 (disabled). | Safety |
| REQ-009 | READY Flag Consistency | When vehicle_state=170 system shall set ready_flag=1. When vehicle_state=30 system shall set ready_flag=0. These two fields must always be consistent. | State Control |
| REQ-010 | Test Duration Compliance | Each single-signal test shall complete within 120 seconds. Based on real HIL data, actual_duration averages approximately 100 seconds. | Timing |

---

## Chapter 4: Risk Assessment Methodology

### 4.1 Five-Dimension Scoring Algorithm

Each requirement is scored on five dimensions, each rated 1–10:

| Dimension | Weight | Definition |
|-----------|--------|------------|
| **Criticality** | 0.30 | Impact of failure on vehicle safety or charging function. Score 10 = directly prevents charging or causes safety hazard. |
| **Boundary Sensitivity** | 0.25 | Whether the requirement has precise numeric boundaries that can be tested at exact thresholds. Score 10 = exact voltage boundary known from real data. |
| **Complexity** | 0.20 | Number of conditions, signals, or state combinations involved. Score 10 = multiple signals interact. |
| **State Impact** | 0.15 | Whether the requirement affects vehicle_state or ready_flag transitions. Score 10 = directly drives state change. |
| **Testability** | 0.10 | How easily the requirement can be validated via the simulator API. Score 10 = single deterministic API call with exact expected output. |

### 4.2 Composite Risk Score Formula

```
Risk Score = (Criticality × 0.30) + (Boundary × 0.25) + (Complexity × 0.20)
           + (State Impact × 0.15) + (Testability × 0.10)
```

### 4.3 Priority Mapping

| Risk Score | Priority | Meaning |
|-----------|----------|---------|
| ≥ 7.0 | **High** | Must test first; failures here block vehicle operation |
| 4.0 – 6.9 | **Medium** | Test in second pass; failures cause safety warnings |
| < 4.0 | **Low** | Test last; failures are detectable but non-critical |

---

## Chapter 5: Risk Analysis Results

### 5.1 Complete Scoring Table

| Req ID | Criticality (×0.30) | Boundary (×0.25) | Complexity (×0.20) | State (×0.15) | Testability (×0.10) | **Risk Score** | **Priority** |
|--------|---------------------|------------------|--------------------|---------------|---------------------|----------------|--------------|
| REQ-001 | 9 | 10 | 4 | 9 | 10 | **8.35** | **High** |
| REQ-002 | 8 | 10 | 3 | 8 | 10 | **7.90** | **High** |
| REQ-003 | 8 | 9 | 3 | 8 | 10 | **7.65** | **High** |
| REQ-004 | 7 | 8 | 6 | 9 | 9 | **7.65** | **High** |
| REQ-005 | 7 | 8 | 3 | 7 | 10 | **7.10** | **High** |
| REQ-006 | 7 | 8 | 3 | 7 | 10 | **7.10** | **High** |
| REQ-007 | 7 | 8 | 3 | 7 | 10 | **7.10** | **High** |
| REQ-008 | 6 | 5 | 4 | 7 | 10 | **6.25** | **Medium** |
| REQ-009 | 8 | 3 | 5 | 10 | 8 | **6.85** | **Medium** |
| REQ-010 | 3 | 2 | 2 | 1 | 9 | **3.05** | **Low** |

### 5.2 Scoring Rationale

**REQ-001 (Score: 8.35 — Highest)**  
CC2 voltage is the primary wake-up signal. An incorrect boundary here means the entire charging process fails. The [4.8V, 7.7V] boundary is confirmed by 2168+ real records with exact known thresholds, making both Criticality and Boundary scores maximum. Complexity is low (single signal, single condition).

**REQ-002 / REQ-003 (Score: 7.90 / 7.65)**  
Below and above bounds of the CC2 range. 35 and 37 real records respectively confirm the FAIL behavior with high confidence. State impact is high (direct vehicle_state transition). Slightly lower than REQ-001 because these are FAIL paths rather than the nominal path.

**REQ-004 (Score: 7.65)**  
Sleep trigger is a distinct state transition (status=3, not 4) requiring a different test interface (`/simulate/sleep`). Complexity is higher than single-signal tests (5-signal fixed combination). High state impact because it exercises the third state branch.

**REQ-005 / REQ-006 / REQ-007 (Score: 7.10 each)**  
Safety signals with precise numeric FAIL ranges. All have confirmed real-data boundaries. Lower than CC2 requirements because these signals are secondary (non-primary wake path) but still directly affect vehicle safety.

**REQ-008 (Score: 6.25 — Medium)**  
Binary signal with known FAIL value (=1). Boundary sensitivity is low (binary, no range). Interaction with CC2 wake protocol adds some complexity.

**REQ-009 (Score: 6.85 — Medium)**  
Consistency constraint between two output fields. No specific boundary values — instead tests an invariant across all scenarios. High state impact but low boundary sensitivity.

**REQ-010 (Score: 3.05 — Low)**  
Timing requirement. The simulator always returns within milliseconds (HTTP response). The actual_duration field is a simulated value. No real timing failure scenario is testable via the simulator API.

---

## Chapter 6: Risk Matrix

### 6.1 Bubble Chart (ASCII)

The following matrix plots Boundary Sensitivity (X-axis) vs. Criticality (Y-axis). Bubble size indicates Complexity. Color indicates Priority (H=High, M=Medium, L=Low).

```
Criticality
    10 │
       │
     9 │  REQ-001(H)●
       │
     8 │  REQ-002(H)●   REQ-003(H)●
       │
     7 │                            REQ-004(H)●  REQ-005(H)●
       │                            REQ-006(H)●  REQ-007(H)●
     6 │                    REQ-008(M)○   REQ-009(M)○
       │
     5 │
       │
     3 │                                              REQ-010(L)△
       │
       └──────────────────────────────────────────────────────────
         1    2    3    4    5    6    7    8    9   10
                                              Boundary Sensitivity

Legend: ● High Priority   ○ Medium Priority   △ Low Priority
        Bubble size represents Complexity score
```

### 6.2 Key Observations from Matrix

1. **Top-right cluster (REQ-001~007)**: High criticality + high boundary sensitivity = highest testing value. These 7 requirements should form the core test suite.
2. **Middle band (REQ-008, REQ-009)**: Medium priority; both involve inter-signal or inter-field relationships rather than simple boundary checks.
3. **Bottom-left (REQ-010)**: Low boundary sensitivity and low criticality; timing compliance is a non-issue for the software simulator.

---

## Chapter 7: Testing Priority Recommendations

Based on the risk scores, the recommended test execution order is:

### Priority 1 — Critical (Execute First)

| Order | Requirement | Rationale |
|-------|-------------|-----------|
| 1 | **REQ-001** (CC2 valid range) | Highest score; nominal path; all other tests depend on understanding CC2 behavior |
| 2 | **REQ-002** (CC2 below bound) | Defines lower BVA boundary; 35 records confirm; immediate safety impact |
| 3 | **REQ-003** (CC2 above bound) | Defines upper BVA boundary; completes CC2 coverage |
| 4 | **REQ-004** (Sleep trigger) | Third state branch; unique interface; must verify independently |

### Priority 2 — Safety Signals (Execute Second)

| Order | Requirement | Rationale |
|-------|-------------|-----------|
| 5 | **REQ-005** (CC voltage cable) | Safety signal with known fault range |
| 6 | **REQ-006** (CP amplitude) | Safety signal with known fault range |
| 7 | **REQ-007** (Supply voltage) | Safety signal with known fault range |

### Priority 3 — Consistency and Conflicts (Execute Third)

| Order | Requirement | Rationale |
|-------|-------------|-----------|
| 8 | **REQ-009** (READY flag consistency) | Cross-field invariant; verify across all PASS and FAIL results |
| 9 | **REQ-008** (Network wake conflict) | Binary signal; quick to test; medium risk |

### Priority 4 — Non-Functional (Execute Last)

| Order | Requirement | Rationale |
|-------|-------------|-----------|
| 10 | **REQ-010** (Test duration) | Low risk; verify `actual_duration < 120` in any test response |

---

## Appendix: Test Plan — Test Items

### A.1 Functional Test Items

| Suite ID | Feature Area | Test Items | Interface |
|----------|-------------|------------|-----------|
| TS-001 | CC2 Voltage — Normal Wake | EP valid class, BVA at 4.8V / 7.7V / midpoint 6.3V | POST /simulate |
| TS-002 | CC2 Voltage — Below Bound | EP invalid low class, BVA at 4.7V / 0V / 4.8V boundary | POST /simulate |
| TS-003 | CC2 Voltage — Above Bound | EP invalid high class, BVA at 7.8V / 9.0V / 12.0V special | POST /simulate |
| TS-004 | CC2 Voltage — Sleep Trigger | Fixed 5-signal combination, verify status=3 | POST /simulate/sleep |
| TS-005 | CC / CP / Supply Safety Signals | EP and BVA for three secondary signals | POST /simulate |
| TS-006 | Network Wake Conflict | Binary signal exhaustive test (values 0 and 1) | POST /simulate |
| TS-007 | READY Flag Consistency | Cross-check ready_flag vs vehicle_state across all suites | All endpoints |

### A.2 Non-Functional Test Items

| Item | Description | Pass Criterion |
|------|-------------|----------------|
| NFT-001 | Response Time | Each `/simulate` call completes within 120s | `actual_duration` field ≤ 120 |
| NFT-002 | Batch Throughput | 500-item batch completes without error | HTTP 200, array length = 500 |
| NFT-003 | Invalid Input Handling | Non-existent signal name returns validation error | HTTP 422 |

### A.3 System Architecture (Three-Service Overview)

```
┌─────────────────────────────────────────────────────────┐
│              AutoTestDesign Tool (Port 8000)             │
│                                                         │
│  RequirementInput → RiskAnalysis → TestCaseDesign       │
│       FR1.0/1.1        FR2.0           FR3.0(+GAN)      │
│                                            │             │
│                                  simulator_client.py    │
└────────────────────────────────────────────┼────────────┘
                                             │ HTTP POST /simulate
                                             ▼
┌─────────────────────────────────────────────────────────┐
│         VCU Behavior Simulator (Port 8001)               │
│                                                         │
│  POST /simulate       ← single signal test              │
│  POST /simulate/sleep ← sleep combination test          │
│  POST /simulate/batch ← bulk test                       │
└─────────────────────────────────────────────────────────┘
                         ↕ (test results flow back up)
┌─────────────────────────────────────────────────────────┐
│              React Frontend (Port 3000)                  │
│                                                         │
│  Dashboard / TestManagement / ResultAnalysis /          │
│  ReportCenter / SystemSettings                          │
└─────────────────────────────────────────────────────────┘
```
