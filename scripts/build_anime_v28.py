#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V28 Windows ZIP from preserved V19–V27 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v28"/"build_interaction_v28.py"
spec=importlib.util.spec_from_file_location("anime_v28",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V28_CHARACTER_WORLD_INTERACTION_WINDOWS.zip"
HTML="AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html"

README="""AI ANIME FACTORY V28 — CHARACTER / WORLD INTERACTION / WINDOWS 10
================================================================
Оригинальный V19, V20 сюжет, V21 визуал, V22 эмоции,
V23 персонажи, V24 движения, V25 бой, V26 камера,
V27 окружение, V28 взаимодействие.

ЗАПУСК
1. Распакуйте ZIP в отдельную папку Windows 10 64-bit.
2. Запустите RUN_WINDOWS.bat или откройте
   AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html в Chrome/Edge.
3. Вкладка «Взаимодействие V28» → выберите сцену.
4. Настройте контакт ног, пыль, отражённый свет, следы боя и вспышки.
5. Нажмите «Сохранить взаимодействие V28», проверьте кадры До/После.
6. Экспортируйте JSON проекта и 4 PNG-кадра. Сохраните JSON отдельно.
7. Для переноса V27 сделайте JSON-экспорт в V27 и импорт в V28.
8. Для MP4 отдельно потребуется FFmpeg (в ZIP его нет).

ТРЕБОВАНИЯ И ОГРАНИЧЕНИЯ
- Автономному HTML не нужен Python. Для монтажа MP4 нужен FFmpeg.
- При Windows 10 / 8 ГБ RAM рекомендуется 640x360 и 6 FPS.
- В ZIP включены исходные модули, тесты, резерв оригинального
  V19 в backup и SHA256-манифест. CRC32 каждого файла проверяется.
- Эффекты контакта рассчитаны для 2D Canvas, не физическая симуляция.
- Промахи/уклонения не становятся попаданиями из-за эффектов.
- Пользовательские PNG персонажей не перерисовываются.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html"\r\n')

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
        ("source","tests/test_anime_v26.py"),
        ("source","tests/test_anime_v27.py"),
        ("source","tests/test_anime_v28.py"),
        ("source","tests/smoke_browser_v27.py"),
        ("source","tests/smoke_browser_v28.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV28Release/1",
        "version":28,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27/V28 features",
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
    print("V28 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
