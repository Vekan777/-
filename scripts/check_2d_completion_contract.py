#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2D release contract: prevent scope drift and premature FINAL / 3D claims.

Standard-library only, so it is safe in CI, Win10, and offline source checkouts.
Use: python scripts/check_2d_completion_contract.py
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"anime-factory/roadmap/2d_completion_contract.json"
REQUIRED_GATES={
 "ASSET_LAYERS","ART_IMPORT","ASSET_PORTABLE","ASSET_LICENSE",
 "REAL_RIG","KEYFRAME_TIMELINE","REUSABLE_MOTION","MIGRATION_SAFE",
 "AUDIO_PORTABLE","LIPSYNC","AUDIO_VIDEO_SYNC","SUBTITLE_SYNC",
 "BATCH_MOVIES","STREAMING_RENDER","MP4_EXPORT","BACKUP_RESTORE",
 "TWO_EPISODES","ONE_UI","LEGACY_ROUNDTRIP","WORKING_DEMO_60_180S",
 "ONE_ARCHIVE","WINDOWS10_LOW_SPEC","AUTOMATED_REGRESSION",
 "HUMAN_VISUAL_REVIEW","RELEASE_CHECKLIST","3D_GATE"
}
def inspect():
 d=json.loads(CONTRACT.read_text(encoding="utf-8"))
 issues=[]
 def check(ok,message):
  if not ok:issues.append(message)
 policy=d["release_policy"];versions=d["versions"];accept=d["acceptance"]
 expected=list(range(45,51))
 check(d["schema"]=="AIAnimeFactory/2DCompletionContract/1","Invalid contract schema")
 check(d["baseline"]["version"]==44,"Baseline must be published V44")
 check([v["id"] for v in versions]==expected,"Six major versions must be V45–V50, no extras")
 check(policy["total_remaining_major"]==6 and policy["last_major_2d"]==50 and
  policy["unified_major"]==49 and policy["qa_final_major"]==50 and
  policy["prohibit_more_major_2d"] is True,"Version freeze violated")
 check(policy["three_d_product"]=="3D Edition v1","3D must be separate product")
 ids=[x["id"] for x in accept]
 check(set(ids)==REQUIRED_GATES and len(ids)==len(REQUIRED_GATES),
  "Incomplete or duplicated 2D acceptance gates")
 for v in versions:
  check(v["gate_ids"] and all(g in REQUIRED_GATES for g in v["gate_ids"]),
    "Missing gate or unknown gate in V"+str(v["id"]))
  check(v["status"] in ("PLANNED","IN_PROGRESS","PASS","FAILED"),
    "Invalid release status "+str(v["id"]))
 for gate in accept:
  check(type(gate["passed"]) is bool,"Gate passed must be bool: "+gate["id"])
  check(gate["kind"] in ("automated","manual","automated+manual"),
    "Gate lacks test methodology "+gate["id"])
 for issue in d["hard_blockers"]:
  check(issue["version_to_fix"] in expected,"Blocker lacks finite target: "+issue["id"])
  check(issue["status"] in ("OPEN","IN_PROGRESS","FIXED_AND_VERIFIED"),
    "Blocker has invalid state")
  check((ROOT/issue["source"]).is_file(),"Broken source evidence: "+issue["source"])
 for ref in d["references"]:
  check((ROOT/ref).is_file(),"Roadmap document absent: "+ref)
 check((ROOT/d["baseline"]["source"]).is_file(),"Published V44 source baseline missing")
 all_pass=all(v["status"]=="PASS" for v in versions) and all(g["passed"] for g in accept)
 no_blockers=all(issue["status"]=="FIXED_AND_VERIFIED" for issue in d["hard_blockers"])
 if d["status"]=="2D_FINAL_ACCEPTED":
  check(all_pass and no_blockers,"PREMATURE 2D FINAL: unresolved acceptance or blocker")
 elif d["status"]!="PLANNED_NOT_FINISHED":
  check(d["status"]=="IN_PROGRESS","Invalid overall completion state")
 if d["status"]=="PLANNED_NOT_FINISHED":
  check(not all(g["passed"] for g in accept),
   "Contradiction: all gates pass but roadmap still says PLANNED")
 return d,issues,all_pass,no_blockers

def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--require-final",action="store_true",
  help="Fail until entire 2D V50 final contract is accepted")
 args=cli.parse_args()
 data,problems,accepted,clear=inspect()
 final=data["status"]=="2D_FINAL_ACCEPTED" and accepted and clear
 if args.require_final and not final:
  problems.append("V50 is NOT accepted: cannot start 3D Edition")
 print("2D version freeze: V45–V50; V49 UNIFIED; V50 FINAL QA")
 print("Current status:",data["status"])
 print("Acceptance:",sum(x["passed"] for x in data["acceptance"]),
       "of",len(data["acceptance"]),"gates")
 print("Verified blockers fixed:",
  sum(x["status"]=="FIXED_AND_VERIFIED" for x in data["hard_blockers"]),
  "of",len(data["hard_blockers"]))
 if problems:
  for x in problems:print("ERROR:",x)
  raise SystemExit(1)
 print("Contract valid. This is NOT proof of software acceptance.")
if __name__=="__main__":main()
