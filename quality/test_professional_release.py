#!/usr/bin/env python3
"""Professional release gate: verifies the release candidate has the expected engineering controls."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "index.html",
    "manifest.webmanifest",
    "knowledge/competencies.json",
    "governance/WISDOM_GOVERNANCE.md",
    "governance/CONTINUITY_AND_COMPLETION_CONTRACT.md",
    "governance/PROFESSIONAL_RELEASE_STANDARD.md",
    "quality/test_go_gate.py",
    "quality/test_production_contract.py",
    "quality/test_release_contract.py",
    "autonomy/test_controller.py",
    "autonomy/test_mission_plan.py",
    "autonomy/test_intent_routing.py",
    "autonomy/test_wisdom_governance.py",
    ".github/workflows/autonomy-regression.yml",
    ".github/workflows/pages.yml",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"(?i)universally\s+correct"),
    re.compile(r"(?i)100%\s+(?:correct|guaranteed|error[- ]free)"),
    re.compile(r"(?i)unlimited\s+availability"),
    re.compile(r"(?i)official\s+verified\s+source.*user[- ]provided"),
]


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> None:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).is_file() or (ROOT / p).stat().st_size == 0]
    assert not missing, f"missing professional release assets: {missing}"

    kb = json.loads(read("knowledge/competencies.json"))
    records = kb.get("records")
    assert isinstance(records, list) and records, "structured knowledge is empty"
    assert all(isinstance(r, dict) for r in records), "knowledge records must be objects"
    assert all(r.get("id") and r.get("grade") and r.get("subject") for r in records), "unstable knowledge record"

    html = read("index.html")
    assert len(html) > 1000
    for marker in ("كفايات Ω", "inferMission", "retrieveMission", "WISDOM", "Cross-Domain", "القيادة الذاتية"):
        assert marker in html, f"critical product marker missing: {marker}"

    manifest = json.loads(read("manifest.webmanifest"))
    assert manifest.get("lang") == "ar" and manifest.get("dir") == "rtl"
    assert manifest.get("display") == "standalone"

    controller = read("autonomy/controller.py")
    for marker in ("SAFE_STOP", "NO CLAIM", "RECOVER_OR_ESCALATE"):
        assert marker in controller, f"bounded autonomy marker missing: {marker}"

    pages = read(".github/workflows/pages.yml")
    assert "actions/deploy-pages@v4" in pages
    assert "Runtime smoke test" in pages
    assert "curl --fail" in pages

    workflow = read(".github/workflows/autonomy-regression.yml")
    for marker in ("test_go_gate.py", "test_professional_release.py", "test_intent_routing.py", "test_wisdom_governance.py"):
        assert marker in workflow, f"CI gate missing: {marker}"

    combined = "\n".join(read(p) for p in REQUIRED_FILES)
    hits = [p.pattern for p in FORBIDDEN_PATTERNS if p.search(combined)]
    assert not hits, f"unsupported production claim detected: {hits}"

    print("PROFESSIONAL RELEASE GATE: PASS")
    print("Evidence posture: BUILT/TESTED controls structurally present")
    print("Deployment and runtime claims remain evidence-scoped")


if __name__ == "__main__":
    main()
