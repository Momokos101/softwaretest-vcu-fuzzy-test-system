"""
导出服务。
支持 JSON / CSV / Excel，并生成需求-风险-测试用例追踪矩阵。
"""
import io
import json
from typing import Any

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from api.models.schemas import ExportFormat, ExportRequest
from api.services import requirement_service, risk_service, test_design_service


def export_data(request: ExportRequest) -> tuple[bytes, str, str]:
    data = _collect_data(request)

    if request.format == ExportFormat.JSON:
        return _export_json(data)
    if request.format == ExportFormat.CSV:
        return _export_csv(data)
    return _export_excel(data)


def _collect_data(request: ExportRequest) -> dict[str, Any]:
    selected_ids = set(request.requirement_ids or [])

    def selected(req_id: str) -> bool:
        return not selected_ids or req_id in selected_ids

    data: dict[str, Any] = {}
    requirements = [r for r in requirement_service.get_all_requirements() if selected(r.id)]
    risks = [r for r in risk_service.get_all_risk_results() if selected(r.requirement_id)]
    cases = [c for c in test_design_service.get_all_test_cases() if selected(c.requirement_id)]

    allowed_techniques = set()
    if request.scope.include_ep_cases:
        allowed_techniques.add("ep")
    if request.scope.include_bva_cases:
        allowed_techniques.add("bva")
    if request.scope.include_dt_cases:
        allowed_techniques.add("dt")
    if allowed_techniques:
        cases = [c for c in cases if c.technique.value in allowed_techniques]

    if request.scope.include_requirements:
        data["requirements"] = [r.model_dump(mode="json") for r in requirements]
    if request.scope.include_risk_analysis:
        data["risk_analysis"] = [r.model_dump(mode="json") for r in risks]
    if request.scope.include_test_cases:
        case_rows = [c.model_dump(mode="json") for c in cases]
        if not request.scope.include_execution_results:
            for row in case_rows:
                row["execution_result"] = None
        data["test_cases"] = case_rows
    if request.scope.include_traceability_matrix:
        data["traceability_matrix"] = _build_traceability(requirements, risks, cases)

    return data


def _build_traceability(requirements, risks, cases) -> list[dict[str, Any]]:
    risk_by_req = {risk.requirement_id: risk for risk in risks}
    cases_by_req: dict[str, list] = {}
    for case in cases:
        cases_by_req.setdefault(case.requirement_id, []).append(case)

    rows = []
    for req in requirements:
        risk = risk_by_req.get(req.id)
        linked_cases = cases_by_req.get(req.id, [])
        rows.append(
            {
                "requirement_id": req.id,
                "requirement": req.raw_text,
                "risk_score": risk.total_score if risk else None,
                "priority": risk.priority if risk else None,
                "test_case_count": len(linked_cases),
                "test_case_ids": ",".join(case.id for case in linked_cases),
            }
        )
    return rows


def _export_json(data: dict[str, Any]) -> tuple[bytes, str, str]:
    content = json.dumps(data, ensure_ascii=False, indent=2)
    return content.encode("utf-8"), "application/json", "autotestdesign_export.json"


def _export_csv(data: dict[str, Any]) -> tuple[bytes, str, str]:
    output = io.StringIO()
    target = "traceability_matrix" if data.get("traceability_matrix") else "test_cases"
    rows = data.get(target) or data.get("requirements") or []
    pd.DataFrame(rows).to_csv(output, index=False)
    return output.getvalue().encode("utf-8-sig"), "text/csv", "autotestdesign_export.csv"


def _export_excel(data: dict[str, Any]) -> tuple[bytes, str, str]:
    wb = Workbook()
    wb.remove(wb.active)

    _add_sheet(wb, "Requirements", data.get("requirements", []))
    _add_sheet(wb, "Risk Analysis", data.get("risk_analysis", []))
    _add_sheet(wb, "Test Cases", data.get("test_cases", []))
    _add_sheet(wb, "Traceability", data.get("traceability_matrix", []))

    if not wb.sheetnames:
        _add_sheet(wb, "Export", [{"message": "No data selected"}])

    output = io.BytesIO()
    wb.save(output)
    return (
        output.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "autotestdesign_export.xlsx",
    )


def _add_sheet(wb: Workbook, name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    ws = wb.create_sheet(name[:31])
    headers = list(rows[0].keys())
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAF7")

    for row in rows:
        ws.append([_stringify(row.get(header)) for header in headers])

    for column in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in column)
        ws.column_dimensions[column[0].column_letter].width = min(max(max_len + 2, 12), 60)


def _stringify(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value
