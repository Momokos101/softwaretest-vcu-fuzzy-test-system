"""
Suite C — Decision Table Testing
Coverage: REQ-008/009/010/011 (Module A, sleep condition h1 AND h2 AND h3)
Technique: ISO 29119-4 Decision Table
ISO 9126: Functionality / Suitability
RPN: 2 (Extensive)

Sleep conditions:
  h1: VCUO_bDIAG_VCUIdle_flg = 1
  h2: VCUO_bDIAG_AuthComplete_flg = 1
  h3: can_stopped = True

Decision table: 2^3 = 8 rules
  Rule C-008 (1,1,1) is the only EXPECTED (sleep); all others are ERROR

Note: VCU must be in state11 before testing sleep (requires a prior wake).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402


class SuiteC_DecisionTable(unittest.TestCase):

    def _wake(self):
        """Helper: bring VCU to state11 via a clean wake."""
        self.sim.reset()
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11, "Pre-condition: VCU must be in state11")

    def setUp(self):
        self.sim = VCUSimulator()

    # ── Rule C-001: h1=0, h2=0, h3=0 ────────────────────────────────────────

    def test_TC_C_001_none_satisfied(self):
        """TC-C-001 | h1=0, h2=0, h3=0 → sleep fails, state stays 11"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=0,
            VCUO_bDIAG_AuthComplete_flg=0,
            can_stopped=False,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")

    # ── Rule C-002: h1=0, h2=0, h3=1 ────────────────────────────────────────

    def test_TC_C_002_only_h3(self):
        """TC-C-002 | h1=0, h2=0, h3=1 → sleep fails (missing h1, h2)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=0,
            VCUO_bDIAG_AuthComplete_flg=0,
            can_stopped=True,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h1", r["detail"])
        self.assertIn("h2", r["detail"])

    # ── Rule C-003: h1=0, h2=1, h3=0 ────────────────────────────────────────

    def test_TC_C_003_only_h2(self):
        """TC-C-003 | h1=0, h2=1, h3=0 → sleep fails (missing h1, h3)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=0,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=False,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h1", r["detail"])
        self.assertIn("h3", r["detail"])

    # ── Rule C-004: h1=0, h2=1, h3=1 ────────────────────────────────────────

    def test_TC_C_004_h2_and_h3_only(self):
        """TC-C-004 | h1=0, h2=1, h3=1 → sleep fails (missing h1)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=0,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h1", r["detail"])
        self.assertNotIn("h2", r["detail"])

    # ── Rule C-005: h1=1, h2=0, h3=0 ────────────────────────────────────────

    def test_TC_C_005_only_h1(self):
        """TC-C-005 | h1=1, h2=0, h3=0 → sleep fails (missing h2, h3)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=0,
            can_stopped=False,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h2", r["detail"])
        self.assertIn("h3", r["detail"])

    # ── Rule C-006: h1=1, h2=0, h3=1 ────────────────────────────────────────

    def test_TC_C_006_h1_and_h3_only(self):
        """TC-C-006 | h1=1, h2=0, h3=1 → sleep fails (missing h2)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=0,
            can_stopped=True,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h2", r["detail"])
        self.assertNotIn("h3", r["detail"])

    # ── Rule C-007: h1=1, h2=1, h3=0 ────────────────────────────────────────

    def test_TC_C_007_h1_and_h2_only(self):
        """TC-C-007 | h1=1, h2=1, h3=0 → sleep fails (missing h3 / CAN not stopped)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=False,
        )
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "error")
        self.assertIn("h3", r["detail"])

    # ── Rule C-008: h1=1, h2=1, h3=1 ────────────────────────────────────────

    def test_TC_C_008_all_three_satisfied(self):
        """TC-C-008 | h1=1, h2=1, h3=1 → SLEEP (state09, bus=0, result=expected)"""
        self._wake()
        r = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=0.01,
        )
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertEqual(r["result_type"], "expected")
        self.assertEqual(r["test_status"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
