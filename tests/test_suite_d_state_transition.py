"""
Suite D — State Transition Testing (All-Transitions)
Coverage: REQ-001~012/015/016 (Module A + B state machine)
Technique: ISO 29119-4 State Transition Testing, All-Transitions criterion
ISO 9126: Reliability / Maturity
RPN: 1 (Extensive — highest priority)

States:
  state09 (sleep)          vehicle_state=9
  state10 (init/stuck)     vehicle_state=10
  state11 (run)            vehicle_state=11
  fault_protection         vehicle_state=10 (maps to init), state_name="fault_protection"
  undervoltage_shutdown    vehicle_state=9  (maps to sleep), state_name="undervoltage_shutdown"

All-Transitions coverage (7 paths + fault paths):
  T01  state09 → state11  (normal wake, w1)
  T02  state11 → state09  (normal sleep, h1∧h2∧h3)
  T03  state09 → fault_protection  (overvoltage)
  T04  fault_protection → state09  (reset)
  T05  state09 → undervoltage_shutdown  (undervoltage)
  T06  undervoltage_shutdown → state09  (reset)
  T07  state09 → state10  (stuck trigger via rapid cycles)
  T08  state11 → state11  (sleep rejected, stay in run)
  T09  fault_protection → reject wake  (wake blocked while in fault)
  T10  state09 wake output fields consistency (REQ-013)
  T11  state11 wake output fields consistency (REQ-013)
  T12  reset clears rapid cycle counter
  T13  DTC_001 generated on stuck (REQ-020)
  T14  DTC_002 generated on overvoltage (REQ-020)
  T15  DTC_003 generated on undervoltage (REQ-020)
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402


class SuiteD_StateTransition(unittest.TestCase):

    def setUp(self):
        self.sim = VCUSimulator()

    # ── T01  state09 → state11 ────────────────────────────────────────────────

    def test_TC_D_001_sleep_to_run_normal_wake(self):
        """TC-D-001 | T01 | state09 → state11 via supply_voltage wake"""
        self.assertEqual(self.sim.state, 9)  # start at sleep
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["state_name"], "state11")
        self.assertEqual(r["result_type"], "expected")

    # ── T02  state11 → state09 ────────────────────────────────────────────────

    def test_TC_D_002_run_to_sleep_all_conditions(self):
        """TC-D-002 | T02 | state11 → state09 via h1∧h2∧h3"""
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(self.sim.state, 11)

        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
        )
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertEqual(r["result_type"], "expected")

    # ── T03  state09 → fault_protection ──────────────────────────────────────

    def test_TC_D_003_sleep_to_fault_overvoltage(self):
        """TC-D-003 | T03 | state09 → fault_protection via supply_voltage > 16 V"""
        r = self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertEqual(r["state_name"], "fault_protection")
        self.assertEqual(r["power_alarm_flag"], 1)
        self.assertEqual(r["result_type"], "error")

    # ── T04  fault_protection → state09 ──────────────────────────────────────

    def test_TC_D_004_fault_to_sleep_via_reset(self):
        """TC-D-004 | T04 | fault_protection → state09 via POST /reset"""
        self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertEqual(self.sim.state, "fault_protection")

        self.sim.reset(clear_dtc=True)
        state = self.sim.get_state()
        self.assertEqual(state["vehicle_state"], 9)
        self.assertEqual(state["state_name"], "state09")

    # ── T05  state09 → undervoltage_shutdown ─────────────────────────────────

    def test_TC_D_005_sleep_to_undervoltage(self):
        """TC-D-005 | T05 | state09 → undervoltage_shutdown via supply_voltage < 6 V"""
        r = self.sim.simulate(supply_voltage=5.5, duration_ms=15)
        self.assertEqual(r["state_name"], "undervoltage_shutdown")
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertEqual(r["result_type"], "error")

    # ── T06  undervoltage_shutdown → state09 ─────────────────────────────────

    def test_TC_D_006_undervoltage_to_sleep_via_reset(self):
        """TC-D-006 | T06 | undervoltage_shutdown → state09 via reset"""
        self.sim.simulate(supply_voltage=5.5, duration_ms=15)
        self.assertEqual(self.sim.state, "undervoltage_shutdown")

        self.sim.reset(clear_dtc=True)
        state = self.sim.get_state()
        self.assertEqual(state["vehicle_state"], 9)
        self.assertEqual(state["state_name"], "state09")

    # ── T07  state09 → state10 (stuck) ───────────────────────────────────────

    def test_TC_D_007_rapid_cycles_trigger_stuck(self):
        """TC-D-007 | T07 | 3 rapid wake-sleep cycles → state10 stuck on 4th wake"""
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 10)
        self.assertEqual(r["state_name"], "state10")

    # ── T08  state11 → state11 (sleep rejected) ──────────────────────────────

    def test_TC_D_008_run_stays_run_when_sleep_rejected(self):
        """TC-D-008 | T08 | state11 → state11 when only h1+h2 (missing h3)"""
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=False,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")

    # ── T09  fault_protection → wake blocked ─────────────────────────────────

    def test_TC_D_009_wake_blocked_when_in_fault(self):
        """TC-D-009 | T09 | attempt wake while in fault_protection → rejected"""
        self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertEqual(self.sim.state, "fault_protection")

        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("fault_protection", r["detail"])

    # ── T10  state09 output field consistency (REQ-013) ──────────────────────

    def test_TC_D_010_sleep_state_output_consistency(self):
        """TC-D-010 | T10 | state09 → bus_message_flag=0, vehicle_mode≠run"""
        state = self.sim.get_state()
        self.assertEqual(state["vehicle_state"], 9)
        r = self.sim.simulate(supply_voltage=8.9, duration_ms=15)  # stays asleep
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertEqual(r["vehicle_state"], 9)

    # ── T11  state11 output field consistency (REQ-013) ──────────────────────

    def test_TC_D_011_run_state_output_consistency(self):
        """TC-D-011 | T11 | state11 → bus_message_flag=1, ready_flag=1"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["bus_message_flag"], 1)
        self.assertEqual(r["ready_flag"], 1)

    # ── T12  reset clears rapid cycle counter ────────────────────────────────

    def test_TC_D_012_reset_clears_rapid_cycle_counter(self):
        """TC-D-012 | T12 | reset after rapid cycles → next wake succeeds normally"""
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )
        self.sim.reset()
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")

    # ── T13  DTC_001 generated on stuck (REQ-020) ────────────────────────────

    def test_TC_D_013_dtc_001_on_stuck(self):
        """TC-D-013 | T13 | state10 stuck → DTC_001 in active_dtcs"""
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertIn("DTC_001", r["active_dtcs"])

    # ── T14  DTC_002 generated on overvoltage (REQ-020) ──────────────────────

    def test_TC_D_014_dtc_002_on_overvoltage(self):
        """TC-D-014 | T14 | fault_protection → DTC_002 in active_dtcs"""
        r = self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertIn("DTC_002", r["active_dtcs"])

    # ── T15  DTC_003 generated on undervoltage (REQ-020) ─────────────────────

    def test_TC_D_015_dtc_003_on_undervoltage(self):
        """TC-D-015 | T15 | undervoltage_shutdown → DTC_003 in active_dtcs"""
        r = self.sim.simulate(supply_voltage=5.5, duration_ms=15)
        self.assertIn("DTC_003", r["active_dtcs"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
