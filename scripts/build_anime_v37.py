#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V37 Windows release: preserves entire V36 package and all V19–V36 source."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
PARENT=ROOT/"scripts"/"build_anime_v36.py"
BUILDER=ROOT/"anime-factory"/"v37"/"build_subtitles_v37.py"
NAME="AI_ANIME_FACTORY_V37_SUBTITLES_DELIVERY_WINDOWS.zip"
HTML="AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html"
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
old=load(PARENT,"v36release")
builder=load(BUILDER,"v37editor")
RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html"\r\n'
INTRO="""AI ANIME FACTORY V37 — СУБТИТРЫ И КОНТРОЛЬ ВЫПУСКА
=================================================
1. Полностью распакуйте архив в НОВУЮ папку. Не стирайте старые версии.
2. Откройте RUN_WINDOWS.bat (или HTML в Chrome/Edge).
3. В «Аудит V30» экспортируйте полный JSON проекта.
4. «Субтитры V37» — выберите эпизод и сцену, укажите начало/конец
   относительно сцены, имя говорящего и точный текст, сохраните.
5. Просмотрите кадры, запустите аудит, скачайте SRT, VTT и JSON.
6. В «Звук / экспорт V36» снова прикрепите собственные аудиофайлы,
   если браузер был перезапущен, и запишите WebM с субтитрами.
7. Для MP4 используйте CONVERT_MP4_WINDOWS.bat с FFmpeg,
   добавленным в PATH или tools\\ffmpeg\\bin\\ffmpeg.exe.
8. Для старого ноутбука используйте 640x360 и 6 FPS.

V37 не изменяет сюжет, исходные длительности и возможности V19–V36.
Внутри backup/ хранится и подлинный V19, и полный V36 ZIP.
Речь/музыка автоматически не генерируются; аудиофайлы не живут в JSON.
WebM пишется в реальном времени. Это 2D-аниматик, не профессиональный 3D.
Смотрите также source/V37_README_RU.md (подробная инструкция).
"""

def sha(d):return hashlib.sha256(d).hexdigest()
def assemble(dest):
 with tempfile.TemporaryDirectory(prefix="anime-v37-") as tmp:
  oldzip=Path(tmp)/old.NAME
  old.assemble(oldzip)
  parent_bytes=oldzip.read_bytes()
  with zipfile.ZipFile(oldzip) as z:
   if z.testzip():raise RuntimeError("V36 package CRC mismatch")
   entries={n:z.read(n) for n in z.namelist() if n!="BUILD_MANIFEST.json"}
  entries["backup/"+old.NAME]=parent_bytes
 entries[HTML]=builder.build().encode("utf-8")
 entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
 entries["README_RU.txt"]=INTRO.encode("utf-8")
 for rel in ("anime-factory/v37/subtitles_v37.js",
             "anime-factory/v37/build_subtitles_v37.py",
             "anime-factory/v37/README_RU.md",
             "scripts/build_anime_v37.py",
             "tests/test_anime_v37.py",
             "tests/smoke_browser_v37.py"):
  file=ROOT/rel
  if not file.is_file():raise FileNotFoundError("Missing V37 source "+str(file))
  entries["source/V37_"+file.name]=file.read_bytes()
 manifest={"schema":"AnimeFactoryV37Release/1","version":37,
  "parentV36ZipSha256":sha(parent_bytes),
  "originalV19Sha256":sha(V19.read_bytes()),
  "files":[{"path":p,"bytes":len(d),"sha256":sha(d)} for p,d in sorted(entries.items())]}
 entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
 out=Path(dest).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():out.unlink()
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                      compresslevel=6,allowZip64=True) as z:
  for key,val in sorted(entries.items()):z.writestr(key,val)
 with zipfile.ZipFile(out) as z:
  if z.testzip():raise RuntimeError("Bad CRC32 V37")
  if set(z.namelist())!=set(entries):raise RuntimeError("Missing V37 ZIP files")
  stored=json.loads(z.read("BUILD_MANIFEST.json"))
  for info in stored["files"]:
   raw=z.read(info["path"])
   if sha(raw)!=info["sha256"] or len(raw)!=info["bytes"]:
    raise RuntimeError("V37 SHA256 mismatch "+info["path"])
  if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=V19.read_bytes():
   raise RuntimeError("V19 source mutated")
  if sha(z.read("backup/"+old.NAME))!=stored["parentV36ZipSha256"]:
   raise RuntimeError("V36 ZIP backup mutated")
  for name in ("source/assembly_v35.js","source/audio_v36.js",
               "source/V37_subtitles_v37.js","CONVERT_MP4_WINDOWS.bat"):
   if name not in z.namelist():raise RuntimeError("Missing preserved component "+name)
 print("V37 ZIP VERIFIED",out,"bytes",out.stat().st_size,
  "entries",len(entries),"sha256",sha(out.read_bytes()))
 return out
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",default=str(ROOT/"dist"/NAME))
 parser.add_argument("--selftest",action="store_true")
 args=parser.parse_args()
 if args.selftest:
  builder.selftest()
  with tempfile.TemporaryDirectory(prefix="v37-test-") as tmp:assemble(Path(tmp)/NAME)
 else:assemble(args.out)
if __name__=="__main__":main()
