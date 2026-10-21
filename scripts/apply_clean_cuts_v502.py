#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply V50.2 CLEAN CUTS on top of the previous, verified Motion Rig ZIP.
No forced upgrades or silent scene overwrites. The original ZIP is untouched.
Original source files, assets and two videos remain inside the source archive.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"anime-factory/v50_2/clean_cuts_v502.js"
EXPECTED_RIG_SHA256="6f569e3974143544ce208e8653f201480242b7441effd6ea16f6454f3049d47f"
HTML_NAME="AI_Anime_Factory_V50_2_MOTION_READY.html"
PROJECT_NAME="PROJECT_V502_MOTION_READY.json"
INSERT_ANCHOR="requestAnimationFrame(tick);\n})();\n</script></body></html>"

def build(source: Path,target: Path):
    if source.resolve()==target.resolve():
        raise ValueError("Source and output ZIP must be different")
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError("Source ZIP CRC error")
        names=set(z.namelist())
        required={HTML_NAME,PROJECT_NAME,"SOURCE/motion_rig_v502.js",
          "VIDEOS/EPISODE_01_70S_RUSSIAN.mp4",
          "VIDEOS/EPISODE_02_70S_RUSSIAN.mp4"}
        if not required.issubset(names):
            raise RuntimeError("Wrong base ZIP; missing "+str(sorted(required-names)))
        rig=z.read("SOURCE/motion_rig_v502.js")
        if hashlib.sha256(rig).hexdigest()!=EXPECTED_RIG_SHA256:
            raise RuntimeError("Unknown/changed motion source, refusing silent patch")
        html=z.read(HTML_NAME).decode("utf-8")
        if html.count(INSERT_ANCHOR)!=1 or "window.v502Motion" not in html:
            raise RuntimeError("Unexpected upstream HTML, manual review required")
        patched=html.replace(INSERT_ANCHOR,
            "\n"+PATCH.read_text(encoding="utf-8")+"\n"+INSERT_ANCHOR,1)
        patched=patched.replace("if(!P)buildSeason();else{renderAll();show('project');",
            "if(P&&!P.v502CleanCuts)P.v502CleanCuts={enabled:true,"
            "quality:'ILLUSTRATED_STILLS_NOT_FRAME_ANIMATION',artApproval:false};"
            "if(!P)buildSeason();else{renderAll();show('project');",1)
        project=json.loads(z.read(PROJECT_NAME).decode("utf-8"))
        canon=project["pilotProductionV50"]["originalV50ProjectSha256"]
        if len(project["episodes"])<6 or len(canon)!=64:
            raise RuntimeError("Source story may be incomplete")
        project["v502CleanCuts"]={"enabled":True,"artApproval":False,
                   "quality":"ILLUSTRATED_STILLS_NOT_FRAME_ANIMATION"}
        target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=7) as out:
            for entry in z.infolist():
                if entry.filename in {HTML_NAME,PROJECT_NAME}:continue
                out.writestr(entry.filename,z.read(entry.filename))
            out.writestr(HTML_NAME,patched.encode("utf-8"))
            out.writestr(PROJECT_NAME,json.dumps(
                project,ensure_ascii=False,indent=2).encode("utf-8"))
            out.writestr("SOURCE/clean_cuts_v502.js",PATCH.read_bytes())
            out.writestr("CLEAN_CUTS_MANIFEST.json",json.dumps({
                "status":"ART_REVIEW_REQUIRED",
                "source_motion_sha256":EXPECTED_RIG_SHA256,
                "original_story_sha256":canon,
                "patch_sha256":hashlib.sha256(PATCH.read_bytes()).hexdigest(),
                "original_videos_retained":True,
                "note":"Old videos are unchanged; re-render to see CLEAN CUTS in MP4."
            },ensure_ascii=False,indent=2))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert z.read(PROJECT_NAME)
    print("CLEAN CUTS SOURCE PACKAGE",target,target.stat().st_size,
          hashlib.sha256(target.read_bytes()).hexdigest())
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--base-zip",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    v=a.parse_args();build(v.base_zip,v.out)
if __name__=="__main__":main()
