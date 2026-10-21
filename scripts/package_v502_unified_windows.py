#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 reproducible portable Windows ZIP generated only from GitHub source,
13 native JPG, full original V19–V50 editor, and optional verified MP4.
Never describes a technical preview as a completed professional anime series.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"anime-factory/v50_2/art"
STUDIO="AI_Anime_Factory_V50_2_UNIFIED.html"
PROJECT="PROJECT_V502_UNIFIED.json"
DOC=ROOT/"anime-factory/v50_2/UNIFIED_README_RU.md"
SOURCE=[
 "anime-factory/v50_2/build_complete_v502.py",
 "anime-factory/v50_2/director_v502.js",
 "anime-factory/v50_2/art_pass_preview.js",
 "anime-factory/v50_2/motion_rig_v502.js",
 "anime-factory/v50_2/clean_cuts_v502.js",
 "anime-factory/v50_2/build_director_v502.py",
 "anime-factory/v50_1/build_cinematic_v501.py",
 "anime-factory/v50_1/cinematic_pilot_v501.js",
 "scripts/postprocess_v502.py",
 "scripts/render_anime_v48.py",
 "scripts/render_v502_offline.py"
]
def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--html",required=True)
    cli.add_argument("--project",required=True)
    cli.add_argument("--out",required=True)
    cli.add_argument("--video-dir")
    x=cli.parse_args()
    html=Path(x.html).resolve();project=Path(x.project).resolve()
    data=json.loads(project.read_text(encoding="utf-8"))
    assert data["format"]=="AIAnimeFactoryProject"
    assert len(data.get("episodes",[]))>=6
    assert data["v502Director"]["enabled"]
    assert not data["productionV50"]["qaAccepted"]
    # The upstream postprocessor deliberately DOES NOT write new toggles to
    # the canonical JSON. Produce a copy for this ZIP, matching the HTML.
    import importlib.util
    builder=ROOT/"anime-factory/v50_2/build_complete_v502.py"
    spec=importlib.util.spec_from_file_location("v502_unified",builder)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    normalized=mod.checked_project(project)
    assert all(normalized[k]["enabled"] for k in
               ("v502Director","v502Art","v502MotionRig","v502CleanCuts"))
    normalized_json=json.dumps(normalized,ensure_ascii=False,indent=2).encode("utf-8")
    out=Path(x.out).resolve()
    if html==out or project==out:raise RuntimeError("No file overwrite")
    out.parent.mkdir(parents=True,exist_ok=True)
    media=[]
    if x.video_dir:
        d=Path(x.video_dir).resolve()
        # Old V50.2 packages two pilot videos, scripted Season V50.2
        # must include ALL six previews to avoid dropping former episodes.
        numbers=range(1,7) if data.get("seasonScriptV502") else (1,2)
        for n in numbers:
            movie=d/f"episode_{n:02d}.mp4"
            if not movie.is_file() or movie.stat().st_size<100000:
                raise RuntimeError("Missing verified MP4 "+str(movie))
            media.append(movie)
    manifest={"status":"TECHNICAL_PREVIEW_ARTISTIC_REVIEW_REQUIRED",
       "projectFingerprint":data["pilotProductionV50"]["originalV50ProjectSha256"],
       "videoCount":len(media),"licenseApproval":False,
       "artApproval":False,"files":{}}
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        def add_disk(path,destination):
            z.write(path,destination)
            manifest["files"][destination]=sha(path)
        add_disk(html,STUDIO)
        z.writestr(PROJECT,normalized_json)
        manifest["files"][PROJECT]=hashlib.sha256(normalized_json).hexdigest()
        add_disk(DOC,"README_RU.md")
        for name in SOURCE:
            add_disk(ROOT/name,"SOURCE/"+Path(name).name)
        for p in sorted(ART.glob("*.jpg")):
            add_disk(p,"ART/"+p.name)
        for p in media:
            add_disk(p,"VIDEOS/"+p.name)
        for name in ("scripts/render_anime_v48.py","scripts/postprocess_v502.py","scripts/render_v502_offline.py"):
            add_disk(ROOT/name,Path(name).name)
        z.writestr("RUN_WINDOWS.bat",
                   '@echo off\r\nstart "" "%~dp0'+STUDIO+'"\r\n')
        z.writestr("SETUP_WINDOWS.bat",
                   '@echo off\r\npy -3 -m pip install playwright==1.56.0\r\n'
                   'py -3 -m playwright install chromium\r\npause\r\n')
        z.writestr("RENDER_2_RU_MP4_WINDOWS.bat",
                   '@echo off\r\ncd /d "%~dp0"\r\n'
                   'if exist "tools\\ffmpeg\\bin\\ffmpeg.exe" '
                   'set "PATH=%CD%\\tools\\ffmpeg\\bin;%PATH%"\r\n'
                   'py -3 render_anime_v48.py --html "'+STUDIO+
                   '" --project "'+PROJECT+
                   '" --out NEW_EPISODES --episodes 1,2 --fps 6 --mp4\r\npause\r\n')
        z.writestr("RENDER_HD_12FPS_WINDOWS.bat",
                   '@echo off\r\ncd /d "%~dp0"\r\n'
                   'if exist "tools\\ffmpeg\\bin\\ffmpeg.exe" '
                   'set "PATH=%CD%\\tools\\ffmpeg\\bin;%PATH%"\r\n'
                   'py -3 -m pip install numpy playwright==1.56.0\r\n'
                   'py -3 -m playwright install chromium\r\n'
                   'py -3 render_v502_offline.py --html "'+STUDIO+
                   '" --project "'+PROJECT+
                   '" --out NEW_HD_VIDEO --episodes 1,2 --fps 12 --width 960\r\npause\r\n')
        z.writestr("tools/ffmpeg/bin/README_RU.txt",
                   "Из уже имеющегося ffmpeg-9.0.2-full_build.zip "
                   "извлеките ffmpeg.exe и ffprobe.exe сюда.")
        z.writestr("MANIFEST_SHA256.json",json.dumps(
            manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(out) as z:
        bad=z.testzip()
        if bad:raise RuntimeError("ZIP CRC failed: "+bad)
        for path,digest in manifest["files"].items():
            if hashlib.sha256(z.read(path)).hexdigest()!=digest:
                raise RuntimeError("Bad archive member "+path)
    print("V50.2 reproducible Windows archive",out,out.stat().st_size,
          "SHA256",sha(out),"13 true JPEG","videos",len(media),
          "art quality signoff False")
if __name__=="__main__":main()
