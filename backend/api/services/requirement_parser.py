"""
需求解析服务。
使用可解释的正则规则提取任务书要求的四类结构：
Input Fields、Data Ranges、Conditions、Actions。
"""
import re
from datetime import datetime
from typing import Any, Dict, List

from api.models.schemas import ParsedRequirement


SIGNAL_ALIASES = {
    "CC2电压": [r"CC2\s*(?:电压|voltage)", r"CC2电压"],
    "CC电压值": [r"CC\s*(?:电压值|电压|voltage)", r"CC电压值"],
    "CP幅值": [r"CP\s*(?:幅值|amplitude)", r"CP幅值"],
    "供电电压": [r"(?:供电电压|supply\s*voltage)"],
    "网络唤醒报文使能状态": [r"(?:网络唤醒报文使能状态|网络唤醒|network\s*wake(?:\s*enable)?)"],
}

RANGE_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*[Vv]?\s+(?:to|至|到|-|~)\s+(\d+(?:\.\d+)?)\s*[Vv]?"),
    re.compile(r"\[(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\]\s*[Vv]?"),
    re.compile(r"(\d+(?:\.\d+)?)\s*[Vv]?\s*(?:-|~|至|到)\s*(\d+(?:\.\d+)?)\s*[Vv]?"),
]
THRESHOLD_PATTERNS = [
    re.compile(r"(?:exceeds|above|greater than|>|高于|大于|超过)\s*(\d+(?:\.\d+)?)\s*[Vv]?"),
    re.compile(r"(?:below|drops below|less than|<|低于|小于)\s*(\d+(?:\.\d+)?)\s*[Vv]?"),
]
CONDITION_PATTERNS = [
    re.compile(r"\b(?:when|if|while|during)\b\s+(.+?)(?=\s+(?:the\s+)?(?:VCU\s+)?(?:shall|must|will)\b|[;。；]|$)", re.I),
    re.compile(r"(?:当|如果|若|在)(.+?)(?:时|情况下|条件下)"),
]
ACTION_PATTERNS = [
    re.compile(r"\b(?:shall|must|will)\s+(.+?)(?:\.|;|$)", re.I),
    re.compile(r"(?:应|应该|必须|将|需要)\s*([^，。；]+)"),
    re.compile(r"(?:VCU|系统)\s*(唤醒|休眠|进入[^，。；]*|保持[^，。；]*|输出[^，。；]*)"),
]


def parse_requirement(requirement_id: str, raw_text: str) -> ParsedRequirement:
    """解析需求文本。"""
    input_fields = _extract_input_fields(raw_text)
    data_ranges = _extract_data_ranges(raw_text, input_fields)
    conditions = _extract_conditions(raw_text)
    actions = _extract_actions(raw_text)

    structures_found = sum(
        [bool(input_fields), bool(data_ranges), bool(conditions), bool(actions)]
    )
    confidence = round(structures_found / 4, 2)

    return ParsedRequirement(
        requirement_id=requirement_id,
        input_fields=input_fields,
        data_ranges=data_ranges,
        conditions=conditions,
        actions=actions,
        parse_confidence=confidence,
        updated_at=datetime.now(),
    )


def _extract_input_fields(text: str) -> List[str]:
    fields: List[str] = []
    for canonical, aliases in SIGNAL_ALIASES.items():
        if any(re.search(alias, text, re.I) for alias in aliases):
            fields.append(canonical)

    generic_pattern = re.compile(
        r"([A-Za-z0-9_一-龥]+(?:电压值|电压|幅值|状态|报文|信号))"
    )
    for match in generic_pattern.findall(text):
        if match not in fields and not re.fullmatch(r"(?:输入|检测|供电)", match):
            fields.append(match)

    return _unique(fields)


def _extract_data_ranges(text: str, fields: List[str]) -> Dict[str, Dict[str, Any]]:
    ranges: Dict[str, Dict[str, Any]] = {}
    if not fields:
        return ranges

    range_matches = _find_ranges(text)
    if not range_matches:
        return ranges

    for field in fields:
        field_pos = _field_position(text, field)
        chosen = _nearest_range(field_pos, range_matches)
        if chosen:
            ranges[field] = chosen

    return ranges


def _find_ranges(text: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for pattern in RANGE_PATTERNS:
        for match in pattern.finditer(text):
            low, high = float(match.group(1)), float(match.group(2))
            matches.append(
                {
                    "type": "range",
                    "min": min(low, high),
                    "max": max(low, high),
                    "_position": match.start(),
                }
            )

    for index, pattern in enumerate(THRESHOLD_PATTERNS):
        for match in pattern.finditer(text):
            value = float(match.group(1))
            operator = ">" if index == 0 else "<"
            threshold = {
                "type": "threshold",
                "operator": operator,
                "threshold": value,
                "exclusive": True,
                "_position": match.start(),
            }
            excluded_values = _extract_excluded_values(text[match.end():])
            if excluded_values:
                threshold["excluded_values"] = excluded_values
            matches.append(threshold)

    for match in re.finditer(r"(?:equals|equal to|=|等于)\s*(\d+(?:\.\d+)?)\s*[Vv]?", text, re.I):
        value = float(match.group(1))
        matches.append(
            {
                "type": "equality",
                "operator": "==",
                "value": value,
                "_position": match.start(),
            }
        )

    return matches


def _field_position(text: str, field: str) -> int:
    idx = text.find(field)
    if idx >= 0:
        return idx

    for alias in SIGNAL_ALIASES.get(field, []):
        match = re.search(alias, text, re.I)
        if match:
            return match.start()
    return 0


def _nearest_range(field_pos: int, ranges: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    if not ranges:
        return None
    chosen = min(ranges, key=lambda item: abs(item["_position"] - field_pos))
    return {key: value for key, value in chosen.items() if key != "_position"}


def _extract_excluded_values(text_after_threshold: str) -> List[float]:
    """提取阈值条件后的排除值，例如 not the sleep trigger 12.0V。"""
    excluded_values: List[float] = []
    window = text_after_threshold[:120]
    window = re.split(r",|\b(?:the\s+)?(?:VCU\s+)?(?:shall|must|will)\b", window, maxsplit=1, flags=re.I)[0]
    if re.search(r"(?:not|except|excluding|不是|除外)", window, re.I):
        for value in re.findall(r"(\d+(?:\.\d+)?)\s*[Vv]?", window):
            excluded_values.append(float(value))
    return excluded_values


def _extract_conditions(text: str) -> List[str]:
    conditions: List[str] = []
    for pattern in CONDITION_PATTERNS:
        conditions.extend(match.strip(" ，,") for match in pattern.findall(text))
    return _unique([c for c in conditions if c])


def _extract_actions(text: str) -> List[str]:
    actions: List[str] = []
    for pattern in ACTION_PATTERNS:
        actions.extend(match.strip(" ，,") for match in pattern.findall(text))
    return _unique([a for a in actions if a])


def _unique(items: List[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for item in items:
        normalized = item.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result
