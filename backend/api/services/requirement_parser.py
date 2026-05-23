"""LLM-backed requirement parsing for AutoTestDesign V2."""
from __future__ import annotations

from datetime import datetime
from typing import Any, List

from api.models.schemas import ParsedRequirement
from api.services.llm_client import llm_client
from api.services.prompt_service import require_prompt


async def parse_requirements_from_text(raw_text: str) -> List[ParsedRequirement]:
    prompt = require_prompt("parse")
    payload, model, elapsed_ms = await llm_client.generate_json(
        operation="requirements.parse",
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt.format(raw_text=raw_text),
        expected_type="object",
    )
    items = payload.get("requirements")
    if not isinstance(items, list):
        raise ValueError("LLM parse response must include requirements array")
    return [_to_parsed_requirement(item, model, elapsed_ms) for item in items]


async def parse_requirement(requirement_id: str, raw_text: str) -> ParsedRequirement:
    parsed = await parse_requirements_from_text(f"{requirement_id}: {raw_text}")
    if not parsed:
        raise ValueError("LLM returned no parsed requirements")
    item = parsed[0]
    item.requirement_id = requirement_id
    return item


def _to_parsed_requirement(item: dict[str, Any], model: str, elapsed_ms: float) -> ParsedRequirement:
    requirement_id = str(item.get("requirement_id") or item.get("id") or "").strip()
    if not requirement_id:
        requirement_id = "REQ-UNASSIGNED"
    return ParsedRequirement(
        requirement_id=requirement_id,
        title=item.get("title"),
        module=item.get("module"),
        description=item.get("description") or "",
        input_fields=_normalize_input_fields(item.get("input_fields") or []),
        conditions=_normalize_conditions(item.get("conditions") or []),
        expected_actions=_normalize_expected_actions(item.get("expected_actions") or []),
        parse_confidence=float(item.get("parse_confidence", 1.0)),
        llm_model=model,
        elapsed_ms=elapsed_ms,
        updated_at=datetime.now(),
    )


def _normalize_input_fields(raw_fields: list[Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for raw in raw_fields:
        if isinstance(raw, str):
            fields.append({"name": raw, "data_type": "float", "valid_range": None, "unit": None, "has_timing": False})
            continue
        if not isinstance(raw, dict):
            continue
        field = dict(raw)
        valid_range = field.get("valid_range")
        if isinstance(valid_range, str):
            field["valid_range"] = {"expression": valid_range}
        elif valid_range is not None and not isinstance(valid_range, dict):
            field["valid_range"] = {"value": valid_range}
        field.setdefault("data_type", "float")
        field.setdefault("has_timing", False)
        fields.append(field)
    return fields


def _normalize_conditions(raw_conditions: list[Any]) -> list[dict[str, Any]]:
    allowed = {"timing", "logical", "combined", "threshold", "state", "scenario"}
    aliases = {
        "duration": "timing",
        "time": "timing",
        "temporal": "timing",
        "range": "threshold",
        "value": "threshold",
        "transition": "state",
    }
    conditions: list[dict[str, Any]] = []
    for raw in raw_conditions:
        if isinstance(raw, str):
            conditions.append({"type": "logical", "description": raw, "threshold": None})
            continue
        if not isinstance(raw, dict):
            continue
        condition = dict(raw)
        condition_type = str(condition.get("type") or "logical").strip().lower()
        condition["type"] = aliases.get(condition_type, condition_type if condition_type in allowed else "logical")
        condition["description"] = condition.get("description") or condition.get("condition") or ""
        conditions.append(condition)
    return conditions


def _normalize_expected_actions(raw_actions: list[Any]) -> list[dict[str, Any]]:
    allowed_ops = {"eq", "gte", "lte", "gt", "lt", "contains"}
    aliases = {"=": "eq", "==": "eq", ">=": "gte", "<=": "lte", ">": "gt", "<": "lt"}
    actions: list[dict[str, Any]] = []
    for raw in raw_actions:
        if isinstance(raw, str):
            actions.append({"output_field": "detail", "expected_value": raw, "operator": "contains"})
            continue
        if not isinstance(raw, dict):
            continue
        action = dict(raw)
        action["output_field"] = action.get("output_field") or action.get("name") or action.get("field") or "detail"
        action["expected_value"] = action.get("expected_value", action.get("value"))
        operator = str(action.get("operator") or "eq").strip().lower()
        action["operator"] = aliases.get(operator, operator if operator in allowed_ops else "eq")
        actions.append(action)
    return actions
