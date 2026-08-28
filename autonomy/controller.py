#!/usr/bin/env python3
"""Kefayat Ω bounded autonomous control plane."""
from __future__ import annotations
import hashlib, json, os, time
from pathlib import Path
from typing import Any
ROOT=Path(os.environ.get("KEFAYAT_ROOT",str(Path(__file__).resolve().parents[1]))).resolve(); AUTO=ROOT/"autonomy"
STATE=AUTO/"mission-state.json"; LEDGER=AUTO/"evidence-ledger.jsonl"; PLAN=AUTO/"mission-plan.json"; KB=ROOT/"knowledge"/"competencies.json"
MAX_STAGNANT_CYCLES=3; ALLOWED_GRADES={1,2,3,4}; ALLOWED_SUBJECTS={"arabic","mathematics","islamic_education","nurturing"}
def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
 return h.hexdigest()
def default_state()->dict[str,Any]:
 return {"mission_id":"KEFAYAT-AUTO-001","baseline_id":"MASTER-OMEGA-vΩ.7.4-OAC-01-OAG-01","phase":"BOOT","status":"RUNNING","completed_tasks":[],"open_gaps":["FULL_AUTONOMOUS_DEVELOPMENT","REAL_MISSION_PILOT"],"blockers":[],"attempt_counters":{},"stagnant_cycles":0,"last_checkpoint":None,"artifact_identities":{},"evidence_state":"UNREPORTED","claim_state":"NO CLAIM","release_state":"NOT READY","next_best_action":"BOOTSTRAP","history":[]}
def load_state()->dict[str,Any]:
 if not STATE.exists(): return default_state()
 try:
  s=json.loads(STATE.read_text(encoding="utf-8")); assert isinstance(s,dict); return s
 except Exception:
  s=default_state(); s["status"]="BLOCKED"; s["blockers"]=["STATE_CORRUPT"]; return s
def save_state(s:dict[str,Any])->None:
 AUTO.mkdir(parents=True,exist_ok=True); t=STATE.with_suffix(".tmp"); t.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(t,STATE)
