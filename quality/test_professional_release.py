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
    "intent/intent-engine.js",
    "artifact/pdf-artifact-engine.js",
    "artifact/android-webview-bridge.js",
    "knowledge/competencies.json",
    "governance/WISDOM_GOVERNANCE.md",
    "governance/INTENT_FULFILLMENT_CONTRACT.md",
    "governance/CONTINUITY_AND_COMPLETION_CONTRACT.md",
    "governance/PROFESSIONAL_RELEASE_STANDARD.md",
    "quality/test_go_gate.py",
    "quality/test_production_contract.py",
    "quality/test_release_contract.py",
    "quality/test_runtime_browser.py",
    "autonomy/test_controller.py",
    "autonomy/test_mission_plan.py",
    "autonomy/test_intent_routing.py",
    "autonomy/test_wisdom_governance.py",
    "tests/test_intent_contract_engine.py",
    "tests/test_pdf_artifact_engine.py",
    "tests/test_android_pdf_bridge_contract.py",
    ".github/workflows/intent-fulfillment-regression.yml",
    ".github/workflows/autonomy-regression.yml",
    ".github/workflows/production-gate.yml",
    ".github/workflows/android-release.yml",
    ".github/workflows/pages.yml",
]

CLAIM_SCAN_FILES = [
    "README.md",
    "index.html",
    "intent/intent-engine.js",
    "governance/WISDOM_GOVERNANCE.md",
    "governance/INTENT_FULFILLMENT_CONTRACT.md",
    "governance/CONTINUITY_AND_COMPLETION_CONTRACT.md",
    "governance/PROFESSIONAL_RELEASE_STANDARD.md",
    "autonomy/controller.py",
    ".github/workflows/autonomy-regression.yml",
    ".github/workflows/production-gate.yml",
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
    for marker in ("كفايات Ω", "inferMission", "retrieveMission", "WISDOM", "Cross-Domain", "القيادة الذاتية", "Intent Contract", "Acceptance Oracle", "KefayatArtifact"):
        assert marker in html, f"critical product marker missing: {marker}"

    intent = read("intent/intent-engine.js")
    for marker in ("compileContract", "inferGradeFromEvidence", "retrieveEvidence", "acceptanceOracle", "P0_GOLDEN_RENDER"):
        assert marker in intent, f"intent engine marker missing: {marker}"
    artifact = read("artifact/pdf-artifact-engine.js")
    for marker in ("serializeImagePdf", "buildLessonPdf", "semanticMath", "EXPLICIT_TOKEN_GEOMETRY_TO_CANVAS_RASTER_PDF"):
        assert marker in artifact, f"artifact engine marker missing: {marker}"
    android_bridge = read("artifact/android-webview-bridge.js")
    for marker in ("KefayatAndroid.beginPdf", "KefayatAndroid.appendPdfChunk", "KefayatAndroid.finishPdf", "CHUNK_BYTES"):
        assert marker in android_bridge, f"Android PDF bridge marker missing: {marker}"

    manifest = json.loads(read("manifest.webmanifest"))
    assert manifest.get("lang") == "ar" and manifest.get("dir") == "rtl"
    assert manifest.get("display") == "standalone"

    controller = read("autonomy/controller.py")
    for marker in ("SAFE_STOP", "NO CLAIM", "RECOVER_OR_ESCALATE"):
        assert marker in controller, f"bounded autonomy marker missing: {marker}"

    pages = read(".github/workflows/pages.yml")
    for marker in ("actions/deploy-pages@v4", "Runtime smoke test", "curl --fail", "test_intent_contract_engine.py", "test_pdf_artifact_engine.py", "test_runtime_browser.py"):
        assert marker in pages, f"Pages release gate missing: {marker}"

    production = read(".github/workflows/production-gate.yml")
    for marker in ("Intent Contract + Fulfillment regression", "PDF artifact serializer regression", "Android PDF bridge contract", "browser-runtime", "poppler-utils", "gradle-version: '8.11.1'", "assets/intent/intent-engine.js", "assets/artifact/pdf-artifact-engine.js", "assets/artifact/android-webview-bridge.js"):
        assert marker in production, f"Production gate missing: {marker}"

    signed = read(".github/workflows/android-release.yml")
    for marker in ("gradle-version: '8.11.1'", "artifact/android-webview-bridge.js", "assets/artifact/android-webview-bridge.js", "apksigner"):
        assert marker in signed, f"Signed Android release gate missing: {marker}"

    workflow = read(".github/workflows/autonomy-regression.yml")
    for marker in ("test_go_gate.py", "test_professional_release.py", "test_intent_routing.py", "test_wisdom_governance.py"):
        assert marker in workflow, f"CI gate missing: {marker}"

    combined = "\n".join(read(p) for p in CLAIM_SCAN_FILES)
    hits = [p.pattern for p in FORBIDDEN_PATTERNS if p.search(combined)]
    assert not hits, f"unsupported production claim detected: {hits}"

    print("PROFESSIONAL RELEASE GATE: PASS")
    print("Evidence posture: intent/fulfillment/PDF/Android delivery controls structurally present")
    print("Physical-device, Gemini-runtime, signed-secret availability, and school-field claims remain evidence-scoped")


if __name__ == "__main__":
    main()
