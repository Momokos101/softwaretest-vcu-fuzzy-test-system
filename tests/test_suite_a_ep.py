"""
Suite A — Equivalence Partitioning (EP)
Coverage: REQ-001 ~ REQ-007 (Module A, 7-path wake triggers)
Technique: ISO 29119-4 Equivalence Partitioning
ISO 9126: Functionality / Suitability
RPN: 2 (Extensive)

Coverage Items per signal:
  I-Wx-1  Valid class   : value satisfies condition + timing (where required) → wake
  I-Wx-2  Invalid class : value does NOT satisfy condition                    → no wake
  I-Wx-3  Timing class  : value OK but duration insufficient (w1/w6/w7 only)  → no wake

21 test cases: 7 signals × 3 EP classes each
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402


class SuiteA_EP(unittest.TestCase):

    def setUp(self):
        self.sim = VCUSimulator()

    # ── W1  供电电压  REQ-001  (threshold > 9 V, duration ≥ 10 ms) ──────────

    def test_TC_A_001_w1_valid_class(self):
        """TC-A-001 | I-W1-1 | supply_voltage=9.3 V, duration=15 ms → WAKE state11, reason=1"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 1)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_002_w1_invalid_value_class(self):
        """TC-A-002 | I-W1-2 | supply_voltage=8.9 V (below 9 V) → NO WAKE state09"""
        r = self.sim.simulate(supply_voltage=8.9, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["pdcu_wake_reason"], 0)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_003_w1_invalid_timing_class(self):
        """TC-A-003 | I-W1-3 | supply_voltage=9.3 V, duration=8 ms (< 10 ms) → timing rejected"""
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=8)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W2  CAN 网络报文  REQ-002  (ID ∈ [0x400, 0x47F]) ────────────────────

    def test_TC_A_004_w2_valid_class(self):
        """TC-A-004 | I-W2-1 | can_msg_id=0x430 (in range) → WAKE reason=2"""
        r = self.sim.simulate(can_msg_id=0x430)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 2)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_005_w2_invalid_low_class(self):
        """TC-A-005 | I-W2-2 | can_msg_id=0x200 (below range) → NO WAKE"""
        r = self.sim.simulate(can_msg_id=0x200)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_006_w2_invalid_high_class(self):
        """TC-A-006 | I-W2-3 | can_msg_id=0x500 (above range) → NO WAKE"""
        r = self.sim.simulate(can_msg_id=0x500)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W3  CP 信号  REQ-003  (cp_voltage > 9 V) ────────────────────────────

    def test_TC_A_007_w3_valid_class(self):
        """TC-A-007 | I-W3-1 | cp_voltage=10.0 V > 9 V → WAKE reason=3"""
        r = self.sim.simulate(cp_voltage=10.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 3)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_008_w3_invalid_low_class(self):
        """TC-A-008 | I-W3-2 | cp_voltage=8.0 V ≤ 9 V → NO WAKE"""
        r = self.sim.simulate(cp_voltage=8.0)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_009_w3_on_boundary_class(self):
        """TC-A-009 | I-W3-3 | cp_voltage=9.0 V (exactly at threshold, not > 9 V) → NO WAKE"""
        r = self.sim.simulate(cp_voltage=9.0)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W4  CC 信号  REQ-004  (cc_voltage < 4.4 V) ──────────────────────────

    def test_TC_A_010_w4_valid_class(self):
        """TC-A-010 | I-W4-1 | cc_voltage=4.0 V < 4.4 V → WAKE reason=4"""
        r = self.sim.simulate(cc_voltage=4.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 4)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_011_w4_invalid_high_class(self):
        """TC-A-011 | I-W4-2 | cc_voltage=4.5 V ≥ 4.4 V → NO WAKE"""
        r = self.sim.simulate(cc_voltage=4.5)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_012_w4_on_boundary_class(self):
        """TC-A-012 | I-W4-3 | cc_voltage=4.4 V (not < 4.4 V) → NO WAKE"""
        r = self.sim.simulate(cc_voltage=4.4)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W5  CC2 信号  REQ-005  (cc2_voltage < ubr_threshold) ────────────────

    def test_TC_A_013_w5_valid_class(self):
        """TC-A-013 | I-W5-1 | cc2_voltage=4.0 V (below ubr_threshold) → WAKE reason=5"""
        r = self.sim.simulate(cc2_voltage=4.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 5)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_014_w5_invalid_high_class(self):
        """TC-A-014 | I-W5-2 | cc2_voltage=8.0 V (above ubr_threshold) → NO WAKE"""
        r = self.sim.simulate(cc2_voltage=8.0)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_015_w5_on_boundary_class(self):
        """TC-A-015 | I-W5-3 | cc2_voltage=4.4 V (ubr_threshold, not <) → NO WAKE"""
        r = self.sim.simulate(cc2_voltage=4.4)  # threshold = 4.4 V per V2_WAKE_THRESHOLDS
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W6  口盖信号  REQ-006  (hood_voltage > 4 V, duration ≥ 10 ms) ───────

    def test_TC_A_016_w6_valid_class(self):
        """TC-A-016 | I-W6-1 | hood_voltage=4.5 V, duration=15 ms → WAKE reason=6"""
        r = self.sim.simulate(hood_voltage=4.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 6)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_017_w6_invalid_value_class(self):
        """TC-A-017 | I-W6-2 | hood_voltage=3.5 V (≤ 4 V) → NO WAKE"""
        r = self.sim.simulate(hood_voltage=3.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_018_w6_invalid_timing_class(self):
        """TC-A-018 | I-W6-3 | hood_voltage=4.5 V, duration=8 ms (< 10 ms) → NO WAKE"""
        r = self.sim.simulate(hood_voltage=4.5, duration_ms=8)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    # ── W7  门板信号  REQ-007  (door_voltage < 1 V, duration ≥ 10 ms) ───────

    def test_TC_A_019_w7_valid_class(self):
        """TC-A-019 | I-W7-1 | door_voltage=0.5 V, duration=15 ms → WAKE reason=7"""
        r = self.sim.simulate(door_voltage=0.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 7)
        self.assertEqual(r["result_type"], "expected")

    def test_TC_A_020_w7_invalid_value_class(self):
        """TC-A-020 | I-W7-2 | door_voltage=1.5 V (≥ 1 V) → NO WAKE"""
        r = self.sim.simulate(door_voltage=1.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")

    def test_TC_A_021_w7_invalid_timing_class(self):
        """TC-A-021 | I-W7-3 | door_voltage=0.5 V, duration=8 ms (< 10 ms) → NO WAKE"""
        r = self.sim.simulate(door_voltage=0.5, duration_ms=8)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["result_type"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
