#!/usr/bin/env python3
"""Behavioral adversarial regression for the Kefayat Ω control plane."""
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
PLAN = ROOT / "autonomy" / "mission-plan.json"
EXTRA = [
    "state/verified-state.json",
    "baselines/golden-render/contract.json",
    "governance/verified-baseline-control-plane.md",
    "GEM_KNOWLEDGE_PACK/02_MATH_VISUAL_CONSTITUTION.md",
    "evidence/imported/Ω_GOLDEN_RENDER_TEST_SUITE_v1.0.md",
    "evidence/imported/Ω_RELEASE_EVIDENCE_v4.2.txt",
]


def isolated_repo() -> Path:
    work = Path(tempfile.mkdtemp(prefix="kefayat-auto-test-"))
    (work / "autonomy").mkdir(parents=True)
    (work / "knowledge").mkdir(parents=True)
    shutil.copy2(CONTROLLER, work / "autonomy/controller.py")
    shutil.copy2(KB, work / "knowledge/competencies.json")
    shutil.copy2(PLAN, work / "autonomy/mission-plan.json")
    for rel in EXTRA:
        src = ROOT / rel
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return work


def run_controller(repo: Path) -> dict:
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["KEFAYAT_ROOT"] = str(repo)
    proc = subprocess.run(["python3", str(repo / "autonomy/controller.py")], cwd=repo, text=True, capture_output=True, env=env, check=False)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def read_state(repo: Path) -> dict:
    return json.loads((repo / "autonomy/mission-state.json").read_text(encoding="utf-8"))


def write_state(repo: Path, state: dict) -> None:
    (repo / "autonomy/mission-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bootstrap_fully(repo: Path) -> tuple[dict, dict]:
    result = run_controller(repo)
    state = read_state(repo)
    expected = {"VALIDATE_PLAN", "VALIDATE_KB", "CHECK_STATE_INTEGRITY", "VALIDATE_BASELINE_CONTROL_PLANE", "CHECK_RELEASE_GATE"}
    assert expected.issubset(set(result["actions"])), result
    assert state["status"] == "WAITING_EXTERNAL_EVIDENCE", state
    assert state["next_best_action"] == "WAIT_FOR_EXTERNAL_EVIDENCE_OR_CONTROL_PLANE_CHANGE", state
    assert "BASELINE_CONTROL_PLANE_VALIDATED" in state["completed_tasks"], state
    assert "RELEASE_GATE_CHECKED" in state["completed_tasks"], state
    assert state["artifact_identities"].get("control_plane_fingerprint"), state
    return result, state


def test_kb_shape_and_identity() -> None:
    data = json.loads(KB.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and data.get("records") and isinstance(data.get("coverage"), list)
    ids = [record["id"] for record in data["records"]]
    assert len(ids) == len(set(ids))
    assert all(record["grade"] in {1, 2, 3, 4} for record in data["records"])
    assert all(record["subject"] in {"arabic", "mathematics", "islamic_education", "nurturing"} for record in data["records"])


def test_single_run_drains_internal_work() -> None:
    repo = isolated_repo()
    result, state = bootstrap_fully(repo)
    assert result["action"] == "CHECK_RELEASE_GATE", result
    assert state["artifact_identities"].get("competencies.json") == sha256(repo / "knowledge/competencies.json"), state
    assert state["evidence_state"] == "VERIFIED_SOURCE_SCOPE", state
    assert state["release_state"] == "CONTROL_PLANE_READY__EXTERNAL_RUNTIME_FIELD_NOT_PROVEN", state
    assert "GEMINI RUNTIME AND FIELD ASSURANCE NOT PROVEN" in state["claim_state"], state


def test_wait_state_has_no_checkpoint_churn() -> None:
    repo = isolated_repo()
    bootstrap_fully(repo)
    before = sha256(repo / "autonomy/mission-state.json")
    result = run_controller(repo)
    after = sha256(repo / "autonomy/mission-state.json")
    assert result["action"] == "IDLE_WAITING_EXTERNAL_EVIDENCE", result
    assert result["actions"] == [], result
    assert before == after, (before, after)


def test_corrupt_state_fails_closed() -> None:
    repo = isolated_repo()
    (repo / "autonomy/mission-state.json").write_text("{broken", encoding="utf-8")
    result = run_controller(repo)
    state = read_state(repo)
    assert result["status"] == "BLOCKED", result
    assert "STATE_CORRUPT" in state["blockers"], state
    assert result["next"] == "RECOVER_OR_ESCALATE", result


def test_control_plane_change_requalifies_in_same_run() -> None:
    repo = isolated_repo()
    _, state = bootstrap_fully(repo)
    state["artifact_identities"]["control_plane_fingerprint"] = "0" * 64
    state["status"] = "WAITING_EXTERNAL_EVIDENCE"
    write_state(repo, state)
    result = run_controller(repo)
    final = read_state(repo)
    assert "VALIDATE_BASELINE_CONTROL_PLANE" in result["actions"], result
    assert "CHECK_RELEASE_GATE" in result["actions"], result
    assert final["status"] == "WAITING_EXTERNAL_EVIDENCE", final
    assert final["artifact_identities"]["control_plane_fingerprint"] != "0" * 64, final
    ledger = (repo / "autonomy/evidence-ledger.jsonl").read_text(encoding="utf-8")
    assert "AUTO-RECOVERY-BASELINE-01" in ledger, ledger


def test_release_gate_preserves_truthful_claim_scope() -> None:
    repo = isolated_repo()
    _, state = bootstrap_fully(repo)
    ledger = (repo / "autonomy/evidence-ledger.jsonl").read_text(encoding="utf-8")
    assert state["release_state"] == "CONTROL_PLANE_READY__EXTERNAL_RUNTIME_FIELD_NOT_PROVEN"
    assert "SOURCE BASELINE VERIFIED" in state["claim_state"]
    assert "NOT PROVEN" in state["claim_state"]
    assert '"test_id": "AUTO-RELEASE-01"' in ledger
    assert '"decision": "BLOCKED"' in ledger


def test_controller_controls_exist() -> None:
    text = CONTROLLER.read_text(encoding="utf-8")
    for needle in (
        "MAX_ACTIONS_PER_RUN",
        "WAITING_EXTERNAL_EVIDENCE",
        "AUTO-RELEASE-01",
        "AUTO-RECOVERY-BASELINE-01",
        "ACTION_BUDGET_EXHAUSTED",
        "IDLE_WAITING_EXTERNAL_EVIDENCE",
        "R = B + A" if False else "VALIDATE_BASELINE_CONTROL_PLANE",
    ):
        assert needle in text, needle


def test_kb_sha256_is_stable() -> None:
    value = sha256(KB)
    assert len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


if __name__ == "__main__":
    for fn in (
        test_kb_shape_and_identity,
        test_single_run_drains_internal_work,
        test_wait_state_has_no_checkpoint_churn,
        test_corrupt_state_fails_closed,
        test_control_plane_change_requalifies_in_same_run,
        test_release_gate_preserves_truthful_claim_scope,
        test_controller_controls_exist,
        test_kb_sha256_is_stable,
    ):
        fn()
    print("AUTONOMY ADVERSARIAL REGRESSION: PASS")
