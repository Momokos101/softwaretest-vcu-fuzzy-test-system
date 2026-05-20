"""
VCU仿真器HTTP客户端。
默认调用真实仿真器 http://localhost:8001，与 Member 1 交接文档保持一致。
"""
import os
from datetime import datetime
from typing import Any, List

import httpx

from api.models.schemas import ExecutionResult, TestCase, TestCaseStatus


class SimulatorClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("VCU_SIMULATOR_URL") or "http://localhost:8001").rstrip("/")

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def simulate(self, signal_name: str, value: float, data_type: str = "float") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.post(
                f"{self.base_url}/simulate",
                json={"signal_name": signal_name, "value": value, "data_type": data_type},
            )
            response.raise_for_status()
            return response.json()

    async def simulate_sleep(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.post(
                f"{self.base_url}/simulate/sleep",
                json={
                    "cc2_voltage": 12.0,
                    "cc_voltage": 12.0,
                    "cp_amplitude": 0.0,
                    "supply_voltage": 0.0,
                    "network_wake_enable": 0.0,
                },
            )
            response.raise_for_status()
            return response.json()

    async def simulate_batch(self, test_cases: List[TestCase]) -> List[dict[str, Any]]:
        payload = [
            {"signal_name": tc.signal_name, "value": tc.test_value, "data_type": "float"}
            for tc in test_cases
            if tc.expected_result != "SLEEP"
        ]
        results: List[dict[str, Any]] = []
        if payload:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                response = await client.post(f"{self.base_url}/simulate/batch", json=payload)
                response.raise_for_status()
                results = response.json()
        return results

    async def execute_test_case(self, test_case: TestCase) -> ExecutionResult:
        if test_case.expected_result == "SLEEP":
            data = await self.simulate_sleep()
        else:
            data = await self.simulate(test_case.signal_name, test_case.test_value)
        return _build_execution_result(test_case, data)


simulator_client = SimulatorClient()


async def execute_single(test_case: TestCase) -> TestCase:
    """执行单个测试用例并原位更新状态。"""
    try:
        result = await simulator_client.execute_test_case(test_case)
        _apply_result(test_case, result)
    except Exception as exc:
        test_case.status = TestCaseStatus.ERROR
        test_case.execution_result = {
            "error": str(exc),
            "detail": f"仿真器调用失败，请确认 {simulator_client.base_url} 已启动",
            "match_expected": False,
            "executed_at": datetime.now().isoformat(),
        }
    return test_case


async def execute_batch(test_cases: List[TestCase]) -> List[TestCase]:
    """批量执行。含SLEEP用例时单独调用休眠接口，其余优先使用/simulate/batch。"""
    regular_cases = [tc for tc in test_cases if tc.expected_result != "SLEEP"]
    sleep_cases = [tc for tc in test_cases if tc.expected_result == "SLEEP"]

    try:
        batch_results = await simulator_client.simulate_batch(regular_cases)
        for test_case, data in zip(regular_cases, batch_results):
            _apply_result(test_case, _build_execution_result(test_case, data))
    except Exception:
        for test_case in regular_cases:
            await execute_single(test_case)

    for test_case in sleep_cases:
        await execute_single(test_case)

    return test_cases


def _build_execution_result(test_case: TestCase, data: dict[str, Any]) -> ExecutionResult:
    return ExecutionResult(
        test_case_id=test_case.id,
        test_status=data["test_status"],
        vehicle_state=data["vehicle_state"],
        vehicle_mode=data["vehicle_mode"],
        ready_flag=data["ready_flag"],
        actual_duration=data.get("actual_duration", 0.0),
        detail=data.get("detail", ""),
        executed_at=datetime.now(),
        match_expected=(
            data["test_status"] == test_case.expected_status
            and data["vehicle_state"] == test_case.expected_vehicle_state
        ),
    )


def _apply_result(test_case: TestCase, result: ExecutionResult) -> None:
    test_case.execution_result = {
        "test_status": result.test_status,
        "vehicle_state": result.vehicle_state,
        "vehicle_mode": result.vehicle_mode,
        "ready_flag": result.ready_flag,
        "actual_duration": result.actual_duration,
        "detail": result.detail,
        "expected_status": test_case.expected_status,
        "expected_vehicle_state": test_case.expected_vehicle_state,
        "match_expected": result.match_expected,
        "executed_at": result.executed_at.isoformat(),
    }
    test_case.status = TestCaseStatus.PASS if result.match_expected else TestCaseStatus.FAIL
