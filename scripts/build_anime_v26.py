#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V26 Windows ZIP from preserved V19–V25 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v26"/"build_cinematic_v26.py"
spec=importlib.util.spec_from_file_location("anime_v26",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V26_CINEMATIC_COMBAT_WINDOWS.zip"
HTML="AI_Anime_Factory_V26_CINEMATIC_COMBAT.html"

README="""AI ANIME FACTORY V26 — CINEMATIC COMBAT / WINDOWS 10 x64
=======================================================
Интеграция V19 (оригинал), V20 (сюжет), V21 (визуал),
V22 (актёрская постановка), V23 (персонажи),
V24 (движение), V25 (бой), V26 (камера и монтаж).

БЫСТРЫЙ ЗАПУСК
1. Распакуйте ZIP целиком в отдельную папку на Windows 10.
2. Откройте RUN_WINDOWS.bat или файл
   AI_Anime_Factory_V26_CINEMATIC_COMBAT.html в Chrome/Edge.
3. Перейдите на вкладку «Камера V26» и выберите боевую сцену.
4. Измените планы, выразительность, слежение за действием,
   акцент на ударе, кинополосы и переходы.
5. Сравните кадры V25/V26 и нажмите «Сохранить режиссуру V26».
6. Экспортируйте JSON всего проекта и сохраните его резервную копию.
7. Кнопкой «Скачать 4 кадра PNG» выгрузите раскадровку сцены.
8. Для сборки MP4 потребуется отдельный FFmpeg (не входит в ZIP).

ДОПОЛНИТЕЛЬНО
- На Windows 10, 8 ГБ оперативной памяти начните с 640x360 / 6 FPS.
- Python для автономного HTML редактора устанавливать НЕ нужно.
- Подлинный V19 лежит в backup. Все версии V20–V25 объединены без
  перезаписи источников; CRC32 и SHA256 проверяются при сборке ZIP.
- Старый проект V25 можно перенести экспортом и импортом JSON.
- 2D камера Canvas с эффектом масштаба, сдвигом, кинополосами и
  монтажным затемнением, НЕ настоящий 3D или motion capture.
- Оригинальные пользовательские PNG не перезаписываются.
- Точность ударов определяется прежними событиями V19/V17.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V26_CINEMATIC_COMBAT.html"\r\n')

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
        ("source","tests/test_anime_v23.py"),
        ("source","tests/test_anime_v24.py"),
        ("source","tests/test_anime_v25.py"),
        ("source","tests/test_anime_v26.py"),
        ("source","tests/smoke_browser_v25.py"),
        ("source","tests/smoke_browser_v26.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV26Release/1",
        "version":26,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26 features",
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
    print("V26 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