def record(s:dict[str,Any],tid:str,expected:str,observed:str,decision:str,method:str)->None:
 AUTO.mkdir(parents=True,exist_ok=True); e={"timestamp_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"mission_id":s["mission_id"],"test_id":tid,"expected":expected,"observed":observed,"method":method,"decision":decision}; LEDGER.open("a",encoding="utf-8").write(json.dumps(e,ensure_ascii=False)+"\n")
def validate_plan(s:dict[str,Any])->bool:
 try:
  d=json.loads(PLAN.read_text(encoding="utf-8")); assert d["mission_id"]==s["mission_id"]; assert d["baseline_id"]==s["baseline_id"]; assert isinstance(d["phases"],list) and len(d["phases"])>=6; assert isinstance(d["gates"],dict) and len(d["gates"])>=6; assert d["stop_conditions"]; record(s,"AUTO-PLAN-01","bounded mission plan is valid","valid","PASS","JSON + invariant checks"); return True
 except Exception as e:
  s["blockers"]=[x for x in s["blockers"] if not x.startswith("PLAN_INVALID")]+[f"PLAN_INVALID:{type(e).__name__}"]; record(s,"AUTO-PLAN-01","bounded mission plan is valid",str(e),"NO-GO","mission-plan invariant checks"); return False
def validate_kb(s:dict[str,Any])->bool:
 if not KB.exists(): record(s,"AUTO-KB-01","canonical KB exists","missing","BLOCKED","filesystem"); s["blockers"].append("KB_MISSING"); return False
 try:
  d=json.loads(KB.read_text(encoding="utf-8")); assert isinstance(d,dict); rs,cv=d.get("records"),d.get("coverage"); assert isinstance(rs,list) and isinstance(cv,list) and rs; ids=set()
  for r in rs:
   assert isinstance(r,dict)
   for k in ("id","grade","subject","provenance","source_text"): assert k in r
   assert r["id"] not in ids; ids.add(r["id"]); assert r["grade"] in ALLOWED_GRADES; assert r["subject"] in ALLOWED_SUBJECTS; assert isinstance(r["source_text"],str) and r["source_text"].strip(); assert isinstance(r["provenance"],dict) and r["provenance"].get("status")
  s["artifact_identities"]["competencies.json"]=digest(KB); record(s,"AUTO-KB-01","valid canonical competency records",f"{len(rs)} records; {len(cv)} coverage entries","PASS","JSON + invariants"); return True
 except Exception as e: record(s,"AUTO-KB-01","valid canonical competency records",str(e),"NO-GO","invariant checks"); return False
def check_state(s:dict[str,Any])->bool:
 req=("mission_id","baseline_id","phase","status","completed_tasks","blockers","next_best_action","artifact_identities","evidence_state","claim_state","release_state"); missing=[k for k in req if k not in s]; record(s,"AUTO-STATE-01","required durable state","complete" if not missing else str(missing),"PASS" if not missing else "BLOCKED","schema invariant check"); return not missing
def choose_next(s:dict[str,Any])->str:
 if s.get("status") in {"BLOCKED","SAFE_STOP","NO-GO"}: return "RECOVER_OR_ESCALATE"
 t=s["completed_tasks"]
 if "PLAN_VALIDATED" not in t:return "VALIDATE_PLAN"
 if "KB_VALIDATED" not in t:return "VALIDATE_KB"
 if "STATE_INTEGRITY_CHECKED" not in t:return "CHECK_STATE_INTEGRITY"
 if "RELEASE_GATE_CHECKED" not in t:return "CHECK_RELEASE_GATE"
 return "WAIT_FOR_NEXT_MISSION"
def sig(s:dict[str,Any])->str: return json.dumps({k:s.get(k) for k in ("phase","status","completed_tasks","open_gaps","blockers","attempt_counters","artifact_identities","evidence_state","claim_state","release_state","next_best_action")},sort_keys=True,ensure_ascii=False)
def main()->int:
 s=load_state(); s["phase"]="CONTROL_LOOP"; s["status"]="RUNNING" if s.get("status") not in {"BLOCKED","SAFE_STOP","NO-GO"} else s["status"]; before=sig(s); a=choose_next(s); s["next_best_action"]=a
 if a=="VALIDATE_PLAN":
  if validate_plan(s): s["completed_tasks"].append("PLAN_VALIDATED")
  else:s["status"]="NO-GO"
 elif a=="VALIDATE_KB":
  if validate_kb(s): s["completed_tasks"].append("KB_VALIDATED"); s["phase"]="VERIFY"
  else:s["status"]="BLOCKED"
 elif a=="CHECK_STATE_INTEGRITY":
  if check_state(s): s["completed_tasks"].append("STATE_INTEGRITY_CHECKED")
  else:s["status"]="BLOCKED"
 elif a=="CHECK_RELEASE_GATE":
  s["release_state"]="NOT READY"; s["claim_state"]="NO CLAIM"; record(s,"AUTO-RELEASE-01","release gates proven","full autonomous development and real-mission assurance not proven","BLOCKED","claim-scope gate"); s["completed_tasks"].append("RELEASE_GATE_CHECKED")
 elif a=="RECOVER_OR_ESCALATE": record(s,"AUTO-RECOVERY-01","safe recovery or explicit escalation",s.get("status","UNKNOWN"),"BLOCKED","conservative recovery gate")
 after=sig(s); s["stagnant_cycles"]=int(s.get("stagnant_cycles",0))+1 if before==after else 0
 if s["stagnant_cycles"]>=MAX_STAGNANT_CYCLES and s["status"]=="RUNNING": s["status"]="SAFE_STOP"; s["blockers"]=[x for x in s["blockers"] if x!="STAGNATION_DETECTED"]+["STAGNATION_DETECTED"]; record(s,"AUTO-WATCHDOG-01","progress or bounded stop","stagnation","SAFE_STOP","progress watchdog")
 s["last_checkpoint"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()); s["history"].append({"action":a,"status":s["status"],"checkpoint":s["last_checkpoint"]}); save_state(s); print(json.dumps({"mission_id":s["mission_id"],"action":a,"status":s["status"],"next":choose_next(s)},ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
