"""
Coverage gap tests — target the uncovered branches in simulator.py
to bring simulator.py branch coverage above 90% (Tollgate 1 requirement).

Uncovered branches addressed here:
  L85-91   simulate_batch()
  L120-121 get_performance() with data
  L273     _detect_wake_reason() catch-all (no wake signal provided)
  L358     _default_power_current() STATE_INIT branch without explicit current
  L372-385 _normalize_legacy_payload() legacy signal name mapping
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vcu_simulator"))

from simulator import VCUSimulator  # noqa: E402


class CoverageGapTests(unittest.TestCase):

    def setUp(self):
        self.sim = VCUSimulator()

    # ── Lines 85-91: simulate_batch() ────────────────────────────────────────

    def test_simulate_batch_basic(self):
        """simulate_batch() processes a list of requests sequentially without resetting state.
        First request: valid wake → state11.
        Second request: invalid voltage → no state change, stays state11 (VCU is stateful)."""
        requests = [
            {"supply_voltage": 9.3, "duration_ms": 15},
            {"supply_voltage": 8.9, "duration_ms": 15},
        ]
        results = self.sim.simulate_batch(requests)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["vehicle_state"], 11)
        self.assertEqual(results[0]["result_type"], "expected")
        # Second call: voltage too low → error, but VCU already in state11 (no state regression)
        self.assertEqual(results[1]["result_type"], "error")
        self.assertEqual(results[1]["vehicle_state"], 11)

    def test_simulate_batch_preserves_signal_name(self):
        """simulate_batch() attaches signal_name and input_value from the request."""
        requests = [{"signal_name": "供电电压", "value": 9.3, "supply_voltage": 9.3, "duration_ms": 15}]
        results = self.sim.simulate_batch(requests)
        self.assertEqual(results[0]["signal_name"], "供电电压")
        self.assertEqual(results[0]["input_value"], 9.3)

    # ── Lines 120-121: get_performance() with data ────────────────────────────

    def test_get_performance_after_simulations(self):
        """get_performance() returns correct stats after test executions."""
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)
        self.sim.simulate(supply_voltage=8.9, duration_ms=15)

        perf = self.sim.get_performance()
        self.assertEqual(perf["total_requests"], 2)
        self.assertGreater(perf["max_actual_duration"], 0)
        self.assertGreater(perf["average_actual_duration"], 0)
        self.assertEqual(len(perf["durations"]), 2)

    # ── Line 273: _detect_wake_reason() no-signal catch-all ──────────────────

    def test_simulate_with_no_wake_signal(self):
        """When simulate() receives no recognized wake signal, no wake is triggered."""
        r = self.sim.simulate(power_current=0.03)  # only power, no wake signal
        self.assertEqual(r["vehicle_state"], 9)
        self.assertEqual(r["pdcu_wake_reason"], 0)
        self.assertEqual(r["result_type"], "error")

    # ── Line 358: _default_power_current() STATE_INIT without explicit current

    def test_stuck_state_default_current(self):
        """When stuck in state10 with no explicit power_current, default stuck current is used."""
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )
        r = self.sim.simulate(supply_voltage=9.3, duration_ms=15)  # no power_current arg
        self.assertEqual(r["vehicle_state"], 10)
        stuck_current = self.sim.config["power"]["stuck_current_a"]
        self.assertEqual(r["power_current"], stuck_current)

    # ── Lines 372-385: _normalize_legacy_payload() ───────────────────────────

    def test_legacy_supply_voltage_signal_name(self):
        """Legacy payload with signal_name='供电电压' maps to supply_voltage."""
        r = self.sim.simulate(signal_name="供电电压", value=9.3, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 1)

    def test_legacy_cp_signal_name(self):
        """Legacy payload with signal_name='CP幅值' maps to cp_voltage."""
        r = self.sim.simulate(signal_name="CP幅值", value=10.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 3)

    def test_legacy_cc_signal_name(self):
        """Legacy payload with signal_name='CC电压值' maps to cc_voltage."""
        r = self.sim.simulate(signal_name="CC电压值", value=4.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 4)

    def test_legacy_cc2_signal_name(self):
        """Legacy payload with signal_name='CC2电压' maps to cc2_voltage."""
        r = self.sim.simulate(signal_name="CC2电压", value=4.0)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 5)

    def test_legacy_hood_signal_name(self):
        """Legacy payload with signal_name='口盖信号' maps to hood_voltage."""
        r = self.sim.simulate(signal_name="口盖信号", value=4.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 6)

    def test_legacy_door_signal_name(self):
        """Legacy payload with signal_name='门板信号' maps to door_voltage."""
        r = self.sim.simulate(signal_name="门板信号", value=0.5, duration_ms=15)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 7)

    def test_legacy_can_network_signal_name(self):
        """Legacy payload with signal_name='网络唤醒报文使能状态', value=1 maps to can_msg_id=0x400."""
        r = self.sim.simulate(signal_name="网络唤醒报文使能状态", value=1)
        self.assertEqual(r["vehicle_state"], 11)
        self.assertEqual(r["pdcu_wake_reason"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
