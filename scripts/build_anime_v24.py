#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V24 Windows ZIP from preserved V19–V23 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v24"/"build_animation_v24.py"
spec=importlib.util.spec_from_file_location("anime_v24",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V24_CHARACTER_ANIMATION_WINDOWS.zip"
HTML="AI_Anime_Factory_V24_CHARACTER_ANIMATION.html"

README="""AI ANIME FACTORY V24 — CHARACTER ANIMATION / WINDOWS 10
=====================================================
База: V19 (оригинал), сюжет V20, визуал V21,
постановка актёров V22, модели V23, движения V24.

ЗАПУСК
1. Распакуйте ZIP целиком в отдельную папку Windows.
2. Запустите RUN_WINDOWS.bat или откройте HTML-файл
   AI_Anime_Factory_V24_CHARACTER_ANIMATION.html в Chrome/Edge.
3. Откройте «Анимация V24», выберите сцену.
4. Настройте шаги, перенос веса, подготовку к удару, отдачу
   после попадания и вторичную инерцию. Сравните кадры «До»/«После».
5. Нажмите «Сохранить движение V24», экспортируйте JSON проекта
   в отдельную резервную папку, затем сохраните 4 контрольных PNG.
6. Вкладки V19–V23 и сюжет остаются в программе.
7. Для MP4 понадобится установленный отдельно FFmpeg.
8. В комплекте есть SHA256-манифест, исходники и копия V19.

РЕКОМЕНДАЦИИ
- Ноутбук Windows 10 x64, Intel i7-3630QM, GT 740M, 8 ГБ RAM:
  начните с 640×360, 6 FPS, одной серии за проход.
- Python для самого HTML редактора устанавливать не требуется.
- Перенос проекта из V23: сначала сделайте экспорт JSON из V23,
  затем импортируйте в V24 и проверьте сцены/героев/историю.
- Процедурная 2D-анимация не заменяет нарисованные кадры,
  3D персонажей, полноценный IK или motion capture.
- Новые движения меняют лишь векторный риг и fallback-части;
  импортированные авторские PNG не перерисовываются.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V24_CHARACTER_ANIMATION.html"\r\n')

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
        ("source","tests/test_anime_v23.py"),
        ("source","tests/smoke_browser_v23.py"),
        ("source","tests/test_anime_v24.py"),
        ("source","tests/smoke_browser_v24.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV24Release/1",
        "version":24,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24 features",
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
    print("V24 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
