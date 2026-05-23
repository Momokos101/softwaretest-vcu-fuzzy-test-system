import time

ALARM_THRESHOLD_A = 0.2
ALARM_DURATION_MS = 500
SLEEP_MAX_CURRENT_A = 0.01


class PowerMonitor:
    def __init__(self) -> None:
        self._high_current_start: float | None = None
        self.power_alarm_flag = 0

    def update(self, current_a: float | None, config: dict | None = None) -> int:
        """Module E: set alarm after sustained high current."""
        if current_a is None:
            return self.power_alarm_flag

        alarm_threshold_a = (config or {}).get("run_alarm_threshold_a", ALARM_THRESHOLD_A)
        alarm_duration_ms = (config or {}).get("run_alarm_duration_ms", ALARM_DURATION_MS)
        now = time.time() * 1000
        if current_a > alarm_threshold_a:
            if self._high_current_start is None:
                self._high_current_start = now
            elif now - self._high_current_start >= alarm_duration_ms:
                self.power_alarm_flag = 1
        else:
            self._high_current_start = None
            self.power_alarm_flag = 0
        return self.power_alarm_flag

    def check_sleep_compliance(self, current_a: float, config: dict | None = None) -> bool:
        sleep_max_current_a = (config or {}).get("sleep_expected_current_a", SLEEP_MAX_CURRENT_A)
        return current_a <= sleep_max_current_a

    def reset(self) -> None:
        self._high_current_start = None
        self.power_alarm_flag = 0
