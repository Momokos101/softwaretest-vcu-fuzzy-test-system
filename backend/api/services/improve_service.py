"""Second-round fuzzy testing improvement suggestions."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import List

from api.models.schemas import CoverageItemCreate, ImproveRequest, ImproveSuggestion, TestCase
from api.services import coverage_service, test_design_service
from api.services.llm_client import llm_client
from api.services.prompt_service import require_prompt


_suggestions: list[ImproveSuggestion] = []


async def generate_improvements(request: ImproveRequest) -> List[ImproveSuggestion]:
    cases = test_design_service.get_all_test_cases()
    if request.requirement_ids:
        cases = [case for case in cases if case.requirement_id in request.requirement_ids]
    if request.failed_only:
        cases = [case for case in cases if case.status.value in {"fail", "error"}]

    context = {
        "failed_only": request.failed_only,
        "max_suggestions": request.max_suggestions,
        "test_cases": [case.model_dump(mode="json") for case in cases],
    }
    prompt = require_prompt("improve")
    payload, _, _ = await llm_client.generate_json(
        operation="improve.generate",
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt.format(execution_context_json=json.dumps(context, ensure_ascii=False, indent=2)),
        expected_type="object",
    )
    raw = payload.get("suggestions")
    if not isinstance(raw, list):
        raise ValueError("LLM improve response must include suggestions array")

    suggestions: list[ImproveSuggestion] = []
    for item in raw[: request.max_suggestions]:
        coverage_raw = item.get("coverage_item") or {}
        coverage = coverage_service.create_coverage_item(
            CoverageItemCreate(
                requirement_id=str(coverage_raw.get("requirement_id") or item.get("requirement_id")),
                title=coverage_raw.get("title") or item.get("title") or "Improvement coverage",
                description=coverage_raw.get("description") or item.get("reason") or "",
                technique=coverage_raw.get("technique") or "BVA",
                iso9126_characteristic=coverage_raw.get("iso9126_characteristic"),
                priority=coverage_raw.get("priority") or "High",
            )
        )
        test_case = _build_optional_test_case(item.get("test_case"), coverage.id)
        suggestion = ImproveSuggestion(
            id=str(uuid.uuid4()),
            requirement_id=coverage.requirement_id,
            title=item.get("title") or coverage.title,
            reason=item.get("reason") or "",
            coverage_item=coverage,
            test_case=test_case,
            created_at=datetime.now(),
        )
        _suggestions.append(suggestion)
        suggestions.append(suggestion)
    return suggestions


def list_suggestions() -> List[ImproveSuggestion]:
    return list(_suggestions)


def _build_optional_test_case(raw: object, coverage_item_id: str) -> TestCase | None:
    if not isinstance(raw, dict):
        return None
    create = {
        "requirement_id": str(raw.get("requirement_id")),
        "coverage_item_id": coverage_item_id,
        "title": raw.get("title") or "Improvement test case",
        "technique": raw.get("technique") or "BVA",
        "type": raw.get("type", 1),
        "in_data": raw.get("in_data") or [],
        "expected_results": raw.get("expected_results") or [],
        "error": raw.get("error") or [],
        "est_time": raw.get("est_time", 20.0),
        "oracle_reasoning": raw.get("oracle_reasoning") or "",
    }
    from api.models.schemas import TestCaseCreate

    return test_design_service.create_test_case(TestCaseCreate(**create))
