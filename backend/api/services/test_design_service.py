"""LLM-backed V2 test case design and CRUD."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import List, Optional

from api.models.schemas import (
    BulkTestGenerationRequest,
    ExpectedOutput,
    ParsedRequirement,
    TestCase,
    TestCaseCreate,
    TestCaseStatus,
    TestCaseUpdate,
    TestGenerationRequest,
    TestInput,
    TestTechnique,
)
from api.services import _persist, coverage_service, requirement_service
from api.services.llm_client import llm_client
from api.services.prompt_service import require_prompt


_test_cases: List[TestCase] = _persist.load_list("test_cases", TestCase)


def _save() -> None:
    _persist.save_list("test_cases", _test_cases)


async def generate_test_cases(request: TestGenerationRequest, parsed_req: ParsedRequirement) -> List[TestCase]:
    coverage_items = [
        item for item in coverage_service.list_coverage_items(parsed_req.requirement_id)
        if not request.coverage_item_ids or item.id in request.coverage_item_ids
    ]
    strategy = coverage_service.get_strategy(parsed_req.requirement_id)
    techniques = [_normalize_technique(item) for item in (request.techniques or strategy.techniques)]

    context = {
        "requirement": parsed_req.model_dump(mode="json"),
        "coverage_items": [item.model_dump(mode="json") for item in coverage_items],
        "strategy": {**strategy.model_dump(mode="json"), "techniques": techniques},
        "bva_delta": request.bva_delta,
    }
    cases = await _generate_from_context(context)
    if request.regenerate:
        delete_by_requirement(parsed_req.requirement_id)
    _test_cases.extend(cases)
    _save()
    return cases


async def generate_all_test_cases(request: BulkTestGenerationRequest) -> List[TestCase]:
    requirement_ids = request.requirement_ids or [req.id for req in requirement_service.get_all_requirements() if req.parsed]
    generated: list[TestCase] = []
    for req_id in requirement_ids:
        parsed = requirement_service.get_parsed_requirement(req_id)
        if not parsed:
            continue
        techniques = request.techniques or coverage_service.get_strategy(req_id).techniques
        generated.extend(
            await generate_test_cases(
                TestGenerationRequest(
                    requirement_id=req_id,
                    techniques=techniques,
                    bva_delta=request.bva_delta,
                    regenerate=request.regenerate,
                ),
                parsed,
            )
        )
    return generated


def create_test_case(create: TestCaseCreate) -> TestCase:
    now = datetime.now()
    case = TestCase(id=str(uuid.uuid4()), created_at=now, updated_at=now, **create.model_dump())
    _test_cases.append(case)
    _save()
    return case


def get_all_test_cases(requirement_id: Optional[str] = None) -> List[TestCase]:
    if requirement_id:
        return [case for case in _test_cases if case.requirement_id == requirement_id]
    return list(_test_cases)


def get_test_case(case_id: str) -> Optional[TestCase]:
    return next((case for case in _test_cases if case.id == case_id), None)


def update_test_case(case_id: str, update: TestCaseUpdate) -> Optional[TestCase]:
    case = get_test_case(case_id)
    if not case:
        return None

    for field in ("title", "technique", "type", "in_data", "expected_results", "error", "est_time", "oracle_reasoning"):
        value = getattr(update, field)
        if value is not None:
            setattr(case, field, value)

    # Compatibility with the old table editor.
    if update.signal_name is not None:
        if case.in_data:
            case.in_data[0].name = update.signal_name
        else:
            case.in_data.append(TestInput(name=update.signal_name, value=update.test_value or 0.0))
    if update.test_value is not None:
        if case.in_data:
            case.in_data[0].value = update.test_value
        else:
            case.in_data.append(TestInput(name=update.signal_name or "signal", value=update.test_value))
    if update.expected_result is not None:
        _set_legacy_expected(case, update.expected_result)
    if update.expected_vehicle_state is not None:
        _upsert_expected(case, "vehicle_state", "eq", update.expected_vehicle_state)

    case.updated_at = datetime.now()
    _save()
    return case


def delete_test_case(case_id: str) -> bool:
    original_len = len(_test_cases)
    _test_cases[:] = [case for case in _test_cases if case.id != case_id]
    removed = len(_test_cases) < original_len
    if removed:
        _save()
    return removed


def delete_by_requirement(requirement_id: str) -> None:
    _test_cases[:] = [case for case in _test_cases if case.requirement_id != requirement_id]
    _save()


def mark_execution(case_id: str, execution_result: dict, passed: bool) -> Optional[TestCase]:
    case = get_test_case(case_id)
    if not case:
        return None
    case.execution_result = execution_result
    case.status = TestCaseStatus.PASS if passed else TestCaseStatus.FAIL
    case.updated_at = datetime.now()
    _save()
    return case


async def _generate_from_context(context: dict) -> List[TestCase]:
    prompt = require_prompt("testcase")
    payload, _, _ = await llm_client.generate_json(
        operation="testcase.generate",
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt.format(design_context_json=json.dumps(context, ensure_ascii=False, indent=2)),
        expected_type="object",
    )
    raw_cases = payload.get("test_cases")
    if not isinstance(raw_cases, list):
        raise ValueError("LLM test case response must include test_cases array")

    now = datetime.now()
    cases: list[TestCase] = []
    for item in raw_cases:
        cases.append(
            TestCase(
                id=str(uuid.uuid4()),
                requirement_id=str(item.get("requirement_id") or context["requirement"]["requirement_id"]),
                coverage_item_id=item.get("coverage_item_id"),
                title=item.get("title") or "Generated test case",
                technique=_technique_enum(item.get("technique")),
                type=_case_type(item.get("type")),
                in_data=_normalize_in_data(item.get("in_data") or []),
                expected_results=_normalize_expected_results(item.get("expected_results") or []),
                error=_normalize_error(item.get("error")),
                est_time=float(item.get("est_time", 20.0)),
                oracle_reasoning=item.get("oracle_reasoning") or "",
                created_at=now,
                updated_at=now,
            )
        )
    return cases


def _normalize_error(value: object) -> list[dict[str, object]]:
    """Coerce the LLM 'error' field into a valid BqErrorOracle list.

    The LLM occasionally returns a bare description string (e.g. the REQ-014
    timeout case returns 'Timeout expected') instead of the expected list of
    error-oracle objects. Such non-list payloads would fail TestCase validation;
    we drop them here (the timing oracle is carried by expected_results anyway).
    """
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _normalize_technique(value: str) -> str:
    return str(value).upper().replace("EQUIVALENCE_PARTITIONING", "EP").replace("BOUNDARY_VALUE_ANALYSIS", "BVA")


def _technique_enum(value: object) -> TestTechnique:
    normalized = _normalize_technique(str(value or "EP"))
    mapping = {
        "EP": TestTechnique.EQUIVALENCE_PARTITIONING,
        "BVA": TestTechnique.BOUNDARY_VALUE_ANALYSIS,
        "DT": TestTechnique.DECISION_TABLE,
        "ST": TestTechnique.STATE_TRANSITION,
        "SC": TestTechnique.SCENARIO,
        "SCENARIO": TestTechnique.SCENARIO,
    }
    return mapping.get(normalized, TestTechnique.EQUIVALENCE_PARTITIONING)


def _case_type(value: object) -> int:
    if value is None:
        return 1
    if isinstance(value, int):
        return value
    text = str(value).strip().lower()
    if text in {"2", "type2", "sleep", "negative_sleep", "scenario_sleep"}:
        return 2
    return 1


def _normalize_in_data(raw_items: list[object]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for raw in raw_items:
        if isinstance(raw, dict):
            item = dict(raw)
            item["name"] = item.get("name") or item.get("signal_name") or item.get("field") or "input"
            item["data_type"] = item.get("data_type") or "float"
            item["value"] = item.get("value", item.get("test_value"))
            items.append(item)
    return items


def _normalize_expected_results(raw_items: list[object]) -> list[dict[str, object]]:
    allowed_ops = {"eq", "ne", "gte", "lte", "gt", "lt", "contains"}
    aliases = {"=": "eq", "==": "eq", "!=": "ne", "<>": "ne", "≠": "ne", "neq": "ne", ">=": "gte", "<=": "lte", ">": "gt", "<": "lt"}
    items: list[dict[str, object]] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        item["name"] = item.get("name") or item.get("output_field") or item.get("field") or "result_type"
        operator = str(item.get("operator") or "eq").strip().lower()
        item["operator"] = aliases.get(operator, operator if operator in allowed_ops else "eq")
        item["value"] = item.get("value", item.get("expected_value"))
        item["out_type"] = _safe_int(item.get("out_type"), default=1)
        item["out_range"] = _safe_int(item.get("out_range"), default=_out_range_for_operator(str(item["operator"])))
        items.append(item)
    return items


def _out_range_for_operator(operator: str) -> int:
    if operator in {"gte", "gt"}:
        return 1
    if operator in {"lte", "lt"}:
        return 3
    return 2


def _safe_int(value: object, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _set_legacy_expected(case: TestCase, expected: str) -> None:
    if expected == "PASS":
        _upsert_expected(case, "result_type", "eq", "expected")
        _upsert_expected(case, "vehicle_state", "eq", 11)
    elif expected == "SLEEP":
        _upsert_expected(case, "result_type", "eq", "sleep")
        _upsert_expected(case, "vehicle_state", "eq", 9)
    else:
        _upsert_expected(case, "result_type", "eq", "error")


def _upsert_expected(case: TestCase, name: str, operator: str, value: object) -> None:
    for item in case.expected_results:
        if item.name == name:
            item.operator = operator  # type: ignore[assignment]
            item.value = value
            return
    case.expected_results.append(ExpectedOutput(name=name, operator=operator, value=value))  # type: ignore[arg-type]
