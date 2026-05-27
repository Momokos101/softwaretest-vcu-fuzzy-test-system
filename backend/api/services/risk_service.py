"""LLM-backed ISO 9126 + Tech×Business risk analysis."""
from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from api.models.schemas import ParsedRequirement, RiskAnalysisResult, RiskDimension
from api.services import _persist
from api.services.llm_client import llm_client
from api.services.prompt_service import require_prompt


_risk_results: dict[str, RiskAnalysisResult] = _persist.load_dict("risk_results", RiskAnalysisResult)


def _save() -> None:
    _persist.save_dict("risk_results", _risk_results)


async def analyze_risk(requirement_id: str, parsed_req: ParsedRequirement) -> RiskAnalysisResult:
    results = await analyze_risks([parsed_req])
    if not results:
        raise ValueError("LLM returned no risk result")
    result = results[0]
    result.requirement_id = requirement_id
    _risk_results[requirement_id] = result
    _save()
    return result


async def analyze_risks(parsed_requirements: List[ParsedRequirement]) -> List[RiskAnalysisResult]:
    prompt = require_prompt("risk")
    requirements_json = json.dumps([item.model_dump(mode="json") for item in parsed_requirements], ensure_ascii=False, indent=2)
    payload, model, elapsed_ms = await llm_client.generate_json(
        operation="risk.analyze",
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt.format(requirements_json=requirements_json),
        expected_type="object",
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("LLM risk response must include items array")

    results = [_to_risk_result(item, model, elapsed_ms) for item in items]
    for result in results:
        _risk_results[result.requirement_id] = result
    _save()
    return results


def get_risk_analysis(requirement_id: str) -> Optional[RiskAnalysisResult]:
    return _risk_results.get(requirement_id)


def adjust_risk(
    requirement_id: str,
    dimensions: RiskDimension | None = None,
    *,
    iso9126_characteristic: str | None = None,
    tech_risk: int | None = None,
    business_risk: int | None = None,
    reasoning: str | None = None,
) -> RiskAnalysisResult:
    existing = _risk_results.get(requirement_id)
    if dimensions:
        tech_risk = dimensions.tech_risk
        business_risk = dimensions.business_risk
    tech = tech_risk or (existing.tech_risk if existing else 3)
    business = business_risk or (existing.business_risk if existing else 3)
    rpn = tech * business
    result = RiskAnalysisResult(
        requirement_id=requirement_id,
        iso9126_characteristic=(iso9126_characteristic or (existing.iso9126_characteristic if existing else "Functionality")),  # type: ignore[arg-type]
        tech_risk=tech,
        business_risk=business,
        rpn=rpn,
        extent=_extent_for_rpn(rpn),
        reasoning=reasoning or (existing.reasoning if existing else "Manual risk override"),
        llm_model=existing.llm_model if existing else None,
        elapsed_ms=existing.elapsed_ms if existing else None,
        created_at=datetime.now(),
    )
    _risk_results[requirement_id] = result
    _save()
    return result


def get_all_risk_results() -> List[RiskAnalysisResult]:
    return list(_risk_results.values())


def _to_risk_result(item: dict, model: str, elapsed_ms: float) -> RiskAnalysisResult:
    tech = int(item.get("tech_risk", 3))
    business = int(item.get("business_risk", 3))
    rpn = int(item.get("rpn", tech * business))
    return RiskAnalysisResult(
        requirement_id=str(item.get("requirement_id") or item.get("id")),
        iso9126_characteristic=item.get("iso9126_characteristic", "Functionality"),
        tech_risk=tech,
        business_risk=business,
        rpn=rpn,
        extent=item.get("extent") or _extent_for_rpn(rpn),
        reasoning=item.get("reasoning", ""),
        llm_model=model,
        elapsed_ms=elapsed_ms,
        created_at=datetime.now(),
    )


def _extent_for_rpn(rpn: int) -> str:
    if rpn <= 5:
        return "Extensive"
    if rpn <= 10:
        return "Broad"
    if rpn <= 15:
        return "Cursory"
    return "Low priority"
