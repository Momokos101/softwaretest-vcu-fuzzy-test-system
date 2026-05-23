"""AutoTestDesign V2 test design routes."""
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from api.models.schemas import (
    BulkTestGenerationRequest,
    TestCase,
    TestCaseCreate,
    TestCaseUpdate,
    TestGenerationRequest,
)
from api.services import requirement_service, simulator_client, test_design_service

router = APIRouter()


@router.post("/test-cases/generate", response_model=List[TestCase])
async def generate_test_cases(request: TestGenerationRequest):
    parsed = requirement_service.get_parsed_requirement(request.requirement_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    try:
        return await test_design_service.generate_test_cases(request, parsed)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/test-cases/generate-all", response_model=List[TestCase])
async def generate_all_test_cases(request: BulkTestGenerationRequest):
    try:
        return await test_design_service.generate_all_test_cases(request)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/test-cases", response_model=TestCase)
async def create_test_case(request: TestCaseCreate):
    return test_design_service.create_test_case(request)


@router.get("/test-cases", response_model=List[TestCase])
async def get_test_cases(requirement_id: Optional[str] = None):
    return test_design_service.get_all_test_cases(requirement_id)


@router.get("/test-cases/{case_id}", response_model=TestCase)
async def get_test_case(case_id: str):
    case = test_design_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case


@router.put("/test-cases/{case_id}", response_model=TestCase)
async def update_test_case(case_id: str, update: TestCaseUpdate):
    case = test_design_service.update_test_case(case_id, update)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case


@router.delete("/test-cases/{case_id}")
async def delete_test_case(case_id: str):
    if not test_design_service.delete_test_case(case_id):
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"message": "Deleted successfully"}


@router.post("/test-cases/{case_id}/execute", response_model=TestCase)
async def execute_test_case(case_id: str):
    case = test_design_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return await simulator_client.execute_single(case)


@router.post("/test-cases/execute/batch", response_model=List[TestCase])
async def execute_batch_legacy(request: dict):
    ids = request.get("test_case_ids") or []
    cases = [test_design_service.get_test_case(case_id) for case_id in ids]
    cases = [case for case in cases if case is not None]
    if not cases:
        raise HTTPException(status_code=404, detail="No valid test cases found")
    return await simulator_client.execute_batch(cases, reset_before_run=request.get("reset_before_run", True))
