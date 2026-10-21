#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V47 verified Windows ZIP; complete V46 parent, V19 original, SHA/CRC and help."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PREVIOUS=ROOT/"scripts/build_anime_v46.py"
BUILDER=ROOT/"anime-factory/v47/build_voice_v47.py"
NAME="AI_ANIME_FACTORY_V47_PORTABLE_VOICE_WINDOWS.zip"
HTML="AI_Anime_Factory_V47_PORTABLE_VOICE.html"
def load(path,name):
 sp=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
parent=load(PREVIOUS,"anime_v46_voice_parent")
builder=load(BUILDER,"anime_v47_builder")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V47_PORTABLE_VOICE.html"\r\n'
README="""AI ANIME FACTORY V47 — VOICE/LIP SYNC / WINDOWS 10
====================================================
1. Полностью распакуйте ZIP в НОВУЮ папку.
2. Запустите RUN_WINDOWS.bat, откройте HTML в Chrome/Edge.
3. Сначала сделайте резерв старого полного JSON проекта.
4. Откройте «Озвучка и губы V47», выберите сцену и слот звука.
5. Импортируйте WAV/MP3/OGG/WebM/M4A до 1.5 МБ на файл.
6. Для голоса выберите говорящего и включите движение рта.
7. Настройте громкость/смещение и сохраните.
8. Скачайте ПОЛНЫЙ проект JSON с аудиобайтами и PNG.
9. Перезапустите страницу, проверьте экспорт без повторной загрузки.
10. В «Звук / экспорт V36» создайте настоящий WebM со звуком.
11. MP4: CONVERT_MP4_WINDOWS.bat + ffmpeg.exe в PATH / tools.
V47 — амплитудный lip sync, НЕ настоящий фонемный анализ.
Длинные сериалы и потоковый MP4 будут в V48; V49 unified, V50 QA.
Все исходники V19–V46 сохранены, ZIP V46 внутри backup/.
Подробности: source/V47_README_RU.md.
"""
def digest(data):return hashlib.sha256(data).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v47-") as tmp:
  prev=Path(tmp)/parent.NAME
  parent.assemble(prev)
  prev_bytes=prev.read_bytes()
  with zipfile.ZipFile(prev) as z:
   if z.testzip():raise RuntimeError("V46 ZIP CRC32 mismatch")
   files={name:z.read(name) for name in z.namelist()
    if name!="BUILD_MANIFEST.json" and
    not(name.startswith("backup/") and name.lower().endswith(".zip"))}
 # Complete immediate parent V46 included, but avoid recursively copying V45
 # archives inside V46 to stay safely under GitHub's 100 MiB file cap.
 files["backup/"+parent.NAME]=prev_bytes
 files[HTML]=builder.build().encode("utf-8")
 files["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 files["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v47/portable_voice_v47.js",
   "anime-factory/v47/build_voice_v47.py",
   "anime-factory/v47/README_RU.md",
   "scripts/build_anime_v47.py",
   "tests/test_anime_v47.py","tests/smoke_browser_v47.py"):
  p=ROOT/rel
  if not p.is_file():raise FileNotFoundError(str(p))
  files["source/V47_"+p.name]=p.read_bytes()
 manifest={"schema":"AnimeFactoryV47VoiceRelease/1","version":47,
   "immediateParentV46SHA256":digest(prev_bytes),
   "originalV19SHA256":digest(V19.read_bytes()),
   "preserves":"V19 original and all V19–V46 sources, complete V46 parent ZIP",
   "media":"Embedded clips in user's own portable scene JSON, no bundled third-party voice",
   "files":[{"path":name,"size":len(data),"sha256":digest(data)}
    for name,data in sorted(files.items())]}
 files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(destination).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise RuntimeError("V47 CRC32 failed")
  m=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(m["files"])+1!=len(z.namelist()):raise RuntimeError("V47 inventory differs")
  for row in m["files"]:
   value=z.read(row["path"])
   if digest(value)!=row["sha256"] or len(value)!=row["size"]:
    raise RuntimeError("Bad SHA/size "+row["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("V19 changed")
  if digest(z.read("backup/"+parent.NAME))!=m["immediateParentV46SHA256"]:
   raise RuntimeError("V46 full ZIP changed")
  for file in ("source/V40_character_art_v40.js",
   "source/V41_silhouette_v41.js","source/V42_stage_v42.js",
   "source/V43_director_v43.js","source/V44_keyposes_v44.js",
   "source/V45_art_assets_v45.js","source/V46_animation_engine_v46.js",
   "source/V47_portable_voice_v47.js","CONVERT_MP4_WINDOWS.bat"):
   if file not in z.namelist():raise RuntimeError("Missing "+file)
 if out.stat().st_size>95*1024*1024:raise RuntimeError("V47 exceeds direct GitHub storage limit")
 print("V47 ZIP VERIFIED",out,out.stat().st_size,len(files),
  "SHA256",digest(out.read_bytes()))
 return out
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--selftest",action="store_true")
 a.add_argument("--out",default=str(ROOT/"dist"/NAME))
 opt=a.parse_args()
 if opt.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as td:assemble(Path(td)/NAME)
 else:assemble(opt.out)
if __name__=="__main__":main()
