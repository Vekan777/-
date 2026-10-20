#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a verified V36 standalone Windows ZIP keeping every V35 release entry."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
V35=ROOT/"scripts"/"build_anime_v35.py"
V36=ROOT/"anime-factory"/"v36"/"build_audio_v36.py"
NAME="AI_ANIME_FACTORY_V36_AUDIO_EPISODE_EXPORT_WINDOWS.zip"
HTML="AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html"
spec=importlib.util.spec_from_file_location("v36_audio",V36)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
oldspec=importlib.util.spec_from_file_location("v35_release",V35)
old=importlib.util.module_from_spec(oldspec)
oldspec.loader.exec_module(old)

README="""AI ANIME FACTORY V36 — AUDIO & EPISODE EXPORT / WINDOWS 10 x64
==============================================================
V36 построена поверх V35; сохранены оригинал V19 и исходники V20–V35.

КАК ЗАПУСТИТЬ
1. Полностью извлеките ZIP V36 в НОВУЮ папку. Не стирайте папку V35.
2. Запустите RUN_WINDOWS.bat или откройте HTML в Chrome/Edge.
3. В «Аудит V30» сохраните полный резерв JSON прежнего проекта.
4. Нажмите «Звук / экспорт V36» и выберите серию и сцену.
5. Выберите «Речь», «Музыка» или «Эффекты» и ваш WAV/MP3/OGG файл.
   Файл должен быть в формате, который умеет декодировать браузер.
6. Отрегулируйте громкость. Сдвиг: 100 = 1 секунда, 50 = 0,5 сек.
   Сохраните настройки. Повторите для остальных дорожек и сцен.
7. Нажмите «Аудит звука», исправьте пропуски и ошибки длительности.
8. «Слушать + смотреть» проиграет Canvas и аудио по таймкодам V35.
9. «Записать и скачать WebM эпизода» сохранит полную серию
   в реальном времени. НЕ меняйте вкладку и не закрывайте окно
   пока запись не закончится и файл не начнёт скачиваться.
10. Сохраните скачанный WebM в распакованную папку рядом с BAT.
11. Для MP4 поставьте FFmpeg, затем перетащите WebM на
    CONVERT_MP4_WINDOWS.bat или просто запустите BAT (если WebM
    лежит рядом). Конвертация использует H.264 / AAC и +faststart.
12. Храните копии исходных аудиофайлов и JSON проекта отдельно.

КАК НАСТРОИТЬ FFMPEG
- FFmpeg НЕ входит в архив V36: exe может весить сотни мегабайт.
- Подходит установленный FFmpeg в PATH, либо скопируйте ffmpeg.exe
  по адресу tools\\ffmpeg\\bin\\ffmpeg.exe относительно BAT.
- Если у вас уже есть ffmpeg-9.0.2-full_build.zip, распакуйте его
  и найдите файл bin\\ffmpeg.exe в соответствующей папке.
- Проверка в CMD: ffmpeg -version
- Команда вручную:
  ffmpeg -i episode.webm -c:v libx264 -crf 22 -preset veryfast
     -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart episode.mp4
  В CMD команда должна быть введена одной строкой.

ОГРАНИЧЕНИЯ
- V36 действительно захватывает Canvas с аудиодорожками в WebM,
  но не создает автоматически речь, музыку и MP4 прямо в HTML.
- Аудиофайлы НЕ встраиваются в JSON и HTML: после повторного
  открытия приложения выберите те же аудиофайлы заново.
- Если аудиофайлы не добавлены, фильм будет без слышимого звука.
- Запись идет в реальном времени; компьютер не должен спать.
- 640x360, 6 FPS — разумный старт для 8 ГБ RAM / GT740M.
- Это 2D-аниматик, не профессиональный 3D-рендер.
- backup/ содержит подлинный V19; все предыдущие исходники в source/.
- BUILD_MANIFEST.json содержит размеры и SHA256; CRC32 проверен.

ПРОВЕРКА РАЗРАБОТКИ
 python anime-factory\\v36\\build_audio_v36.py --selftest
 python -m unittest discover -s tests -p "test_anime_v36.py" -v
 python scripts\\build_anime_v36.py --selftest
"""

