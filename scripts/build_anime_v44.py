#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V44 verified Windows release with all old SOURCE and lean external full-ZIP backups.

GitHub prohibits files >100 MiB: V43 is already ~84 MiB. Do not recursively nest
that executable archive in V44 or make source/downloads impossible. Retain
all V19–V43 sources and original V19 verbatim; link full immutable V43 Releases.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v43.py"
BUILDER=ROOT/"anime-factory/v44/build_keyposes_v44.py"
NAME="AI_ANIME_FACTORY_V44_TRUE_KEYPOSES_WINDOWS.zip"
HTML="AI_Anime_Factory_V44_TRUE_KEYPOSES.html"
FULL_PREVIOUS="https://github.com/Vekan777/-/releases/download/anime-factory-v43/AI_ANIME_FACTORY_V43_ACTION_DIRECTOR_WINDOWS.zip"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
parent=load(PARENT,"v43source_archive")
builder=load(BUILDER,"v44keypose")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V44_TRUE_KEYPOSES.html"\r\n'
README="""AI ANIME FACTORY V44 — TRUE ACTOR KEYPOSES / WINDOWS 10
=========================================================
1. Извлеките весь ZIP в НОВУЮ папку.
2. Запустите RUN_WINDOWS.bat или откройте HTML в Chrome/Edge.
3. Сохраните полный резерв проекта JSON в «Аудит V30».
4. В «Позы персонажей V44» выберите серию и боевую сцену.
5. Настройте стойку, шаг, руки, блок, инерцию и движения ткани.
6. Сохраните. Сравните до/после на одном времени, скачайте PNG.
7. Для фильма со звуком: «Звук / экспорт V36», WAV/MP3/OGG,
   затем «Записать V44 с позами персонажей» (настоящий WebM).
8. Для MP4: CONVERT_MP4_WINDOWS.bat и ffmpeg.exe
   в tools\\ffmpeg\\bin\\ или PATH.
9. Сохраните полный резерв JSON и свои аудиофайлы отдельно.

В архиве есть ВСЕ исходники редакторов V19–V43 и оригинальный V19.
Полный предыдущий ZIP V43 не вложен из-за GitHub 100MiB file cap:
%s
Объединённая V7 также сохраняет исторические Windows ZIP.
V44 — процедурный 2D-риг, не 3D и не motion capture.
Полная инструкция: source/V44_README_RU.md.
"""%FULL_PREVIOUS
def sha(data):return hashlib.sha256(data).hexdigest()
def assemble(target):
 with tempfile.TemporaryDirectory(prefix="anime-v44-") as td:
  old=Path(td)/parent.NAME
  parent.assemble(old)
  parent_data=old.read_bytes()
  with zipfile.ZipFile(old) as z:
   if z.testzip():raise RuntimeError("V43 parent CRC failed")
   # Keep *all* text/image/source assets and the original V19. Only nested
   # historical binary ZIP copies are excluded; their immutable download
   # paths are listed below.
   entries={name:z.read(name) for name in z.namelist()
     if name!="BUILD_MANIFEST.json" and
     not(name.startswith("backup/") and name.lower().endswith(".zip"))}
 prev_link=("Полный архив V43:\n"+FULL_PREVIOUS+
   "\n\nV19–V43 исходный код (и оригинальный V19) присутствует в source/.\n"+
   "Проверенная объединённая фабрика V7 хранится в GitHub Actions.\n"+
   "Причина: GitHub отклоняет отдельные файлы размером более 100MiB.\n")
 entries["backup/PREVIOUS_FULL_RELEASES_RU.txt"]=prev_link.encode("utf-8")
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v44/keyposes_v44.js",
  "anime-factory/v44/build_keyposes_v44.py",
  "anime-factory/v44/README_RU.md",
  "scripts/build_anime_v44.py",
  "tests/test_anime_v44.py","tests/smoke_browser_v44.py"):
  file=ROOT/rel
  if not file.is_file():raise FileNotFoundError(str(file))
  entries["source/V44_"+file.name]=file.read_bytes()
 manifest={"schema":"AnimeFactoryV44LeanRelease/1","version":44,
  "parentV43FullSha256":sha(parent_data),
  "originalV19Sha256":sha(V19.read_bytes()),
  "parentV43Release":FULL_PREVIOUS,
  "preserved":"All V19-V44 historical source, original V19; full V43 external immutable URL",
  "files":[{"path":name,"bytes":len(data),"sha256":sha(data)}
   for name,data in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 dst=Path(target).resolve();dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():dst.unlink()
 with zipfile.ZipFile(dst,"w",compression=zipfile.ZIP_DEFLATED,
    compresslevel=6,allowZip64=True) as z:
  for name,blob in sorted(entries.items()):z.writestr(name,blob)
 with zipfile.ZipFile(dst) as z:
  if z.testzip():raise RuntimeError("V44 CRC failure")
  info=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(z.namelist())!=len(info["files"])+1:raise RuntimeError("Inventory error")
  for row in info["files"]:
   blob=z.read(row["path"])
   if sha(blob)!=row["sha256"] or len(blob)!=row["bytes"]:
    raise RuntimeError("SHA/size wrong "+row["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 overwritten")
  for name in ("source/assembly_v35.js","source/audio_v36.js",
    "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
    "source/V39_performance_v39.js","source/V40_character_art_v40.js",
    "source/V41_silhouette_v41.js","source/V42_stage_v42.js",
    "source/V43_director_v43.js","source/V44_keyposes_v44.js",
    "CONVERT_MP4_WINDOWS.bat"):
   if name not in z.namelist():raise RuntimeError("Missing historical source "+name)
  if info["parentV43FullSha256"]!=sha(parent_data):
   raise RuntimeError("Parent link manifest SHA not grounded")
 if dst.stat().st_size>95*1024*1024:
  raise RuntimeError("Cannot publish direct GitHub ZIP >95 MiB")
 print("V44 ZIP VERIFIED",dst,dst.stat().st_size,len(entries),
       "originalV43SHA256",sha(parent_data),"V44SHA256",sha(dst.read_bytes()))
 return dst
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",default=str(ROOT/"dist"/NAME))
 parser.add_argument("--selftest",action="store_true")
 opts=parser.parse_args()
 if opts.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as td:assemble(Path(td)/NAME)
 else:assemble(opts.out)
if __name__=="__main__":main()
