#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V30 Windows ZIP from preserved V19–V29 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v30"/"build_unified_v30.py"
spec=importlib.util.spec_from_file_location("anime_v30",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V30_UNIFIED_QUALITY_REVIEW_WINDOWS.zip"
HTML="AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html"

README="""AI ANIME FACTORY V30 — UNIFIED QUALITY REVIEW / WINDOWS 10
=========================================================
Объединение подлинного V19 и всех надстроек V20–V29.

УСТАНОВКА И ЗАПУСК
1. Распакуйте ZIP полностью в новую папку на Windows 10 x64.
2. Откройте RUN_WINDOWS.bat либо файл
   AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html в Chrome/Edge.
3. Перейдите на вкладку «Аудит V30» и нажмите
   «Скачать резерв JSON» ПЕРЕД созданием контрольной точки.
4. Нажмите «Зафиксировать контрольную точку».
5. Нажмите «Проверить весь проект» и изучите список
   ошибок, предупреждений и сведений по всем версиям.
6. При необходимости откройте проблемную сцену по кнопке.
7. Скачайте отчёт TXT, контрольный JSON и 4 PNG кадра.
8. Из старой V29 перенесите проект через экспорт/импорт JSON.

ОСОБЕННОСТИ
- V30 не удаляет сюжет, канон, сцены или персонажей;
  исправления сюжетных проблем выполняет сам автор.
- Контрольная точка помогает обнаружить изменения
  после фиксации, но не является автоматическим backup.
- Полный JSON проекта сохраните в отдельной папке/на носителе.
- Оригинал V19 лежит в backup; исходники V20–V30 в source;
  каждый файл ZIP проверен CRC32/SHA256.
- HTML работает без установки Python; для MP4 нужен FFmpeg.
- Для 8 ГБ оперативной памяти начните с 640x360 / 6 FPS.
- Технический аудит не гарантирует качество художественного аниме.
- Формат по-прежнему процедурный 2D Canvas, не 3D.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html"\r\n')

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
        ("source","anime-factory/v30/unified_v30.js"),
        ("source","anime-factory/v30/build_unified_v30.py"),
        ("source","tests/test_anime_v28.py"),
        ("source","tests/test_anime_v29.py"),
        ("source","tests/test_anime_v30.py"),
        ("source","tests/smoke_browser_v29.py"),
        ("source","tests/smoke_browser_v30.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV30Release/1",
        "version":30,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27/V28/V29/V30 features",
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
    print("V30 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
