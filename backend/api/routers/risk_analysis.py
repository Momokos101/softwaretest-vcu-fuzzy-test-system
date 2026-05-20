"""
风险分析路由
"""
from fastapi import APIRouter, HTTPException
from typing import List

from api.models.schemas import RiskAnalysisResult, RiskAdjustmentRequest
from api.services import risk_service, requirement_service

router = APIRouter()


@router.post("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def analyze_risk(req_id: str):
    """分析单个需求风险"""
    parsed = requirement_service.get_parsed_requirement(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")

    return risk_service.analyze_risk(req_id, parsed)


@router.get("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def get_risk_analysis(req_id: str):
    """获取风险分析结果"""
    result = risk_service.get_risk_analysis(req_id)
    if not result:
        raise HTTPException(status_code=404, detail="Risk analysis not found")
    return result


@router.put("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def adjust_risk(req_id: str, request: RiskAdjustmentRequest):
    """调整风险评分"""
    if not requirement_service.get_requirement(req_id):
        raise HTTPException(status_code=404, detail="Requirement not found")
    return risk_service.adjust_risk(req_id, request.dimensions)


@router.get("/risk-analysis/matrix/data", response_model=List[RiskAnalysisResult])
async def get_risk_matrix():
    """获取风险矩阵数据"""
    return risk_service.get_all_risk_results()
