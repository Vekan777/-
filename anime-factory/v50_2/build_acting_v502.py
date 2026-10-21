#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 optional acting/battle pass over six-episode PERFORMANCE editor.
No changes to original story, independent fallback when disabled.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"anime-factory/v50_2/build_season_v502.py"
OVERLAY=Path(__file__).with_name("acting_battle_v502.js")
MARKER="/* END V50.2 PERFORMANCE PASS */"
def build(project=None):
 spec=importlib.util.spec_from_file_location("v502_performance_base",BASE)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 html,meta=module.build(project)
 if html.count(MARKER)!=1:raise ValueError("Missing PERFORMANCE insert marker")
 html=html.replace(MARKER,MARKER+"\n"+OVERLAY.read_text(encoding="utf8")+
                   "\n/* END V50.2 ACTING PASS */",1)
 boot="if(!P)buildSeason();else{renderAll();show('project');"
 if html.count(boot)!=1:raise ValueError("Unexpected boot location")
 html=html.replace(boot,"if(P&&!P.v502Acting)P.v502Acting={enabled:true,"+
                   "artApproval:false,phonemeAligned:false};\n"+boot,1)
 for key in ("window.v502ActingQA","window.v502PerformanceQA","window.v502SeasonStageQA"):
  if key not in html:raise RuntimeError("Missing "+key)
 return html,meta
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project")
 ap.add_argument("--out",required=True)
 ap.add_argument("--selftest",action="store_true")
 args=ap.parse_args()
 s,meta=build(args.project)
 if args.selftest:
  print("V50.2 ACTING source compiled, bytes",len(s.encode()),"JPEGs",meta["artCount"]);return
 dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(s,encoding="utf8")
 print("V50.2 ACTING PROGRAM",dest,hashlib.sha256(dest.read_bytes()).hexdigest())
if __name__=="__main__":main()
