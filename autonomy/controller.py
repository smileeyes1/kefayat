#!/usr/bin/env python3
"""Kefayat Ω bounded autonomous control plane.

The controller is deliberately event-driven and fail-closed. A single run drains
all immediately executable, allow-listed control-plane actions instead of
waiting for one scheduler tick per action. When only external evidence remains,
it enters a durable WAITING_EXTERNAL_EVIDENCE state without checkpoint churn.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("KEFAYAT_ROOT", str(Path(__file__).resolve().parents[1]))).resolve()
AUTO = ROOT / "autonomy"
STATE = AUTO / "mission-state.json"
LEDGER = AUTO / "evidence-ledger.jsonl"
PLAN = AUTO / "mission-plan.json"
KB = ROOT / "knowledge" / "competencies.json"
VERIFIED_STATE = ROOT / "state" / "verified-state.json"
GOLDEN = ROOT / "baselines" / "golden-render" / "contract.json"
AUTH = ROOT / "governance" / "verified-baseline-control-plane.md"
MATH = ROOT / "GEM_KNOWLEDGE_PACK" / "02_MATH_VISUAL_CONSTITUTION.md"
GOLDEN_EVIDENCE = ROOT / "evidence" / "imported" / "Ω_GOLDEN_RENDER_TEST_SUITE_v1.0.md"
RELEASE_EVIDENCE = ROOT / "evidence" / "imported" / "Ω_RELEASE_EVIDENCE_v4.2.txt"

MAX_ACTIONS_PER_RUN = 8
ALLOWED_GRADES = {1, 2, 3, 4}
ALLOWED_SUBJECTS = {"arabic", "mathematics", "islamic_education", "nurturing"}
TERMINAL_FAILURES = {"BLOCKED", "SAFE_STOP", "NO-GO"}
WAITING = "WAITING_EXTERNAL_EVIDENCE"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def control_plane_fingerprint() -> str:
    paths = (AUTH, VERIFIED_STATE, GOLDEN, MATH, GOLDEN_EVIDENCE, RELEASE_EVIDENCE)
    if not all(path.is_file() for path in paths):
        return ""
    h = hashlib.sha256()
    for path in paths:
        rel = str(path.relative_to(ROOT)).encode("utf-8")
        h.update(len(rel).to_bytes(4, "big"))
        h.update(rel)
        h.update(bytes.fromhex(digest(path)))
    return h.hexdigest()


def default_state() -> dict[str, Any]:
    return {
        "mission_id": "KEFAYAT-AUTO-001",
        "baseline_id": "MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01",
        "phase": "BOOT",
        "status": "RUNNING",
        "completed_tasks": [],
        "open_gaps": [
            "FULL_AUTONOMOUS_DEVELOPMENT",
            "REAL_MISSION_PILOT",
            "GEMINI_RUNTIME_ACCEPTANCE",
        ],
        "blockers": [],
        "attempt_counters": {},
        "stagnant_cycles": 0,
        "last_checkpoint": None,
        "artifact_identities": {},
        "evidence_state": "UNREPORTED",
        "claim_state": "NO CLAIM",
        "release_state": "NOT READY",
        "next_best_action": "BOOTSTRAP",
        "history": [],
    }


def load_state() -> dict[str, Any]:
    if not STATE.exists():
        return default_state()
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        assert isinstance(state, dict)
        return state
    except Exception:
        state = default_state()
        state["status"] = "BLOCKED"
        state["blockers"] = ["STATE_CORRUPT"]
        return state


def save_state(state: dict[str, Any]) -> None:
    AUTO.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, STATE)


def record(state: dict[str, Any], test_id: str, expected: str, observed: str, decision: str, method: str) -> None:
    AUTO.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mission_id": state["mission_id"],
        "test_id": test_id,
        "expected": expected,
        "observed": observed,
        "method": method,
        "decision": decision,
    }
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def validate_plan(state: dict[str, Any]) -> bool:
    try:
        data = json.loads(PLAN.read_text(encoding="utf-8"))
        assert data["mission_id"] == state["mission_id"]
        assert data["baseline_id"] == state["baseline_id"]
        assert isinstance(data["phases"], list) and len(data["phases"]) >= 6
        assert isinstance(data["gates"], dict) and len(data["gates"]) >= 6
        assert data["stop_conditions"]
        record(state, "AUTO-PLAN-01", "bounded mission plan is valid", "valid", "PASS", "JSON + invariant checks")
        return True
    except Exception as exc:
        state["blockers"] = [x for x in state["blockers"] if not x.startswith("PLAN_INVALID")]
        state["blockers"].append(f"PLAN_INVALID:{type(exc).__name__}")
        record(state, "AUTO-PLAN-01", "bounded mission plan is valid", str(exc), "NO-GO", "mission-plan invariant checks")
        return False


def validate_kb(state: dict[str, Any]) -> bool:
    if not KB.exists():
        record(state, "AUTO-KB-01", "canonical KB exists", "missing", "BLOCKED", "filesystem")
        append_once(state["blockers"], "KB_MISSING")
        return False
    try:
        data = json.loads(KB.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        records, coverage = data.get("records"), data.get("coverage")
        assert isinstance(records, list) and isinstance(coverage, list) and records
        ids: set[str] = set()
        for item in records:
            assert isinstance(item, dict)
            for key in ("id", "grade", "subject", "provenance", "source_text"):
                assert key in item
            assert item["id"] not in ids
            ids.add(item["id"])
            assert item["grade"] in ALLOWED_GRADES
            assert item["subject"] in ALLOWED_SUBJECTS
            assert isinstance(item["source_text"], str) and item["source_text"].strip()
            assert isinstance(item["provenance"], dict) and item["provenance"].get("status")
        state["artifact_identities"]["competencies.json"] = digest(KB)
        record(state, "AUTO-KB-01", "valid canonical competency records", f"{len(records)} records; {len(coverage)} coverage entries", "PASS", "JSON + invariants")
        return True
    except Exception as exc:
        record(state, "AUTO-KB-01", "valid canonical competency records", str(exc), "NO-GO", "invariant checks")
        return False


def check_state(state: dict[str, Any]) -> bool:
    required = (
        "mission_id", "baseline_id", "phase", "status", "completed_tasks", "blockers",
        "next_best_action", "artifact_identities", "evidence_state", "claim_state", "release_state",
    )
    missing = [key for key in required if key not in state]
    record(state, "AUTO-STATE-01", "required durable state", "complete" if not missing else str(missing), "PASS" if not missing else "BLOCKED", "schema invariant check")
    return not missing


def validate_verified_baseline(state: dict[str, Any]) -> bool:
    try:
        verified = json.loads(VERIFIED_STATE.read_text(encoding="utf-8"))
        contract = json.loads(GOLDEN.read_text(encoding="utf-8"))
        authority = AUTH.read_text(encoding="utf-8")
        math = MATH.read_text(encoding="utf-8")
        assert contract["severity"] == "P0" and contract["status"] == "PROTECTED"
        assert contract["semantic_pattern"] == "A + B = R"
        assert contract["engine_pattern"] == "R = B + A"
        assert contract["operand_identity_immutable"] is True
        assert contract["commutativity_allows_swap"] is False
        assert contract["rtl_bidi_is_authority"] is False
        g01 = contract["fixtures"][0]
        assert g01["engine"] == "□ = ٣ + ٤"
        assert g01["student_eye"] == "٤ + ٣ = □"
        assert verified["golden_render"]["gemini_runtime_acceptance"] == "NOT_PROVEN"
        assert digest(GOLDEN_EVIDENCE) == verified["golden_render"]["source_suite_sha256"]
        assert digest(RELEASE_EVIDENCE) == verified["golden_render"]["release_evidence_sha256"]
        assert "student-eye `٤ + ٣ = □`" in authority
        assert "engine request `□ = ٣ + ٤`" in authority
        assert "TARGET/USER-EYE: ٤ + ٣ = □" in math
        assert "ENGINE REQUEST: □ = ٣ + ٤" in math
        fingerprint = control_plane_fingerprint()
        assert fingerprint
        state["artifact_identities"]["control_plane_fingerprint"] = fingerprint
        state["evidence_state"] = "VERIFIED_SOURCE_SCOPE"
        record(state, "AUTO-BASELINE-01", "protected baseline and imported evidence are internally consistent", f"fingerprint={fingerprint}", "PASS", "JSON + SHA256 + invariant checks")
        return True
    except Exception as exc:
        state["blockers"] = [x for x in state["blockers"] if not x.startswith("BASELINE_INVALID")]
        state["blockers"].append(f"BASELINE_INVALID:{type(exc).__name__}")
        record(state, "AUTO-BASELINE-01", "protected baseline and imported evidence are internally consistent", str(exc), "NO-GO", "verified-baseline invariant checks")
        return False


def recover_on_control_plane_change(state: dict[str, Any]) -> bool:
    current = control_plane_fingerprint()
    previous = state.get("artifact_identities", {}).get("control_plane_fingerprint")
    if not current or not previous or current == previous:
        return False
    state["status"] = "RUNNING"
    state["blockers"] = [x for x in state.get("blockers", []) if x != "STAGNATION_DETECTED"]
    state["stagnant_cycles"] = 0
    state["completed_tasks"] = [
        x for x in state.get("completed_tasks", [])
        if x not in {"BASELINE_CONTROL_PLANE_VALIDATED", "RELEASE_GATE_CHECKED"}
    ]
    state["next_best_action"] = "VALIDATE_BASELINE_CONTROL_PLANE"
    record(state, "AUTO-RECOVERY-BASELINE-01", "changed authority reopens qualification", "control-plane fingerprint changed", "PASS", "fingerprint-triggered recovery")
    return True


def choose_next(state: dict[str, Any]) -> str:
    if state.get("status") in TERMINAL_FAILURES:
        return "RECOVER_OR_ESCALATE"
    completed = state["completed_tasks"]
    if "PLAN_VALIDATED" not in completed:
        return "VALIDATE_PLAN"
    if "KB_VALIDATED" not in completed:
        return "VALIDATE_KB"
    if "STATE_INTEGRITY_CHECKED" not in completed:
        return "CHECK_STATE_INTEGRITY"
    if "BASELINE_CONTROL_PLANE_VALIDATED" not in completed:
        return "VALIDATE_BASELINE_CONTROL_PLANE"
    if "RELEASE_GATE_CHECKED" not in completed:
        return "CHECK_RELEASE_GATE"
    if state.get("open_gaps") or state.get("blockers"):
        return "WAIT_FOR_EXTERNAL_EVIDENCE"
    return "WAIT_FOR_NEXT_MISSION"


def execute_action(state: dict[str, Any], action: str) -> bool:
    if action == "VALIDATE_PLAN":
        if validate_plan(state):
            append_once(state["completed_tasks"], "PLAN_VALIDATED")
            return True
        state["status"] = "NO-GO"
        return False
    if action == "VALIDATE_KB":
        if validate_kb(state):
            append_once(state["completed_tasks"], "KB_VALIDATED")
            state["phase"] = "VERIFY"
            return True
        state["status"] = "BLOCKED"
        return False
    if action == "CHECK_STATE_INTEGRITY":
        if check_state(state):
            append_once(state["completed_tasks"], "STATE_INTEGRITY_CHECKED")
            return True
        state["status"] = "BLOCKED"
        return False
    if action == "VALIDATE_BASELINE_CONTROL_PLANE":
        if validate_verified_baseline(state):
            append_once(state["completed_tasks"], "BASELINE_CONTROL_PLANE_VALIDATED")
            return True
        state["status"] = "NO-GO"
        return False
    if action == "CHECK_RELEASE_GATE":
        state["release_state"] = "CONTROL_PLANE_READY__EXTERNAL_RUNTIME_FIELD_NOT_PROVEN"
        state["claim_state"] = "SOURCE BASELINE VERIFIED; GEMINI RUNTIME AND FIELD ASSURANCE NOT PROVEN"
        record(state, "AUTO-RELEASE-01", "external runtime/field claims require direct evidence", "source baseline verified; external runtime and field assurance remain NOT_PROVEN", "BLOCKED", "claim-scope gate")
        append_once(state["completed_tasks"], "RELEASE_GATE_CHECKED")
        return True
    return False


def state_signature(state: dict[str, Any]) -> str:
    keys = (
        "phase", "status", "completed_tasks", "open_gaps", "blockers", "attempt_counters",
        "artifact_identities", "evidence_state", "claim_state", "release_state", "next_best_action",
    )
    return json.dumps({key: state.get(key) for key in keys}, sort_keys=True, ensure_ascii=False)


def main() -> int:
    state = load_state()
    recovered = recover_on_control_plane_change(state)

    if state.get("status") == "SAFE_STOP" and not recovered:
        print(json.dumps({"mission_id": state["mission_id"], "action": "IDLE_SAFE_STOP", "actions": [], "status": "SAFE_STOP", "next": "WAIT_FOR_CONTROL_PLANE_CHANGE"}, ensure_ascii=False))
        return 0

    if state.get("status") == WAITING and not recovered:
        print(json.dumps({"mission_id": state["mission_id"], "action": "IDLE_WAITING_EXTERNAL_EVIDENCE", "actions": [], "status": WAITING, "next": "WAIT_FOR_EXTERNAL_EVIDENCE_OR_CONTROL_PLANE_CHANGE"}, ensure_ascii=False))
        return 0

    state["phase"] = "CONTROL_LOOP"
    if state.get("status") not in TERMINAL_FAILURES:
        state["status"] = "RUNNING"

    before = state_signature(state)
    actions: list[str] = []

    for _ in range(MAX_ACTIONS_PER_RUN):
        action = choose_next(state)
        if action in {"WAIT_FOR_EXTERNAL_EVIDENCE", "WAIT_FOR_NEXT_MISSION"}:
            if action == "WAIT_FOR_EXTERNAL_EVIDENCE":
                if state.get("status") != WAITING:
                    record(state, "AUTO-WAIT-01", "preserve truthful claim scope while external evidence is unavailable", ";".join(state.get("open_gaps", [])) or "external dependency", "WAIT", "event-driven wait state")
                state["status"] = WAITING
                state["next_best_action"] = "WAIT_FOR_EXTERNAL_EVIDENCE_OR_CONTROL_PLANE_CHANGE"
            else:
                state["status"] = "READY"
                state["next_best_action"] = "WAIT_FOR_NEXT_MISSION"
            break
        if action == "RECOVER_OR_ESCALATE":
            record(state, "AUTO-RECOVERY-01", "safe recovery or explicit escalation", state.get("status", "UNKNOWN"), "BLOCKED", "conservative recovery gate")
            state["next_best_action"] = action
            break

        actions.append(action)
        ok = execute_action(state, action)
        state["history"].append({"action": action, "status": state["status"], "checkpoint": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        if not ok:
            state["next_best_action"] = choose_next(state)
            break
    else:
        state["status"] = "SAFE_STOP"
        append_once(state["blockers"], "ACTION_BUDGET_EXHAUSTED")
        state["next_best_action"] = "RECOVER_OR_ESCALATE"
        record(state, "AUTO-WATCHDOG-01", "bounded progress within action budget", f"{MAX_ACTIONS_PER_RUN} actions exhausted", "SAFE_STOP", "action-budget watchdog")

    if state.get("status") not in {WAITING, "READY"} and state.get("next_best_action") not in {"RECOVER_OR_ESCALATE"}:
        state["next_best_action"] = choose_next(state)

    after = state_signature(state)
    if before == after and not actions:
        state["stagnant_cycles"] = int(state.get("stagnant_cycles", 0)) + 1
    else:
        state["stagnant_cycles"] = 0

    state["last_checkpoint"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_state(state)

    last_action = actions[-1] if actions else ("WAIT_FOR_EXTERNAL_EVIDENCE" if state.get("status") == WAITING else state.get("next_best_action", "NONE"))
    print(json.dumps({"mission_id": state["mission_id"], "action": last_action, "actions": actions, "status": state["status"], "next": state["next_best_action"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
