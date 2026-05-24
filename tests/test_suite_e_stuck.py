"""
Suite E — Stuck Detection Scenario Testing
Coverage: REQ-012/020 (Module A known defect + Module D DTC evidence)
Technique: Scenario Testing + Sequence Testing
ISO 9126: Reliability / Recoverability
RPN: 1 (Extensive — highest priority, known real defect from BAIC requirement doc)

Defect description (from PROJECT_PLAN_V2 §5.2):
  Trigger: 3+ rapid wake-sleep cycles with interval < 1 s
  Symptom: vehicle_state stays at 10, actual_duration > est_time × 2, DTC_001 written
  Evidence: result_type="error" + state_name="state10" + DTC_001 in active_dtcs

10 test cases covering the full stuck scenario lifecycle.
"""

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402

STUCK_THRESHOLD = 3  # rapid_cycle_threshold from config


def _do_rapid_cycle(sim, n):
    """Execute n rapid wake-sleep cycles with no delay between them."""
    for _ in range(n):
        sim.simulate(supply_voltage=9.3, duration_ms=15)
        sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
        )


class SuiteE_StuckScenario(unittest.TestCase):

    def setUp(self):
        self.sim = VCUSimulator()

    # ── SC-E-001  Single cycle — no stuck ────────────────────────────────────

    def test_TC_E_001_single_cycle_no_stuck(self):
        """TC-E-001 | 1 wake-sleep cycle → next wake succeeds (no stuck)"""
        _do_rapid_cycle(self.sim, 1)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")
        self.assertNotIn("DTC_001", r["active_dtcs"])

    # ── SC-E-002  Two cycles — not yet stuck ─────────────────────────────────

    def test_TC_E_002_two_cycles_not_yet_stuck(self):
        """TC-E-002 | 2 rapid cycles → still below threshold, next wake succeeds"""
        _do_rapid_cycle(self.sim, 2)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")

    # ── SC-E-003  Three cycles — stuck triggered ──────────────────────────────

    def test_TC_E_003_three_cycles_stuck_triggered(self):
        """TC-E-003 | 3 rapid cycles → 4th wake triggers state10 stuck (DEF-001)"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 10)
        self.assertEqual(r["state_name"], "state10")
        self.assertEqual(r["result_type"], "error")

    # ── SC-E-004  DTC_001 generated as evidence ───────────────────────────────

    def test_TC_E_004_dtc_001_written_on_stuck(self):
        """TC-E-004 | stuck trigger → DTC_001 in active_dtcs (defect evidence)"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertIn("DTC_001", r["active_dtcs"])

    # ── SC-E-005  actual_duration exceeds est_time × 2 ────────────────────────

    def test_TC_E_005_actual_duration_exceeds_threshold(self):
        """TC-E-005 | stuck → actual_duration > stuck_est_time × 2 (= 41 s)"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        est_time = self.sim.config["timing"]["stuck_est_time"]
        self.assertGreater(r["actual_duration"], est_time * 2)

    # ── SC-E-006  power_alarm_flag set during stuck ───────────────────────────

    def test_TC_E_006_power_alarm_flag_on_stuck(self):
        """TC-E-006 | stuck → power_alarm_flag=1 (Module E alarm triggered)"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["power_alarm_flag"], 1)

    # ── SC-E-007  Reset recovers from stuck ──────────────────────────────────

    def test_TC_E_007_reset_recovers_from_stuck(self):
        """TC-E-007 | after stuck + reset → next wake succeeds (state11)"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)  # trigger stuck
        self.assertEqual(self.sim.state, 10)

        self.sim.reset(clear_dtc=True)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")

    # ── SC-E-008  Stuck can be reproduced again after reset ───────────────────

    def test_TC_E_008_stuck_reproducible_after_reset(self):
        """TC-E-008 | reset then repeat rapid cycles → stuck triggers again"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.sim.reset(clear_dtc=True)

        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 10)
        self.assertIn("DTC_001", r["active_dtcs"])

    # ── SC-E-009  Slow cycles (interval > 1 s) never stuck ───────────────────

    def test_TC_E_009_slow_cycles_no_stuck(self):
        """TC-E-009 | 3 slow cycles (> 1 s gap) → rapid counter resets, no stuck"""
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            time.sleep(1.1)  # exceed rapid_cycle_interval_s = 1.0 s
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")

    # ── SC-E-010  DTC cleared after reset with clear_dtc=True ────────────────

    def test_TC_E_010_dtc_cleared_after_reset(self):
        """TC-E-010 | stuck → DTC_001 active → reset(clear_dtc=True) → DTC cleared"""
        _do_rapid_cycle(self.sim, STUCK_THRESHOLD)
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertTrue(self.sim.dtc_manager.get_active_codes())

        self.sim.reset(clear_dtc=True)
        records = self.sim.dtc_manager.get_all()
        self.assertTrue(all(rec["status"] == "cleared" for rec in records))
        self.assertEqual(self.sim.dtc_manager.get_active_codes(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
