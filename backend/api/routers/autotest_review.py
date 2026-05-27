"""Interactive Review routes for AutoTestDesign V2."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Query

from api.models.schemas import (
    BatchExecutionRequest,
    CoverageItem,
    CoverageItemCreate,
    CoverageItemUpdate,
    ImproveRequest,
    ImproveSuggestion,
    PerformanceMetric,
    PromptTemplate,
    PromptUpdate,
    ResultsSummary,
    StrategyUpdate,
    TestCase,
    TestStrategy,
)
from api.services import (
    coverage_service,
    improve_service,
    performance_service,
    prompt_service,
    simulator_client,
    test_design_service,
)

router = APIRouter()


@router.post("/coverage-items/generate", response_model=List[CoverageItem])
async def generate_coverage_items(
    requirement_ids: Optional[List[str]] = Body(default=None),
    mode: str = Query(default="dedupe", pattern="^(dedupe|replace|append)$"),
):
    """Generate coverage items via LLM.

    Query param `mode` (default `dedupe`):
      - dedupe : skip LLM items whose (requirement_id, title) already exist (idempotent)
      - replace: delete existing items for affected REQs first, then generate fresh
      - append : legacy append-only behavior (allows duplicates)
    """
    from api.services import requirement_service

    parsed = requirement_service.get_all_parsed_requirements()
    if requirement_ids:
        parsed = [item for item in parsed if item.requirement_id in requirement_ids]
    if not parsed:
        raise HTTPException(status_code=404, detail="No parsed requirements found")
    try:
        return await coverage_service.generate_coverage_items(parsed, mode=mode)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/coverage-items", response_model=List[CoverageItem])
async def list_coverage_items(requirement_id: Optional[str] = None):
    return coverage_service.list_coverage_items(requirement_id)


@router.post("/coverage-items", response_model=CoverageItem)
async def create_coverage_item(request: CoverageItemCreate):
    return coverage_service.create_coverage_item(request)


@router.put("/coverage-items/{item_id}", response_model=CoverageItem)
async def update_coverage_item(item_id: str, request: CoverageItemUpdate):
    item = coverage_service.update_coverage_item(item_id, request)
    if not item:
        raise HTTPException(status_code=404, detail="Coverage item not found")
    return item


@router.delete("/coverage-items/{item_id}")
async def delete_coverage_item(item_id: str):
    if not coverage_service.delete_coverage_item(item_id):
        raise HTTPException(status_code=404, detail="Coverage item not found")
    return {"message": "Deleted successfully"}


@router.get("/strategies/{req_id}", response_model=TestStrategy)
async def get_strategy(req_id: str):
    return coverage_service.get_strategy(req_id)


@router.put("/strategies/{req_id}", response_model=TestStrategy)
async def update_strategy(req_id: str, request: StrategyUpdate):
    return coverage_service.update_strategy(req_id, request)


@router.post("/strategies/{req_id}/regenerate", response_model=List[TestCase])
async def regenerate_strategy(req_id: str):
    from api.models.schemas import TestGenerationRequest
    from api.services import requirement_service

    parsed = requirement_service.get_parsed_requirement(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    strategy = coverage_service.get_strategy(req_id)
    return await test_design_service.generate_test_cases(
        TestGenerationRequest(requirement_id=req_id, techniques=strategy.techniques, regenerate=True),
        parsed,
    )


@router.get("/prompts", response_model=List[PromptTemplate])
async def list_prompts():
    return prompt_service.list_prompts()


@router.get("/prompts/{prompt_type}", response_model=PromptTemplate)
async def get_prompt(prompt_type: str):
    prompt = prompt_service.get_prompt(prompt_type)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.put("/prompts/{prompt_type}", response_model=PromptTemplate)
async def update_prompt(prompt_type: str, request: PromptUpdate):
    prompt = prompt_service.update_prompt(prompt_type, request)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("/execute", response_model=List[TestCase])
async def execute(request: BatchExecutionRequest):
    """Execute the design test cases by running the real pytest suite
    (tests/test_suite_from_design.py) and feeding results back per case.

    The frontend "执行全部" calls this. We run pytest (which executes the 96
    reviewed design cases against the VCU via the input adapter), parse the
    JUnit XML, and mark each tool test case pass/fail by its uuid. This makes
    the Results tab reflect the genuine pytest execution.
    """
    import asyncio

    from api.services import pytest_runner

    if not test_design_service.get_all_test_cases():
        raise HTTPException(status_code=404, detail="No test cases found")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, pytest_runner.run_and_mark)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"pytest execution failed: {exc}") from exc
    return test_design_service.get_all_test_cases()


@router.get("/results/summary", response_model=ResultsSummary)
async def results_summary():
    from api.services import requirement_service

    cases = test_design_service.get_all_test_cases()
    total = len(cases)
    passed = sum(1 for item in cases if item.status.value == "pass")
    failed = sum(1 for item in cases if item.status.value == "fail")
    errors = sum(1 for item in cases if item.status.value == "error")
    covered_requirements = {item.requirement_id for item in cases}
    all_requirements = {item.id for item in requirement_service.get_all_requirements()}

    dtc_counts: dict[str, int] = {}
    failure_reasons: dict[str, int] = {}
    for case in cases:
        result = case.execution_result or {}
        actual = result.get("actual_output") or {}
        for dtc in actual.get("active_dtcs", []) or []:
            code = dtc.get("code") if isinstance(dtc, dict) else str(dtc)
            dtc_counts[code] = dtc_counts.get(code, 0) + 1
        for mismatch in result.get("mismatches", []) or []:
            failure_reasons[mismatch] = failure_reasons.get(mismatch, 0) + 1

    return ResultsSummary(
        total=total,
        passed=passed,
        failed=failed,
        errors=errors,
        pass_rate=round(passed / total, 4) if total else 0.0,
        coverage_rate=round(len(covered_requirements) / len(all_requirements), 4) if all_requirements else 0.0,
        dtc_counts=dtc_counts,
        failure_reasons=failure_reasons,
        performance=performance_service.summary(),
    )


@router.post("/improve", response_model=List[ImproveSuggestion])
async def improve(request: ImproveRequest):
    try:
        return await improve_service.generate_improvements(request)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/performance", response_model=List[PerformanceMetric])
async def performance(operation: Optional[str] = None):
    return performance_service.list_metrics(operation)
