"""
Tollgate 2 — Integration Tests (HTTP API)
Tests the VCU simulator via its REST API using httpx.
Covers the 3 mandatory integration paths from PROJECT_PLAN_V2 STP-5.2:

  Path 1: MOD-B → MOD-A  (overvoltage/undervoltage guard blocks state transition)
  Path 2: MOD-A → MOD-D  (state10 stuck → DTC_001 written, GET /dtc confirms)
  Path 3: MOD-A → MOD-E  (state09 power_current ≤ 0.01 A compliance)

Requires VCU simulator running at http://localhost:8001
Start with: uvicorn main:app --port 8001 &
"""

import unittest
import httpx

BASE = "http://localhost:8001"


def _is_alive():
    try:
        httpx.get(f"{BASE}/state", timeout=2)
        return True
    except Exception:
        return False


def simulate(**kwargs):
    r = httpx.post(f"{BASE}/simulate", json=kwargs, timeout=10)
    r.raise_for_status()
    return r.json()


def reset(clear_dtc=False):
    r = httpx.post(f"{BASE}/reset", params={"clear_dtc": clear_dtc}, timeout=10)
    r.raise_for_status()
    return r.json()


def get_state():
    r = httpx.get(f"{BASE}/state", timeout=10)
    r.raise_for_status()
    return r.json()


def get_dtc():
    r = httpx.get(f"{BASE}/dtc", timeout=10)
    r.raise_for_status()
    return r.json()


_SKIP_MSG = "VCU simulator not running at localhost:8001 — start with: uvicorn main:app --port 8001 &"
_SERVER_UP = _is_alive()


@unittest.skipUnless(_SERVER_UP, _SKIP_MSG)
class IntegrationPath1_ModB_to_ModA(unittest.TestCase):
    """Path 1: MOD-B signal guard → MOD-A state machine.
    Overvoltage and undervoltage signals must be blocked BEFORE entering state machine.
    """

    def setUp(self):
        reset(clear_dtc=True)

    def test_INT_001_overvoltage_blocks_state_transition(self):
        """INT-001 | MOD-B→A | supply_voltage=16.5V → fault_protection, NOT state11"""
        r = simulate(supply_voltage=16.5, duration_ms=15)
        self.assertEqual(r["state_name"], "fault_protection")
        self.assertNotEqual(r["vehicle_state"], 11)
        self.assertEqual(r["power_alarm_flag"], 1)
        self.assertEqual(r["result_type"], "error")

    def test_INT_002_undervoltage_blocks_state_transition(self):
        """INT-002 | MOD-B→A | supply_voltage=5.5V → undervoltage_shutdown, NOT state11"""
        r = simulate(supply_voltage=5.5, duration_ms=15)
        self.assertEqual(r["state_name"], "undervoltage_shutdown")
        self.assertNotEqual(r["vehicle_state"], 11)
        self.assertEqual(r["bus_message_flag"], 0)
        self.assertEqual(r["result_type"], "error")

    def test_INT_003_debounce_does_not_change_state(self):
        """INT-003 | MOD-B→A | duration=4ms (noise) → rejected, stays state09"""
        r = simulate(supply_voltage=9.3, duration_ms=4)
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["signal_guard_result"]["fault_type"], "debounce_rejected")

    def test_INT_004_normal_signal_passes_guard_after_reset(self):
        """INT-004 | MOD-B→A | valid signal after reset from fault → state11"""
        simulate(supply_voltage=16.5, duration_ms=15)
        reset(clear_dtc=True)
        r = simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["result_type"], "expected")


@unittest.skipUnless(_SERVER_UP, _SKIP_MSG)
class IntegrationPath2_ModA_to_ModD(unittest.TestCase):
    """Path 2: MOD-A stuck detection → MOD-D DTC generation."""

    def setUp(self):
        reset(clear_dtc=True)

    def _rapid_cycle(self, n):
        for _ in range(n):
            simulate(supply_voltage=9.3, duration_ms=15)
            simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )

    def test_INT_005_dtc_001_written_on_stuck(self):
        """INT-005 | MOD-A→D | 3 rapid cycles → 4th wake → GET /dtc returns DTC_001"""
        self._rapid_cycle(3)
        r = simulate(supply_voltage=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 10)
        dtc_list = get_dtc()
        codes = [d["code"] for d in dtc_list]
        self.assertIn("DTC_001", codes)

    def test_INT_006_dtc_001_status_is_active(self):
        """INT-006 | MOD-A→D | DTC_001 must have status=active"""
        self._rapid_cycle(3)
        simulate(supply_voltage=9.3, duration_ms=15)
        dtc_list = get_dtc()
        dtc_001 = next((d for d in dtc_list if d["code"] == "DTC_001"), None)
        self.assertIsNotNone(dtc_001)
        self.assertEqual(dtc_001["status"], "active")

    def test_INT_007_reset_clears_dtc_001(self):
        """INT-007 | MOD-D | POST /reset with clear_dtc → all DTCs status=cleared"""
        self._rapid_cycle(3)
        simulate(supply_voltage=9.3, duration_ms=15)
        reset(clear_dtc=True)
        dtc_list = get_dtc()
        for d in dtc_list:
            self.assertEqual(d["status"], "cleared")

    def test_INT_008_dtc_002_on_overvoltage(self):
        """INT-008 | MOD-B→D | overvoltage → GET /dtc returns DTC_002"""
        simulate(supply_voltage=16.5, duration_ms=15)
        dtc_list = get_dtc()
        codes = [d["code"] for d in dtc_list]
        self.assertIn("DTC_002", codes)


@unittest.skipUnless(_SERVER_UP, _SKIP_MSG)
class IntegrationPath3_ModA_to_ModE(unittest.TestCase):
    """Path 3: MOD-A state09 → MOD-E power compliance."""

    def setUp(self):
        reset(clear_dtc=True)

    def test_INT_009_sleep_power_compliant(self):
        """INT-009 | MOD-A→E | sleep with power_current=0.01A → no alarm (REQ-024)"""
        simulate(supply_voltage=9.3, duration_ms=15)
        r = simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=0.01,
        )
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["power_alarm_flag"], 0)

    def test_INT_010_sleep_power_non_compliant_triggers_alarm(self):
        """INT-010 | MOD-A→E | sleep with power_current=0.06A > 0.05A → power_alarm_flag=1"""
        simulate(supply_voltage=9.3, duration_ms=15)
        r = simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=0.06,
        )
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["power_alarm_flag"], 1)

    def test_INT_011_get_state_reflects_live_state(self):
        """INT-011 | GET /state | returns current vehicle_state, power_alarm_flag, active_dtcs"""
        state = get_state()
        self.assertIn("vehicle_state", state)
        self.assertIn("power_alarm_flag", state)
        self.assertIn("active_dtcs", state)
        self.assertEqual(state["vehicle_state"], 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
