#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V48 Windows delivery: full V47 backup, source continuity and batch render launcher."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PREVIOUS=ROOT/"scripts/build_anime_v47.py"
BUILDER=ROOT/"anime-factory/v48/build_episode_v48.py"
NAME="AI_ANIME_FACTORY_V48_EPISODE_ENGINE_WINDOWS.zip"
HTML="AI_Anime_Factory_V48_EPISODE_ENGINE.html"
def load(path,name):
 sp=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
parent=load(PREVIOUS,"anime_v47_episode_parent")
builder=load(BUILDER,"anime_v48_episode_builder")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V48_EPISODE_ENGINE.html"\r\n'
SETUP=r"""@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
py -3 --version >nul 2>&1
if errorlevel 1 (
 set "PYTHON=python"
) else (
 set "PYTHON=py -3"
)
%PYTHON% --version
if errorlevel 1 (
 echo Python not found. Download Python 3.11+ x64 from https://www.python.org/downloads/windows/
 pause
 exit /b 1
)
echo Installing Python Playwright 1.56.0 and Chromium browser; internet is required.
%PYTHON% -m pip install --user "playwright==1.56.0"
if errorlevel 1 (echo Playwright install failed & pause & exit /b 1)
%PYTHON% -m playwright install chromium
if errorlevel 1 (echo Chromium install failed & pause & exit /b 1)
echo Installation complete. FFmpeg+FFprobe also required for verified MP4.
pause
"""
BATCH=r"""@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist "PROJECT_INPUT.json" (
 echo Missing PROJECT_INPUT.json! Export full portable JSON from the V48 editor.
 echo Rename it to PROJECT_INPUT.json and place next to RUN_BATCH_WINDOWS.bat.
 pause
 exit /b 2
)
if exist "tools\ffmpeg\bin\ffmpeg.exe" (
 set "PATH=%CD%\tools\ffmpeg\bin;%PATH%"
)
py -3 --version >nul 2>&1
if errorlevel 1 (
 set "PYTHON=python"
) else (
 set "PYTHON=py -3"
)
%PYTHON% --version
if errorlevel 1 (echo Install Python 3.11+ x64 first. & pause & exit /b 1)
%PYTHON% "source\V48_render_anime_v48.py" --html "AI_Anime_Factory_V48_EPISODE_ENGINE.html" --project "PROJECT_INPUT.json" --out "OUTPUT" --fps 6 --mp4
if errorlevel 1 (
 echo Render error: see V48_RENDER_CHECKPOINT.json under OUTPUT if present.
 pause
 exit /b 1
)
echo Finished: WebM, H264/AAC MP4 and SRT/VTT are under OUTPUT.
pause
"""
README="""AI ANIME FACTORY V48 / EPISODE PRODUCTION ENGINE / WINDOWS
===========================================================
1. Extract the ENTIRE ZIP into a NEW folder.
2. Double-click RUN_WINDOWS.bat. Chrome/Edge opens the full editor.
3. Go to "Монтаж серий V48" for full timeline preview, credits,
   subtitle exports (SRT/VTT), soundtrack and one-episode WebM.
4. Export FULL portable project JSON with your pictures and audio,
   rename file to PROJECT_INPUT.json, put it next to BAT scripts.
5. Install Python 3.11+ x64 once (https://www.python.org/downloads/windows/).
6. Run SETUP_BATCH_WINDOWS.bat once with internet: Playwright Chromium.
7. Put ffmpeg.exe + ffprobe.exe in tools\\ffmpeg\\bin\\ or PATH.
8. Run RUN_BATCH_WINDOWS.bat for sequential WebM+MP4, subtitles,
   checksum checkpoint and automatic resume from completed episodes.
9. Completed videos appear in OUTPUT folder; restart BAT after failure.
10. Original story, V19 and all V20–V47 are retained.
V48 is real-time 2D Canvas recording, not claimed to be a professional
20-minute broadcast-anime render or automatic high-end art generator.
V49 Unified, V50 Deep QA remain unfinished, 3D after V50 acceptance.
Full Russian guide: source/V48_README_RU.md
"""
def digest(data):return hashlib.sha256(data).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v48-") as tmp:
  prev=Path(tmp)/parent.NAME
  parent.assemble(prev)
  previous=prev.read_bytes()
  with zipfile.ZipFile(prev) as z:
   if z.testzip():raise RuntimeError("V47 parent ZIP has bad CRC32")
   files={name:z.read(name) for name in z.namelist()
    if name!="BUILD_MANIFEST.json" and
    not(name.startswith("backup/") and name.lower().endswith(".zip"))}
 files["backup/"+parent.NAME]=previous
 files[HTML]=builder.build().encode("utf-8")
 files["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 files["SETUP_BATCH_WINDOWS.bat"]=SETUP.encode("utf-8")
 files["RUN_BATCH_WINDOWS.bat"]=BATCH.encode("utf-8")
 files["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v48/episode_engine_v48.js",
   "anime-factory/v48/build_episode_v48.py",
   "anime-factory/v48/README_RU.md",
   "scripts/build_anime_v48.py","scripts/render_anime_v48.py",
   "tests/test_anime_v48.py","tests/smoke_browser_v48.py",
   "anime-factory/roadmap/2D_FINAL_TO_V50_RU.md"):
  file=ROOT/rel
  if not file.is_file():raise FileNotFoundError(file)
  files["source/V48_"+file.name]=file.read_bytes()
 manifest={"schema":"AnimeFactoryV48EpisodeRelease/1","version":48,
  "originalV19SHA256":digest(V19.read_bytes()),
  "immediateParentV47SHA256":digest(previous),
  "preservation":"complete V47 ZIP; all V19–V47 source; original V19",
  "batch":"per-completed-episode SHA256 checkpoint; FFprobe verified WebM+MP4 and SRT/VTT",
  "files":[{"path":n,"bytes":len(b),"sha256":digest(b)}
   for n,b in sorted(files.items())]}
 files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(destination).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for n,b in sorted(files.items()):z.writestr(n,b)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise RuntimeError("V48 CRC32 failure")
  m=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(z.namelist())!=len(m["files"])+1:raise RuntimeError("ZIP inventory mismatch")
  for item in m["files"]:
   data=z.read(item["path"])
   if len(data)!=item["bytes"] or digest(data)!=item["sha256"]:
    raise RuntimeError("SHA256 mismatch "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 content changed")
  if digest(z.read("backup/"+parent.NAME))!=m["immediateParentV47SHA256"]:
   raise RuntimeError("Original complete V47 backup changed")
  for n in ("source/V45_art_assets_v45.js","source/V46_animation_engine_v46.js",
   "source/V47_portable_voice_v47.js","source/V48_episode_engine_v48.js",
   "source/V48_render_anime_v48.py","SETUP_BATCH_WINDOWS.bat",
   "RUN_BATCH_WINDOWS.bat","CONVERT_MP4_WINDOWS.bat"):
   if n not in z.namelist():raise RuntimeError("Missing "+n)
 if out.stat().st_size>95*1024*1024:
  raise RuntimeError("GitHub direct file limit; avoid recursively nested ZIPs")
 print("V48 WINDOWS ZIP VERIFIED",out,out.stat().st_size,len(files),
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
