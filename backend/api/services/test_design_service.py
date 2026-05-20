"""
测试设计服务。
根据结构化需求生成 EP / BVA / Decision Table 用例，并使用仿真器约定的
PASS/FAIL/SLEEP oracle 填充预期结果。
"""
import uuid
from datetime import datetime
from typing import List, Optional

from api.models.schemas import (
    ParsedRequirement,
    TestCase,
    TestCaseStatus,
    TestCaseUpdate,
    TestGenerationRequest,
    TestTechnique,
)


_test_cases: List[TestCase] = []

SIGNAL_RULES = {
    "CC2电压": {"kind": "valid_range", "min": 4.8, "max": 7.7, "low": 3.0, "high": 9.0},
    "CC电压值": {"kind": "fail_range", "min": 0.1, "max": 3.9, "low": 0.0, "high": 12.0},
    "CP幅值": {"kind": "fail_range", "min": 9.1, "max": 12.9, "low": 0.0, "high": 14.0},
    "供电电压": {"kind": "fail_range", "min": 9.1, "max": 15.9, "low": 0.0, "high": 18.0},
    "网络唤醒报文使能状态": {"kind": "binary_fail_one", "min": 0.0, "max": 1.0, "low": 0.0, "high": 1.0},
}


def generate_test_cases(request: TestGenerationRequest, parsed_req: ParsedRequirement) -> List[TestCase]:
    cases: List[TestCase] = []
    fields = parsed_req.input_fields or list(parsed_req.data_ranges.keys())

    for technique in request.techniques:
        if technique == TestTechnique.EQUIVALENCE_PARTITIONING:
            cases.extend(_generate_ep_cases(request.requirement_id, parsed_req, fields))
        elif technique == TestTechnique.BOUNDARY_VALUE_ANALYSIS:
            cases.extend(_generate_bva_cases(request.requirement_id, parsed_req, fields, request.bva_delta or 0.1))
        elif technique == TestTechnique.DECISION_TABLE:
            cases.extend(_generate_dt_cases(request.requirement_id, parsed_req, fields))

    _test_cases.extend(cases)
    return cases


def _generate_ep_cases(requirement_id: str, parsed_req: ParsedRequirement, fields: List[str]) -> List[TestCase]:
    cases: List[TestCase] = []
    for field in fields:
        rule = _rule_for(field, parsed_req)
        if rule["kind"] == "binary_fail_one":
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, 0.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, 1.0, "FAIL"))
            continue
        if rule["kind"] == "fail_above":
            threshold = rule["threshold"]
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, threshold - 1.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, threshold + 1.0, "FAIL"))
            continue
        if rule["kind"] == "fail_below":
            threshold = rule["threshold"]
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, threshold + 1.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, threshold - 1.0, "FAIL"))
            continue

        low, high = rule["min"], rule["max"]
        midpoint = _midpoint(low, high)
        if rule["kind"] == "valid_range":
            cases.extend(
                [
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, midpoint, "PASS"),
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, rule["low"], "FAIL"),
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, rule["high"], "FAIL"),
                ]
            )
        else:
            cases.extend(
                [
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, midpoint, "FAIL"),
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, rule["low"], "PASS"),
                    _make_case(requirement_id, TestTechnique.EQUIVALENCE_PARTITIONING, field, rule["high"], "PASS"),
                ]
            )
    return cases


def _generate_bva_cases(
    requirement_id: str,
    parsed_req: ParsedRequirement,
    fields: List[str],
    delta: float,
) -> List[TestCase]:
    cases: List[TestCase] = []
    for field in fields:
        rule = _rule_for(field, parsed_req)
        if rule["kind"] == "binary_fail_one":
            cases.append(_make_case(requirement_id, TestTechnique.BOUNDARY_VALUE_ANALYSIS, field, 0.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.BOUNDARY_VALUE_ANALYSIS, field, 1.0, "FAIL"))
            continue
        if rule["kind"] in {"fail_above", "fail_below"}:
            threshold = rule["threshold"]
            for value in [threshold - delta, threshold, threshold + delta]:
                cases.append(
                    _make_case(
                        requirement_id,
                        TestTechnique.BOUNDARY_VALUE_ANALYSIS,
                        field,
                        round(value, 2),
                        _expected_for(rule, value),
                    )
                )
            continue

        low, high = rule["min"], rule["max"]
        midpoint = _midpoint(low, high)
        values = [
            low - delta,
            low,
            low + delta,
            midpoint,
            high,
            high + delta,
            high + 2 * delta,
        ]
        for value in values:
            cases.append(
                _make_case(
                    requirement_id,
                    TestTechnique.BOUNDARY_VALUE_ANALYSIS,
                    field,
                    round(value, 2),
                    _expected_for(rule, value),
                )
            )
    return cases


