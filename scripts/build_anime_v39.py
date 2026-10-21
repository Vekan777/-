#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V39 standalone Windows ZIP; backup V38 and all V19–V38 sources intact."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v38.py"
BUILDER=ROOT/"anime-factory/v39/build_performance_v39.py"
NAME="AI_ANIME_FACTORY_V39_CHARACTER_ACTION_WINDOWS.zip"
HTML="AI_Anime_Factory_V39_CHARACTER_ACTION.html"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=load(PARENT,"v38release")
builder=load(BUILDER,"v39performance")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V39_CHARACTER_ACTION.html"\r\n'
INTRO="""AI ANIME FACTORY V39 — CHARACTER ACTION / WINDOWS 10
====================================================
1. Распакуйте полностью в отдельную папку, НЕ поверх V38.
2. Дважды нажмите RUN_WINDOWS.bat (или откройте HTML в Chrome/Edge).
3. Во вкладке «Аудит V30» сохраните полный проект в JSON.
4. Во вкладке «Персонажи и бой V39» выберите боевую сцену.
5. Отрегулируйте энергию движения, выражения лица, подготовку
   к удару, инерцию и визуальные эффекты; нажмите «Сохранить».
6. Проверьте перед/после: выключите и включите V39, сохраните.
7. Скачайте 4 PNG, JSON настроек, просмотрите аудит.
8. Для WebM со звуком откройте «Звук / экспорт V36», повторно
   приложите собственные WAV/MP3/OGG и запишите готовый эпизод.
9. Для MP4 перетащите WebM на CONVERT_MP4_WINDOWS.bat;
   ffmpeg.exe в tools\\ffmpeg\\bin\\ или PATH.
10. Сделайте резерв полного JSON. Историю проекта не удаляйте.

Движения — процедурный 2D риг, НЕ 3D и не профессиональный
аниме-рендер. Звуковые файлы НЕ хранятся в проектном JSON.
Рекомендуется 640x360 и 6 FPS для ноутбука с 8 ГБ RAM.
Полная инструкция: source/V39_README_RU.md.
Архив V38 и оригинальный V19 сохранены в backup/.
"""
def sha(b):return hashlib.sha256(b).hexdigest()
def assemble(dest):
 with tempfile.TemporaryDirectory(prefix="anime-v39-") as tmp:
  previous=Path(tmp)/old.NAME
  old.assemble(previous)
  parent_bytes=previous.read_bytes()
  with zipfile.ZipFile(previous) as z:
   if z.testzip():raise RuntimeError("V38 ZIP CRC32 failed")
   entries={n:z.read(n) for n in z.namelist() if n!="BUILD_MANIFEST.json"}
 entries["backup/"+old.NAME]=parent_bytes
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=INTRO.encode("utf-8")
 for rel in ("anime-factory/v39/performance_v39.js",
  "anime-factory/v39/build_performance_v39.py",
  "anime-factory/v39/README_RU.md",
  "scripts/build_anime_v39.py",
  "tests/test_anime_v39.py","tests/smoke_browser_v39.py"):
  src=ROOT/rel
  if not src.is_file():raise FileNotFoundError("Missing "+str(src))
  entries["source/V39_"+src.name]=src.read_bytes()
 doc={"schema":"AnimeFactoryV39Release/1","version":39,
  "parentV38Sha256":sha(parent_bytes),
  "originalV19Sha256":sha(V19.read_bytes()),
  "preservation":"V19 original, complete V20–V38 source and full V38 parent ZIP",
  "files":[{"path":k,"bytes":len(v),"sha256":sha(v)} for k,v in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(doc,ensure_ascii=False,indent=2).encode("utf-8")
 dest=Path(dest).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.unlink()
 with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 with zipfile.ZipFile(dest) as z:
  if z.testzip():raise RuntimeError("V39 ZIP CRC32 mismatch")
  if set(z.namelist())!=set(entries):raise RuntimeError("ZIP inventory mismatch")
  saved=json.loads(z.read("BUILD_MANIFEST.json"))
  for item in saved["files"]:
   data=z.read(item["path"])
   if len(data)!=item["bytes"] or sha(data)!=item["sha256"]:
    raise RuntimeError("V39 SHA256 failure "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 overwritten")
  if sha(z.read("backup/"+old.NAME))!=saved["parentV38Sha256"]:
   raise RuntimeError("Parent V38 ZIP modified")
  for path in ("source/assembly_v35.js","source/audio_v36.js",
   "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
   "source/V39_performance_v39.js","CONVERT_MP4_WINDOWS.bat"):
   if path not in z.namelist():raise RuntimeError("Historical source missing "+path)
 print("V39 ZIP VERIFIED",dest,"bytes",dest.stat().st_size,
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
