#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V43 reproducible Windows release; nested full previous V42 archive and original V19."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts/build_anime_v42.py"
BUILDER=ROOT/"anime-factory/v43/build_director_v43.py"
NAME="AI_ANIME_FACTORY_V43_ACTION_DIRECTOR_WINDOWS.zip"
HTML="AI_Anime_Factory_V43_ACTION_DIRECTOR.html"
def load(file,name):
 spec=importlib.util.spec_from_file_location(name,file)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
parent=load(PARENT,"v42_release")
builder=load(BUILDER,"v43_director")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V43_ACTION_DIRECTOR.html"\r\n'
README="""AI ANIME FACTORY V43 — ACTION CAMERA DIRECTOR / WINDOWS 10
===========================================================
1. Полностью распакуйте ZIP в отдельную папку, не поверх V42.
2. Дважды нажмите RUN_WINDOWS.bat (HTML откроется в Chrome/Edge).
3. На вкладке «Аудит V30» сделайте резервный полный JSON.
4. «Режиссёр боя V43»: выберите эпизод и боевую сцену.
5. Выберите режиссёрский стиль, план и настройте камеру.
   Для комфорта можно отключить тряску галочкой «Уменьшение движения».
6. Сохраните настройки и сравните кадры на одном таймкоде.
7. Скачайте PNG контрольных кадров, JSON-план, проверьте аудит.
8. Для WebM со звуком откройте «Звук / экспорт V36»,
   повторно приложите свои WAV/MP3/OGG и запишите серию.
9. Для MP4 используйте CONVERT_MP4_WINDOWS.bat и FFmpeg
   из tools\\ffmpeg\\bin\\ffmpeg.exe или системного PATH.
10. Сделайте итоговый резерв проекта JSON.

Исходный V19 и всё V20–V42 сохранены; архив V42 в backup/.
Настоящая камера для 2D-аниматика, НЕ профессиональный 3D.
Ноутбук 8GB/GT740M: 640×360, 6 FPS.
Подробная инструкция: source/V43_README_RU.md.
"""
def sha(blob):return hashlib.sha256(blob).hexdigest()
def assemble(destination):
 with tempfile.TemporaryDirectory(prefix="anime-v43-") as temp:
  prev=Path(temp)/parent.NAME
  parent.assemble(prev)
  parent_content=prev.read_bytes()
  with zipfile.ZipFile(prev) as zp:
   if zp.testzip():raise RuntimeError("V42 parent CRC32 error")
   entries={n:zp.read(n) for n in zp.namelist() if n!="BUILD_MANIFEST.json"}
 entries["backup/"+parent.NAME]=parent_content
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=README.encode("utf-8")
 for rel in ("anime-factory/v43/director_v43.js",
  "anime-factory/v43/build_director_v43.py",
  "anime-factory/v43/README_RU.md",
  "scripts/build_anime_v43.py","tests/test_anime_v43.py",
  "tests/smoke_browser_v43.py"):
  src=ROOT/rel
  if not src.exists():raise FileNotFoundError("V43 missing "+str(src))
  entries["source/V43_"+src.name]=src.read_bytes()
 manifest={"schema":"AnimeFactoryV43Release/1","version":43,
  "parentV42Sha256":sha(parent_content),
  "originalV19Sha256":sha(V19.read_bytes()),
  "preservation":"original V19 + complete V20–V42 source + entire V42 ZIP",
  "files":[{"path":p,"bytes":len(d),"sha256":sha(d)}
           for p,d in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 dest=Path(destination).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():dest.unlink()
 with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,
  compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):z.writestr(name,data)
 with zipfile.ZipFile(dest) as z:
  if z.testzip():raise RuntimeError("V43 ZIP CRC32 error")
  doc=json.loads(z.read("BUILD_MANIFEST.json"))
  if len(doc["files"])+1!=len(z.namelist()):raise RuntimeError("V43 inventory changed")
  for item in doc["files"]:
   raw=z.read(item["path"])
   if len(raw)!=item["bytes"] or sha(raw)!=item["sha256"]:
    raise RuntimeError("V43 manifest mismatch "+item["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("V19 was altered")
  if sha(z.read("backup/"+parent.NAME))!=doc["parentV42Sha256"]:
   raise RuntimeError("V42 full release was modified")
  for path in ("source/assembly_v35.js","source/audio_v36.js",
    "source/V37_subtitles_v37.js","source/V38_cinematic_v38.js",
    "source/V39_performance_v39.js","source/V40_character_art_v40.js",
    "source/V41_silhouette_v41.js","source/V42_stage_v42.js",
    "source/V43_director_v43.js","CONVERT_MP4_WINDOWS.bat"):
   if path not in z.namelist():raise RuntimeError("Legacy source missing: "+path)
 print("V43 ZIP VERIFIED",dest,dest.stat().st_size,
  len(entries),"SHA256",sha(dest.read_bytes()))
 return dest
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--out",default=str(ROOT/"dist"/NAME))
 args=p.parse_args()
 if args.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory() as temp:assemble(Path(temp)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
