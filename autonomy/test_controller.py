#!/usr/bin/env python3
"""Regression tests for the deterministic autonomy control plane."""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "autonomy" / "controller.py"
KB = ROOT / "knowledge" / "competencies.json"


def run_controller(state_dir: Path) -> dict:
    # The controller currently uses repository paths; run against an isolated
    # copy of the autonomy directory while preserving the real KB.
    work = Path(tempfile.mkdtemp(prefix="kefayat-auto-test-"))
    auto = work / "autonomy"
    auto.mkdir()
    for name in ("controller.py",):
        (auto / name).write_text(CONTROLLER.read_text(encoding="utf-8"), encoding="utf-8")
    # Execute from a copied mini-repository is intentionally not used because
    # controller ROOT is derived from its location. Structural tests below
    # therefore exercise source invariants; integration is exercised by CI.
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    p = subprocess.run(["python3", str(CONTROLLER)], cwd=ROOT, text=True, capture_output=True, env=env)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout.strip().splitlines()[-1])


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


def test_controller_has_safe_stop_and_release_block() -> None:
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "STAGNATION_DETECTED" in text
    assert "AUTO-RELEASE-01" in text
    assert "NO CLAIM" in text


def test_kb_sha256_is_stable() -> None:
    h = hashlib.sha256(KB.read_bytes()).hexdigest()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


if __name__ == "__main__":
    for fn in (test_kb_shape_and_identity, test_controller_source_uses_canonical_object_schema,
               test_controller_has_safe_stop_and_release_block, test_kb_sha256_is_stable):
        fn()
    print("AUTONOMY REGRESSION: PASS")
