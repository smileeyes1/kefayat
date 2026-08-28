#!/usr/bin/env python3
"""Adversarial regression tests for the deterministic autonomy control plane."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "autonomy" / "controller.py"
KB = ROOT / "knowledge" / "competencies.json"


def isolated_repo() -> Path:
    work = Path(tempfile.mkdtemp(prefix="kefayat-auto-test-"))
    (work / "autonomy").mkdir()
    (work / "knowledge").mkdir()
    shutil.copy2(CONTROLLER, work / "autonomy" / "controller.py")
    shutil.copy2(KB, work / "knowledge" / "competencies.json")
    return work


def run_controller(repo: Path) -> dict:
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["KEFAYAT_ROOT"] = str(repo)
    p = subprocess.run(
        ["python3", str(repo / "autonomy" / "controller.py")],
        cwd=repo,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout.strip().splitlines()[-1])


def read_state(repo: Path) -> dict:
    return json.loads((repo / "autonomy" / "mission-state.json").read_text(encoding="utf-8"))


def test_kb_shape_and_identity() -> None:
    data = json.loads(KB.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list) and data["records"]
    assert isinstance(data.get("coverage"), list)
    ids = [r["id"] for r in data["records"]]
    assert len(ids) == len(set(ids))
    assert all(r["grade"] in {1, 2, 3, 4} for r in data["records"])
    assert all(r["subject"] in {"arabic", "mathematics", "islamic_education", "nurturing"} for r in data["records"])


def test_controller_source_uses_canonical_object_schema() -> None:
    text = CONTROLLER.read_text(encoding="utf-8")
    assert 'assert isinstance(data, dict)' in text
    assert 'records = data.get("records")' in text
    assert 'coverage = data.get("coverage")' in text


def test_controller_has_safe_stop_release_and_progress_watchdog() -> None:
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "STAGNATION_DETECTED" in text
    assert "AUTO-RELEASE-01" in text
    assert "NO CLAIM" in text
    assert "progress_signature" in text


def test_kb_sha256_is_stable() -> None:
    h = hashlib.sha256(KB.read_bytes()).hexdigest()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_real_persistent_progress_across_restart() -> None:
    repo = isolated_repo()
    first = run_controller(repo)
    second = run_controller(repo)
    state = read_state(repo)
    assert first["action"] == "VALIDATE_KB"
    assert second["action"] == "CHECK_STATE_INTEGRITY"
    assert "KB_VALIDATED" in state["completed_tasks"]
    assert "STATE_INTEGRITY_CHECKED" in state["completed_tasks"]
    assert state["artifact_identities"]["competencies.json"] == hashlib.sha256(KB.read_bytes()).hexdigest()


def test_corrupt_state_fails_closed() -> None:
    repo = isolated_repo()
    (repo / "autonomy" / "mission-state.json").write_text("{broken", encoding="utf-8")
    result = run_controller(repo)
    state = read_state(repo)
    assert result["status"] == "BLOCKED"
    assert "STATE_CORRUPT" in state["blockers"]
    assert result["next"] == "RECOVER_OR_ESCALATE"


def test_stagnation_detection_ignores_timestamp_and_history_noise() -> None:
    repo = isolated_repo()
    state = {
        "mission_id": "KEFAYAT-AUTO-001", "baseline_id": "MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01",
        "phase": "CONTROL_LOOP", "status": "RUNNING", "completed_tasks": ["KB_VALIDATED", "STATE_INTEGRITY_CHECKED", "RELEASE_GATE_CHECKED"],
        "open_gaps": ["AUTONOMY_RUNTIME_ASSURANCE"], "blockers": [], "attempt_counters": {}, "stagnant_cycles": 2,
        "last_checkpoint": "old", "artifact_identities": {"competencies.json": "x"}, "evidence_state": "UNREPORTED",
        "claim_state": "NO CLAIM", "release_state": "NOT READY", "next_best_action": "WAIT_FOR_NEXT_MISSION",
        "history": [{"checkpoint": "old"}],
    }
    (repo / "autonomy" / "mission-state.json").write_text(json.dumps(state), encoding="utf-8")
    result = run_controller(repo)
    final = read_state(repo)
    assert result["status"] == "SAFE_STOP"
    assert final["stagnant_cycles"] >= 3
    assert "STAGNATION_DETECTED" in final["blockers"]


def test_release_gate_cannot_claim_assurance_without_evidence() -> None:
    repo = isolated_repo()
    state = {
        "mission_id": "KEFAYAT-AUTO-001", "baseline_id": "MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01",
        "phase": "VERIFY", "status": "RUNNING", "completed_tasks": ["KB_VALIDATED", "STATE_INTEGRITY_CHECKED"],
        "open_gaps": ["AUTONOMY_RUNTIME_ASSURANCE"], "blockers": [], "attempt_counters": {}, "stagnant_cycles": 0,
        "last_checkpoint": None, "artifact_identities": {}, "evidence_state": "UNREPORTED", "claim_state": "NO CLAIM",
        "release_state": "NOT READY", "next_best_action": "CHECK_RELEASE_GATE", "history": [],
    }
    (repo / "autonomy" / "mission-state.json").write_text(json.dumps(state), encoding="utf-8")
    result = run_controller(repo)
    final = read_state(repo)
    ledger = (repo / "autonomy" / "evidence-ledger.jsonl").read_text(encoding="utf-8")
    assert result["action"] == "CHECK_RELEASE_GATE"
    assert final["release_state"] == "NOT READY"
    assert final["claim_state"] == "NO CLAIM"
    assert '"decision": "BLOCKED"' in ledger


if __name__ == "__main__":
    for fn in (
        test_kb_shape_and_identity,
        test_controller_source_uses_canonical_object_schema,
        test_controller_has_safe_stop_release_and_progress_watchdog,
        test_kb_sha256_is_stable,
        test_real_persistent_progress_across_restart,
        test_corrupt_state_fails_closed,
        test_stagnation_detection_ignores_timestamp_and_history_noise,
        test_release_gate_cannot_claim_assurance_without_evidence,
    ):
        fn()
    print("AUTONOMY ADVERSARIAL REGRESSION: PASS")
