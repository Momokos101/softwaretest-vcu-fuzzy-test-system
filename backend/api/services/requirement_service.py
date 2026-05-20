"""
需求管理服务
提供需求的CRUD操作和导入功能
"""
import csv
import io
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile

from api.models.schemas import (
    Requirement, RequirementCreate, RequirementUpdate,
    RequirementSource, ParsedRequirement
)
from api.services.requirement_parser import parse_requirement

# 内存存储
_requirements: List[Requirement] = []
_parsed_requirements: dict[str, ParsedRequirement] = {}


def import_from_csv(file: UploadFile) -> List[Requirement]:
    """从CSV导入需求"""
    content = file.file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))

    requirements = []
    for row in reader:
        raw_text = row.get('requirement') or row.get('需求') or row.get('raw_text') or row.get('text') or ''
        if raw_text:
            req = create_requirement(RequirementCreate(
                source=RequirementSource.CSV,
                raw_text=raw_text
            ))
            requirements.append(req)

    return requirements


def import_from_text(text: str) -> List[Requirement]:
    """从文本导入需求"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    requirements = []
    for line in lines:
        req = create_requirement(RequirementCreate(
            source=RequirementSource.TEXT,
            raw_text=line
        ))
        requirements.append(req)

    return requirements


def create_requirement(req_create: RequirementCreate) -> Requirement:
    """创建需求"""
    req = Requirement(
        id=str(uuid.uuid4()),
        source=req_create.source,
        raw_text=req_create.raw_text,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        parsed=False
    )
    _requirements.append(req)
    return req


def get_all_requirements() -> List[Requirement]:
    """获取所有需求"""
    return _requirements


def get_requirement(req_id: str) -> Optional[Requirement]:
    """获取单个需求"""
    for req in _requirements:
        if req.id == req_id:
            return req
    return None


def update_requirement(req_id: str, req_update: RequirementUpdate) -> Optional[Requirement]:
    """更新需求"""
    for req in _requirements:
        if req.id == req_id:
            req.raw_text = req_update.raw_text
            req.parsed = False
            req.updated_at = datetime.now()
            _parsed_requirements.pop(req_id, None)
            return req
    return None


def delete_requirement(req_id: str) -> bool:
    """删除需求"""
    global _requirements
    original_len = len(_requirements)
    _requirements = [r for r in _requirements if r.id != req_id]

    if req_id in _parsed_requirements:
        del _parsed_requirements[req_id]

    return len(_requirements) < original_len


def parse_requirement_by_id(req_id: str) -> Optional[ParsedRequirement]:
    """解析需求"""
    req = get_requirement(req_id)
    if not req:
        return None

    parsed = parse_requirement(req_id, req.raw_text)
    _parsed_requirements[req_id] = parsed

    req.parsed = True
    req.updated_at = datetime.now()

    return parsed


def parse_all_requirements(only_unparsed: bool = True) -> List[ParsedRequirement]:
    """批量解析需求"""
    results = []
    for req in _requirements:
        if only_unparsed and req.parsed:
            existing = _parsed_requirements.get(req.id)
            if existing:
                results.append(existing)
            continue

        parsed = parse_requirement(req.id, req.raw_text)
        _parsed_requirements[req.id] = parsed
        req.parsed = True
        req.updated_at = datetime.now()
        results.append(parsed)
    return results


def get_parsed_requirement(req_id: str) -> Optional[ParsedRequirement]:
    """获取解析结果"""
    return _parsed_requirements.get(req_id)


def update_parsed_requirement(req_id: str, parsed: ParsedRequirement) -> Optional[ParsedRequirement]:
    """更新解析结果"""
    if req_id not in _parsed_requirements:
        return None

    parsed.updated_at = datetime.now()
    _parsed_requirements[req_id] = parsed
    return parsed
