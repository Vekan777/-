#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V40 standalone Windows ZIP; backup V39 and all V19–V39 sources intact."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v39.py"
BUILDER=ROOT/"anime-factory/v40/build_art_v40.py"
NAME="AI_ANIME_FACTORY_V40_CHARACTER_ART_WINDOWS.zip"
HTML="AI_Anime_Factory_V40_CHARACTER_ART.html"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=load(PARENT,"v39release")
builder=load(BUILDER,"v40art")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V40_CHARACTER_ART.html"\r\n'
INTRO="""AI ANIME FACTORY V40 — CHARACTER ART / WINDOWS 10
=================================================
1. Полностью распакуйте ZIP в новую папку, не поверх V39.
2. Откройте RUN_WINDOWS.bat либо HTML в Chrome/Edge.
3. Сохраните полный JSON проекта во вкладке «Аудит V30».
4. В «Рисовка V40» выберите персонажа и профиль.
5. Настройте глаза, волосы, контуры, костюм и блики. Сохраните.
6. Сравните настоящие кадры до/после на одном таймкоде.
7. Скачайте PNG и JSON художественных настроек.
8. Чтобы записать WebM с новой рисовкой и звуком, перейдите
   в «Звук / экспорт V36», подключите собственные WAV/MP3/OGG.
9. Для MP4 используйте CONVERT_MP4_WINDOWS.bat и установленный
   FFmpeg (PATH или tools\\ffmpeg\\bin\\ffmpeg.exe).
10. Создайте новый полный резерв JSON проекта.

V40 изменяет векторные 2D детали, не авторские PNG/PSD.
Не является 3D-анимацией или автоматически сгенерированным аниме.
Система V19–V39 и полный архив V39 сохранены.
Подробная инструкция source/V40_README_RU.md.
"""
def sha(b):return hashlib.sha256(b).hexdigest()
def assemble(dest):
 with tempfile.TemporaryDirectory(prefix="anime-v40-") as tmp:
  previous=Path(tmp)/old.NAME
  old.assemble(previous)
  parent_bytes=previous.read_bytes()
  with zipfile.ZipFile(previous) as z:
   if z.testzip():raise RuntimeError("V39 ZIP CRC32 failed")
   entries={n:z.read(n) for n in z.namelist() if n!="BUILD_MANIFEST.json"}
 entries["backup/"+old.NAME]=parent_bytes
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=INTRO.encode("utf-8")
 for rel in ("anime-factory/v40/character_art_v40.js",
  "anime-factory/v40/build_art_v40.py",
  "anime-factory/v40/README_RU.md",
  "scripts/build_anime_v40.py",
  "tests/test_anime_v40.py","tests/smoke_browser_v40.py"):
  src=ROOT/rel
  if not src.is_file():raise FileNotFoundError("Missing "+str(src))
  entries["source/V40_"+src.name]=src.read_bytes()
 doc={"schema":"AnimeFactoryV40Release/1","version":40,
  "parentV39Sha256":sha(parent_bytes),
  "originalV19Sha256":sha(V19.read_bytes()),
  "preservation":"V19 original, complete V20–V39 source and full V39 parent ZIP",
  "files":[{"path":k,"bytes":len(v),"sha256":sha(v)} for k,v in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(doc,ensure_ascii=False,indent=2).encode("utf-8")
 dest=Path(dest).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.unlink()
 with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 with zipfile.ZipFile(dest) as z:
  if z.testzip():raise RuntimeError("V40 ZIP CRC32 mismatch")
  if set(z.namelist())!=set(entries):raise RuntimeError("ZIP inventory mismatch")
  saved=json.loads(z.read("BUILD_MANIFEST.json"))
  for item in saved["files"]:
   data=z.read(item["path"])
   if len(data)!=item["bytes"] or sha(data)!=item["sha256"]:
    raise RuntimeError("V40 SHA256 failure "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 overwritten")
  if sha(z.read("backup/"+old.NAME))!=saved["parentV39Sha256"]:
   raise RuntimeError("Parent V39 ZIP modified")
  for path in ("source/assembly_v35.js","source/audio_v36.js",
   "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js","source/V39_performance_v39.js",
   "source/V40_character_art_v40.js","CONVERT_MP4_WINDOWS.bat"):
   if path not in z.namelist():raise RuntimeError("Historical source missing "+path)
 print("V40 ZIP VERIFIED",dest,"bytes",dest.stat().st_size,
  "entries",len(entries),"sha256",sha(dest.read_bytes()))
 return dest
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 a=p.parse_args()
 if a.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as d:assemble(Path(d)/NAME)
 else:assemble(a.out)
if __name__=="__main__":main()