RUN='@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\nstart "" "AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html"\r\n'
CONVERT=r"""@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "INPUT=%~1"
if not defined INPUT (
  for %%F in (*.webm) do if not defined INPUT set "INPUT=%%~fF"
)
if not defined INPUT (
  echo Error: WebM not found. Drag your V36 .webm onto this BAT, or put it beside the BAT.
  pause
  exit /b 2
)
if not exist "%INPUT%" (
  echo Error: missing input "%INPUT%"
  pause
  exit /b 2
)
set "FFMPEG="
if exist "%~dp0tools\ffmpeg\bin\ffmpeg.exe" set "FFMPEG=%~dp0tools\ffmpeg\bin\ffmpeg.exe"
if not defined FFMPEG if exist "%~dp0ffmpeg.exe" set "FFMPEG=%~dp0ffmpeg.exe"
if not defined FFMPEG (
  where ffmpeg >nul 2>nul
  if not errorlevel 1 set "FFMPEG=ffmpeg"
)
if not defined FFMPEG (
  echo Error: FFmpeg not found. Add ffmpeg.exe to tools\ffmpeg\bin\ or to PATH.
  pause
  exit /b 3
)
for %%I in ("%INPUT%") do set "OUTPUT=%%~dpnI.mp4"
echo Input: "%INPUT%"
echo Output: "%OUTPUT%"
"%FFMPEG%" -hide_banner -y -i "%INPUT%" -map 0:v:0 -map 0:a? -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "%OUTPUT%"
if errorlevel 1 (
  echo Error: MP4 conversion failed. See FFmpeg output above.
  pause
  exit /b 1
)
echo MP4 ready: "%OUTPUT%"
pause
"""

def sha(data):
    return hashlib.sha256(data).hexdigest()

def assemble(destination):
    original=V19.read_bytes()
    with tempfile.TemporaryDirectory(prefix="anime-v36-") as tmp:
        base=Path(tmp)/"v35.zip"
        old.assemble(base)
        with zipfile.ZipFile(base) as arc:
            if arc.testzip():raise RuntimeError("V35 parent ZIP broken")
            entries={n:arc.read(n) for n in arc.namelist()
                     if n not in ("BUILD_MANIFEST.json","RUN_WINDOWS.bat","README_RU.txt")}
    entries[HTML]=module.build().encode("utf-8")
    entries["RUN_WINDOWS.bat"]=RUN.encode("utf-8")
    entries["CONVERT_MP4_WINDOWS.bat"]=CONVERT.encode("utf-8")
    entries["README_RU.txt"]=README.encode("utf-8")
    for rel in ("anime-factory/v36/audio_v36.js",
                "anime-factory/v36/build_audio_v36.py",
                "anime-factory/v36/README_RU.md",
                "tests/test_anime_v36.py",
                "tests/smoke_browser_v36.py"):
        if (ROOT/rel).exists():
            entries["source/"+Path(rel).name]=(ROOT/rel).read_bytes()
    for filename in ("README_RU.md",):
        entries["source/V36_"+filename]=(ROOT/"anime-factory"/"v36"/filename).read_bytes()
    manifest={"schema":"AnimeFactoryV36Release/1","version":36,
        "preservation":"V19 original + V20–V35 all source files + V36",
        "files":[{"path":p,"bytes":len(d),"sha256":sha(d)}
                  for p,d in sorted(entries.items())]}
    entries["BUILD_MANIFEST.json"]=json.dumps(
        manifest,ensure_ascii=False,indent=2).encode("utf-8")
    out=Path(destination).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as archive:
        for name,data in sorted(entries.items()):archive.writestr(name,data)
    with zipfile.ZipFile(out) as archive:
        if archive.testzip():raise RuntimeError("V36 bad CRC32")
        if set(archive.namelist())!=set(entries):raise RuntimeError("V36 missing entry")
        stored=json.loads(archive.read("BUILD_MANIFEST.json"))
        for info in stored["files"]:
            if sha(archive.read(info["path"]))!=info["sha256"]:
                raise RuntimeError("V36 SHA256 mismatch: "+info["path"])
        if archive.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=original:
            raise RuntimeError("The V19 original was modified")
        if "source/assembly_v35.js" not in entries:
            raise RuntimeError("V35 source unexpectedly lost")
    print("V36 ZIP VERIFIED",out,out.stat().st_size,len(entries),sha(out.read_bytes()))
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(ROOT/"dist"/NAME))
    parser.add_argument("--selftest",action="store_true")
    args=parser.parse_args()
    if args.selftest:
        module.selftest()
        with tempfile.TemporaryDirectory() as tmp:assemble(Path(tmp)/NAME)
        return
    assemble(args.out)

if __name__=="__main__":
    main()
