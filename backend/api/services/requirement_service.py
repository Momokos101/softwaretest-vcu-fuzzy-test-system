"""Requirement import, storage, and LLM parsing for AutoTestDesign V2."""
from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile

from api.models.schemas import (
    ParsedRequirement,
    Requirement,
    RequirementCreate,
    RequirementSource,
    RequirementUpdate,
)
from api.services import _persist
from api.services.requirement_parser import parse_requirement, parse_requirements_from_text


_requirements: List[Requirement] = _persist.load_list("requirements", Requirement)
_parsed_requirements: dict[str, ParsedRequirement] = _persist.load_dict("parsed_requirements", ParsedRequirement)


def _save() -> None:
    _persist.save_list("requirements", _requirements)
    _persist.save_dict("parsed_requirements", _parsed_requirements)


VCU_DEMO_REQUIREMENTS: list[dict[str, str]] = [
    {"id": "REQ-001", "module": "A", "title": "硬线供电唤醒 w1", "priority": "High", "raw_text": "供电电压 > 9V 持续 >= 10ms 时 VCU 应从 state09 唤醒到 state11，pdcu_wake_reason=1。"},
    {"id": "REQ-002", "module": "A/C", "title": "CAN 网络唤醒 w2", "priority": "High", "raw_text": "CAN 总线收到 0x400~0x47F 报文时 VCU 应唤醒，pdcu_wake_reason=2。"},
    {"id": "REQ-003", "module": "A", "title": "CP 信号唤醒 w3", "priority": "Medium", "raw_text": "CP 幅值 > 9V 上升沿触发 VCU 唤醒，pdcu_wake_reason=3。"},
    {"id": "REQ-004", "module": "A", "title": "CC 信号唤醒 w4", "priority": "Medium", "raw_text": "CC 电压下降至 < 4.4V 时触发 VCU 唤醒，pdcu_wake_reason=4。"},
    {"id": "REQ-005", "module": "A", "title": "CC2 信号唤醒 w5", "priority": "Medium", "raw_text": "CC2 UBR 电压下降沿触发 VCU 唤醒，pdcu_wake_reason=5。"},
    {"id": "REQ-006", "module": "A", "title": "口盖信号唤醒 w6", "priority": "Low", "raw_text": "口盖电压 > 4V 持续 >= 10ms 触发 VCU 唤醒，pdcu_wake_reason=6。"},
    {"id": "REQ-007", "module": "A", "title": "门板信号唤醒 w7", "priority": "Low", "raw_text": "门板电压 < 1V 持续 >= 10ms 触发 VCU 唤醒，pdcu_wake_reason=7。"},
    {"id": "REQ-008", "module": "A", "title": "休眠条件 h1", "priority": "High", "raw_text": "VCUIdle_flg=1 是 VCU 进入休眠 state09 的必要条件之一。"},
    {"id": "REQ-009", "module": "A", "title": "休眠条件 h2", "priority": "High", "raw_text": "AuthComplete_flg=1 是 VCU 进入休眠 state09 的必要条件之一。"},
    {"id": "REQ-010", "module": "A/C", "title": "休眠条件 h3", "priority": "High", "raw_text": "CAN 0x400~0x47F 停止发送是 VCU 进入休眠 state09 的必要条件之一。"},
    {"id": "REQ-011", "module": "A", "title": "三条件同时才休眠", "priority": "High", "raw_text": "h1 AND h2 AND h3 全部满足时 VCU 进入 state09，任一不满足时维持当前状态。"},
    {"id": "REQ-012", "module": "A/D", "title": "卡死缺陷检测", "priority": "High", "raw_text": "连续 3 次以上快速唤醒-休眠且相邻间隔 < 1s 时，VCU 可能卡死在 state10，actual_duration 超时并记录 DTC_001。"},
    {"id": "REQ-013", "module": "A", "title": "输出字段一致性", "priority": "Medium", "raw_text": "VCU 处于 state11 时 bus_message_flag=1；处于 state09 时 bus_message_flag=0。"},
    {"id": "REQ-014", "module": "A", "title": "响应时序合规", "priority": "Medium", "raw_text": "type1 测试 actual_duration <= 20s；type2 测试 actual_duration <= 60s。"},
    {"id": "REQ-015", "module": "B", "title": "过压保护", "priority": "High", "raw_text": "供电电压 > 16V 时 VCU 进入 fault_protection，拒绝唤醒并置 power_alarm_flag=1，同时记录 DTC_002。"},
    {"id": "REQ-016", "module": "B", "title": "欠压保护", "priority": "High", "raw_text": "供电电压 < 6V 时 VCU 进入 undervoltage_shutdown，并强制 bus_message_flag=0，同时记录 DTC_003。"},
    {"id": "REQ-017", "module": "B", "title": "信号去抖", "priority": "Medium", "raw_text": "w1/w6/w7 信号 duration < 5ms 时视为噪声，不触发任何状态转移。"},
    {"id": "REQ-018", "module": "C", "title": "CAN ID 过滤", "priority": "Medium", "raw_text": "VCU 仅处理 CAN ID 0x400~0x47F 范围报文；超出范围的 ID 静默丢弃，不触发唤醒。"},
    {"id": "REQ-019", "module": "C", "title": "CAN 总线离线检测", "priority": "Medium", "raw_text": "CAN error_counter > 255 时进入 bus_off，bus_off_flag=1 且 bus_message_flag=0。"},
    {"id": "REQ-020", "module": "D", "title": "DTC 故障码生成", "priority": "High", "raw_text": "state10 卡死写入 DTC_001；过压保护写入 DTC_002；欠压保护写入 DTC_003。"},
    {"id": "REQ-021", "module": "D", "title": "DTC 信息查询", "priority": "Low", "raw_text": "GET /dtc 返回所有 DTC 信息，包含代码、状态、触发次数和时间戳。"},
    {"id": "REQ-022", "module": "D", "title": "DTC 清除", "priority": "Low", "raw_text": "POST /reset 且 clear_dtc=true 时清除所有 DTC，DTC 状态置为 cleared。"},
    {"id": "REQ-023", "module": "E", "title": "功耗告警", "priority": "Medium", "raw_text": "state11 下 power_current > 0.2A 持续 > 500ms 时 power_alarm_flag=1。"},
    {"id": "REQ-024", "module": "E", "title": "低功耗合规", "priority": "Medium", "raw_text": "state09 下 power_current 必须 <= 0.01A。"},
]


