#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build AI Anime Factory V22 Windows ZIP with full V19 backup and SHA256 manifest."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v22"/"build_acting_v22.py"
spec=importlib.util.spec_from_file_location("anime_v22",GEN)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

README="""AI ANIME FACTORY V22 — ACTING & COMBAT / WINDOWS 10 x64
======================================================
Основа: исходный V19, улучшения сюжета V20, визуал V21,
новые актёрские ключи и ясная постановка боя V22.

1. Распакуйте ZIP полностью в отдельную папку.
2. Запустите RUN_WINDOWS.bat (или откройте V22 HTML в Chrome/Edge).
3. Вкладка «Персонажи и бой V22»: выберите сцену.
4. Для главного героя и второго персонажа задайте эмоции по времени.
5. Сохраните актёрский ключ и параметры сцены, затем JSON проекта.
6. Нажмите «Сохранить 4 актёрских кадра PNG» для проверки.
7. В остальных вкладках сохранились V19 и функции V20–V21.
8. Штатный экспорт кадров -> ZIP/PNG, для MP4 используйте FFmpeg.
9. Оригинальный HTML V19 сохранён в папке backup.
10. Не удаляйте резервную копию JSON перед импортом старого проекта.

Ваш ноутбук Windows 10 x64 / 8 ГБ RAM: предпросмотр 640×360, 6 FPS,
рендер одной серии за раз. Для полноценного 3D и нейронного видео
нужна другая графическая инфраструктура.

Это работающий по коду 2D-аниматик, а не профессиональный аниме-сериал.
Тесты браузера / CI показывают техническую работоспособность, но не
доказывают качество художественной анимации.
"""


def assemble(dest):
    original=V19.read_bytes()
    html=mod.build().encode("utf-8")
    entries={
        "AI_Anime_Factory_V22_ACTING_COMBAT.html":html,
        "backup/AI_Anime_Factory_V19_ORIGINAL.html":original,
        "README_RU.txt":README.encode("utf-8"),
        "RUN_WINDOWS.bat":('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
                           'start "" "AI_Anime_Factory_V22_ACTING_COMBAT.html"\r\n').encode(),
        "source/acting_v22.js":(ROOT/"anime-factory"/"v22"/"acting_v22.js").read_bytes(),
        "source/build_acting_v22.py":GEN.read_bytes(),
        "source/visual_v21.js":(ROOT/"anime-factory"/"v21"/"visual_v21.js").read_bytes(),
        "source/story_v20.js":(ROOT/"anime-factory"/"v20"/"story_v20.js").read_bytes(),
        "source/test_anime_v22.py":(ROOT/"tests"/"test_anime_v22.py").read_bytes()
    }
    manifest={
        "schema":"AnimeFactoryV22Release/1","version":22,
        "source":"original V19 plus V20/V21/V22 extensions",
        "files":[{"path":n,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
                 for n,b in sorted(entries.items())]
    }
    entries["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
    dest=Path(dest).resolve()
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as out:
        for name,body in sorted(entries.items()):
            out.writestr(name,body)
    with zipfile.ZipFile(dest) as result:
        if result.testzip():raise RuntimeError("CRC32 failed")
        md=json.loads(result.read("BUILD_MANIFEST.json"))
        if set(result.namelist())!=set(entries):raise RuntimeError("File inventory differs")
        for entry in md["files"]:
            data=result.read(entry["path"])
            if len(data)!=entry["bytes"] or hashlib.sha256(data).hexdigest()!=entry["sha256"]:
                raise RuntimeError("SHA256 verification mismatch")
        if result.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=original:
            raise RuntimeError("V19 backup modified")
    print("V22 ZIP VERIFIED",dest,"bytes",dest.stat().st_size,"files",len(entries))
    return dest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(ROOT/"dist"/"AI_ANIME_FACTORY_V22_ACTING_COMBAT_WINDOWS.zip"))
    parser.add_argument("--selftest",action="store_true")
    args=parser.parse_args()
    if args.selftest:mod.selftest();return
    assemble(args.out)

if __name__=="__main__":main()
