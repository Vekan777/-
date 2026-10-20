#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V23 Windows standalone ZIP from preserved V19–V22 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v23"/"build_character_v23.py"
spec=importlib.util.spec_from_file_location("anime_v23",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V23_CHARACTER_QUALITY_WINDOWS.zip"
HTML="AI_Anime_Factory_V23_CHARACTER_QUALITY.html"

README="""AI ANIME FACTORY V23 — CHARACTER QUALITY / WINDOWS 10 x64
=======================================================
Действующая база: подлинный V19, сюжет и бои V20, V21 визуал,
V22 актёрская постановка, V23 качество процедурного персонажа.

БЫСТРЫЙ СТАРТ
1. Распакуйте ZIP полностью (например D:\\AI_ANIME_FACTORY_V23).
2. Дважды нажмите RUN_WINDOWS.bat или откройте файл
   AI_Anime_Factory_V23_CHARACTER_QUALITY.html в Chrome/Edge.
3. Выберите вкладку «Персонажи V23», героя, телосложение и настройки.
4. «Сохранить персонажа V23» записывает настройки в браузерный проект.
5. Экспортируйте JSON проекта в старой вкладке и сохраните копию вне ПК.
6. «Сохранить 4 кадра PNG» создаёт контактный лист сцены.
7. Вкладки сюжета V20, атмосферы V21, актёрской постановки V22
   продолжают работать. Импорт старого JSON сохраняет сюжетные данные.
8. Для MP4 используйте отдельный FFmpeg, он не включён в ZIP.

Технические границы:
- Система создаёт 2D векторный аниматик, не полномасштабную 3D анимацию.
- Новые детали изменяют встроенный процедурный риг; пользовательский арт
  PNG/cutout не дорисовывается и не перезаписывается.
- На Windows 10 с 8 ГБ RAM начните с предпросмотра 640x360, 6 FPS.
- V19 оригинал помещён в backup без изменений.
- Python для работы HTML-студии не требуется, браузер работает локально.
- Исходники и инструкция включены для воспроизводимости и проверки.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V23_CHARACTER_QUALITY.html"\r\n')

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
        ("source","tests/test_anime_v23.py"),
        ("source","tests/smoke_browser_v23.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV23Release/1",
        "version":23,
        "source":"genuine V19 + additive V20/V21/V22/V23 features",
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
    print("V23 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
