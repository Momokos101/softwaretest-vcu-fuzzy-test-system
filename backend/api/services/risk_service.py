"""
风险分析服务。
实现任务书指定的5维度加权评分算法，所有维度和总分均使用0-10尺度。
"""
from datetime import datetime
from typing import List, Optional

from api.models.schemas import ParsedRequirement, RiskAnalysisResult, RiskDimension


_risk_results: dict[str, RiskAnalysisResult] = {}

WEIGHTS = {
    "criticality": 0.35,
    "boundary_sensitivity": 0.25,
    "complexity": 0.20,
    "state_impact": 0.15,
    "testability": 0.05,
}


def analyze_risk(requirement_id: str, parsed_req: ParsedRequirement) -> RiskAnalysisResult:
    """自动分析单条需求风险。"""
    dimensions = _auto_assess_dimensions(parsed_req)
    result = _build_result(requirement_id, dimensions)
    _risk_results[requirement_id] = result
    return result


def get_risk_analysis(requirement_id: str) -> Optional[RiskAnalysisResult]:
    return _risk_results.get(requirement_id)


def adjust_risk(requirement_id: str, dimensions: RiskDimension) -> RiskAnalysisResult:
    """人工覆盖5维分值，用于Interactive Review。"""
    result = _build_result(requirement_id, dimensions)
    _risk_results[requirement_id] = result
    return result


def get_all_risk_results() -> List[RiskAnalysisResult]:
    return list(_risk_results.values())


def _build_result(requirement_id: str, dimensions: RiskDimension) -> RiskAnalysisResult:
    total_score = _calculate_total_score(dimensions)
    return RiskAnalysisResult(
        requirement_id=requirement_id,
        dimensions=dimensions,
        total_score=total_score,
        priority=_determine_priority(total_score),
        created_at=datetime.now(),
    )


def _auto_assess_dimensions(parsed_req: ParsedRequirement) -> RiskDimension:
    text = " ".join(parsed_req.actions + parsed_req.conditions + parsed_req.input_fields)

    criticality = 8.0 if any(keyword in text for keyword in ["唤醒", "休眠", "READY", "ready", "wake", "sleep"]) else 5.0
    boundary_sensitivity = min(10.0, 4.0 + len(parsed_req.data_ranges) * 2.0)
    complexity = min(10.0, 3.0 + len(parsed_req.conditions) * 1.5 + max(0, len(parsed_req.input_fields) - 1))
    state_impact = 8.0 if any(keyword in text for keyword in ["state", "模式", "状态", "READY", "ready"]) else 5.5
    testability = max(2.0, round(parsed_req.parse_confidence * 10, 1))

    return RiskDimension(
        criticality=criticality,
        boundary_sensitivity=boundary_sensitivity,
        complexity=complexity,
        state_impact=state_impact,
        testability=testability,
    )


def _calculate_total_score(dimensions: RiskDimension) -> float:
    score = (
        dimensions.criticality * WEIGHTS["criticality"]
        + dimensions.boundary_sensitivity * WEIGHTS["boundary_sensitivity"]
        + dimensions.complexity * WEIGHTS["complexity"]
        + dimensions.state_impact * WEIGHTS["state_impact"]
        + dimensions.testability * WEIGHTS["testability"]
    )
    return round(score, 2)


def _determine_priority(score: float) -> str:
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"
