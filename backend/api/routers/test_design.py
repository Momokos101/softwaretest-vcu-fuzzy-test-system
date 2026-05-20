"""
测试设计路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from api.models.schemas import (
    TestCase, TestCaseUpdate, TestGenerationRequest, BatchExecutionRequest
)
from api.services import test_design_service, requirement_service, simulator_client

router = APIRouter()


@router.post("/test-cases/generate", response_model=List[TestCase])
async def generate_test_cases(request: TestGenerationRequest):
    """生成测试用例"""
    parsed = requirement_service.get_parsed_requirement(request.requirement_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")

    return test_design_service.generate_test_cases(request, parsed)


@router.get("/test-cases", response_model=List[TestCase])
async def get_test_cases(requirement_id: Optional[str] = None):
    """获取测试用例列表"""
    return test_design_service.get_all_test_cases(requirement_id)


@router.get("/test-cases/{case_id}", response_model=TestCase)
async def get_test_case(case_id: str):
    """获取单个测试用例"""
    case = test_design_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case


@router.put("/test-cases/{case_id}", response_model=TestCase)
async def update_test_case(case_id: str, update: TestCaseUpdate):
    """更新测试用例"""
    case = test_design_service.update_test_case(case_id, update)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return case


@router.delete("/test-cases/{case_id}")
async def delete_test_case(case_id: str):
    """删除测试用例"""
    success = test_design_service.delete_test_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"message": "Deleted successfully"}


@router.post("/test-cases/{case_id}/execute", response_model=TestCase)
async def execute_test_case(case_id: str):
    """执行单个测试用例"""
    case = test_design_service.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Test case not found")

    return await simulator_client.execute_single(case)


@router.post("/test-cases/execute/batch", response_model=List[TestCase])
async def execute_batch(request: BatchExecutionRequest):
    """批量执行测试用例"""
    cases = [test_design_service.get_test_case(cid) for cid in request.test_case_ids]
    cases = [c for c in cases if c is not None]

    if not cases:
        raise HTTPException(status_code=404, detail="No valid test cases found")

    return await simulator_client.execute_batch(cases)
