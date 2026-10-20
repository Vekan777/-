#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build checksum-verified V25 Windows ZIP from preserved V19–V24 code."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v25"/"build_combat_v25.py"
spec=importlib.util.spec_from_file_location("anime_v25",GEN)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NAME="AI_ANIME_FACTORY_V25_COMBAT_CHOREOGRAPHY_WINDOWS.zip"
HTML="AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html"

README="""AI ANIME FACTORY V25 — COMBAT CHOREOGRAPHY / WINDOWS 10
=====================================================
Основной HTML — интеграция оригинального V19, сюжет V20,
визуал V21, актёрская постановка V22, модели V23,
анимация V24 и новая постановка боя V25.

ИНСТРУКЦИЯ
1. Распакуйте весь ZIP в отдельную папку на Windows 10 x64.
2. Дважды нажмите RUN_WINDOWS.bat или откройте
   AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html в Chrome/Edge.
3. Вкладка «Хореография V25»: выберите боевую сцену.
4. Отрегулируйте дистанцию, шаг, защиту, реакции и ритм.
5. Сравните В24/В25 на одинаковом времени. Нажмите Сохранить V25.
6. Выгрузите JSON проекта как резервную копию; экспортируйте четыре PNG.
7. Существующие серии, диалоги, способности и предыдущие
   настройки остаются доступны во всех прежних вкладках.
8. Для MP4 потребуется FFmpeg, не входящий в архив.

СТАТУС И ОГРАНИЧЕНИЯ
- ZIP не содержит Python: работа HTML возможна без него.
- При 8 ГБ RAM начинайте с 640x360 и 6 FPS.
- Включены исходники, README, SHA256-манифест, резерв V19.
- Для переноса откройте старую V24 и выгрузите JSON;
  загрузите копию в V25 и проверьте сцены и героев.
- Это постановочный 2D-аниматик, не motion capture,
  физическая система попаданий или готовая 3D-анимация.
- Никакие события промаха не превращаются автоматически в попадания.
- Пользовательские PNG и авторские изображения не перерисовываются.
"""

RUN=('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
     'start "" "AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html"\r\n')

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
        ("source","anime-factory/v25/combat_v25.js"),
        ("source","anime-factory/v25/build_combat_v25.py"),
        ("source","tests/test_anime_v25.py"),
        ("source","tests/smoke_browser_v25.py"),
    ):
        entries[folder+"/"+Path(path).name]=(ROOT/path).read_bytes()
    manifest={
        "schema":"AnimeFactoryV25Release/1",
        "version":25,
        "source":"genuine V19 + additive V20/V21/V22/V23/V24/V25 features",
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
    print("V25 ZIP VERIFIED",out,"bytes",out.stat().st_size,
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
