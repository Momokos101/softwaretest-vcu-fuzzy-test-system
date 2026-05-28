"""FR 7.0 — Test Suite Optimization.

Two capabilities over the tool's own test suite:

1. prioritize_suite()  — risk-based PRIORITIZATION: order every test case by the
   requirement's RPN (ascending; RPN=1 == highest risk runs first), using the
   risk analysis from FR 2.0. This is the "execution order" evidence.

2. minimize_suite()    — coverage-based MINIMIZATION: greedy set-cover that keeps
   the smallest subset of test cases still covering every coverage unit, where a
   coverage unit = (requirement × technique × polarity) — i.e. each Coverage Item
   at both positive and negative polarity. Proves coverage is not reduced.
"""
from __future__ import annotations

from api.services import risk_service, test_design_service

_DEFAULT_RPN = 99


def _rpn_map() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in risk_service.get_all_risk_results():
        out[r.requirement_id] = {"rpn": r.rpn, "extent": r.extent, "priority": r.priority}
    return out


def _rpn(req: str, rmap: dict[str, dict]) -> int:
    return (rmap.get(req) or {}).get("rpn", _DEFAULT_RPN)


def _polarity(case) -> str:
    """negative = 期望 VCU 报错/卡死；positive = 期望成功唤醒/休眠。"""
    rt = None
    stuck = False
    for e in case.expected_results:
        if e.name == "result_type":
            rt = e.value
        if e.name == "vehicle_state" and e.operator == "eq" and e.value in (10, "10"):
            stuck = True
    return "negative" if (rt == "error" or stuck) else "positive"


def _signature(case) -> tuple[str, str, str]:
    """覆盖单元 = (需求, 技术, 正负向) —— 等价于 Coverage Item × polarity。"""
    return (case.requirement_id, case.technique.value, _polarity(case))


def prioritize_suite() -> dict:
    """FR 7.0 — 按风险(RPN)对测试套件优先级排序。"""
    rmap = _rpn_map()
    cases = test_design_service.get_all_test_cases()
    ordered = sorted(cases, key=lambda c: (_rpn(c.requirement_id, rmap), c.requirement_id, c.technique.value))

    items = []
    band_counts: dict[int, int] = {}
    for rank, c in enumerate(ordered, start=1):
        rpn = _rpn(c.requirement_id, rmap)
        meta = rmap.get(c.requirement_id) or {}
        band_counts[rpn] = band_counts.get(rpn, 0) + 1
        items.append({
            "rank": rank,
            "case_id": c.id,
            "requirement_id": c.requirement_id,
            "title": c.title,
            "technique": c.technique.value,
            "polarity": _polarity(c),
            "rpn": rpn,
            "extent": meta.get("extent"),
            "priority": meta.get("priority"),
            "status": c.status.value,
        })

    bands = [
        {"rpn": rpn, "count": band_counts[rpn], "priority": (rmap_priority(rpn))}
        for rpn in sorted(band_counts)
    ]
    return {
        "criterion": "风险优先级（RPN 升序：RPN=1 风险最高，最先执行）。RPN 来自 FR 2.0 风险分析。",
        "total": len(items),
        "items": items,
        "bands": bands,
    }


def rmap_priority(rpn: int) -> str:
    if rpn <= 5:
        return "High"
    if rpn <= 10:
        return "Medium"
    return "Low"


def minimize_suite() -> dict:
    """FR 7.0 — 基于覆盖效率最小化测试套件（贪心 set-cover）。"""
    rmap = _rpn_map()
    cases = list(test_design_service.get_all_test_cases())
    universe = {_signature(c) for c in cases}

    # 贪心：每轮选"新覆盖单元最多"的用例；平手时取风险更高(RPN 更小)、再取耗时更短。
    remaining = set(universe)
    pool = list(cases)
    kept = []
    while remaining:
        best = None
        best_cov: set = set()
        for c in pool:
            cov = {_signature(c)} & remaining
            better = len(cov) > len(best_cov)
            tie = (
                len(cov) == len(best_cov)
                and cov
                and best is not None
                and (_rpn(c.requirement_id, rmap), c.est_time) < (_rpn(best.requirement_id, rmap), best.est_time)
            )
            if better or tie:
                best, best_cov = c, cov
        if not best_cov:
            break
        kept.append((best, best_cov))
        remaining -= best_cov
        pool.remove(best)

    kept_ids = {c.id for c, _ in kept}
    dropped = [c for c in cases if c.id not in kept_ids]

    def row(c, covered=None):
        return {
            "case_id": c.id,
            "requirement_id": c.requirement_id,
            "title": c.title,
            "technique": c.technique.value,
            "polarity": _polarity(c),
            "rpn": _rpn(c.requirement_id, rmap),
            **({"covers": ["×".join(u) for u in sorted(covered)]} if covered is not None else
               {"redundant_on": "×".join(_signature(c))}),
        }

    reqs_all = {c.requirement_id for c in cases}
    reqs_kept = {c.requirement_id for c, _ in kept}
    rt_all = {(c.requirement_id, c.technique.value) for c in cases}
    rt_kept = {(c.requirement_id, c.technique.value) for c, _ in kept}
    kept_units = {_signature(c) for c, _ in kept}

    before, after = len(cases), len(kept)
    return {
        "criterion": "覆盖最小化（贪心 set-cover）。覆盖单元 = 需求 × 技术 × 正负向（等价于 Coverage Item × polarity）。平手时优先保留高风险(RPN 小)、低耗时用例。",
        "before": before,
        "after": after,
        "removed": before - after,
        "reduction_pct": round(100 * (before - after) / before, 1) if before else 0.0,
        "coverage_units_total": len(universe),
        "coverage_units_retained": len(kept_units),
        "coverage_retained_pct": round(100 * len(kept_units) / len(universe), 1) if universe else 100.0,
        "requirements_retained": f"{len(reqs_kept)}/{len(reqs_all)}",
        "req_technique_retained": f"{len(rt_kept)}/{len(rt_all)}",
        "full_coverage_retained": kept_units == universe,
        "kept": [row(c, cov) for c, cov in kept],
        "dropped": [row(c) for c in dropped],
    }
