#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verified V42 standalone Windows ZIP, preserving complete V41 release."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v41.py"
BUILDER=ROOT/"anime-factory/v42/build_stage_v42.py"
NAME="AI_ANIME_FACTORY_V42_STAGE_DEPTH_WINDOWS.zip"
HTML="AI_Anime_Factory_V42_STAGE_DEPTH.html"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
parent=load(PARENT,"v41release")
builder=load(BUILDER,"v42stage")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V42_STAGE_DEPTH.html"\r\n'
README="""AI ANIME FACTORY V42 — СВЕТ И ГЛУБИНА / WINDOWS 10
====================================================
1. Полностью распакуйте ZIP в НОВУЮ папку.
2. Дважды нажмите RUN_WINDOWS.bat (либо HTML в Chrome/Edge).
3. На вкладке «Аудит V30» экспортируйте полный резерв JSON.
4. Откройте «Свет и атмосфера V42», выберите эпизод и сцену.
5. Выберите рассвет, грозу, угли или ночь; настройте глубину,
   свет, атмосферу, частицы и ветер, нажмите «Сохранить».
6. Проверьте кадры и видео, скачайте 4 PNG и настройки JSON.
7. Для WebM со звуком откройте «Звук / экспорт V36», снова
   прикрепите WAV/MP3/OGG, запишите видеосерию.
8. Для MP4 используйте CONVERT_MP4_WINDOWS.bat и FFmpeg
   по пути tools\\ffmpeg\\bin\\ffmpeg.exe или через PATH.
9. Сохраните полный JSON после работы. Аудиофайлы отдельно.

Весь V19–V41 сохранён; полный V41 ZIP лежит в backup/.
Настоящая 2D атмосфера, НЕ 3D-сцена или профессиональный рендер.
Для 8 ГБ ОЗУ и GT740M начните с 640x360 и 6 FPS.
Подробная инструкция: source/V42_README_RU.md.
"""
def sha(data):return hashlib.sha256(data).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v42-") as work:
  prev=Path(work)/parent.NAME
  parent.assemble(prev)
  parent_blob=prev.read_bytes()
  with zipfile.ZipFile(prev) as z:
   if z.testzip():raise RuntimeError("V41 parent ZIP invalid")
   entries={name:z.read(name) for name in z.namelist()
            if name!="BUILD_MANIFEST.json"}
 entries["backup/"+parent.NAME]=parent_blob
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v42/stage_v42.js",
             "anime-factory/v42/build_stage_v42.py",
             "anime-factory/v42/README_RU.md",
             "scripts/build_anime_v42.py",
             "tests/test_anime_v42.py","tests/smoke_browser_v42.py"):
  src=ROOT/rel
  if not src.is_file():raise FileNotFoundError(str(src))
  entries["source/V42_"+src.name]=src.read_bytes()
 manifest={"schema":"AnimeFactoryV42Release/1","version":42,
  "parentV41Sha256":sha(parent_blob),
  "originalV19Sha256":sha(V19.read_bytes()),
  "preservation":"untouched V19, original V20-V41 source, complete V41 ZIP",
  "files":[{"path":name,"bytes":len(data),"sha256":sha(data)}
           for name,data in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(destination).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                      compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise RuntimeError("V42 ZIP CRC32 failure")
  doc=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(doc["files"])+1!=len(z.namelist()):raise RuntimeError("ZIP inventory mismatch")
  for item in doc["files"]:
   blob=z.read(item["path"])
   if sha(blob)!=item["sha256"] or len(blob)!=item["bytes"]:
    raise RuntimeError("V42 SHA256 mismatch "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("V19 was altered")
  if sha(z.read("backup/"+parent.NAME))!=doc["parentV41Sha256"]:
   raise RuntimeError("V41 original ZIP was altered")
  for name in ("source/assembly_v35.js","source/audio_v36.js",
   "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
   "source/V39_performance_v39.js","source/V40_character_art_v40.js",
   "source/V41_silhouette_v41.js","source/V42_stage_v42.js",
   "CONVERT_MP4_WINDOWS.bat"):
   if name not in z.namelist():raise RuntimeError("Missing historical source: "+name)
 print("V42 ZIP VERIFIED",out,out.stat().st_size,len(entries),sha(out.read_bytes()))
 return out
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--out",default=str(ROOT/"dist"/NAME))
 cli.add_argument("--selftest",action="store_true")
 args=cli.parse_args()
 if args.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as temp:assemble(Path(temp)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
