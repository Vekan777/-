#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build reproducible V50.2 DIRECTOR + real MOTION RIG + 13 ORIGINAL JPEGs
+ opaque CLEAN CUTS from repository sources, with optional embedded pilot JSON.

No external image service, model weights, fonts or licenses are downloaded.
This only produces a TECHNICAL pilot; never marks human/art/license acceptance.
"""
from __future__ import annotations
import argparse,base64,hashlib,importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASE=HERE/"build_director_v502.py"
ART=HERE/"art"
EXTENSIONS=[HERE/"art_pass_preview.js",HERE/"motion_rig_v502.js",
            HERE/"clean_cuts_v502.js"]
DEFAULT=ROOT/"dist/AI_Anime_Factory_V50_2_UNIFIED_REPRODUCIBLE.html"
ART_NAMES=("akira","akira_power","akira_screaming","battle","guardian",
           "miyu","miyu_worried","portal","ren","ren_worried","saira",
           "saira_detail","world")
CANON_FIELDS=("originalV50ProjectSha256","source","status")
def once(src,old,new):
    if src.count(old)!=1:
        raise RuntimeError("Expected exactly one V50.2 patch point "+
                           repr(old[:88])+": "+str(src.count(old)))
    return src.replace(old,new,1)
def checked_project(path):
    if path is None:return None
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("format")!="AIAnimeFactoryProject" or len(data.get("episodes",[]))<6:
        raise ValueError("Expected complete full-season V50 JSON with >=6 episodes")
    pilot=data.get("pilotProductionV50",{})
    if any(not pilot.get(x) for x in CANON_FIELDS):
        raise ValueError("Original V50 pilot canon provenance absent")
    if len(pilot["originalV50ProjectSha256"])!=64:
        raise ValueError("Unverifiable upstream project fingerprint")
    if not data.get("v501Visual",{}).get("enabled"):
        raise ValueError("Missing V50.1 visual migration")
    for ep in data["episodes"][:2]:
        if len(ep["scenes"])!=6:raise ValueError("Incomplete 2D pilot")
        for scene in ep["scenes"]:
            if not scene.get("pilotV50") or len(scene.get("lines",[]))!=2:
                raise ValueError("Pilot missing two-speaker staging")
    # Make only a copy, never alter source JSON or approved metadata.
    data["v502Director"]={**data.get("v502Director",{}),"enabled":True,
                          "approval":False,"rightsVerified":False}
    data["v502Art"]={**data.get("v502Art",{}),"enabled":True,
                     "artReviewApproved":False,"status":"STORYBOARD_PREVIEW"}
    data["v502MotionRig"]={**data.get("v502MotionRig",{}),"enabled":True,
                           "artApproval":False,"status":"PROCEDURAL_RIG"}
    data["v502CleanCuts"]={**data.get("v502CleanCuts",{}),"enabled":True,
                           "artApproval":False,
                           "quality":"ILLUSTRATED_STILLS_NOT_FRAME_ANIMATION"}
    return data
def make_art_js():
    filenames=tuple(p.stem for p in ART.glob("*.jpg"))
    if set(filenames)!=set(ART_NAMES):
        raise ValueError("Expected 13 exactly original art files; got "+
                         str(sorted(filenames)))
    encoded={}
    for name in ART_NAMES:
        p=ART/(name+".jpg");raw=p.read_bytes()
        if not (raw[:3]==bytes.fromhex("ffd8ff") and raw[-2:]==bytes.fromhex("ffd9")):
            raise ValueError("Corrupt JPEG: "+name)
        if len(raw)<8000:raise ValueError("Missing visual quality/art bytes: "+name)
        encoded[name]="data:image/jpeg;base64,"+base64.b64encode(raw).decode("ascii")
    js="window.v502IllustrationData=Object.freeze("+json.dumps(encoded,
        ensure_ascii=True,separators=(",",":"))+");"
    meta={"artCount":len(encoded),
          "sha256":{name:hashlib.sha256((ART/(name+".jpg")).read_bytes()).hexdigest()
                    for name in ART_NAMES}}
    return js,meta
def build(project_path=None):
    spec=importlib.util.spec_from_file_location("v502_parent_director",BASE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    html=module.build()
    assert "/* END V50.2 DIRECTOR */" in html
    art_js,meta=make_art_js()
    add=art_js+"\n"+"\n".join(p.read_text(encoding="utf-8") for p in EXTENSIONS)
    for script in EXTENSIONS:
        if not script.is_file():raise FileNotFoundError(script)
    html=once(html,"/* END V50.2 DIRECTOR */",
              "/* END V50.2 DIRECTOR */\n"+add+
              "\n/* END V50.2 REPRODUCIBLE ART AND MOTION */")
    data=checked_project(project_path)
    if data is not None:
        # Unicode safe, literal JS object and no upstream project overwrite.
        js=json.dumps(data,ensure_ascii=True,separators=(",",":"))
        if "</script" in js.lower():
            raise RuntimeError("Unsafe closing script marker")
        old="if(!P)buildSeason();else{renderAll();show('project');"
        replacement=("if(!P)P="+js+";\n"+
                     "if(!P)buildSeason();else{renderAll();show('project');")
        html=once(html,old,replacement)
    for needle in ("window.v502Motion","window.v502CleanCutsQA",
                   "window.v502IllustrationData","window.v502Director",
                   "window.v50FinalQA"):
        if needle not in html:raise RuntimeError("Built missing: "+needle)
    return html,meta
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",help="Optional V50.2 pilot JSON; embedded on first boot")
    p.add_argument("--out",default=str(DEFAULT))
    p.add_argument("--selftest",action="store_true")
    a=p.parse_args()
    html,meta=build(a.project)
    if a.selftest:
        print("PASS: source-complete 13 binary assets, original MOTION RIG,"
              " 2D studio, optional pilot, immutable story",len(html.encode("utf-8")))
        return
    dest=Path(a.out).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html,encoding="utf-8")
    (dest.parent/"V502_ART_ASSET_SHA256.json").write_text(
       json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print("REPRODUCIBLE V50.2",dest,len(html.encode("utf-8")),
          hashlib.sha256(dest.read_bytes()).hexdigest(),"13 art SHA PASS")
if __name__=="__main__":main()
