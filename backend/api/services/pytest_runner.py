"""Run the data-driven pytest suite and feed results back into the tool.

This makes the frontend "执行全部" (POST /api/execute) actually run the real
pytest suite (`tests/test_suite_from_design.py`, which executes the 96 reviewed
design cases against the VCU simulator with the input adapter), then maps each
pytest result back to its tool test case via the case uuid embedded in the
JUnit XML testcase name, marking pass/fail. The tool's Results tab then reflects
the genuine pytest execution.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from api.services import test_design_service

_ROOT = Path(__file__).resolve().parents[3]
_TEST_FILE = _ROOT / "tests" / "test_suite_from_design.py"
_OUT_DIR = _ROOT / "docs" / "test_evidence" / "pytest_output"
_XML = _OUT_DIR / "design_suite.xml"
_HTML = _OUT_DIR / "design_suite_report.html"
_DETAILS = _OUT_DIR / "execution_details.json"

_UUID_RE = re.compile(r"\[([0-9a-fA-F]{8}-[0-9a-fA-F-]{27})")


def run_and_mark() -> dict:
    """Run pytest, parse JUnit XML, mark each tool test case pass/fail."""
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove stale details so we never reuse a previous run's output.
    try:
        _DETAILS.unlink()
    except FileNotFoundError:
        pass
    cmd = [
        sys.executable, "-m", "pytest", str(_TEST_FILE), "-q",
        "--junitxml", str(_XML),
        "--html", str(_HTML), "--self-contained-html",
    ]
    proc = subprocess.run(cmd, cwd=str(_ROOT), capture_output=True, text=True, timeout=300)

    # Prefer the rich per-case details (input / expected / actual VCU output /
    # mismatches) written by the test suite; fall back to JUnit XML pass/fail.
    details = _load_details()
    marked = passed = failed = 0
    if details:
        for d in details:
            case_id, ok = d.get("case_id"), bool(d.get("passed"))
            if not test_design_service.get_test_case(case_id):
                continue
            test_design_service.mark_execution(
                case_id,
                {
                    "via": "pytest:test_suite_from_design.py",
                    "passed": ok,
                    "input": d.get("input"),
                    "expected": d.get("expected"),
                    "actual_output": d.get("actual_output"),
                    "mismatches": d.get("mismatches"),
                    "executed_at": datetime.now().isoformat(),
                },
                ok,
            )
            marked += 1
            passed += int(ok)
            failed += int(not ok)
    else:
        for case_id, ok, message in _parse_junit(_XML):
            if not test_design_service.get_test_case(case_id):
                continue
            test_design_service.mark_execution(
                case_id,
                {"via": "pytest", "passed": ok, "detail": message, "executed_at": datetime.now().isoformat()},
                ok,
            )
            marked += 1
            passed += int(ok)
            failed += int(not ok)

    return {
        "engine": "pytest",
        "test_file": str(_TEST_FILE.relative_to(_ROOT)),
        "marked": marked,
        "passed": passed,
        "failed": failed,
        "junit_xml": str(_XML.relative_to(_ROOT)),
        "html_report": str(_HTML.relative_to(_ROOT)),
        "returncode": proc.returncode,
    }


def _load_details() -> list:
    if not _DETAILS.exists():
        return []
    try:
        data = json.loads(_DETAILS.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _parse_junit(xml_path: Path) -> list[tuple[str, bool, str]]:
    if not xml_path.exists():
        return []
    root = ET.parse(xml_path).getroot()
    out: list[tuple[str, bool, str]] = []
    for tc in root.iter("testcase"):
        name = tc.get("name", "")
        m = _UUID_RE.search(name)
        if not m:
            continue
        case_id = m.group(1)
        failure = next((c for c in tc if c.tag in ("failure", "error")), None)
        ok = failure is None
        message = (failure.get("message") or "")[:300] if failure is not None else ""
        out.append((case_id, ok, message))
    return out
