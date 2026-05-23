import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VCU_DIR = ROOT / "vcu_simulator"
sys.path.insert(0, str(VCU_DIR))

from simulator import VCUSimulator  # noqa: E402


class VCUSimulatorV2Test(unittest.TestCase):
    def setUp(self):
        self.sim = VCUSimulator()

    def test_supply_voltage_wake(self):
        result = self.sim.simulate(supply_voltage=9.3, duration_ms=15)

        self.assertEqual(result["vehicle_state"], 11)
        self.assertEqual(result["state_name"], "state11")
        self.assertEqual(result["pdcu_wake_reason"], 1)
        self.assertEqual(result["bus_message_flag"], 1)
        self.assertEqual(result["result_type"], "expected")

    def test_can_id_boundaries(self):
        low_invalid = self.sim.simulate(can_msg_id=0x3FF)
        self.assertEqual(low_invalid["result_type"], "error")
        self.assertEqual(low_invalid["vehicle_state"], 9)

        valid_low = self.sim.simulate(can_msg_id=0x400)
        self.assertEqual(valid_low["vehicle_state"], 11)
        self.assertEqual(valid_low["pdcu_wake_reason"], 2)

        self.sim.reset()
        valid_high = self.sim.simulate(can_msg_id=0x47F)
        self.assertEqual(valid_high["vehicle_state"], 11)
        self.assertEqual(valid_high["pdcu_wake_reason"], 2)

        self.sim.reset()
        high_invalid = self.sim.simulate(can_msg_id=0x480)
        self.assertEqual(high_invalid["result_type"], "error")
        self.assertEqual(high_invalid["vehicle_state"], 9)

    def test_sleep_requires_all_three_conditions(self):
        self.sim.simulate(supply_voltage=9.3, duration_ms=15)

        missing_h3 = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=False,
        )
        self.assertEqual(missing_h3["vehicle_state"], 11)
        self.assertEqual(missing_h3["result_type"], "error")

        sleep = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=0.01,
        )
        self.assertEqual(sleep["vehicle_state"], 9)
        self.assertEqual(sleep["bus_message_flag"], 0)
        self.assertEqual(sleep["result_type"], "expected")

    def test_overvoltage_and_undervoltage_log_dtcs(self):
        overvoltage = self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertEqual(overvoltage["state_name"], "fault_protection")
        self.assertEqual(overvoltage["power_alarm_flag"], 1)
        self.assertIn("DTC_002", overvoltage["active_dtcs"])

        self.sim.reset(clear_dtc=True)
        undervoltage = self.sim.simulate(supply_voltage=5.5, duration_ms=15)
        self.assertEqual(undervoltage["state_name"], "undervoltage_shutdown")
        self.assertEqual(undervoltage["bus_message_flag"], 0)
        self.assertIn("DTC_003", undervoltage["active_dtcs"])

    def test_debounce_rejects_short_timing_signal(self):
        result = self.sim.simulate(supply_voltage=9.3, duration_ms=4)

        self.assertEqual(result["vehicle_state"], 9)
        self.assertEqual(result["signal_guard_result"]["fault_type"], "debounce_rejected")
        self.assertEqual(result["result_type"], "error")

    def test_bus_off_blocks_can_wake(self):
        result = self.sim.simulate(can_error_count=256, can_msg_id=0x400)

        self.assertEqual(result["bus_off_flag"], 1)
        self.assertEqual(result["bus_message_flag"], 0)
        self.assertEqual(result["result_type"], "error")

    def test_dtc_clear_marks_records_cleared(self):
        self.sim.simulate(supply_voltage=16.5, duration_ms=15)
        self.assertTrue(self.sim.dtc_manager.get_active_codes())

        self.sim.reset(clear_dtc=True)
        records = self.sim.dtc_manager.get_all()

        self.assertEqual(records[0]["status"], "cleared")
        self.assertEqual(self.sim.dtc_manager.get_active_codes(), [])

    def test_power_alarm_and_sleep_power_compliance(self):
        self.sim.simulate(supply_voltage=9.3, duration_ms=15, power_current=0.25)
        time.sleep(0.55)
        alarm = self.sim.simulate(cp_voltage=10.0, power_current=0.25)
        self.assertEqual(alarm["power_alarm_flag"], 1)

        sleep = self.sim.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=0.06,
        )
        self.assertEqual(sleep["vehicle_state"], 9)
        self.assertEqual(sleep["power_alarm_flag"], 1)

    def test_stuck_detection_after_rapid_cycles(self):
        for _ in range(3):
            self.sim.simulate(supply_voltage=9.3, duration_ms=15)
            self.sim.simulate(
                VCUO_bDIAG_VCUIdle_flg=1,
                VCUO_bDIAG_AuthComplete_flg=1,
                can_stopped=True,
            )

        stuck = self.sim.simulate(supply_voltage=9.3, duration_ms=15)

        self.assertEqual(stuck["vehicle_state"], 10)
        self.assertEqual(stuck["state_name"], "state10")
        self.assertGreater(stuck["actual_duration"], 40)
        self.assertIn("DTC_001", stuck["active_dtcs"])

    def test_error_result_maps_to_fail_status(self):
        result = self.sim.simulate(supply_voltage=9.3, duration_ms=8)

        self.assertEqual(result["result_type"], "error")
        self.assertEqual(result["vehicle_state"], 9)
        self.assertEqual(result["test_status"], 4)

    def test_config_update_changes_guard_thresholds(self):
        self.sim.update_config({"guard": {"overvoltage_threshold": 15.0, "debounce_min_ms": 8}})

        overvoltage = self.sim.simulate(supply_voltage=15.5, duration_ms=15)
        self.assertEqual(overvoltage["state_name"], "fault_protection")
        self.assertEqual(overvoltage["signal_guard_result"]["fault_type"], "overvoltage")

        self.sim.reset(clear_dtc=True)
        debounce = self.sim.simulate(supply_voltage=9.3, duration_ms=7)
        self.assertEqual(debounce["signal_guard_result"]["fault_type"], "debounce_rejected")

    def test_config_update_changes_can_thresholds(self):
        self.sim.update_config({"can": {"valid_id_min": 0x410, "valid_id_max": 0x41F, "bus_off_threshold": 3}})

        old_low = self.sim.simulate(can_msg_id=0x400)
        self.assertEqual(old_low["result_type"], "error")
        self.assertEqual(old_low["test_status"], 4)

        valid = self.sim.simulate(can_msg_id=0x410)
        self.assertEqual(valid["vehicle_state"], 11)
        self.assertEqual(valid["pdcu_wake_reason"], 2)

        self.sim.reset()
        bus_off = self.sim.simulate(can_error_count=4, can_msg_id=0x410)
        self.assertEqual(bus_off["bus_off_flag"], 1)
        self.assertEqual(bus_off["test_status"], 4)

    def test_config_update_changes_power_thresholds(self):
        self.sim.update_config({"power": {"run_alarm_threshold_a": 0.1, "run_alarm_duration_ms": 100}})
        self.sim.simulate(supply_voltage=9.3, duration_ms=15, power_current=0.15)
        time.sleep(0.12)
        alarm = self.sim.simulate(cp_voltage=10.0, power_current=0.15)

        self.assertEqual(alarm["power_alarm_flag"], 1)

    def test_simulate_sleep_v2_state(self):
        result = self.sim.simulate_sleep()

        self.assertEqual(result["vehicle_state"], 9)
        self.assertEqual(result["state_name"], "state09")
        self.assertEqual(result["test_status"], 3)

    def test_all_wake_reasons(self):
        cases = [
            ({"supply_voltage": 9.3, "duration_ms": 15}, 1),
            ({"can_msg_id": 0x400}, 2),
            ({"cp_voltage": 10.0}, 3),
            ({"cc_voltage": 4.0}, 4),
            ({"cc2_voltage": 4.0}, 5),
            ({"hood_voltage": 4.5, "duration_ms": 15}, 6),
            ({"door_voltage": 0.5, "duration_ms": 15}, 7),
        ]

        for payload, wake_reason in cases:
            with self.subTest(wake_reason=wake_reason):
                self.sim.reset()
                result = self.sim.simulate(**payload)
                self.assertEqual(result["vehicle_state"], 11)
                self.assertEqual(result["pdcu_wake_reason"], wake_reason)


if __name__ == "__main__":
    unittest.main()
