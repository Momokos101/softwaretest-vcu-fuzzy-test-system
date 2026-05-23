# VCU Simulator V2 Modification Plan

This local plan records the approved implementation scope for aligning
`vcu_simulator/` with `docs/PROJECT_PLAN_V2.md`. It is intended for local
execution only and does not need to be uploaded to the remote repository.

## Scope

Implement the VCU behavior simulator described in PROJECT_PLAN_V2:

- Module A: state machine for wake, initialization, run, sleep, and stuck fault
- Module B: signal guard for overvoltage, undervoltage, and debounce rejection
- Module C: CAN manager for ID filtering and bus-off detection
- Module D: DTC manager for diagnostic trouble code lifecycle
- Module E: power monitor for current alarm and sleep power compliance

## Execution Plan

1. Create `vcu_simulator/modules/` and implement Module B/C/D/E files:
   - `signal_guard.py`
   - `can_manager.py`
   - `dtc_manager.py`
   - `power_monitor.py`

2. Rewrite `vcu_simulator/models.py` around V2 request and response fields.
   Keep old response fields only as optional compatibility fields.

3. Update `vcu_simulator/constants.py` so V2 thresholds are primary:
   wake thresholds, sleep conditions, overvoltage, undervoltage, debounce,
   CAN ID bounds, bus-off threshold, and power thresholds.

4. Refactor `vcu_simulator/simulator.py` into a stateful simulator:
   - Initial state: `state09` represented by `vehicle_state=9`
   - Wake path: `state09 -> state10 -> state11`
   - Sleep path: `state11 -> state09`
   - Overvoltage path: `fault_protection`
   - Undervoltage path: `undervoltage_shutdown`
   - Stuck fault: more than 3 rapid wake-sleep cycles with adjacent interval
     below 1 second leaves the simulator in `state10`, increases duration, and
     logs `DTC_001`.

5. Expand `vcu_simulator/main.py`:
   - Keep existing `/health`, `/simulate`, `/simulate/batch`, `/simulate/sleep`,
     `/signals`, and `/reset` where practical.
   - Add V2 APIs: `GET /state`, `GET /config`, `PUT /config`, `GET /dtc`,
     and `GET /performance`.
   - Extend `/reset` to support `clear_dtc=true`.

6. Add V2 tests covering the high-risk and interface-critical requirements:
   - Wake triggers REQ-001 through REQ-007
   - Sleep necessary and sufficient conditions REQ-008 through REQ-011
   - Stuck detection REQ-012
   - Output consistency and duration REQ-013 through REQ-014
   - Signal guard REQ-015 through REQ-017
   - CAN filtering and bus-off REQ-018 through REQ-019
   - DTC logging, query, and clear REQ-020 through REQ-022
   - Power alarm and sleep power compliance REQ-023 through REQ-024

7. Run focused tests first, then compatibility checks for existing backend
   simulator calls.
