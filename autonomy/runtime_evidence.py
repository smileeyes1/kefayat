#!/usr/bin/env python3
"""Reconcile durable CI-browser evidence into the autonomous mission state.

This module is intentionally narrow: it can promote only claims directly proven
by evidence/runtime-browser-ci.json. Physical-device, Gemini-runtime, field-pilot
and official-source claims remain outside its authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("KEFAYAT_ROOT", str(Path(__file__).resolve().parents[1]))).resolve()
STATE = ROOT / "autonomy" / "mission-state.json"
LEDGER = ROOT / "autonomy" / "evidence-ledger.jsonl"
EVIDENCE = ROOT / "evidence" / "runtime-browser-ci.json"
KB = ROOT / "knowledge" / "competencies.json"

REQUIRED_ASSERTIONS = {
    "desktop_online_runtime": "PASS",
    "desktop_offline_runtime": "PASS",
    "mobile_390px_online_runtime": "PASS",
    "mobile_390px_offline_runtime": "PASS",
    "service_worker_active_desktop": "PASS",
    "service_worker_active_mobile": "PASS",
    "offline_cache_fetch_desktop": "PASS",
    "offline_cache_fetch_mobile": "PASS",
    "rtl_document_direction": "PASS",
    "horizontal_overflow_desktop": "PASS_NONE",
    "horizontal_overflow_mobile": "PASS_NONE",
    "page_errors_desktop": "PASS_NONE",
    "page_errors_mobile": "PASS_NONE",
}
REQUIRED_NOT_PROVEN = {
    "PHYSICAL_DEVICE",
    "GEMINI_RUNTIME",
    "SCHOOL_FIELD_PILOT",
    "OFFICIAL_SOURCE_VERIFICATION",
}
PROVEN_GAPS = {
    "RUNTIME_BROWSER_DEVICE_EVIDENCE",
    "OFFLINE_CACHE_DEVICE_EVIDENCE",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_evidence(data: dict[str, Any], kb_sha256: str) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "KEFAYAT_RUNTIME_BROWSER_EVIDENCE_V1":
        errors.append("SCHEMA")
    if data.get("status") != "PASS_WITH_SCOPED_CLAIM":
        errors.append("STATUS")
    captured = data.get("captured") if isinstance(data.get("captured"), dict) else {}
    if captured.get("scope") != "REAL_CHROMIUM_LOCAL_RELEASE_TREE":
        errors.append("SCOPE")
    if captured.get("decision") != "PASS_BROWSER_RUNTIME_SCOPE":
        errors.append("DECISION")
    if captured.get("competencies_json_sha256") != kb_sha256:
        errors.append("KB_IDENTITY")
    assertions = data.get("verified_assertions") if isinstance(data.get("verified_assertions"), dict) else {}
    for key, expected in REQUIRED_ASSERTIONS.items():
        if assertions.get(key) != expected:
            errors.append(f"ASSERTION:{key}")
    not_proven = set(data.get("explicitly_not_proven") or [])
    if not REQUIRED_NOT_PROVEN.issubset(not_proven):
        errors.append("CLAIM_BOUNDARY")
    source = data.get("source") if isinstance(data.get("source"), dict) else {}
    if source.get("workflow") != "Production Gate" or source.get("job") != "browser-runtime":
        errors.append("PROVENANCE")
    if not source.get("run_id") or not source.get("job_id") or not source.get("head_sha"):
        errors.append("PROVENANCE_IDENTITY")
    return errors


def reconcile(root: Path = ROOT) -> tuple[bool, str]:
    state_path = root / "autonomy" / "mission-state.json"
    ledger_path = root / "autonomy" / "evidence-ledger.jsonl"
    evidence_path = root / "evidence" / "runtime-browser-ci.json"
    kb_path = root / "knowledge" / "competencies.json"

    if not all(path.is_file() for path in (state_path, evidence_path, kb_path)):
        return False, "REQUIRED_FILE_MISSING"

    state = json.loads(state_path.read_text(encoding="utf-8"))
    data = json.loads(evidence_path.read_text(encoding="utf-8"))
    errors = validate_evidence(data, sha256(kb_path))
    if errors:
        return False, "INVALID_EVIDENCE:" + ",".join(errors)

    before = json.dumps(state, sort_keys=True, ensure_ascii=False)
    state["open_gaps"] = [gap for gap in state.get("open_gaps", []) if gap not in PROVEN_GAPS]
    completed = state.setdefault("completed_tasks", [])
    if "CI_BROWSER_RUNTIME_VALIDATED" not in completed:
        completed.append("CI_BROWSER_RUNTIME_VALIDATED")
    identities = state.setdefault("artifact_identities", {})
    identities["runtime-browser-ci.json"] = sha256(evidence_path)
    identities["runtime_browser_source_head"] = data["source"]["head_sha"]
    state["evidence_state"] = "VERIFIED_SOURCE_AND_CI_BROWSER_SCOPE"
    state["claim_state"] = (
        "SOURCE BASELINE AND REAL CHROMIUM CI RUNTIME VERIFIED; "
        "PHYSICAL DEVICE, GEMINI RUNTIME, FIELD PILOT, AND OFFICIAL SOURCE VERIFICATION NOT PROVEN"
    )
    state["release_state"] = "CONTROL_PLANE_READY__CI_BROWSER_PROVEN__PHYSICAL_RUNTIME_FIELD_NOT_PROVEN"
    state["next_best_action"] = "WAIT_FOR_EXTERNAL_EVIDENCE_OR_CONTROL_PLANE_CHANGE"

    after = json.dumps(state, sort_keys=True, ensure_ascii=False)
    if after != before:
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, state_path)
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "mission_id": state.get("mission_id"),
            "test_id": "AUTO-RUNTIME-EVIDENCE-01",
            "expected": "durable browser evidence changes only claims proven by its scope",
            "observed": "CI browser/mobile/offline scope reconciled; external claim boundaries preserved",
            "method": "schema + provenance + SHA256 + explicit assertion checks",
            "decision": "PASS",
        }
        with ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        return True, "UPDATED"
    return True, "NO_CHANGE"


def main() -> int:
    ok, status = reconcile()
    print(json.dumps({"ok": ok, "status": status}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
