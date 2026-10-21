#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V38 distributable preserving V19–V37 and embedding original V37 ZIP intact."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v37.py"
BUILDER=ROOT/"anime-factory/v38/build_cinematic_v38.py"
NAME="AI_ANIME_FACTORY_V38_CINEMATIC_FINISHING_WINDOWS.zip"
HTML="AI_Anime_Factory_V38_CINEMATIC_FINISHING.html"
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
old=load(PARENT,"v37_release")
editor=load(BUILDER,"v38_editor")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V38_CINEMATIC_FINISHING.html"\r\n'
INTRO="""AI ANIME FACTORY V38 — CINEMATIC FINISHING / WINDOWS 10
=================================================
Весь предыдущий путь V19–V37 остаётся в редакторе.
1. Полностью распакуйте этот ZIP в новую папку.
2. Откройте RUN_WINDOWS.bat (или главный HTML в Chrome/Edge).
3. Скачайте полный резерв JSON во вкладке «Аудит V30».
4. Перейдите в «Кинокамера V38», выберите эпизод и сцену.
5. Отрегулируйте крупность, движение камеры, яркость, контраст,
   цвет, насыщенность, затемнение краёв и полосы. Сохраните.
6. Просмотрите всю серию, экспортируйте 4 настоящих кадра PNG,
   JSON-план монтажа и аудит кинематографии.
7. Для WebM со звуком и субтитрами откройте «Звук / экспорт V36».
   Повторно приложите аудиофайлы WAV/MP3/OGG при необходимости.
8. Для MP4 перетащите скачанный WebM на CONVERT_MP4_WINDOWS.bat.
   FFmpeg положите в tools\\ffmpeg\\bin\\ffmpeg.exe либо PATH.
9. Сделайте резервную копию полного JSON после монтажа.

На 8GB RAM/GT740M начните с 640x360, 6 FPS.
Это процедурное 2D кино, НЕ 3D нейрорендер.
Аудиофайлы не сохраняются внутри JSON/HTML.
Полная инструкция в source/V38_README_RU.md.
Проверены CRC32, SHA256, V19 оригинал и вложенный архив V37.
"""
def sha(data):return hashlib.sha256(data).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v38-") as tmp:
  prev=Path(tmp)/old.NAME
  old.assemble(prev)
  parent_bytes=prev.read_bytes()
  with zipfile.ZipFile(prev) as zip_parent:
   if zip_parent.testzip():raise RuntimeError("Parent V37 archive corrupt")
   entries={n:zip_parent.read(n) for n in zip_parent.namelist()
            if n!="BUILD_MANIFEST.json"}
 entries["backup/"+old.NAME]=parent_bytes
 entries[HTML]=editor.build().encode("utf-8")
 entries["README_RU.txt"]=INTRO.encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 for rel in ("anime-factory/v38/cinematic_v38.js",
  "anime-factory/v38/build_cinematic_v38.py","anime-factory/v38/README_RU.md",
  "scripts/build_anime_v38.py","tests/test_anime_v38.py","tests/smoke_browser_v38.py"):
  p=ROOT/rel
  if not p.is_file():raise FileNotFoundError("Missing V38 source "+str(p))
  entries["source/V38_"+p.name]=p.read_bytes()
 manifest={"schema":"AnimeFactoryV38Release/1","version":38,
  "originalV19Sha256":sha(V19.read_bytes()),
  "parentV37ZipSha256":sha(parent_bytes),
  "sourcePipeline":"preserved V19–V37 + additive V38",
  "files":[{"path":p,"bytes":len(d),"sha256":sha(d)}
           for p,d in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 dest=Path(destination).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.unlink()
 with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,
                      compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 with zipfile.ZipFile(dest) as z:
  if z.testzip():raise RuntimeError("V38 ZIP CRC32 mismatch")
  if set(z.namelist())!=set(entries):raise RuntimeError("V38 ZIP inventory error")
  doc=json.loads(z.read("BUILD_MANIFEST.json"))
  for item in doc["files"]:
   blob=z.read(item["path"])
   if len(blob)!=item["bytes"] or sha(blob)!=item["sha256"]:
    raise RuntimeError("V38 file integrity mismatch: "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("V19 source changed")
  if sha(z.read("backup/"+old.NAME))!=doc["parentV37ZipSha256"]:
   raise RuntimeError("V37 parent ZIP changed")
  for required in ("source/assembly_v35.js","source/audio_v36.js",
                   "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
                   "CONVERT_MP4_WINDOWS.bat"):
   if required not in z.namelist():raise RuntimeError("Missing "+required)
 print("V38 ZIP VERIFIED",dest,"bytes",dest.stat().st_size,
       "entries",len(entries),"sha256",sha(dest.read_bytes()))
 return dest
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--selftest",action="store_true")
 cli.add_argument("--out",default=str(ROOT/"dist"/NAME))
 args=cli.parse_args()
 if args.selftest:
  editor.selftest()
  with tempfile.TemporaryDirectory() as t:assemble(Path(t)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
