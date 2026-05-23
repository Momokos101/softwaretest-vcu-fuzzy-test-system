"""AutoTestDesign V2 requirement routes."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.models.schemas import (
    ParsedRequirement,
    Requirement,
    RequirementCreate,
    RequirementsParseRequest,
    RequirementUpdate,
)
from api.services import requirement_service

router = APIRouter()


@router.post("/requirements/parse", response_model=List[ParsedRequirement])
async def parse_raw_requirements(request: RequirementsParseRequest):
    """FR1.0/1.1: LLM parse raw pasted requirements."""
    try:
        return await requirement_service.parse_raw_text(request.raw_text, source=request.source, persist=request.persist)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/requirements/upload-csv", response_model=List[Requirement])
async def upload_csv(file: UploadFile = File(...)):
    """FR1.0: CSV upload using V2 route."""
    return requirement_service.import_from_csv(file)


@router.get("/requirements/demo", response_model=List[Requirement])
async def load_demo(replace: bool = False):
    """FR1.0: load V2 24-requirement VCU demo."""
    return requirement_service.load_demo_requirements(replace=replace)


@router.post("/requirements/import/csv", response_model=List[Requirement])
async def import_csv_legacy(file: UploadFile = File(...)):
    return requirement_service.import_from_csv(file)


@router.post("/requirements/import/text", response_model=List[Requirement])
async def import_text_legacy(request: dict):
    return requirement_service.import_from_text(request.get("raw_text", ""))


@router.post("/requirements/import/form", response_model=Requirement)
async def import_form(req: RequirementCreate):
    return requirement_service.create_requirement(req)


@router.post("/requirements/parse-all", response_model=List[ParsedRequirement])
async def parse_all_requirements(only_unparsed: bool = True):
    try:
        return await requirement_service.parse_all_requirements(only_unparsed=only_unparsed)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/requirements", response_model=List[Requirement])
async def get_requirements():
    return requirement_service.get_all_requirements()


@router.post("/requirements/analyze-risk")
async def analyze_risk_for_all():
    from api.services import risk_service

    parsed = requirement_service.get_all_parsed_requirements()
    if not parsed:
        raise HTTPException(status_code=404, detail="No parsed requirements found")
    return await risk_service.analyze_risks(parsed)


@router.get("/requirements/{req_id}", response_model=Requirement)
async def get_requirement(req_id: str):
    req = requirement_service.get_requirement(req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.put("/requirements/{req_id}", response_model=Requirement)
async def update_requirement(req_id: str, req_update: RequirementUpdate):
    req = requirement_service.update_requirement(req_id, req_update)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.delete("/requirements/{req_id}")
async def delete_requirement(req_id: str):
    if not requirement_service.delete_requirement(req_id):
        raise HTTPException(status_code=404, detail="Requirement not found")
    return {"message": "Deleted successfully"}


@router.post("/requirements/{req_id}/parse", response_model=ParsedRequirement)
async def parse_requirement(req_id: str):
    try:
        parsed = await requirement_service.parse_requirement_by_id(req_id)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not parsed:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return parsed


@router.get("/requirements/{req_id}/parsed", response_model=ParsedRequirement)
async def get_parsed(req_id: str):
    parsed = requirement_service.get_parsed_requirement(req_id)
    if not parsed:
        raise HTTPException(status_code=404, detail="Parsed requirement not found")
    return parsed


@router.put("/requirements/{req_id}/parsed", response_model=ParsedRequirement)
async def update_parsed(req_id: str, parsed: ParsedRequirement):
    result = requirement_service.update_parsed_requirement(req_id, parsed)
    if not result:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return result
