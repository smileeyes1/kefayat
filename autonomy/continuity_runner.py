#!/usr/bin/env python3
"""Resumable, fail-closed execution runner for Kefayat Ω release work.

The runner executes only repository-owned, allow-listed verification stages.
It never fabricates success, never bypasses a failed gate, and persists a
checkpoint so an interrupted run can resume from the first unmet stage.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "autonomy" / "continuity-state.json"
LEDGER = ROOT / "autonomy" / "evidence-ledger.jsonl"

STAGES = [
    ("KNOWLEDGE", [sys.executable, "tools/build_competencies.py"]),
    ("AUTONOMY", [sys.executable, "autonomy/test_controller.py"]),
    ("MISSION_PLAN", [sys.executable, "autonomy/test_mission_plan.py"]),
    ("INTENT_ROUTING", [sys.executable, "autonomy/test_intent_routing.py"]),
    ("WISDOM", [sys.executable, "autonomy/test_wisdom_governance.py"]),
    ("PRODUCTION", [sys.executable, "quality/test_production_contract.py"]),
    ("PROFESSIONAL", [sys.executable, "quality/test_professional_release.py"]),
    ("RELEASE_CONTRACT", [sys.executable, "quality/test_release_contract.py"]),
    ("GO_GATE", [sys.executable, "quality/test_go_gate.py"]),
]


def load() -> dict:
    if not STATE.exists():
        return {"status": "RUNNING", "completed": [], "failed": [], "last_stage": None}
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("state must be an object")
        return data
    except Exception as exc:
        return {"status": "SAFE_STOP", "completed": [], "failed": ["STATE_CORRUPT"], "last_stage": None, "error": str(exc)}


def save(data: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE)


def log(stage: str, expected: str, observed: str, decision: str) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runner": "continuity_runner",
        "stage": stage,
        "expected": expected,
        "observed": observed,
        "decision": decision,
    }
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    state = load()
    if state.get("status") == "SAFE_STOP":
        print(json.dumps({"status": "SAFE_STOP", "reason": state.get("error", "STATE_CORRUPT")}, ensure_ascii=False))
        return 2

    state["status"] = "RUNNING"
    completed = set(state.get("completed", []))

    for stage, command in STAGES:
        if stage in completed:
            continue
        state["last_stage"] = stage
        save(state)
        print(f"==> {stage}", flush=True)
        result = subprocess.run(command, cwd=ROOT, text=True)
        if result.returncode != 0:
            state["status"] = "NO-GO"
            state.setdefault("failed", []).append(stage)
            save(state)
            log(stage, "stage exits 0", f"exit={result.returncode}", "NO-GO")
            print(json.dumps({"status": "NO-GO", "failed_stage": stage}, ensure_ascii=False))
            return result.returncode or 1
        completed.add(stage)
        state["completed"] = list(dict.fromkeys([*state.get("completed", []), stage]))
        state["status"] = "RUNNING"
        save(state)
        log(stage, "stage exits 0", "exit=0", "PASS")

    state["status"] = "ALL_AUTOMATED_GATES_PASS"
    state["last_stage"] = "GO_GATE"
    save(state)
    log("CONTINUITY", "all allow-listed automated gates pass", "all pass", "PASS")
    print(json.dumps({"status": state["status"], "completed": state["completed"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
