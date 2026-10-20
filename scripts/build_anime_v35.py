#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V35 Windows ZIP from preserved V19–V34 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v35"/"build_assembly_v35.py"
spec=importlib.util.spec_from_file_location("anime_v35",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V35_SCENE_ASSEMBLY_WINDOWS.zip"
HTML="AI_Anime_Factory_V35_SCENE_ASSEMBLY.html"

README="""AI ANIME FACTORY V35 — SCENE ASSEMBLY & PRODUCTION / WINDOWS 10
===============================================================
Сохранены V19 original, сюжет и все V20–V34 редакторы.

ПОДРОБНЫЙ ЗАПУСК
1. Извлеките ZIP ПОЛНОСТЬЮ в новую папку на Windows 10 x64.
2. Запустите RUN_WINDOWS.bat или откройте HTML:
   AI_Anime_Factory_V35_SCENE_ASSEMBLY.html в Chrome/Edge.
3. Сделайте ПОЛНЫЙ резерв проекта JSON во вкладке «Аудит V30».
4. Откройте вкладку «Сборка серии V35» и выберите серию.
5. Выберите сцену и задайте длительность НАПЛЫВА на следующую
   (0–1,5 секунды; автоматически ограничен длиной двух сцен).
6. Нажмите «Сохранить монтажный переход».
7. Используйте «Воспроизвести», «Пауза» и ползунок времени
   для непрерывного просмотра сцен эпизода.
8. Запустите «Проверить всю сборку», скачайте отчёт TXT,
   манифест JSON и 6 реальных кадров PNG из серии.
9. Для переноса из V34 экспортируйте JSON из V34 и импортируйте
   его в V35. Проверьте персонажей, канон и настройки сцен.

ЧТО ВАЖНО
- Начальные сцены не обрезаются, авторские duration не меняются.
- Суммарная длительность = сумма сцен минус наложения.
- Превью объединяет ВИЗУАЛЬНЫЕ кадры, а НЕ звуковые дорожки.
- Экспорт 6 PNG — контрольный лист, не MP4 готовой серии.
- MP4 со сведённым звуком потребует отдельного видеомонтажа
  (FFmpeg); не обещаем автоматического видеосериала.
- История V19–V34, пользовательские PNG не изменяются.
- На старом ноутбуке 8 GB RAM начните с 640x360, 6 FPS.
- Для HTML не нужен Python, в backup исходный V19,
  в source все надстройки V20–V35, ZIP CRC32/SHA256 проверен.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V35_SCENE_ASSEMBLY.html"\r\n')

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
        ("source","anime-factory/v32/keyframes_v32.js"),
        ("source","anime-factory/v32/build_keyframes_v32.py"),
        ("source","anime-factory/v33/acting_v33.js"),
        ("source","anime-factory/v33/build_acting_v33.py"),
        ("source","anime-factory/v34/storyboard_v34.js"),
        ("source","anime-factory/v34/build_storyboard_v34.py"),
        ("source","anime-factory/v35/assembly_v35.js"),
        ("source","anime-factory/v35/build_assembly_v35.py"),
        ("source","tests/test_anime_v33.py"),
        ("source","tests/test_anime_v34.py"),
        ("source","tests/test_anime_v35.py"),
        ("source","tests/smoke_browser_v34.py"),
        ("source","tests/smoke_browser_v35.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV35Release/1",
        "version":35,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25/V26/V27/V28/V29/V30/V31/V32/V33/V34/V35 features",
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
    print("V35 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
