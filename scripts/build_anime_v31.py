#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V31 Windows ZIP from preserved V19–V30 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v31"/"build_visual_v31.py"
spec=importlib.util.spec_from_file_location("anime_v31",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V31_VISUAL_PRODUCTION_REVIEW_WINDOWS.zip"
HTML="AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html"

README="""AI ANIME FACTORY V31 — VISUAL PRODUCTION REVIEW / WINDOWS 10
============================================================
Original V19 + V20–V30 addons retained + V31 real Canvas quality.

ЗАПУСК
1. Распакуйте ZIP в новую папку на Windows 10 64-bit.
2. Запустите RUN_WINDOWS.bat или откройте
   AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html через Edge/Chrome.
3. Скачайте полный JSON проекта (вкладка «Аудит V30»).
4. Откройте «Контроль кадра V31»; выберите сцену.
5. Сравните кадры V30 и V31. При необходимости настройте
   экспозицию, контраст, насыщенность и виньетку.
6. Нажмите «Сохранить качество кадра».
7. Запустите анализ четырёх кадров или первых 24 сцен.
8. Скачайте PNG, текстовый отчёт и JSON с метриками.
9. Для переноса из V30 экспортируйте JSON из V30 и
   импортируйте его в V31. Проверьте прежний сюжет.

ВАЖНО
- Метрики кадра реальны (яркость/контраст/света/тени),
  но не распознают лица и не гарантируют художественный успех.
- Для больших сезонов автоматически проверяются первые 24 сцены.
  Остальные сцены можно проверять по отдельности.
- Изображения автора не перезаписываются: обработка идёт в Canvas.
- Исходник V19 хранится в backup, модули в source;
  встроены контрольные CRC32 и SHA256 всех файлов.
- HTML-редактор не требует Python, MP4 требует внешний FFmpeg.
- Для 8 GB RAM и GT740M рекомендуем 640x360 и 6 FPS.
- Это 2D-аниматик, а не профессиональное 3D или готовое аниме.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html"\r\n')

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
        ("source","anime-factory/v31/visual_v31.js"),
        ("source","anime-factory/v31/build_visual_v31.py"),
        ("source","tests/test_anime_v29.py"),
        ("source","tests/test_anime_v30.py"),
        ("source","tests/test_anime_v31.py"),
        ("source","tests/smoke_browser_v30.py"),
        ("source","tests/smoke_browser_v31.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV31Release/1",
        "version":31,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27/V28/V29/V30/V31 features",
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
    print("V31 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
