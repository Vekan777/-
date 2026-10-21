#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V49 historical, CRC32/SHA256 verified Windows archive with complete V48 parent."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PREVIOUS=ROOT/"scripts/build_anime_v48.py"
BUILDER=ROOT/"anime-factory/v49/build_unified_v49.py"
NAME="AI_ANIME_FACTORY_V49_UNIFIED_STUDIO_WINDOWS.zip"
HTML="AI_Anime_Factory_V49_UNIFIED_STUDIO.html"
def module(p,name):
 sp=importlib.util.spec_from_file_location(name,p)
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
previous=module(PREVIOUS,"v48_unified_delivery_parent")
builder=module(BUILDER,"v49_unified_editor_builder")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V49_UNIFIED_STUDIO.html"\r\n'
README="""AI ANIME FACTORY V49 — UNIFIED 2D PRODUCTION STUDIO / WINDOWS
==============================================================
1. Extract entire ZIP to a NEW folder, do not overwrite V48.
2. Double-click RUN_WINDOWS.bat (Chrome/Edge).
3. Open "Единая студия V49", select an episode and follow:
   Story → Art → Animation → Voice → Subtitles → Episode Export.
4. Download FULL project JSON containing original story, cutouts,
   V46 keyframes and V47 audio before each major edit.
5. Read actual warnings and mark review steps ONLY if you checked them.
   Manual checkboxes do not bypass technical warnings.
6. "Перейти к настоящей записи серии" opens real V48 episode editor.
7. For MP4 season batch: place PROJECT_INPUT.json next to BAT,
   run SETUP_BATCH_WINDOWS.bat (Python 3.11+, internet), then
   RUN_BATCH_WINDOWS.bat with FFmpeg/FFprobe in tools/ffmpeg/bin.
8. OUTPUT folder contains per-episode MP4/WebM and SRT/VTT,
   with resume from checksum-verified completed episodes only.
V49 preserves V19–V48 and complete V48 ZIP under backup/.
V50 remains deep final QA, NOT claimed finished yet. 3D later.
Read source/V49_README_RU.md for FULL Russian instructions.
"""
def digest(x):return hashlib.sha256(x).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v49-") as tmp:
  parent=Path(tmp)/previous.NAME
  previous.assemble(parent)
  oldbytes=parent.read_bytes()
  with zipfile.ZipFile(parent) as z:
   if z.testzip():raise RuntimeError("Broken V48 parent ZIP")
   files={n:z.read(n) for n in z.namelist()
    if n!="BUILD_MANIFEST.json" and
    not(n.startswith("backup/") and n.lower().endswith(".zip"))}
 files["backup/"+previous.NAME]=oldbytes
 files[HTML]=builder.build().encode("utf-8")
 files["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 files["README_RU.txt"]=README.encode("utf-8")
 oldbat=files.get("RUN_BATCH_WINDOWS.bat",b"").decode("utf-8")
 if "AI_Anime_Factory_V48_EPISODE_ENGINE.html" not in oldbat:
  raise RuntimeError("Original V48 batch launcher missing")
 files["RUN_BATCH_WINDOWS.bat"]=oldbat.replace(
  "AI_Anime_Factory_V48_EPISODE_ENGINE.html",HTML).encode("utf-8")
 for rel in ("anime-factory/v49/unified_studio_v49.js",
   "anime-factory/v49/build_unified_v49.py",
   "anime-factory/v49/README_RU.md",
   "scripts/build_anime_v49.py","tests/test_anime_v49.py",
   "tests/smoke_browser_v49.py"):
  file=ROOT/rel
  if not file.is_file():raise FileNotFoundError(file)
  files["source/V49_"+file.name]=file.read_bytes()
 manifest={"schema":"AnimeFactoryV49UnifiedRelease/1","version":49,
  "originalV19SHA256":digest(V19.read_bytes()),
  "immediateParentV48SHA256":digest(oldbytes),
  "preserves":"complete V48 ZIP, historical source V19–V48, original V19",
  "workingStudio":"six-stage 2D unified editor with manual review; no false QA clearance",
  "files":[{"path":n,"bytes":len(content),"sha256":digest(content)}
   for n,content in sorted(files.items())]}
 files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(destination).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for n,content in sorted(files.items()):z.writestr(n,content)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise RuntimeError("CRC32 error")
  m=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(z.namelist())!=len(m["files"])+1:raise RuntimeError("File inventory changed")
  for rec in m["files"]:
   item=z.read(rec["path"])
   if len(item)!=rec["bytes"] or digest(item)!=rec["sha256"]:
    raise RuntimeError("V49 SHA mismatch "+rec["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 changed")
  if digest(z.read("backup/"+previous.NAME))!=m["immediateParentV48SHA256"]:
   raise RuntimeError("Full parent V48 ZIP changed")
  for name in ("source/V45_art_assets_v45.js","source/V46_animation_engine_v46.js",
    "source/V47_portable_voice_v47.js","source/V48_episode_engine_v48.js",
    "source/V49_unified_studio_v49.js","SETUP_BATCH_WINDOWS.bat",
    "RUN_BATCH_WINDOWS.bat","source/V48_render_anime_v48.py"):
   if name not in z.namelist():raise RuntimeError("Missing "+name)
  if HTML not in z.namelist():raise RuntimeError("Missing unified editor HTML")
 if out.stat().st_size>95*1024*1024:
  raise RuntimeError("Archive exceeds direct GitHub 100 MiB file limit")
 print("V49 WINDOWS ZIP VERIFIED",out,out.stat().st_size,len(files),
  "SHA256",digest(out.read_bytes()))
 return out
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 a=p.parse_args()
 if a.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as td:assemble(Path(td)/NAME)
 else:assemble(a.out)
if __name__=="__main__":main()
