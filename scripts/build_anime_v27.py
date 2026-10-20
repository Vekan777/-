#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V27 Windows ZIP from preserved V19–V26 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v27"/"build_world_v27.py"
spec=importlib.util.spec_from_file_location("anime_v27",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V27_WORLD_QUALITY_WINDOWS.zip"
HTML="AI_Anime_Factory_V27_WORLD_QUALITY.html"

README="""AI ANIME FACTORY V27 — WORLD QUALITY / WINDOWS 10 x64
====================================================
Подлинный V19 + V20 сюжет + V21 визуал + V22 игра актёров +
V23 персонажи + V24 движения + V25 бой + V26 камера + V27 мир.

УСТАНОВКА И ЗАПУСК
1. Распакуйте ZIP полностью в отдельную папку Windows 10.
2. Откройте RUN_WINDOWS.bat или HTML:
   AI_Anime_Factory_V27_WORLD_QUALITY.html в браузере Chrome/Edge.
3. Откройте «Мир V27». Выберите сцену и окружение:
   город / лес / храм / поле боя / тип из сценария.
4. Настройте глубину, свет, землю, атмосферу, передний план.
5. Сравните V26/V27, нажмите «Сохранить окружение V27».
6. Экспортируйте JSON проекта как резервную копию; 4 PNG как отчёт.
7. Откройте старые вкладки V19–V26 для проверки истории и героев.
8. Для MP4 отдельно нужен FFmpeg (в архив не включён).

РЕКОМЕНДАЦИИ И ОГРАНИЧЕНИЯ
- При 8 ГБ RAM начинайте с 640x360, 6 FPS, одна серия за проход.
- Python для запуска HTML редактора не требуется.
- Для переноса из V26 выгрузите старый JSON и импортируйте его в V27.
- Исходный HTML V19 сохранён в backup/; остальные надстройки
  не перезаписываются. BUILD_MANIFEST.json, CRC32 и SHA256 проверены.
- Новая глубина, свет и тени процедурные и 2D: это не реальный 3D мир.
- Авторские PNG-изображения персонажей не перезаписываются.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V27_WORLD_QUALITY.html"\r\n')

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
        ("source","tests/test_anime_v23.py"),
        ("source","tests/test_anime_v24.py"),
        ("source","tests/test_anime_v25.py"),
        ("source","tests/test_anime_v26.py"),
        ("source","tests/test_anime_v27.py"),
        ("source","tests/smoke_browser_v26.py"),
        ("source","tests/smoke_browser_v27.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV27Release/1",
        "version":27,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27 features",
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
    print("V27 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
