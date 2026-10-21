#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V46 Windows distribution: full V45 source, cutout editor, engine and verified ZIP."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v45.py"
BUILDER=ROOT/"anime-factory/v46/build_animation_v46.py"
NAME="AI_ANIME_FACTORY_V46_ANIMATION_ENGINE_WINDOWS.zip"
HTML="AI_Anime_Factory_V46_ANIMATION_ENGINE.html"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
parent=load(PARENT,"anime_v45_release")
builder=load(BUILDER,"anime_v46_art")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V46_ANIMATION_ENGINE.html"\r\n'
README="""AI ANIME FACTORY V46 — ANIMATION ENGINE / WINDOWS 10
======================================================
1. Распакуйте ZIP в НОВУЮ папку. Запустите RUN_WINDOWS.bat.
2. Откройте «2D Анимация V46», выберите серию, сцену, роль и слой.
3. Для начала примените «Ходьба», «Защита», «Взмах»,
   «Поклон» или «Тёплый жест» (35 ключей для 7 частей тела).
4. Переместите шкалу времени и установите X/Y/угол/масштаб,
   нажмите «Записать/обновить ключ».
5. Включите полупрозрачные соседние кадры (onion skin).
6. Сохраните анимационный клип в библиотеку, примените к сцене.
7. Скачайте лист реальных PNG, JSON клипов и полный резерв JSON.
8. WebM со звуком: «Звук / экспорт V36», прикрепите WAV/MP3.
9. MP4: CONVERT_MP4_WINDOWS.bat и ffmpeg.exe в PATH/ tools.
V19–V45 сохранены. V47 озвучка, V48 серии, V49 unified, V50 QA
пока не объявлены готовыми. 3D — отдельно после приёмки V50.
Подробности: source/V46_README_RU.md
"""
def sha(d):return hashlib.sha256(d).hexdigest()
def assemble(dest):
 with tempfile.TemporaryDirectory(prefix="anime-v46-") as td:
  prev=Path(td)/parent.NAME
  parent.assemble(prev)
  old=prev.read_bytes()
  with zipfile.ZipFile(prev) as z:
   if z.testzip():raise ValueError("Previous V45 CRC32 failed")
   files={name:z.read(name) for name in z.namelist()
    if name!="BUILD_MANIFEST.json"}
 files["backup/"+parent.NAME]=old
 files[HTML]=builder.build().encode("utf-8")
 files["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 files["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v46/animation_engine_v46.js",
  "anime-factory/v46/build_animation_v46.py",
  "anime-factory/v46/README_RU.md",
  "scripts/build_anime_v46.py","tests/test_anime_v46.py",
  "tests/smoke_browser_v46.py",
  "anime-factory/roadmap/2D_FINAL_TO_V50_RU.md"):
  path=ROOT/rel
  if not path.is_file():raise FileNotFoundError(str(path))
  files["source/V46_"+path.name]=path.read_bytes()
 manifest={"schema":"AnimeFactoryV46AnimationRelease/1","version":46,
  "oldV45SHA256":sha(old),"originalV19SHA256":sha(V19.read_bytes()),
  "preserves":"original V19 + all V20-V45 sources + complete V45 release",
  "development":"V46 editable keyframes and clips; V47–V50 not claimed finished",
  "files":[{"path":name,"bytes":len(content),"sha256":sha(content)}
   for name,content in sorted(files.items())]}
 files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(dest).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,
  allowZip64=True) as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise ValueError("V46 CRC32 failed")
  doc=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(doc["files"])+1!=len(z.namelist()):raise ValueError("Invalid ZIP inventory")
  for item in doc["files"]:
   raw=z.read(item["path"])
   if sha(raw)!=item["sha256"] or len(raw)!=item["bytes"]:
    raise ValueError("Bad SHA256 on "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise ValueError("Original V19 was overwritten")
  if sha(z.read("backup/"+parent.NAME))!=doc["oldV45SHA256"]:
   raise ValueError("V45 backup checksum failed")
  for name in ("source/assembly_v35.js","source/audio_v36.js",
    "source/V40_character_art_v40.js","source/V41_silhouette_v41.js",
    "source/V42_stage_v42.js","source/V43_director_v43.js",
    "source/V44_keyposes_v44.js","source/V45_anime_production_engine_v45.js",
    "source/V45_art_assets_v45.js","source/V46_animation_engine_v46.js",
    "CONVERT_MP4_WINDOWS.bat"):
   if name not in z.namelist():raise ValueError("Historical source missing: "+name)
 if out.stat().st_size>90*1024*1024:raise ValueError("V46 package exceeds GitHub file cap")
 print("V46 ZIP VERIFIED",out,out.stat().st_size,
  len(files),"SHA256",sha(out.read_bytes()))
 return out
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 p.add_argument("--selftest",action="store_true")
 args=p.parse_args()
 if args.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as td:assemble(Path(td)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
