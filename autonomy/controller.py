#!/usr/bin/env python3
"""Kefayat Ω autonomous control plane.

Deterministic, stdlib-only orchestration. This layer does not call an LLM.
It manages durable state, bounded continuation, evidence records, and a
conservative release gate. It never converts absence of evidence into proof.
"""
from __future__ import annotations
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "autonomy"
STATE = AUTO / "mission-state.json"
LEDGER = AUTO / "evidence-ledger.jsonl"
KB = ROOT / "knowledge" / "competencies.json"
MAX_STAGNANT_CYCLES = 3
ALLOWED_GRADES = {1, 2, 3, 4}
ALLOWED_SUBJECTS = {"arabic", "mathematics", "islamic_education", "nurturing"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def default_state() -> dict[str, Any]:
    return {
        "mission_id": "KEFAYAT-AUTO-001",
        "baseline_id": "MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01",
        "phase": "BOOT",
        "status": "RUNNING",
        "completed_tasks": [],
        "open_gaps": [],
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


def record(state: dict[str, Any], test_id: str, expected: str, observed: str,
           decision: str, method: str) -> None:
    AUTO.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mission_id": state["mission_id"],
        "test_id": test_id,
        "expected": expected,
        "observed": observed,
        "method": method,
        "decision": decision,
    }
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def validate_kb(state: dict[str, Any]) -> bool:
    if not KB.exists():
        state["blockers"] = [x for x in state["blockers"] if x != "KB_MISSING"] + ["KB_MISSING"]
        record(state, "AUTO-KB-01", "canonical KB exists", "missing", "BLOCKED", "filesystem")
        return False
    try:
        data = json.loads(KB.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "KB root must be an object"
        records = data.get("records")
        coverage = data.get("coverage")
        assert isinstance(records, list), "records must be an array"
        assert isinstance(coverage, list), "coverage must be an array"
        ids: set[str] = set()
        for i, r in enumerate(records):
            assert isinstance(r, dict), f"record {i} is not an object"
            for k in ("id", "grade", "subject", "provenance", "source_text"):
                assert k in r, f"record {i} missing {k}"
            assert r["id"] not in ids, f"duplicate id: {r['id']}"
            ids.add(r["id"])
            assert r["grade"] in ALLOWED_GRADES, f"bad grade: {r['grade']}"
            assert r["subject"] in ALLOWED_SUBJECTS, f"bad subject: {r['subject']}"
            assert isinstance(r["source_text"], str) and r["source_text"].strip(), f"empty source_text: {r['id']}"
            assert isinstance(r["provenance"], dict) and r["provenance"].get("status"), f"bad provenance: {r['id']}"
        assert records, "no competency records generated"
        state["artifact_identities"]["competencies.json"] = digest(KB)
        record(state, "AUTO-KB-01", "valid canonical competency records", f"{len(records)} records; {len(coverage)} coverage entries", "PASS", "stdlib JSON + invariant checks")
        return True
    except Exception as e:
        state["blockers"] = [x for x in state["blockers"] if not x.startswith("KB_INVALID:")] + [f"KB_INVALID:{type(e).__name__}"]
        record(state, "AUTO-KB-01", "valid canonical competency records", str(e), "NO-GO", "stdlib invariant checks")
        return False


def check_state_integrity(state: dict[str, Any]) -> bool:
    required = ("mission_id", "baseline_id", "phase", "status", "completed_tasks",
                "blockers", "next_best_action", "artifact_identities", "evidence_state",
                "claim_state", "release_state")
    missing = [k for k in required if k not in state]
    if missing:
        record(state, "AUTO-STATE-01", "required durable state", str(missing), "BLOCKED", "schema invariant check")
        return False
    record(state, "AUTO-STATE-01", "required durable state", "complete", "PASS", "schema invariant check")
    return True


def choose_next(state: dict[str, Any]) -> str:
    if state.get("status") in {"BLOCKED", "SAFE_STOP", "NO-GO"}:
        return "RECOVER_OR_ESCALATE"
    if "KB_VALIDATED" not in state["completed_tasks"]:
        return "VALIDATE_KB"
    if "STATE_INTEGRITY_CHECKED" not in state["completed_tasks"]:
        return "CHECK_STATE_INTEGRITY"
    if "RELEASE_GATE_CHECKED" not in state["completed_tasks"]:
        return "CHECK_RELEASE_GATE"
    return "WAIT_FOR_NEXT_MISSION"


def main() -> int:
    state = load_state()
    state["phase"] = "CONTROL_LOOP"
    if state.get("status") not in {"BLOCKED", "SAFE_STOP", "NO-GO"}:
        state["status"] = "RUNNING"

    before = json.dumps(state, sort_keys=True, ensure_ascii=False)
    action = choose_next(state)
    state["next_best_action"] = action

    if action == "VALIDATE_KB":
        if validate_kb(state):
            if "KB_VALIDATED" not in state["completed_tasks"]:
                state["completed_tasks"].append("KB_VALIDATED")
            state["phase"] = "VERIFY"
        else:
            state["status"] = "BLOCKED"
    elif action == "CHECK_STATE_INTEGRITY":
        if check_state_integrity(state):
            if "STATE_INTEGRITY_CHECKED" not in state["completed_tasks"]:
                state["completed_tasks"].append("STATE_INTEGRITY_CHECKED")
        else:
            state["status"] = "BLOCKED"
    elif action == "CHECK_RELEASE_GATE":
        state["release_state"] = "NOT READY"
        state["claim_state"] = "NO CLAIM"
        record(state, "AUTO-RELEASE-01", "release gates proven", "autonomous runtime assurance not yet proven", "BLOCKED", "claim-scope gate")
        if "RELEASE_GATE_CHECKED" not in state["completed_tasks"]:
            state["completed_tasks"].append("RELEASE_GATE_CHECKED")
    elif action == "RECOVER_OR_ESCALATE":
        record(state, "AUTO-RECOVERY-01", "safe recovery or explicit escalation", state.get("status", "UNKNOWN"), "BLOCKED", "conservative recovery gate")

    after = json.dumps(state, sort_keys=True, ensure_ascii=False)
    if before == after:
        state["stagnant_cycles"] = int(state.get("stagnant_cycles", 0)) + 1
    else:
        state["stagnant_cycles"] = 0

    if state["stagnant_cycles"] >= MAX_STAGNANT_CYCLES and state["status"] == "RUNNING":
        state["status"] = "SAFE_STOP"
        state["blockers"] = [x for x in state["blockers"] if x != "STAGNATION_DETECTED"] + ["STAGNATION_DETECTED"]
        record(state, "AUTO-WATCHDOG-01", "progress or bounded stop", "stagnation", "SAFE_STOP", "progress watchdog")

    state["last_checkpoint"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state["history"].append({"action": action, "status": state["status"], "checkpoint": state["last_checkpoint"]})
    save_state(state)
    print(json.dumps({"mission_id": state["mission_id"], "action": action,
                      "status": state["status"], "next": choose_next(state)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
