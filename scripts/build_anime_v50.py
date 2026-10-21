#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50 FINAL Windows deliverable and integrity receipt with complete V49 backup."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PREVIOUS=ROOT/"scripts/build_anime_v49.py"
BUILDER=ROOT/"anime-factory/v50/build_final_v50.py"
NAME="AI_ANIME_FACTORY_V50_FINAL_2D_WINDOWS.zip"
HTML="AI_Anime_Factory_V50_FINAL_2D.html"
def module(file,name):
 sp=importlib.util.spec_from_file_location(name,file)
 obj=importlib.util.module_from_spec(sp);sp.loader.exec_module(obj);return obj
parent=module(PREVIOUS,"anime_v49_parent_for_v50")
builder=module(BUILDER,"anime_v50_final_builder")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V50_FINAL_2D.html"\r\n'
README="""AI ANIME FACTORY V50 FINAL 2D / WINDOWS 10 X64
================================================
1. Extract the complete ZIP into a NEW directory. Do not overwrite V49.
2. Double-click RUN_WINDOWS.bat, or open AI_Anime_Factory_V50_FINAL_2D.html
   in Chrome/Edge. No Python needed for browser-side story/art/animation.
3. Make the FULL project JSON backup before any edits.
4. 'Единая студия V49' is the real six-stage production workflow.
5. 'ФИНАЛЬНАЯ QA V50' audits story, cast IDs, PNG asset integrity,
   cutout keyframe order, audio/mouth amplitude, subtitles, credits and
   per-episode production. Resolve critical errors before releasing.
6. Export final report JSON and full asset/voice/animation project JSON.
7. Human signoff is MANUAL: review EVERY episode and rights to every asset.
8. Produce a real WebM from V48, listen to and watch the final movie.
9. Batch H264/AAC MP4 and SRT/VTT: save PROJECT_INPUT.json next to
   RUN_BATCH_WINDOWS.bat, install Python 3.11+ x64, run
   SETUP_BATCH_WINDOWS.bat (Playwright Chromium) with Internet.
10. Provide your extracted ffmpeg.exe and ffprobe.exe at
    tools\\ffmpeg\\bin\\ (or put both in PATH).
11. Run RUN_BATCH_WINDOWS.bat. OUTPUT has WebM, MP4, SRT, VTT and
    V48_RENDER_CHECKPOINT.json (resume per completed episode).
12. Preserve backup and all original copyrighted/licensed media.
TECHNICAL QA PASS != FINISHED PROFESSIONAL ART. V46 is cutout animation,
V47 lip movement is waveform/RMS, not phoneme recognition.
The series' artistic quality and intellectual property require human review.
This is FINAL V50 — no invented V51. Separate 3D Edition after acceptance.
Full Russian guide: source/V50_README_RU.md
"""
def digest(data):return hashlib.sha256(data).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v50-") as tmp:
  prev=Path(tmp)/parent.NAME
  parent.assemble(prev)
  oldzip=prev.read_bytes()
  with zipfile.ZipFile(prev) as z:
   if z.testzip():raise RuntimeError("V49 parent ZIP CRC32 failure")
   files={name:z.read(name) for name in z.namelist()
    if name!="BUILD_MANIFEST.json" and
    not(name.startswith("backup/") and name.lower().endswith(".zip"))}
 files["backup/"+parent.NAME]=oldzip
 files[HTML]=builder.build().encode("utf-8")
 files["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 files["README_RU.txt"]=README.encode("utf-8")
 batch=files.get("RUN_BATCH_WINDOWS.bat",b"").decode("utf-8")
 if "AI_Anime_Factory_V49_UNIFIED_STUDIO.html" not in batch:
  raise RuntimeError("Historic batch launcher missing V49")
 files["RUN_BATCH_WINDOWS.bat"]=batch.replace(
  "AI_Anime_Factory_V49_UNIFIED_STUDIO.html",HTML).encode("utf-8")
 # Fix real legacy batch bug: CLI must write input JSON to active V50 key.
 # Store corrected script exactly at the path invoked by original Windows BAT.
 files["source/V48_render_anime_v48.py"]=(ROOT/"scripts/render_anime_v48.py").read_bytes()
 for rel in ("anime-factory/v50/deep_qa_v50.js",
   "anime-factory/v50/build_final_v50.py",
   "anime-factory/v50/README_RU.md",
   "scripts/build_anime_v50.py","tests/test_anime_v50.py",
   "tests/test_deep_qa_v50.js","tests/smoke_browser_v50.py"):
  f=ROOT/rel
  if not f.is_file():raise FileNotFoundError(f)
  files["source/V50_"+f.name]=f.read_bytes()
 manifest={"schema":"AnimeFactoryV50Final2DRelease/1","version":50,
  "originalV19SHA256":digest(V19.read_bytes()),
  "immediateParentV49SHA256":digest(oldzip),
  "projectedHistory":"V19 source + V20–V49 modules and complete V49 parent ZIP",
  "qaLevel":"technical CI only; rights and artistic review require user signoff",
  "deepQA":["negative corrupt-project tests","Windows/Linux",
    "Chromium roundtrip of V49 story, actor art, V46 animation, V47 voice",
    "actual WebM with audible signal","MP4 H264/AAC multi-episode regression",
    "resume per completed-episode SHA256"],
  "files":[{"path":name,"bytes":len(data),"sha256":digest(data)}
   for name,data in sorted(files.items())]}
 files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 target=Path(destination).resolve();target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():target.unlink()
 with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 with zipfile.ZipFile(target) as z:
  if z.testzip():raise RuntimeError("V50 ZIP CRC32 error")
  m=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(z.namelist())!=len(m["files"])+1:raise RuntimeError("Final inventory changed")
  for entry in m["files"]:
   data=z.read(entry["path"])
   if len(data)!=entry["bytes"] or digest(data)!=entry["sha256"]:
    raise RuntimeError("Final checksum failure "+entry["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 was modified")
  if digest(z.read("backup/"+parent.NAME))!=m["immediateParentV49SHA256"]:
   raise RuntimeError("Immediate V49 historical ZIP altered")
  for file in ("source/V45_art_assets_v45.js","source/V46_animation_engine_v46.js",
   "source/V47_portable_voice_v47.js","source/V48_episode_engine_v48.js",
   "source/V49_unified_studio_v49.js","source/V50_deep_qa_v50.js",
   "source/V48_render_anime_v48.py",
   "SETUP_BATCH_WINDOWS.bat","RUN_BATCH_WINDOWS.bat",
   "CONVERT_MP4_WINDOWS.bat"):
   if file not in z.namelist():raise RuntimeError("Missing required module "+file)
  assert "AI_Anime_Factory_V50_FINAL_2D.html" in z.namelist()
 if target.stat().st_size>95*1024*1024:
  raise RuntimeError("V50 archive too large for permanent GitHub downloads/")
 print("V50 FINAL WINDOWS ZIP VERIFIED",target,target.stat().st_size,
  "contents",len(files),"SHA256",digest(target.read_bytes()))
 return target
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 a=p.parse_args()
 if a.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as tmp:assemble(Path(tmp)/NAME)
 else:assemble(a.out)
if __name__=="__main__":main()
