"""
需求管理路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from api.models.schemas import (
    Requirement, RequirementCreate, RequirementUpdate, ParsedRequirement
)
from api.services import requirement_service

router = APIRouter()


@router.post("/requirements/import/csv", response_model=List[Requirement])
async def import_csv(file: UploadFile = File(...)):
    """从CSV导入需求"""
    return requirement_service.import_from_csv(file)


@router.post("/requirements/import/text", response_model=List[Requirement])
async def import_text(request: dict):
    """从文本导入需求"""
    raw_text = request.get('raw_text', '')
    return requirement_service.import_from_text(raw_text)


@router.post("/requirements/import/form", response_model=Requirement)
async def import_form(req: RequirementCreate):
    """表单创建需求"""
    return requirement_service.create_requirement(req)


@router.get("/requirements", response_model=List[Requirement])
async def get_requirements():
    """获取所有需求"""
    return requirement_service.get_all_requirements()


@router.get("/requirements/{req_id}", response_model=Requirement)
async def get_requirement(req_id: str):
    """获取单个需求"""
    req = requirement_service.get_requirement(req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.put("/requirements/{req_id}", response_model=Requirement)
async def update_requirement(req_id: str, req_update: RequirementUpdate):
    """更新需求"""
    req = requirement_service.update_requirement(req_id, req_update)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.delete("/requirements/{req_id}")
async def delete_requirement(req_id: str):
    """删除需求"""
    success = requirement_service.delete_requirement(req_id)
    if not success:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return {"message": "Deleted successfully"}


@router.post("/requirements/{req_id}/parse", response_model=ParsedRequirement)
async def parse_requirement(req_id: str):
    """解析需求"""
    parsed = requirement_service.parse_requirement_by_id(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return parsed


@router.post("/requirements/parse-all", response_model=List[ParsedRequirement])
async def parse_all_requirements(only_unparsed: bool = True):
    """批量解析需求"""
    return requirement_service.parse_all_requirements(only_unparsed=only_unparsed)


@router.get("/requirements/{req_id}/parsed", response_model=ParsedRequirement)
async def get_parsed(req_id: str):
    """获取解析结果"""
    parsed = requirement_service.get_parsed_requirement(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    return parsed


@router.put("/requirements/{req_id}/parsed", response_model=ParsedRequirement)
async def update_parsed(req_id: str, parsed: ParsedRequirement):
    """更新解析结果"""
    result = requirement_service.update_parsed_requirement(req_id, parsed)
    if not result:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    return result