def _generate_dt_cases(requirement_id: str, parsed_req: ParsedRequirement, fields: List[str]) -> List[TestCase]:
    cases: List[TestCase] = []
    active_fields = fields or ["CC2电压"]

    for field in active_fields:
        rule = _rule_for(field, parsed_req)
        if rule["kind"] == "binary_fail_one":
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, 0.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, 1.0, "FAIL"))
            continue
        if rule["kind"] == "fail_above":
            threshold = rule["threshold"]
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, threshold - 1.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, threshold + 1.0, "FAIL"))
            continue
        if rule["kind"] == "fail_below":
            threshold = rule["threshold"]
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, threshold + 1.0, "PASS"))
            cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, field, threshold - 1.0, "FAIL"))
            continue

        midpoint = _midpoint(rule["min"], rule["max"])
        cases.append(
            _make_case(
                requirement_id,
                TestTechnique.DECISION_TABLE,
                field,
                midpoint,
                _expected_for(rule, midpoint),
            )
        )
        cases.append(
            _make_case(
                requirement_id,
                TestTechnique.DECISION_TABLE,
                field,
                rule["high"],
                _expected_for(rule, rule["high"]),
            )
        )

    if "CC2电压" in active_fields:
        cases.append(_make_case(requirement_id, TestTechnique.DECISION_TABLE, "CC2电压", 12.0, "SLEEP"))

    return cases


def get_all_test_cases(requirement_id: Optional[str] = None) -> List[TestCase]:
    if requirement_id:
        return [tc for tc in _test_cases if tc.requirement_id == requirement_id]
    return _test_cases


def get_test_case(case_id: str) -> Optional[TestCase]:
    return next((tc for tc in _test_cases if tc.id == case_id), None)


def update_test_case(case_id: str, update: TestCaseUpdate) -> Optional[TestCase]:
    tc = get_test_case(case_id)
    if not tc:
        return None

    if update.signal_name is not None:
        tc.signal_name = update.signal_name
    if update.test_value is not None:
        tc.test_value = update.test_value
    if update.expected_result is not None:
        tc.expected_result = update.expected_result
    if update.expected_status is not None:
        tc.expected_status = update.expected_status
    if update.expected_vehicle_state is not None:
        tc.expected_vehicle_state = update.expected_vehicle_state
    return tc


def delete_test_case(case_id: str) -> bool:
    global _test_cases
    original_len = len(_test_cases)
    _test_cases = [tc for tc in _test_cases if tc.id != case_id]
    return len(_test_cases) < original_len


def _rule_for(field: str, parsed_req: ParsedRequirement) -> dict:
    if field in SIGNAL_RULES:
        return SIGNAL_RULES[field]

    parsed_range = parsed_req.data_ranges.get(field)
    if parsed_range:
        if parsed_range.get("type") == "range" and "min" in parsed_range and "max" in parsed_range:
            low, high = float(parsed_range["min"]), float(parsed_range["max"])
            return {"kind": "valid_range", "min": low, "max": high, "low": low - 1.0, "high": high + 1.0}
        if parsed_range.get("type") == "threshold" and "threshold" in parsed_range:
            threshold = float(parsed_range["threshold"])
            operator = parsed_range.get("operator")
            if operator == ">":
                return {"kind": "fail_above", "min": threshold - 1.0, "max": threshold, "low": threshold - 1.0, "high": threshold + 1.0, "threshold": threshold}
            if operator == "<":
                return {"kind": "fail_below", "min": threshold, "max": threshold + 1.0, "low": threshold - 1.0, "high": threshold + 1.0, "threshold": threshold}
        if parsed_range.get("type") == "equality" and "value" in parsed_range:
            value = float(parsed_range["value"])
            return {"kind": "valid_range", "min": value, "max": value, "low": value - 1.0, "high": value + 1.0}

        # Backward compatibility for manually edited legacy {min,max} JSON.
        low, high = parsed_range["min"], parsed_range["max"]
        return {"kind": "valid_range", "min": float(low), "max": float(high), "low": float(low) - 1.0, "high": float(high) + 1.0}

    return {"kind": "valid_range", "min": 0.0, "max": 1.0, "low": -1.0, "high": 2.0}


def _expected_for(rule: dict, value: float) -> str:
    if rule["kind"] == "valid_range":
        return "PASS" if rule["min"] <= value <= rule["max"] else "FAIL"
    if rule["kind"] == "fail_range":
        return "FAIL" if rule["min"] <= value <= rule["max"] else "PASS"
    if rule["kind"] == "binary_fail_one":
        return "FAIL" if value == 1 else "PASS"
    if rule["kind"] == "fail_above":
        return "FAIL" if value > rule["threshold"] else "PASS"
    if rule["kind"] == "fail_below":
        return "FAIL" if value < rule["threshold"] else "PASS"
    return "FAIL"


def _make_case(
    requirement_id: str,
    technique: TestTechnique,
    signal_name: str,
    test_value: float,
    expected_result: str,
) -> TestCase:
    expected_status = {"PASS": 1, "SLEEP": 3, "FAIL": 4}[expected_result]
    expected_vehicle_state = 170 if expected_result == "PASS" else 30
    return TestCase(
        id=str(uuid.uuid4()),
        requirement_id=requirement_id,
        technique=technique,
        signal_name=signal_name,
        test_value=round(test_value, 2),
        expected_result=expected_result,
        expected_status=expected_status,
        expected_vehicle_state=expected_vehicle_state,
        status=TestCaseStatus.PENDING,
        created_at=datetime.now(),
    )


def _midpoint(low: float, high: float) -> float:
    return round(((low + high) / 2) + 1e-9, 1)