def import_from_csv(file: UploadFile) -> List[Requirement]:
    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    imported: list[Requirement] = []
    for row in reader:
        raw_text = row.get("requirement") or row.get("需求") or row.get("raw_text") or row.get("text") or ""
        if not raw_text.strip():
            continue
        imported.append(
            create_requirement(
                RequirementCreate(
                    id=row.get("id") or row.get("REQ-ID") or row.get("req_id"),
                    source=RequirementSource.CSV,
                    raw_text=raw_text.strip(),
                    title=row.get("title") or row.get("标题"),
                    module=row.get("module") or row.get("模块"),
                    category=row.get("category") or row.get("分类"),
                    priority=row.get("priority") or row.get("风险等级"),
                )
            )
        )
    return imported


def import_from_text(text: str) -> List[Requirement]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [
        create_requirement(RequirementCreate(source=RequirementSource.TEXT, raw_text=line))
        for line in lines
    ]


def load_demo_requirements(replace: bool = False) -> List[Requirement]:
    if replace:
        clear_all()
    imported = []
    for item in VCU_DEMO_REQUIREMENTS:
        existing = get_requirement(item["id"])
        if existing:
            imported.append(existing)
            continue
        imported.append(create_requirement(RequirementCreate(source=RequirementSource.DEMO, **item)))
    return imported


