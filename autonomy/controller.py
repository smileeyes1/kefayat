#!/usr/bin/env python3
"""Kefayat autonomous control plane.

Pure-stdlib, deterministic orchestration layer. It does not call an LLM and
therefore cannot manufacture evidence. It manages safe continuation,
checkpoints, bounded retries, stagnation detection, and release gating.
"""
from __future__ import annotations
import hashlib, json, os, time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "autonomy" / "mission-state.json"
LEDGER = ROOT / "autonomy" / "evidence-ledger.jsonl"
KB = ROOT / "knowledge" / "competencies.json"

MAX_RETRIES = 3
MAX_STAGNANT_CYCLES = 3


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE.exists():
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
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, STATE)


def record(state: dict[str, Any], test_id: str, expected: str, observed: str, decision: str, method: str) -> None:
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
        state["blockers"].append("KB_MISSING")
        record(state, "AUTO-KB-01", "KB exists and is valid JSON", "missing", "BLOCKED", "filesystem")
        return False
    try:
        data = json.loads(KB.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert data, "empty knowledge base"
        ids = set()
        for r in data:
            assert isinstance(r, dict)
            for k in ("id", "grade", "subject", "provenance", "source_text"):
                assert k in r
            assert r["id"] not in ids
            ids.add(r["id"])
            assert r["grade"] in (1,2,3,4)
            assert r["subject"] in ("arabic","mathematics","islamic_education","nurturing")
            assert isinstance(r["source_text"], str) and r["source_text"].strip()
            assert isinstance(r["provenance"], dict) and "status" in r["provenance"]
        state["artifact_identities"]["competencies.json"] = digest(KB)
        record(state, "AUTO-KB-01", "valid non-empty competency records", f"{len(data)} valid records", "PASS", "stdlib JSON + invariant checks")
        return True
    except Exception as e:
        state["blockers"].append(f"KB_INVALID:{type(e).__name__}")
        record(state, "AUTO-KB-01", "valid competency records", str(e), "NO-GO", "stdlib invariant checks")
        return False


def choose_next(state: dict[str, Any]) -> str:
    if state["blockers"]:
        return "DIAGNOSE_BLOCKER"
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
    state["status"] = "RUNNING"
    before = json.dumps(state, sort_keys=True, ensure_ascii=False)
    action = choose_next(state)
    state["next_best_action"] = action

    if action == "VALIDATE_KB":
        if validate_kb(state):
            state["completed_tasks"].append("KB_VALIDATED")
            state["phase"] = "VERIFY"
        else:
            state["status"] = "BLOCKED"
    elif action == "CHECK_STATE_INTEGRITY":
        required = ["mission_id","baseline_id","phase","status","completed_tasks","blockers","next_best_action"]
        missing = [k for k in required if k not in state]
        if missing:
            state["blockers"].append("STATE_MISSING:" + ",".join(missing))
            state["status"] = "BLOCKED"
            record(state, "AUTO-STATE-01", "required durable state", str(missing), "BLOCKED", "schema invariant check")
        else:
            state["completed_tasks"].append("STATE_INTEGRITY_CHECKED")
            record(state, "AUTO-STATE-01", "required durable state", "complete", "PASS", "schema invariant check")
    elif action == "CHECK_RELEASE_GATE":
        # Deliberately conservative: the autonomous controller does not claim
        # release merely because structural checks pass.
        state["release_state"] = "NOT READY"
        record(state, "AUTO-RELEASE-01", "all applicable release gates", "autonomous runtime assurance not yet proven", "BLOCKED", "claim-scope gate")
        state["completed_tasks"].append("RELEASE_GATE_CHECKED")
    else:
        state["status"] = "IDLE"

    after = json.dumps(state, sort_keys=True, ensure_ascii=False)
    if before == after:
        state["stagnant_cycles"] += 1
    else:
        state["stagnant_cycles"] = 0

    if state["stagnant_cycles"] >= MAX_STAGNANT_CYCLES and state["status"] == "RUNNING":
        state["status"] = "SAFE_STOP"
        state["blockers"].append("STAGNATION_DETECTED")
        record(state, "AUTO-WATCHDOG-01", "progress or bounded stop", "stagnation", "SAFE_STOP", "progress watchdog")

    state["last_checkpoint"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state["history"].append({"action": action, "status": state["status"], "checkpoint": state["last_checkpoint"]})
    save_state(state)
    print(json.dumps({"mission_id": state["mission_id"], "action": action, "status": state["status"], "next": choose_next(state)}, ensure_ascii=False))
    return 0 if state["status"] not in ("NO-GO",) else 2

if __name__ == "__main__":
    raise SystemExit(main())
