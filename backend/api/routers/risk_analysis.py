"""AutoTestDesign V2 risk analysis routes."""
from typing import List

from fastapi import APIRouter, HTTPException

from api.models.schemas import RiskAdjustmentRequest, RiskAnalysisResult
from api.services import requirement_service, risk_service

router = APIRouter()


@router.get("/risk-analysis/matrix/data", response_model=List[RiskAnalysisResult])
async def get_risk_matrix():
    return risk_service.get_all_risk_results()


@router.post("/risk-analysis/analyze-all", response_model=List[RiskAnalysisResult])
async def analyze_all_risks():
    parsed = requirement_service.get_all_parsed_requirements()
    if not parsed:
        raise HTTPException(status_code=404, detail="No parsed requirements found")
    try:
        return await risk_service.analyze_risks(parsed)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def analyze_risk(req_id: str):
    parsed = requirement_service.get_parsed_requirement(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    try:
        return await risk_service.analyze_risk(req_id, parsed)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def get_risk_analysis(req_id: str):
    result = risk_service.get_risk_analysis(req_id)
    if not result:
        raise HTTPException(status_code=404, detail="Risk analysis not found")
    return result


@router.put("/risk-analysis/{req_id}", response_model=RiskAnalysisResult)
async def adjust_risk(req_id: str, request: RiskAdjustmentRequest):
    if not requirement_service.get_requirement(req_id):
        raise HTTPException(status_code=404, detail="Requirement not found")
    return risk_service.adjust_risk(
        req_id,
        request.dimensions,
        iso9126_characteristic=request.iso9126_characteristic,
        tech_risk=request.tech_risk,
        business_risk=request.business_risk,
        reasoning=request.reasoning,
    )
