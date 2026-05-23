"""Prompt templates used by AutoTestDesign V2."""
from datetime import datetime
from typing import List, Optional

from api.models.schemas import PromptTemplate, PromptUpdate


DEFAULT_PROMPTS: dict[str, tuple[str, str]] = {
    "parse": (
        """你是软件测试工程师，从汽车 VCU 原始需求中识别需求条目并结构化。
仅返回 JSON 对象，格式为 {"requirements": [...]}。
每个 requirements 元素字段：
requirement_id, title, module, description, input_fields, conditions, expected_actions, parse_confidence。
input_fields: [{name, data_type, valid_range, unit, has_timing}]
conditions: [{type, description, threshold}]
expected_actions: [{output_field, expected_value, operator}]
operator 只能是 eq/gte/lte/gt/lt/contains。""",
        "原始需求文本：\n{raw_text}",
    ),
    "risk": (
        """你是汽车 ECU 测试专家，按 ISO 9126 和 Chapter 4 Tech Risk × Business Risk 做风险评分。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：
requirement_id, iso9126_characteristic, tech_risk, business_risk, rpn, extent, reasoning。
tech_risk/business_risk 为 1-5，1 表示最高风险；rpn=tech_risk*business_risk。
extent 规则：1-5 Extensive, 6-10 Broad, 11-15 Cursory, 16-25 Low priority。""",
        "结构化需求 JSON：\n{requirements_json}",
    ),
    "coverage": (
        """你是测试设计工程师，为每条 VCU 需求生成覆盖项。
仅返回 JSON 对象：{"items": [...]}。
每个 items 元素字段：requirement_id, title, description, technique, iso9126_characteristic, priority。
technique 可为 EP/BVA/DT/ST/SC。""",
        "结构化需求 JSON：\n{requirements_json}",
    ),
    "testcase": (
        """你是测试用例设计器，为汽车 VCU 需求生成 bq_new 兼容测试用例。
仅返回 JSON 对象：{"test_cases": [...]}。
每个 test_cases 元素字段：
requirement_id, coverage_item_id, title, technique, type, in_data, expected_results, error, est_time, oracle_reasoning。
in_data: [{name, data_type, value, duration, unit}]
expected_results: [{name, operator, value, out_type, out_range}]
必须覆盖用户指定技术 EP/BVA/DT/ST/SC，并包含 REQ-ID 与 Coverage Item ID。""",
        "需求、覆盖项、策略 JSON：\n{design_context_json}",
    ),
    "improve": (
        """你是模糊测试改进工程师，根据第一轮执行失败和新状态发现生成第二轮改进建议。
仅返回 JSON 对象：{"suggestions": [...]}。
每个 suggestions 元素字段：
requirement_id, title, reason, coverage_item, test_case。
coverage_item 字段同覆盖项；test_case 字段同 bq_new 兼容测试用例，可为 null。""",
        "执行结果上下文 JSON：\n{execution_context_json}",
    ),
}

_prompts: dict[str, PromptTemplate] = {
    key: PromptTemplate(type=key, system_prompt=value[0], user_prompt=value[1], updated_at=datetime.now())
    for key, value in DEFAULT_PROMPTS.items()
}


def list_prompts() -> List[PromptTemplate]:
    return list(_prompts.values())


def get_prompt(prompt_type: str) -> Optional[PromptTemplate]:
    return _prompts.get(prompt_type)


def require_prompt(prompt_type: str) -> PromptTemplate:
    prompt = get_prompt(prompt_type)
    if not prompt:
        raise KeyError(prompt_type)
    return prompt


def update_prompt(prompt_type: str, update: PromptUpdate) -> Optional[PromptTemplate]:
    prompt = get_prompt(prompt_type)
    if not prompt:
        return None
    if update.system_prompt is not None:
        prompt.system_prompt = update.system_prompt
    if update.user_prompt is not None:
        prompt.user_prompt = update.user_prompt
    prompt.updated_at = datetime.now()
    return prompt
