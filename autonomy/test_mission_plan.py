#!/usr/bin/env python3
"""Regression tests for the bounded autonomous mission plan."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "autonomy" / "mission-plan.json"
CONTROLLER = ROOT / "autonomy" / "controller.py"
REQUIRED_RUNTIME_FILES = [
    "knowledge/competencies.json",
    "state/verified-state.json",
    "baselines/golden-render/contract.json",
    "governance/verified-baseline-control-plane.md",
    "GEM_KNOWLEDGE_PACK/02_MATH_VISUAL_CONSTITUTION.md",
    "evidence/imported/Ω_GOLDEN_RENDER_TEST_SUITE_v1.0.md",
    "evidence/imported/Ω_RELEASE_EVIDENCE_v4.2.txt",
]


def test_plan_contract() -> None:
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    assert data["mission_id"] == "KEFAYAT-AUTO-001"
    assert data["baseline_id"] == "MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01"
    assert len(data["phases"]) >= 6
    assert len(data["gates"]) >= 6
    assert data["stop_conditions"]


def test_controller_is_plan_aware() -> None:
    text = CONTROLLER.read_text(encoding="utf-8")
    assert 'PLAN = AUTO / "mission-plan.json"' in text
    assert "validate_plan" in text
    assert "VALIDATE_PLAN" in text
    assert "MAX_ACTIONS_PER_RUN" in text


def test_first_autonomous_action_validates_plan_and_run_is_bounded() -> None:
    with tempfile.TemporaryDirectory(prefix="kefayat-plan-test-") as td:
        repo = Path(td)
        (repo / "autonomy").mkdir(parents=True)
        shutil.copy2(PLAN, repo / "autonomy/mission-plan.json")
        shutil.copy2(CONTROLLER, repo / "autonomy/controller.py")
        for rel in REQUIRED_RUNTIME_FILES:
            src = ROOT / rel
            dst = repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        env = os.environ.copy()
        env["KEFAYAT_ROOT"] = str(repo)
        env["PYTHONHASHSEED"] = "0"
        proc = subprocess.run(["python3", str(repo / "autonomy/controller.py")], cwd=repo, text=True, capture_output=True, env=env, check=False)
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        assert result["actions"], result
        assert result["actions"][0] == "VALIDATE_PLAN", result
        assert len(result["actions"]) <= 8, result

        state = json.loads((repo / "autonomy/mission-state.json").read_text(encoding="utf-8"))
        assert "PLAN_VALIDATED" in state["completed_tasks"]
        assert state["status"] == "WAITING_EXTERNAL_EVIDENCE", state


if __name__ == "__main__":
    test_plan_contract()
    test_controller_is_plan_aware()
    test_first_autonomous_action_validates_plan_and_run_is_bounded()
    print("MISSION PLAN REGRESSION: PASS")