def create_requirement(req_create: RequirementCreate) -> Requirement:
    now = datetime.now()
    req = Requirement(
        id=req_create.id or str(uuid.uuid4()),
        source=req_create.source,
        raw_text=req_create.raw_text,
        title=req_create.title,
        module=req_create.module,
        category=req_create.category,
        priority=req_create.priority,
        created_at=now,
        updated_at=now,
        parsed=False,
    )
    _replace_requirement(req)
    return req


def get_all_requirements() -> List[Requirement]:
    return list(_requirements)


def get_requirement(req_id: str) -> Optional[Requirement]:
    return next((req for req in _requirements if req.id == req_id), None)


def update_requirement(req_id: str, req_update: RequirementUpdate) -> Optional[Requirement]:
    req = get_requirement(req_id)
    if not req:
        return None
    if req_update.raw_text is not None and req_update.raw_text != req.raw_text:
        req.raw_text = req_update.raw_text
        req.parsed = False
        _parsed_requirements.pop(req_id, None)
    for field in ("title", "module", "category", "priority"):
        value = getattr(req_update, field)
        if value is not None:
            setattr(req, field, value)
    req.updated_at = datetime.now()
    _save()
    return req


def delete_requirement(req_id: str) -> bool:
    original_len = len(_requirements)
    _requirements[:] = [req for req in _requirements if req.id != req_id]
    _parsed_requirements.pop(req_id, None)
    _save()
    return len(_requirements) < original_len


async def parse_raw_text(raw_text: str, source: RequirementSource = RequirementSource.TEXT, persist: bool = True) -> List[ParsedRequirement]:
    parsed_items = await parse_requirements_from_text(raw_text)
    if persist:
        for parsed in parsed_items:
            req = create_requirement(
                RequirementCreate(
                    id=parsed.requirement_id,
                    source=source,
                    raw_text=parsed.description or raw_text,
                    title=parsed.title,
                    module=parsed.module,
                )
            )
            req.parsed = True
            _parsed_requirements[req.id] = parsed
        _save()
    return parsed_items


async def parse_requirement_by_id(req_id: str) -> Optional[ParsedRequirement]:
    req = get_requirement(req_id)
    if not req:
        return None
    parsed = await parse_requirement(req_id, req.raw_text)
    parsed.title = parsed.title or req.title
    parsed.module = parsed.module or req.module
    _parsed_requirements[req_id] = parsed
    req.parsed = True
    req.updated_at = datetime.now()
    _save()
    return parsed


async def parse_all_requirements(only_unparsed: bool = True) -> List[ParsedRequirement]:
    results: list[ParsedRequirement] = []
    for req in _requirements:
        if only_unparsed and req.parsed and req.id in _parsed_requirements:
            results.append(_parsed_requirements[req.id])
            continue
        parsed = await parse_requirement_by_id(req.id)
        if parsed:
            results.append(parsed)
    return results


def get_parsed_requirement(req_id: str) -> Optional[ParsedRequirement]:
    return _parsed_requirements.get(req_id)


def get_all_parsed_requirements() -> List[ParsedRequirement]:
    return list(_parsed_requirements.values())


def update_parsed_requirement(req_id: str, parsed: ParsedRequirement) -> Optional[ParsedRequirement]:
    if not get_requirement(req_id):
        return None
    parsed.requirement_id = req_id
    parsed.updated_at = datetime.now()
    _parsed_requirements[req_id] = parsed
    req = get_requirement(req_id)
    if req:
        req.parsed = True
    _save()
    return parsed


def clear_all() -> None:
    _requirements.clear()
    _parsed_requirements.clear()
    _save()


def _replace_requirement(req: Requirement) -> None:
    for index, existing in enumerate(_requirements):
        if existing.id == req.id:
            _requirements[index] = req
            _parsed_requirements.pop(req.id, None)
            _save()
            return
    _requirements.append(req)
    _save()
