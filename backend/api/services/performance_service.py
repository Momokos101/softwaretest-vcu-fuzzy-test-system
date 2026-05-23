"""AutoTestDesign V2 performance metrics."""
from datetime import datetime
from typing import Any, List

from api.models.schemas import PerformanceMetric


_metrics: List[PerformanceMetric] = []


def record(operation: str, elapsed_ms: float, model: str | None = None, detail: dict[str, Any] | None = None) -> PerformanceMetric:
    metric = PerformanceMetric(
        operation=operation,
        elapsed_ms=round(elapsed_ms, 2),
        model=model,
        detail=detail or {},
        created_at=datetime.now(),
    )
    _metrics.append(metric)
    return metric


def list_metrics(operation: str | None = None) -> List[PerformanceMetric]:
    if operation:
        return [item for item in _metrics if item.operation == operation]
    return list(_metrics)


def summary() -> dict[str, Any]:
    grouped: dict[str, list[float]] = {}
    for item in _metrics:
        grouped.setdefault(item.operation, []).append(item.elapsed_ms)

    return {
        operation: {
            "count": len(values),
            "avg_ms": round(sum(values) / len(values), 2),
            "max_ms": round(max(values), 2),
            "min_ms": round(min(values), 2),
        }
        for operation, values in grouped.items()
        if values
    }
