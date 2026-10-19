#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produce self-contained AI Anime Factory V21 Visual Quality Windows ZIP."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
V21=ROOT/"anime-factory"/"v21"
GEN=V21/"build_visual_v21.py"
spec=importlib.util.spec_from_file_location("anime_visual_v21",GEN)
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
README="""AI ANIME FACTORY V21 — VISUAL QUALITY / WINDOWS 10 x64
=====================================================
Основа: подлинный V19 + V20 Story & Combat + новые слои V21.
Это автономный 2D-аниматик, НЕ профессиональная нейрогенерация видео.

УСТАНОВКА
1. Распакуйте ZIP в отдельную папку. Не запускайте файлы внутри ZIP.
2. Дважды нажмите RUN_WINDOWS.bat или откройте HTML в Chrome/Edge.
3. Перейдите на вкладку «Визуал V21».
4. Выберите сцену, палитру света и погоду, затем настройте интенсивность,
   глубину, лучи, контурный свет, искры и зерно.
5. «Применить и сохранить» сохраняет параметры в проекте JSON.
6. «Режиссёрский пресет» выбирает стиль по типу сцены.
7. «Скачать четыре кадра PNG» формирует сравнимые планы сцены.
8. В штатном разделе «Выпуск / QA» экспортируйте сцену в PNG/ZIP.
9. Для создания MP4 понадобится FFmpeg; прежний экспорт V19 сохранён.
10. Сохраните JSON через «Скачать JSON», делайте резервные копии.

Ваша конфигурация Windows 10 x64, 8 ГБ RAM:
640x360, 6 FPS, один эпизод за проход; HD после проверки памяти.

СОВМЕСТИМОСТЬ
V19 не изменён (сохранён в backup/). V20 Story & Combat включён.
Импорт старого JSON осуществляется через прежнюю кнопку редактора.
Новый localStorage V21 не переписывает локальный ключ V19.
Поля visualV21 хранятся в каждой сцене.

ВНИМАНИЕ
Готовые кадры и художественное качество на конкретном ноутбуке следует
проверить вручную. Реальная 3D-анимация, рисование профессиональных
персонажей нейросетью и автоматический дубляж этим ZIP не обеспечены.
"""


def assemble(out):
    src=V19.read_bytes()
    html=b.build().encode("utf-8")
    files={
       "AI_Anime_Factory_V21_VISUAL_QUALITY.html":html,
       "backup/AI_Anime_Factory_V19_ORIGINAL.html":src,
       "README_RU.txt":README.encode("utf-8"),
       "RUN_WINDOWS.bat":('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
                           'start "" "AI_Anime_Factory_V21_VISUAL_QUALITY.html"\r\n').encode("utf-8"),
       "source/visual_v21.js":(V21/"visual_v21.js").read_bytes(),
       "source/build_visual_v21.py":GEN.read_bytes(),
       "source/story_v20.js":(ROOT/"anime-factory"/"v20"/"story_v20.js").read_bytes(),
       "source/build_story_v20.py":(ROOT/"anime-factory"/"v20"/"build_story_v20.py").read_bytes(),
       "source/test_anime_v21.py":(ROOT/"tests"/"test_anime_v21.py").read_bytes(),
    }
    manifest={"format":"AnimeVisualV21/1",
              "sourceVersion":19,"version":21,
              "status":"CI verified syntax & structural QA; visual local test pending",
              "files":[{"path":name,"size":len(data),"sha256":hashlib.sha256(data).hexdigest()}
                       for name,data in sorted(files.items())]}
    files["BUILD_MANIFEST.json"]=json.dumps(manifest,ensure_ascii=False,indent=2).encode("utf-8")
    out=Path(out).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():out.unlink()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as z:
        for name,data in sorted(files.items()):
            z.writestr(name,data)
    with zipfile.ZipFile(out) as z:
        if z.testzip():raise ValueError("ZIP CRC32 failed")
        m=json.loads(z.read("BUILD_MANIFEST.json"))
        if set(z.namelist()) != set(files):raise ValueError("ZIP file list differs")
        for item in m["files"]:
            blob=z.read(item["path"])
            if len(blob)!=item["size"] or hashlib.sha256(blob).hexdigest()!=item["sha256"]:
                raise ValueError("ZIP manifest SHA256 differs")
        if z.read("backup/AI_Anime_Factory_V19_ORIGINAL.html")!=src:
            raise ValueError("V19 backup mismatch")
    print("V21 ZIP VERIFIED",str(out),"bytes",out.stat().st_size,"files",len(files))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default=str(ROOT/"dist"/"AI_ANIME_FACTORY_V21_VISUAL_QUALITY_WINDOWS.zip"))
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    if args.selftest:
        b.selftest()
    else:
        assemble(args.out)

if __name__=="__main__":
    main()
