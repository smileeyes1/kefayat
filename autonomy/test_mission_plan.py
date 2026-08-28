#!/usr/bin/env python3
"""Regression tests for the bounded autonomous mission plan."""
import json, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"autonomy"/"mission-plan.json"
CONTROLLER=ROOT/"autonomy"/"controller.py"

def test_plan_contract():
 d=json.loads(PLAN.read_text(encoding="utf-8"))
 assert d["mission_id"]=="KEFAYAT-PRO-001"
 assert d["baseline_id"]=="MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01"
 assert len(d["phases"])>=6
 assert len(d["gates"])>=6
 assert d["stop_conditions"]

def test_controller_is_plan_aware():
 t=CONTROLLER.read_text(encoding="utf-8")
 assert 'PLAN=AUTO/"mission-plan.json"' in t
 assert "validate_plan" in t
 assert "VALIDATE_PLAN" in t

def test_first_autonomous_action_validates_plan():
 with tempfile.TemporaryDirectory(prefix="kefayat-plan-test-") as td:
  repo=Path(td); (repo/"autonomy").mkdir(); (repo/"knowledge").mkdir()
  import shutil
  shutil.copy2(PLAN,repo/"autonomy/mission-plan.json")
  shutil.copy2(CONTROLLER,repo/"autonomy/controller.py")
  shutil.copy2(ROOT/"knowledge/competencies.json",repo/"knowledge/competencies.json")
  env=os.environ.copy(); env["KEFAYAT_ROOT"]=str(repo); env["PYTHONHASHSEED"]="0"
  p=subprocess.run(["python3",str(repo/"autonomy/controller.py")],cwd=repo,text=True,capture_output=True,env=env,check=False)
  assert p.returncode==0,p.stderr
  result=json.loads(p.stdout.strip().splitlines()[-1])
  assert result["action"]=="VALIDATE_PLAN"
  state=json.loads((repo/"autonomy/mission-state.json").read_text(encoding="utf-8"))
  assert "PLAN_VALIDATED" in state["completed_tasks"]

if __name__=="__main__":
 test_plan_contract(); test_controller_is_plan_aware(); test_first_autonomous_action_validates_plan(); print("MISSION PLAN REGRESSION: PASS")
