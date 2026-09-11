#!/usr/bin/env python3
"""Adversarial tests for scoped runtime-evidence reconciliation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "autonomy" / "runtime_evidence.py"

spec = importlib.util.spec_from_file_location("runtime_evidence", MODULE_PATH)
assert spec and spec.loader
runtime_evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime_evidence)


def isolated_repo() -> Path:
    work = Path(tempfile.mkdtemp(prefix="kefayat-runtime-evidence-"))
    for rel in (
        "autonomy/mission-state.json",
        "evidence/runtime-browser-ci.json",
        "knowledge/competencies.json",
    ):
        src = ROOT / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return work


def read_state(repo: Path) -> dict:
    return json.loads((repo / "autonomy/mission-state.json").read_text(encoding="utf-8"))


def test_valid_evidence_promotes_only_scoped_claims() -> None:
    repo = isolated_repo()
    ok, status = runtime_evidence.reconcile(repo)
    assert ok and status in {"UPDATED", "NO_CHANGE"}, (ok, status)
    state = read_state(repo)
    assert "CI_BROWSER_RUNTIME_VALIDATED" in state["completed_tasks"], state
    assert "RUNTIME_BROWSER_DEVICE_EVIDENCE" not in state["open_gaps"], state
    assert "OFFLINE_CACHE_DEVICE_EVIDENCE" not in state["open_gaps"], state
    assert "FIELD_PILOT_EVIDENCE" in state["open_gaps"], state
    assert "OFFICIAL_SOURCE_VERIFICATION" in state["open_gaps"], state
    assert "NOT PROVEN" in state["claim_state"], state
    assert state["evidence_state"] == "VERIFIED_SOURCE_AND_CI_BROWSER_SCOPE", state
    assert state["release_state"] == "CONTROL_PLANE_READY__CI_BROWSER_PROVEN__PHYSICAL_RUNTIME_FIELD_NOT_PROVEN", state


def test_kb_identity_mismatch_fails_closed() -> None:
    repo = isolated_repo()
    evidence_path = repo / "evidence/runtime-browser-ci.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["captured"]["competencies_json_sha256"] = "0" * 64
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = read_state(repo)
    ok, status = runtime_evidence.reconcile(repo)
    after = read_state(repo)
    assert not ok and "KB_IDENTITY" in status, status
    assert before == after, (before, after)


def test_missing_claim_boundary_fails_closed() -> None:
    repo = isolated_repo()
    evidence_path = repo / "evidence/runtime-browser-ci.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["explicitly_not_proven"] = [
        item for item in evidence["explicitly_not_proven"] if item != "PHYSICAL_DEVICE"
    ]
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = read_state(repo)
    ok, status = runtime_evidence.reconcile(repo)
    after = read_state(repo)
    assert not ok and "CLAIM_BOUNDARY" in status, status
    assert before == after, (before, after)


def test_assertion_regression_fails_closed() -> None:
    repo = isolated_repo()
    evidence_path = repo / "evidence/runtime-browser-ci.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["verified_assertions"]["mobile_390px_offline_runtime"] = "FAIL"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    before = read_state(repo)
    ok, status = runtime_evidence.reconcile(repo)
    after = read_state(repo)
    assert not ok and "ASSERTION:mobile_390px_offline_runtime" in status, status
    assert before == after, (before, after)


if __name__ == "__main__":
    for fn in (
        test_valid_evidence_promotes_only_scoped_claims,
        test_kb_identity_mismatch_fails_closed,
        test_missing_claim_boundary_fails_closed,
        test_assertion_regression_fails_closed,
    ):
        fn()
    print("RUNTIME EVIDENCE ADVERSARIAL REGRESSION: PASS")
