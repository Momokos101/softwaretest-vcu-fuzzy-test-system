"""Coverage item and strategy management for AutoTestDesign V2."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import List, Optional

from api.models.schemas import (
    CoverageItem,
    CoverageItemCreate,
    CoverageItemUpdate,
    ParsedRequirement,
    StrategyUpdate,
    TestStrategy,
)
from api.services.llm_client import llm_client
from api.services.prompt_service import require_prompt


_coverage_items: dict[str, CoverageItem] = {}
_strategies: dict[str, TestStrategy] = {}


async def generate_coverage_items(
    parsed_requirements: List[ParsedRequirement],
    mode: str = "dedupe",
) -> List[CoverageItem]:
    """Generate coverage items from LLM.

    mode:
      - "dedupe" (default, safe): skip LLM items whose (requirement_id, title)
        already exists; idempotent under repeated clicks.
      - "replace": delete all existing items for the affected requirement_ids
        BEFORE generating; useful when user wants a fresh LLM regenerate.
      - "append": legacy behavior — always append; allows duplicates.
    """
    if mode not in ("dedupe", "replace", "append"):
        raise ValueError(f"invalid mode {mode!r}; expected dedupe|replace|append")

    affected_req_ids = {p.requirement_id for p in parsed_requirements}

    if mode == "replace":
        # Drop existing items for affected REQs before generating
        to_remove = [k for k, v in _coverage_items.items() if v.requirement_id in affected_req_ids]
        for k in to_remove:
            del _coverage_items[k]

    prompt = require_prompt("coverage")
    requirements_json = json.dumps([item.model_dump(mode="json") for item in parsed_requirements], ensure_ascii=False, indent=2)
    payload, _, _ = await llm_client.generate_json(
        operation="coverage.generate",
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt.format(requirements_json=requirements_json),
        expected_type="object",
    )
    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("LLM coverage response must include items array")

    if mode == "dedupe":
        existing_keys = {(v.requirement_id, v.title) for v in _coverage_items.values()}
        raw_items = [
            r for r in raw_items
            if (str(r.get("requirement_id")), r.get("title") or "Coverage Item") not in existing_keys
        ]

    items = [
        create_coverage_item(
            CoverageItemCreate(
                requirement_id=str(item.get("requirement_id")),
                title=item.get("title") or "Coverage Item",
                description=item.get("description") or "",
                technique=item.get("technique") or "EP",
                iso9126_characteristic=item.get("iso9126_characteristic"),
                priority=item.get("priority") or "Medium",
            )
        )
        for item in raw_items
    ]
    return items


def list_coverage_items(requirement_id: str | None = None) -> List[CoverageItem]:
    items = list(_coverage_items.values())
    if requirement_id:
        items = [item for item in items if item.requirement_id == requirement_id]
    return items


def get_coverage_item(item_id: str) -> Optional[CoverageItem]:
    return _coverage_items.get(item_id)


def create_coverage_item(create: CoverageItemCreate) -> CoverageItem:
    now = datetime.now()
    item = CoverageItem(
        id=str(uuid.uuid4()),
        requirement_id=create.requirement_id,
        title=create.title,
        description=create.description,
        technique=create.technique,
        iso9126_characteristic=create.iso9126_characteristic,
        priority=create.priority,
        created_at=now,
        updated_at=now,
    )
    _coverage_items[item.id] = item
    ensure_strategy(item.requirement_id)
    return item


def update_coverage_item(item_id: str, update: CoverageItemUpdate) -> Optional[CoverageItem]:
    item = get_coverage_item(item_id)
    if not item:
        return None
    for field in ("title", "description", "technique", "iso9126_characteristic", "priority"):
        value = getattr(update, field)
        if value is not None:
            setattr(item, field, value)
    item.updated_at = datetime.now()
    return item


def delete_coverage_item(item_id: str) -> bool:
    return _coverage_items.pop(item_id, None) is not None


def ensure_strategy(requirement_id: str) -> TestStrategy:
    strategy = _strategies.get(requirement_id)
    if strategy:
        return strategy
    techniques = sorted({item.technique for item in list_coverage_items(requirement_id)}) or ["EP", "BVA"]
    strategy = TestStrategy(
        requirement_id=requirement_id,
        techniques=techniques,
        rationale="Default strategy generated from coverage items.",
        updated_at=datetime.now(),
    )
    _strategies[requirement_id] = strategy
    return strategy


def get_strategy(requirement_id: str) -> TestStrategy:
    return ensure_strategy(requirement_id)


def update_strategy(requirement_id: str, update: StrategyUpdate) -> TestStrategy:
    strategy = TestStrategy(
        requirement_id=requirement_id,
        techniques=update.techniques,
        rationale=update.rationale or "",
        updated_at=datetime.now(),
    )
    _strategies[requirement_id] = strategy
    return strategy


def list_strategies() -> List[TestStrategy]:
    return list(_strategies.values())
