from __future__ import annotations

from copy import deepcopy
from time import time
from typing import Any

from constants import (
    BATTERY_VOLTAGE,
    BMS_WAKE_CMD,
    MCU_WAKE_CMD,
    STATE_FAULT_PROTECTION,
    STATE_INIT,
    STATE_RUN,
    STATE_SLEEP,
    STATE_UNDERVOLTAGE_SHUTDOWN,
    V2_CONFIG,
)
from modules.can_manager import CANManager
from modules.dtc_manager import DTCManager
from modules.power_monitor import PowerMonitor
from modules.signal_guard import validate_signal


class VCUSimulator:
    """Stateful VCU behavior simulator defined by PROJECT_PLAN_V2.md."""

    def __init__(self) -> None:
        self.config = deepcopy(V2_CONFIG)
        self.can_manager = CANManager()
        self.dtc_manager = DTCManager()
        self.power_monitor = PowerMonitor()
        self.state: int | str = STATE_SLEEP
        self._rapid_sleep_timestamps: list[float] = []
        self._performance: list[dict[str, Any]] = []

    def simulate(self, **payload: Any) -> dict:
        self._normalize_legacy_payload(payload)

        if payload.get("can_error_count", 0):
            self.can_manager.report_error(int(payload["can_error_count"]), self.config["can"])

        signal_guard_result = self._run_signal_guard(payload)
        if not signal_guard_result["valid"]:
            result = self._handle_guard_rejection(signal_guard_result, payload)
            self._record_performance("type1", result["actual_duration"])
            return result

        if self._has_sleep_inputs(payload):
            result = self._handle_sleep(payload, signal_guard_result)
            self._record_performance("type2", result["actual_duration"])
            return result

        wake_reason, reason_detail = self._detect_wake_reason(payload)
        if wake_reason:
            result = self._handle_wake(wake_reason, reason_detail, signal_guard_result, payload)
        else:
            result = self._response(
                result_type="error",
                pdcu_wake_reason=0,
                actual_duration=self.config["timing"]["type1_nominal_duration"],
                detail=reason_detail or "未满足任何唤醒条件，VCU保持当前状态",
                signal_guard_result=signal_guard_result,
                power_current=payload.get("power_current"),
            )

        self._record_performance("type1", result["actual_duration"])
        return result

    def simulate_sleep(
        self,
        cc2_voltage: float = 12.0,
        cc_voltage: float = 12.0,
        cp_amplitude: float = 0.0,
        supply_voltage: float = 0.0,
        network_wake_enable: float = 0.0,
    ) -> dict:
        return self.simulate(
            VCUO_bDIAG_VCUIdle_flg=1,
            VCUO_bDIAG_AuthComplete_flg=1,
            can_stopped=True,
            power_current=self.config["power"]["sleep_expected_current_a"],
        )

    def simulate_batch(self, requests: list) -> list:
        results = []
        for req in requests:
            result = self.simulate(**dict(req))
            result["signal_name"] = req.get("signal_name")
            result["input_value"] = req.get("value")
            results.append(result)
        return results

    def reset(self, clear_dtc: bool = False) -> None:
        self.state = STATE_SLEEP
        self.can_manager.reset()
        self.power_monitor.reset()
        self._rapid_sleep_timestamps = []
        if clear_dtc:
            self.dtc_manager.clear_all()

    def get_state(self) -> dict:
        return {
            "vehicle_state": self._vehicle_state(),
            "state_name": self._state_name(),
            "vehicle_mode": self._vehicle_mode(),
            "bus_message_flag": self._bus_message_flag(),
            "power_alarm_flag": self.power_monitor.power_alarm_flag,
            "bus_off_flag": int(self.can_manager.bus_off),
            "active_dtcs": self.dtc_manager.get_active_codes(),
        }

    def get_config(self) -> dict:
        return deepcopy(self.config)

    def update_config(self, update: dict) -> dict:
        self._deep_update(self.config, update)
        return self.get_config()

    def get_performance(self) -> dict:
        durations = [item["actual_duration"] for item in self._performance]
        return {
            "total_requests": len(self._performance),
            "type1_requests": sum(1 for item in self._performance if item["type"] == "type1"),
            "type2_requests": sum(1 for item in self._performance if item["type"] == "type2"),
            "max_actual_duration": max(durations) if durations else 0.0,
            "average_actual_duration": sum(durations) / len(durations) if durations else 0.0,
            "durations": durations,
        }

    def _handle_guard_rejection(self, guard: dict, payload: dict[str, Any]) -> dict:
        fault_type = guard["fault_type"]
        if fault_type == "overvoltage":
            self.state = STATE_FAULT_PROTECTION
            self.dtc_manager.log_dtc("DTC_002", guard["reason"])
            self.power_monitor.power_alarm_flag = 1
            detail = "过压保护触发，拒绝唤醒并进入 fault_protection"
        elif fault_type == "undervoltage":
            self.state = STATE_UNDERVOLTAGE_SHUTDOWN
            self.dtc_manager.log_dtc("DTC_003", guard["reason"])
            detail = "欠压保护触发，关闭CAN通信并进入 undervoltage_shutdown"
        else:
            detail = guard["reason"]

        return self._response(
            result_type="error",
            pdcu_wake_reason=0,
            actual_duration=self.config["timing"]["type1_nominal_duration"],
            detail=detail,
            signal_guard_result=guard,
            power_current=payload.get("power_current"),
        )

    def _handle_wake(self, wake_reason: int, detail: str, guard: dict, payload: dict[str, Any]) -> dict:
        if self.state in {STATE_FAULT_PROTECTION, STATE_UNDERVOLTAGE_SHUTDOWN}:
            return self._response(
                result_type="error",
                pdcu_wake_reason=0,
                actual_duration=self.config["timing"]["type1_nominal_duration"],
                detail=f"当前处于 {self._state_name()}，需要reset后才能唤醒",
                signal_guard_result=guard,
                power_current=payload.get("power_current"),
            )

        if len(self._rapid_sleep_timestamps) >= self.config["timing"]["rapid_cycle_threshold"]:
            self.state = STATE_INIT
            actual_duration = self.config["timing"]["stuck_est_time"] * 2 + 1
            self.dtc_manager.log_dtc("DTC_001", "连续快速唤醒-休眠导致 state10 卡死")
            self.power_monitor.power_alarm_flag = 1
            return self._response(
                result_type="error",
                pdcu_wake_reason=wake_reason,
                actual_duration=actual_duration,
                detail=f"{detail}；触发state10卡死缺陷，actual_duration超过估计时间2倍",
                signal_guard_result=guard,
                power_current=self.config["power"]["stuck_current_a"],
            )

        self.state = STATE_INIT
        self.state = STATE_RUN
        return self._response(
            result_type="expected",
            pdcu_wake_reason=wake_reason,
            actual_duration=self.config["timing"]["type1_nominal_duration"],
            detail=f"{detail}，Module B校验通过，唤醒成功",
            signal_guard_result=guard,
            power_current=payload.get("power_current"),
        )

    def _handle_sleep(self, payload: dict[str, Any], guard: dict) -> dict:
        h1 = payload.get("VCUO_bDIAG_VCUIdle_flg") == 1
        h2 = payload.get("VCUO_bDIAG_AuthComplete_flg") == 1
        h3 = payload.get("can_stopped") is True
        current = payload.get("power_current")

        if h1 and h2 and h3:
            self.state = STATE_SLEEP
            now = time()
            if self._rapid_sleep_timestamps and now - self._rapid_sleep_timestamps[-1] >= self.config["timing"]["rapid_cycle_interval_s"]:
                self._rapid_sleep_timestamps = []
            self._rapid_sleep_timestamps.append(now)
            if current is not None and not self.power_monitor.check_sleep_compliance(float(current), self.config["power"]):
                self.power_monitor.power_alarm_flag = 1
            else:
                self.power_monitor.power_alarm_flag = 0
            return self._response(
                result_type="expected",
                pdcu_wake_reason=0,
                actual_duration=self.config["timing"]["type2_nominal_duration"],
                detail="h1/h2/h3同时满足，VCU进入state09休眠",
                signal_guard_result=guard,
                power_current=current,
            )

        missing = []
        if not h1:
            missing.append("h1")
        if not h2:
            missing.append("h2")
        if not h3:
            missing.append("h3")
        return self._response(
            result_type="error",
            pdcu_wake_reason=0,
            actual_duration=self.config["timing"]["type2_nominal_duration"],
            detail=f"休眠条件不完整（缺少{','.join(missing)}），状态保持不变",
            signal_guard_result=guard,
            power_current=current,
        )

    def _detect_wake_reason(self, payload: dict[str, Any]) -> tuple[int, str]:
        wake = self.config["wake"]

        if payload.get("supply_voltage") is not None:
            value = float(payload["supply_voltage"])
            duration_ms = payload.get("duration_ms")
            if value > wake["supply_voltage"] and duration_ms is not None and duration_ms >= wake["supply_duration_ms"]:
                return 1, f"供电电压={value}V > 9V，持续{duration_ms}ms >= 10ms"
            if value > wake["supply_voltage"]:
                return 0, f"供电电压={value}V满足值条件，但持续时间不足"
            return 0, f"供电电压={value}V未超过9V"

        if payload.get("can_msg_id") is not None:
            result = self.can_manager.process_message(int(payload["can_msg_id"]), self.config["can"])
            return (2, result["reason"]) if result["wake_triggered"] else (0, result["reason"])

        if payload.get("cp_voltage") is not None:
            value = float(payload["cp_voltage"])
            return (3, f"CP信号={value}V > 9V") if value > wake["cp_voltage"] else (0, f"CP信号={value}V未超过9V")

        if payload.get("cc_voltage") is not None:
            value = float(payload["cc_voltage"])
            return (4, f"CC信号={value}V < 4.4V") if value < wake["cc_voltage"] else (0, f"CC信号={value}V未低于4.4V")

        if payload.get("cc2_voltage") is not None:
            value = float(payload["cc2_voltage"])
            threshold = wake["cc2_ubr_threshold"]
            return (5, f"CC2信号={value}V < UBR阈值{threshold}V") if value < threshold else (0, f"CC2信号={value}V未低于UBR阈值")

        if payload.get("hood_voltage") is not None:
            value = float(payload["hood_voltage"])
            duration_ms = payload.get("duration_ms")
            if value > wake["hood_voltage"] and duration_ms is not None and duration_ms >= wake["hood_duration_ms"]:
                return 6, f"口盖信号={value}V > 4V，持续{duration_ms}ms >= 10ms"
            return 0, "口盖信号未同时满足电压和时序条件"

        if payload.get("door_voltage") is not None:
            value = float(payload["door_voltage"])
            duration_ms = payload.get("duration_ms")
            if value < wake["door_voltage"] and duration_ms is not None and duration_ms >= wake["door_duration_ms"]:
                return 7, f"门板信号={value}V < 1V，持续{duration_ms}ms >= 10ms"
            return 0, "门板信号未同时满足电压和时序条件"

        return 0, ""

    def _run_signal_guard(self, payload: dict[str, Any]) -> dict:
        if payload.get("supply_voltage") is not None:
            return validate_signal("供电电压", float(payload["supply_voltage"]), payload.get("duration_ms"), self.config["guard"])
        if payload.get("hood_voltage") is not None:
            return validate_signal("口盖信号", float(payload["hood_voltage"]), payload.get("duration_ms"), self.config["guard"])
        if payload.get("door_voltage") is not None:
            return validate_signal("门板信号", float(payload["door_voltage"]), payload.get("duration_ms"), self.config["guard"])
        return {"valid": True, "fault_type": None, "reason": "信号有效"}

    def _response(
        self,
        result_type: str,
        pdcu_wake_reason: int,
        actual_duration: float,
        detail: str,
        signal_guard_result: dict,
        power_current: float | None,
    ) -> dict:
        current = self._default_power_current(power_current)
        if self.state == STATE_RUN:
            self.power_monitor.update(current, self.config["power"])

        if result_type == "error":
            test_status = 4
        elif self.state == STATE_RUN:
            test_status = 1
        elif self.state == STATE_SLEEP:
            test_status = 3
        else:
            test_status = 4
        return {
            "vehicle_state": self._vehicle_state(),
            "vehicle_mode": self._vehicle_mode(),
            "power_current": current,
            "bus_message_flag": self._bus_message_flag(),
            "pdcu_wake_reason": pdcu_wake_reason,
            "actual_duration": actual_duration,
            "result_type": result_type,
            "power_alarm_flag": self.power_monitor.power_alarm_flag,
            "bus_off_flag": int(self.can_manager.bus_off),
            "active_dtcs": self.dtc_manager.get_active_codes(),
            "signal_guard_result": signal_guard_result,
            "detail": detail,
            "state_name": self._state_name(),
            "test_status": test_status,
            "ready_flag": 1 if self.state == STATE_RUN else 0,
            "bms_wake_cmd": BMS_WAKE_CMD,
            "mcu_wake_cmd": MCU_WAKE_CMD,
            "battery_voltage": BATTERY_VOLTAGE,
        }

    def _vehicle_state(self) -> int:
        if isinstance(self.state, int):
            return self.state
        if self.state == STATE_FAULT_PROTECTION:
            return STATE_INIT
        if self.state == STATE_UNDERVOLTAGE_SHUTDOWN:
            return STATE_SLEEP
        return STATE_SLEEP

    def _state_name(self) -> str:
        if self.state == STATE_SLEEP:
            return "state09"
        if self.state == STATE_INIT:
            return "state10"
        if self.state == STATE_RUN:
            return "state11"
        return str(self.state)

    def _vehicle_mode(self) -> int:
        return 5 if self.state == STATE_RUN else 2

    def _bus_message_flag(self) -> int:
        if self.can_manager.bus_off or self.state in {STATE_SLEEP, STATE_UNDERVOLTAGE_SHUTDOWN}:
            return 0
        return 1 if self.state == STATE_RUN else 0

    def _default_power_current(self, current: float | None) -> float:
        if current is not None:
            return float(current)
        if self.state == STATE_RUN:
            return self.config["power"]["run_expected_current_a"]
        if self.state == STATE_INIT:
            return self.config["power"]["stuck_current_a"]
        return self.config["power"]["sleep_expected_current_a"]

    def _has_sleep_inputs(self, payload: dict[str, Any]) -> bool:
        return any(
            key in payload and payload[key] is not None
            for key in ("VCUO_bDIAG_VCUIdle_flg", "VCUO_bDIAG_AuthComplete_flg", "can_stopped")
        )

    def _normalize_legacy_payload(self, payload: dict[str, Any]) -> None:
        signal_name = payload.get("signal_name")
        value = payload.get("value")
        if signal_name is None or value is None:
            return
        if signal_name == "供电电压":
            payload.setdefault("supply_voltage", value)
        elif signal_name in {"CP幅值", "CP信号"}:
            payload.setdefault("cp_voltage", value)
        elif signal_name in {"CC电压值", "CC信号"}:
            payload.setdefault("cc_voltage", value)
        elif signal_name in {"CC2电压", "CC2信号"}:
            payload.setdefault("cc2_voltage", value)
        elif signal_name == "口盖信号":
            payload.setdefault("hood_voltage", value)
        elif signal_name == "门板信号":
            payload.setdefault("door_voltage", value)
        elif signal_name in {"网络唤醒报文使能状态", "CAN网络报文"} and value:
            payload.setdefault("can_msg_id", 0x400)

    def _record_performance(self, request_type: str, actual_duration: float) -> None:
        self._performance.append({"type": request_type, "actual_duration": actual_duration})

    def _deep_update(self, target: dict, update: dict) -> None:
        for key, value in update.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
