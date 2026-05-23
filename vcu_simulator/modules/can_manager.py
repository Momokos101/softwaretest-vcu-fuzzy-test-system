CAN_VALID_ID_MIN = 0x400
CAN_VALID_ID_MAX = 0x47F
BUS_OFF_THRESHOLD = 255


class CANManager:
    def __init__(self) -> None:
        self.error_counter = 0
        self.bus_off = False

    def process_message(self, msg_id: int, config: dict | None = None) -> dict:
        """Module C: filter CAN messages and report whether they wake the VCU."""
        valid_id_min = (config or {}).get("valid_id_min", CAN_VALID_ID_MIN)
        valid_id_max = (config or {}).get("valid_id_max", CAN_VALID_ID_MAX)
        if self.bus_off:
            return {"wake_triggered": False, "reason": "总线处于 bus_off 状态"}
        if not (valid_id_min <= msg_id <= valid_id_max):
            return {"wake_triggered": False, "reason": f"ID 0x{msg_id:03X} 超出有效范围"}
        return {"wake_triggered": True, "reason": f"ID 0x{msg_id:03X} 在有效范围内，触发唤醒"}

    def report_error(self, count: int = 1, config: dict | None = None) -> None:
        bus_off_threshold = (config or {}).get("bus_off_threshold", BUS_OFF_THRESHOLD)
        self.error_counter += max(0, count)
        if self.error_counter > bus_off_threshold:
            self.bus_off = True

    def reset(self) -> None:
        self.error_counter = 0
        self.bus_off = False
