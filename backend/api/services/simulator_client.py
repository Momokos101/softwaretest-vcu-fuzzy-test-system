"""HTTP client for the V2 VCU simulator API."""
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, List

import httpx

from api.models.schemas import ExecutionResult, TestCase, TestCaseStatus
from api.services import performance_service, test_design_service


class SimulatorClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("VCU_SIMULATOR_URL") or "http://localhost:8001").rstrip("/")

    async def reset(self, clear_dtc: bool = False) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            # VCU simulator /reset uses a query param, not a JSON body
            response = await client.post(f"{self.base_url}/reset", params={"clear_dtc": clear_dtc})
            response.raise_for_status()
            return response.json()

    async def state(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(f"{self.base_url}/state")
            response.raise_for_status()
            return response.json()

    async def config(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(f"{self.base_url}/config")
            response.raise_for_status()
            return response.json()

    async def dtc(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(f"{self.base_url}/dtc")
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else data.get("dtcs", [])

    async def performance(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(f"{self.base_url}/performance")
            response.raise_for_status()
            return response.json()

    async def simulate(self, test_case: TestCase) -> dict[str, Any]:
        payload = _case_to_payload(test_case)
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(f"{self.base_url}/simulate", json=payload)
            response.raise_for_status()
            return response.json()

    async def execute_test_case(self, test_case: TestCase) -> ExecutionResult:
        started = time.perf_counter()
        actual = await self.simulate(test_case)
        elapsed_ms = (time.perf_counter() - started) * 1000
        passed, mismatches = _compare_expected(actual, test_case)
        performance_service.record(
            "simulator.execute",
            elapsed_ms,
            detail={"test_case_id": test_case.id, "requirement_id": test_case.requirement_id},
        )
        return ExecutionResult(
            test_case_id=test_case.id,
            request_payload=_case_to_payload(test_case),
            actual_output=actual,
            expected_output=test_case.expected_results,
            match_expected=passed,
            mismatches=mismatches,
            executed_at=datetime.now(),
            elapsed_ms=round(elapsed_ms, 2),
        )


simulator_client = SimulatorClient()


async def execute_single(test_case: TestCase) -> TestCase:
    try:
        result = await simulator_client.execute_test_case(test_case)
        return _apply_result(test_case, result)
    except Exception as exc:
        test_case.status = TestCaseStatus.ERROR
        test_case.execution_result = {
            "error": str(exc),
            "detail": f"V2 simulator call failed. Check {simulator_client.base_url}",
            "match_expected": False,
            "executed_at": datetime.now().isoformat(),
        }
        return test_case


async def execute_batch(test_cases: List[TestCase], reset_before_run: bool = True) -> List[TestCase]:
    if reset_before_run:
        try:
            await simulator_client.reset(clear_dtc=False)
        except Exception as exc:
            raise Exception(
                f"VCU 仿真器连接失败 ({simulator_client.base_url})。"
                f"请先启动仿真器: cd vcu_simulator && python main.py。错误: {exc}"
            ) from exc
    results = []
    for case in test_cases:
        results.append(await execute_single(case))
    return results


def _apply_result(test_case: TestCase, result: ExecutionResult) -> TestCase:
    test_case.execution_result = result.model_dump(mode="json")
    test_case.status = TestCaseStatus.PASS if result.match_expected else TestCaseStatus.FAIL
    test_case.updated_at = datetime.now()
    return test_case


def _case_to_payload(test_case: TestCase) -> dict[str, Any]:
    return {
        "type": test_case.type,
        "in_data": [item.model_dump(mode="json", exclude_none=True) for item in test_case.in_data],
        "expected_results": [item.model_dump(mode="json") for item in test_case.expected_results],
        "error": [item.model_dump(mode="json") for item in test_case.error],
        "est_time": test_case.est_time,
        "requirement_id": test_case.requirement_id,
        "test_case_id": test_case.id,
    }


def _compare_expected(actual: dict[str, Any], test_case: TestCase) -> tuple[bool, list[str]]:
    mismatches: list[str] = []
    for expected in test_case.expected_results:
        actual_value = actual.get(expected.name)
        if not _matches(actual_value, expected.operator, expected.value):
            mismatches.append(
                f"{expected.name}: expected {expected.operator} {expected.value}, actual {actual_value}"
            )
    return not mismatches, mismatches


def _matches(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "contains":
        return isinstance(actual, list | str | dict) and expected in actual
    try:
        actual_num = float(actual)
        expected_num = float(expected)
    except (TypeError, ValueError):
        return False
    if operator == "gte":
        return actual_num >= expected_num
    if operator == "lte":
        return actual_num <= expected_num
    if operator == "gt":
        return actual_num > expected_num
    if operator == "lt":
        return actual_num < expected_num
    return False
