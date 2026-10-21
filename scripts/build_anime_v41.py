#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V41 Windows release, keeping original V19 and COMPLETE previous V40 ZIP."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v40.py"
BUILDER=ROOT/"anime-factory/v41/build_silhouette_v41.py"
NAME="AI_ANIME_FACTORY_V41_SILHOUETTE_STUDIO_WINDOWS.zip"
HTML="AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html"
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(module)
 return module
parent=load(PARENT,"v40release")
builder=load(BUILDER,"v41silhouettes")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html"\r\n'
README="""AI ANIME FACTORY V41 — СИЛУЭТЫ И КОСТЮМЫ / WINDOWS 10
======================================================
1. Извлеките весь ZIP в новую папку, не поверх старых версий.
2. Запустите RUN_WINDOWS.bat или откройте главный HTML в Chrome/Edge.
3. Сохраните полный резервный JSON на вкладке «Аудит V30».
4. На вкладке «Силуэты V41» выберите персонажа и тип:
   защитник, разведчик или маг; настройте плащ, броню, причёску.
5. Нажмите «Сохранить силуэт персонажа». Сравните один и тот же
   кадр до/после и сохраните четыре реальных PNG и настройки JSON.
6. Для WebM со звуком вернитесь в «Звук / экспорт V36»; снова
   выберите свои аудиофайлы WAV/MP3/OGG и начните запись серии.
7. Для MP4 перетащите сохранённый WebM на CONVERT_MP4_WINDOWS.bat.
   Требуется ffmpeg.exe в PATH или tools\\ffmpeg\\bin\\ffmpeg.exe.
8. После работы экспортируйте полный резерв JSON.

Это процедурная 2D-графика, не профессиональный 3D/нейроаниме.
Авторские файлы PNG/PSD остаются неизменными. Весь код V19–V40 и
полная исходная сборка V40 сохранены внутри нового архива.
Для слабого ноутбука используйте 640x360, 6 FPS.
Полная инструкция: source/V41_README_RU.md.
"""
def sha(blob):return hashlib.sha256(blob).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v41-") as folder:
  oldzip=Path(folder)/parent.NAME
  parent.assemble(oldzip)
  oldbytes=oldzip.read_bytes()
  with zipfile.ZipFile(oldzip) as z:
   if z.testzip():raise RuntimeError("Parent V40 ZIP has bad CRC")
   entries={name:z.read(name) for name in z.namelist()
            if name!="BUILD_MANIFEST.json"}
 entries["backup/"+parent.NAME]=oldbytes
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v41/silhouette_v41.js",
             "anime-factory/v41/build_silhouette_v41.py",
             "anime-factory/v41/README_RU.md",
             "scripts/build_anime_v41.py","tests/test_anime_v41.py",
             "tests/smoke_browser_v41.py"):
  src=ROOT/rel
  if not src.is_file():raise FileNotFoundError(str(src))
  entries["source/V41_"+src.name]=src.read_bytes()
 doc={"schema":"AnimeFactoryV41Release/1","version":41,
  "parentV40Sha256":sha(oldbytes),
  "originalV19Sha256":sha(V19.read_bytes()),
  "preservation":"original V19 + V20-V40 sources + full V40 ZIP",
  "files":[{"path":name,"bytes":len(blob),"sha256":sha(blob)}
           for name,blob in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(doc,ensure_ascii=False,indent=2).encode("utf-8")
 dst=Path(destination).resolve();dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():dst.unlink()
 with zipfile.ZipFile(dst,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,blob in sorted(entries.items()):z.writestr(name,blob)
 with zipfile.ZipFile(dst) as z:
  if z.testzip():raise RuntimeError("V41 ZIP CRC failed")
  saved=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(saved["files"])+1!=len(z.namelist()):raise RuntimeError("Wrong V41 ZIP inventory")
  for item in saved["files"]:
   blob=z.read(item["path"])
   if len(blob)!=item["bytes"] or sha(blob)!=item["sha256"]:
    raise RuntimeError("SHA256 mismatch: "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("Original V19 modified")
  if sha(z.read("backup/"+parent.NAME))!=saved["parentV40Sha256"]:
   raise RuntimeError("Original V40 ZIP corrupted")
  for item in ("source/assembly_v35.js","source/audio_v36.js",
               "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
               "source/V39_performance_v39.js","source/V40_character_art_v40.js",
               "source/V41_silhouette_v41.js","CONVERT_MP4_WINDOWS.bat"):
   if item not in z.namelist():raise RuntimeError("Missing source: "+item)
 print("V41 ZIP VERIFIED",dst,dst.stat().st_size,len(entries),"SHA256",sha(dst.read_bytes()))
 return dst
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 p.add_argument("--selftest",action="store_true")
 args=p.parse_args()
 if args.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as d:assemble(Path(d)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
