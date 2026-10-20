#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V29 Windows ZIP from preserved V19–V28 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v29"/"build_polish_v29.py"
spec=importlib.util.spec_from_file_location("anime_v29",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V29_ANIMATION_COMBAT_POLISH_WINDOWS.zip"
HTML="AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html"

README="""AI ANIME FACTORY V29 — ANIMATION & COMBAT POLISH / WINDOWS 10
============================================================
Исходник V19 и последовательные V20 сюжет, V21 визуал,
V22 эмоции, V23 персонажи, V24 анимация, V25 бой,
V26 камера, V27 мир, V28 взаимодействие, V29 ритм.

БЫСТРЫЙ ЗАПУСК
1. Распакуйте ZIP целиком в новую папку Windows 10 x64.
2. Дважды нажмите RUN_WINDOWS.bat или откройте
   AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html в Chrome/Edge.
3. Вкладка «Анимация V29» → выберите боевую сцену.
4. Настройте синхронизацию фаз, опору ног, затухание,
   силу реакции и плавность; сравните кадры V28/V29.
5. Нажмите «Сохранить движения V29», выгрузите JSON
   всего проекта для резервного копирования и 4 PNG кадра.
6. Для переноса проекта из V28 экспортируйте JSON из V28
   и импортируйте в V29, затем проверьте сюжет и персонажей.
7. Для MP4 нужен отдельно установленный FFmpeg (не входит в ZIP).

ПРОИЗВОДИТЕЛЬНОСТЬ, БЕЗОПАСНОСТЬ, ОГРАНИЧЕНИЯ
- На ноутбуке с 8 ГБ оперативной памяти начните с 640x360, 6 FPS.
- Python для самого автономного HTML редактора не требуется.
- Исходный V19 в backup/, исходники надстроек в source/.
- Проверка ZIP выполняется по CRC32 и SHA-256 каждого файла.
- Физической инверсной кинематики, motion capture и 3D здесь нет.
- Исходы «попадание/промах/блок/уклонение» берутся из старых
  данных V19/V17 и не генерируются автоматически.
- Импортированные пользователем PNG не перерисовываются.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html"\r\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def assemble(dest):
    original=V19.read_bytes()
    generated=module.build().encode("utf-8")
    entries={
        HTML:generated,
        "backup/AI_Anime_Factory_V19_ORIGINAL.html":original,
        "README_RU.txt":README.encode("utf-8"),
        "RUN_WINDOWS.bat":RUN.encode("utf-8"),
    }
    for folder,path in (
        ("source","anime-factory/v20/story_v20.js"),
        ("source","anime-factory/v20/build_story_v20.py"),
        ("source","anime-factory/v21/visual_v21.js"),
        ("source","anime-factory/v21/build_visual_v21.py"),
        ("source","anime-factory/v22/acting_v22.js"),
        ("source","anime-factory/v22/build_acting_v22.py"),
        ("source","anime-factory/v23/character_v23.js"),
        ("source","anime-factory/v23/build_character_v23.py"),
        ("source","anime-factory/v24/animation_v24.js"),
        ("source","anime-factory/v24/build_animation_v24.py"),
        ("source","anime-factory/v25/combat_v25.js"),
        ("source","anime-factory/v25/build_combat_v25.py"),
        ("source","anime-factory/v26/cinematic_v26.js"),
        ("source","anime-factory/v26/build_cinematic_v26.py"),
        ("source","anime-factory/v27/world_v27.js"),
        ("source","anime-factory/v27/build_world_v27.py"),
        ("source","anime-factory/v28/interaction_v28.js"),
        ("source","anime-factory/v28/build_interaction_v28.py"),
        ("source","anime-factory/v29/polish_v29.js"),
        ("source","anime-factory/v29/build_polish_v29.py"),
        ("source","tests/test_anime_v27.py"),
        ("source","tests/test_anime_v28.py"),
        ("source","tests/test_anime_v29.py"),
        ("source","tests/smoke_browser_v28.py"),
        ("source","tests/smoke_browser_v29.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV29Release/1",
        "version":29,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27/V28/V29 features",
        "files":[{"path":n,"bytes":len(d),"sha256":sha(d)}
                 for n,d in sorted(entries.items())]
    }
    entries["BUILD_MANIFEST.json"]=json.dumps(
        manifest,ensure_ascii=False,indent=2).encode("utf-8")
    out=Path(dest).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as archive:
        for name,content in sorted(entries.items()):
            archive.writestr(name,content)
    with zipfile.ZipFile(out) as archive:
        if archive.testzip():
            raise RuntimeError("CRC32 integrity failure")
        if set(archive.namelist())!=set(entries):
            raise RuntimeError("ZIP inventory mismatch")
        saved=json.loads(archive.read("BUILD_MANIFEST.json"))
        for item in saved["files"]:
            content=archive.read(item["path"])
            if len(content)!=item["bytes"] or sha(content)!=item["sha256"]:
                raise RuntimeError("SHA256 mismatch "+item["path"])
        if archive.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=original:
            raise RuntimeError("Original V19 backup changed")
    print("V29 ZIP VERIFIED",out,"bytes",out.stat().st_size,
          "entries",len(entries),"sha256",sha(out.read_bytes()))
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(ROOT/"dist"/NAME))
    parser.add_argument("--selftest",action="store_true")
    args=parser.parse_args()
    if args.selftest: module.selftest();return
    assemble(args.out)

if __name__=="__main__":
    main()
