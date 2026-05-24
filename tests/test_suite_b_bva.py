"""
Suite B — Boundary Value Analysis (BVA)
Coverage: REQ-001/006/007/015/016/017 (Module A + B voltage & timing boundaries)
Technique: ISO 29119-4 Boundary Value Analysis
ISO 9126: Functionality/Accuracy + Reliability/Maturity
RPN: 2 (Extensive)

BVA points per boundary: below / on / above  (3-point BVA)

Boundaries tested:
  B1  supply_voltage  = 9.0 V  (wake threshold)
  B2  timing          = 10 ms  (w1/w6/w7 duration threshold)
  B3  hood_voltage    = 4.0 V  (wake threshold)
  B4  door_voltage    = 1.0 V  (wake threshold)
  B5  overvoltage     = 16.0 V (Module B guard upper)
  B6  undervoltage    = 6.0 V  (Module B guard lower)
  B7  debounce        = 5 ms   (Module B noise rejection)

24 test cases total
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402


class SuiteB_BVA(unittest.TestCase):

    def setUp(self):
        self.sim = VCUSimulator()

    # ── B1  supply_voltage = 9.0 V boundary (REQ-001) ───────────────────────

    def test_TC_B_001_supply_below_9v(self):
        """TC-B-001 | B1-below | supply_voltage=8.9 V, duration=15 ms → NO WAKE"""
        r = self.sim.simulate(supply_voltage=8.9, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_002_supply_on_9v(self):
        """TC-B-002 | B1-on | supply_voltage=9.0 V (not > 9 V) → NO WAKE"""
        r = self.sim.simulate(supply_voltage=9.0, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_003_supply_above_9v(self):
        """TC-B-003 | B1-above | supply_voltage=9.1 V, duration=15 ms → WAKE"""
        r = self.sim.simulate(supply_voltage=9.1, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 1)

    # ── B2  timing = 10 ms boundary for supply_voltage (REQ-001) ─────────────

    def test_TC_B_004_timing_below_10ms(self):
        """TC-B-004 | B2-below | supply_voltage=9.3 V, duration=9 ms → timing rejected"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=9)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_005_timing_on_10ms(self):
        """TC-B-005 | B2-on | supply_voltage=9.3 V, duration=10 ms (exactly ≥ 10) → WAKE"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=10)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 1)

    def test_TC_B_006_timing_above_10ms(self):
        """TC-B-006 | B2-above | supply_voltage=9.3 V, duration=11 ms → WAKE"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=11)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 1)

    # ── B3  hood_voltage = 4.0 V boundary (REQ-006) ─────────────────────────

    def test_TC_B_007_hood_below_4v(self):
        """TC-B-007 | B3-below | hood_voltage=3.9 V → NO WAKE"""
        r = self.sim.simulate(hood_voltage=3.9, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_008_hood_on_4v(self):
        """TC-B-008 | B3-on | hood_voltage=4.0 V (not > 4 V) → NO WAKE"""
        r = self.sim.simulate(hood_voltage=4.0, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_009_hood_above_4v(self):
        """TC-B-009 | B3-above | hood_voltage=4.1 V, duration=15 ms → WAKE reason=6"""
        r = self.sim.simulate(hood_voltage=4.1, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 6)

    # ── B4  door_voltage = 1.0 V boundary (REQ-007) ─────────────────────────

    def test_TC_B_010_door_above_1v(self):
        """TC-B-010 | B4-above | door_voltage=1.1 V (not < 1 V) → NO WAKE"""
        r = self.sim.simulate(door_voltage=1.1, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_011_door_on_1v(self):
        """TC-B-011 | B4-on | door_voltage=1.0 V (not < 1 V) → NO WAKE"""
        r = self.sim.simulate(door_voltage=1.0, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_012_door_below_1v(self):
        """TC-B-012 | B4-below | door_voltage=0.9 V, duration=15 ms → WAKE reason=7"""
        r = self.sim.simulate(door_voltage=0.9, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 7)

    # ── B5  overvoltage = 16.0 V boundary (REQ-015, Module B) ───────────────

    def test_TC_B_013_overvoltage_below_16v(self):
        """TC-B-013 | B5-below | supply_voltage=15.9 V → normal wake (not overvoltage)"""
        r = self.sim.simulate(supply_voltage=15.9, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertNotEqual(r["state_name"], "fault_protection")

    def test_TC_B_014_overvoltage_on_16v(self):
        """TC-B-014 | B5-on | supply_voltage=16.0 V (not > 16 V) → normal wake"""
        r = self.sim.simulate(supply_voltage=16.0, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertNotEqual(r["state_name"], "fault_protection")

    def test_TC_B_015_overvoltage_above_16v(self):
        """TC-B-015 | B5-above | supply_voltage=16.1 V → fault_protection, DTC_002"""
        r = self.sim.simulate(supply_voltage=16.1, duration_ms=15)
        self.assertEqual(r["state_name"], "fault_protection")
        self.assertEqual(r["power_alarm_flag"], 1)
        self.assertIn("DTC_002", r["active_dtcs"])

    # ── B6  undervoltage = 6.0 V boundary (REQ-016, Module B) ───────────────

    def test_TC_B_016_undervoltage_above_6v(self):
        """TC-B-016 | B6-above | supply_voltage=6.1 V → NOT undervoltage_shutdown (Module B guard passes)
        Note: 6.1 V does not trigger undervoltage protection (threshold < 6 V), but also does not
        satisfy the wake threshold (> 9 V), so state stays 09 for a different reason (low value)."""
        r = self.sim.simulate(supply_voltage=6.1, duration_ms=15)
        self.assertNotEqual(r["state_name"], "undervoltage_shutdown")  # guard did NOT fire
        self.assertEqual(r["vehicle_state"], 9)  # no wake because 6.1 V < 9 V threshold
        self.assertIsNone(r["signal_guard_result"].get("fault_type"))  # no guard fault

    def test_TC_B_017_undervoltage_on_6v(self):
        """TC-B-017 | B6-on | supply_voltage=6.0 V (not < 6 V, guard does not fire)
        Guard allows 6.0 V through; wake fails because 6.0 V < 9 V threshold."""
        r = self.sim.simulate(supply_voltage=6.0, duration_ms=15)
        self.assertNotEqual(r["state_name"], "undervoltage_shutdown")  # guard did NOT fire
        self.assertEqual(r["vehicle_state"], 9)
        self.assertIsNone(r["signal_guard_result"].get("fault_type"))

    def test_TC_B_018_undervoltage_below_6v(self):
        """TC-B-018 | B6-below | supply_voltage=5.9 V → undervoltage_shutdown, bus=0"""
        r = self.sim.simulate(supply_voltage=5.9, duration_ms=15)
        self.assertEqual(r["state_name"], "undervoltage_shutdown")
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertIn("DTC_003", r["active_dtcs"])

    # ── B7  debounce = 5 ms boundary (REQ-017, Module B) ────────────────────

    def test_TC_B_019_debounce_below_5ms(self):
        """TC-B-019 | B7-below | supply_voltage=9.3 V, duration=4 ms → noise rejected"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=4)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["signal_guard_result"]["fault_type"], "debounce_rejected")

    def test_TC_B_020_debounce_on_5ms(self):
        """TC-B-020 | B7-on | supply_voltage=9.3 V, duration=5 ms → noise rejected (< threshold means < 5, so 5ms passes guard but fails timing)"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=5)
        # 5 ms passes debounce (>= 5 ms is valid signal), but 5 < 10 ms wake timing → still no wake
        self.assertNotEqual(r["signal_guard_result"]["fault_type"], "debounce_rejected")
        self.assertEqual(r["vehicle_state"], 9)

    def test_TC_B_021_debounce_above_5ms(self):
        """TC-B-021 | B7-above | supply_voltage=9.3 V, duration=6 ms → guard passes, timing still short"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=6)
        self.assertNotEqual(r["signal_guard_result"]["fault_type"], "debounce_rejected")
        self.assertEqual(r["vehicle_state"], 9)  # 6 ms < 10 ms wake threshold

    # ── Additional BVA: CAN ID range boundaries (REQ-018, Module C) ─────────

    def test_TC_B_022_can_id_below_range(self):
        """TC-B-022 | CAN-BVA-below | can_msg_id=0x3FF (one below valid range) → NO WAKE"""
        r = self.sim.simulate(can_msg_id=0x3FF)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_B_023_can_id_low_boundary(self):
        """TC-B-023 | CAN-BVA-on-low | can_msg_id=0x400 (low boundary, inclusive) → WAKE"""
        r = self.sim.simulate(can_msg_id=0x400)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 2)

    def test_TC_B_024_can_id_high_boundary(self):
        """TC-B-024 | CAN-BVA-on-high | can_msg_id=0x47F (high boundary, inclusive) → WAKE"""
        self.sim.reset()
        r = self.sim.simulate(can_msg_id=0x47F)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
