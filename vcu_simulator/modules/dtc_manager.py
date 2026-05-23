from datetime import datetime


class DTCManager:
    def __init__(self) -> None:
        self._dtcs: dict[str, dict] = {}

    def log_dtc(self, code: str, reason: str) -> None:
        """Module D: record a DTC and increment its trigger count."""
        now = datetime.now().isoformat()
        if code not in self._dtcs:
            self._dtcs[code] = {
                "count": 0,
                "first_seen": now,
                "last_seen": None,
                "status": "active",
                "reason": reason,
            }
        self._dtcs[code]["count"] += 1
        self._dtcs[code]["last_seen"] = now
        self._dtcs[code]["status"] = "active"
        self._dtcs[code]["reason"] = reason

    def get_all(self) -> list[dict]:
        return [{"code": code, **data} for code, data in self._dtcs.items()]

    def get_active_codes(self) -> list[str]:
        return [code for code, data in self._dtcs.items() if data["status"] == "active"]

    def clear_all(self) -> None:
        for code in self._dtcs:
            self._dtcs[code]["status"] = "cleared"
