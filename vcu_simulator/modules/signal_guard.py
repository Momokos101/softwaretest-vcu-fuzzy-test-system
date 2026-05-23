OVERVOLTAGE_THRESHOLD = 16.0
UNDERVOLTAGE_THRESHOLD = 6.0
DEBOUNCE_MIN_MS = 5

TIMING_SIGNALS = {"供电电压", "口盖信号", "门板信号"}


def validate_signal(
    signal_name: str,
    value: float,
    duration_ms: int | None = None,
    config: dict | None = None,
) -> dict:
    """Module B: validate raw input before state-machine processing."""
    overvoltage_threshold = (config or {}).get("overvoltage_threshold", OVERVOLTAGE_THRESHOLD)
    undervoltage_threshold = (config or {}).get("undervoltage_threshold", UNDERVOLTAGE_THRESHOLD)
    debounce_min_ms = (config or {}).get("debounce_min_ms", DEBOUNCE_MIN_MS)

    if signal_name == "供电电压" and value > overvoltage_threshold:
        return {
            "valid": False,
            "fault_type": "overvoltage",
            "reason": f"供电电压 {value}V 超过过压阈值 {overvoltage_threshold}V",
        }

    if signal_name == "供电电压" and value < undervoltage_threshold:
        return {
            "valid": False,
            "fault_type": "undervoltage",
            "reason": f"供电电压 {value}V 低于欠压阈值 {undervoltage_threshold}V",
        }

    if signal_name in TIMING_SIGNALS and duration_ms is not None and duration_ms < debounce_min_ms:
        return {
            "valid": False,
            "fault_type": "debounce_rejected",
            "reason": f"持续时间 {duration_ms}ms < 去抖阈值 {debounce_min_ms}ms，判定为噪声",
        }

    return {"valid": True, "fault_type": None, "reason": "信号有效"}
