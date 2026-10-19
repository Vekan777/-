#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produce self-contained AI Rescue Factory V7 Unified candidate distribution.
Embeds all V1..V6 release ZIPs unchanged and genuine V19 HTML (plus V20.3
non-destructive candidate). SHA256 manifest validated after writing.
Python 3.10+, standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = "_v7/manifest.json"
MAX_FILES = 10000
MAX_TOTAL = 8 * 1024 ** 3
MAX_FILE = 2 * 1024 ** 3
ARCHIVE_NAME = "AI_RESCUE_FACTORY_V7_UNIFIED_CANDIDATE_WINDOWS.zip"

README_RU = """AI RESCUE FACTORY V7 — UNIFIED CANDIDATE / WINDOWS 10 x64
===========================================================
ПРОЧИТАЙТЕ ПЕРЕД ЗАПУСКОМ
Это автономная сборочная система, а не замена ChatGPT, не полноценный
3D-игровой движок и не профессиональная нейросеть для рисования аниме.
В V7 сохранена база V1–V6, подлинный HTML редактора V19 и восстановленный
кандидат V20.3. Большие исходные ZIP/MP4 эпизодов из библиотеки в архив
не входят; не выдавайте их за включённые материалы.

УСТАНОВКА
1. Установите Python 3.10 или новее для Windows 64-bit из python.org.
   Рекомендуем NTFS, свободное место на диске от 2 ГБ.
2. Распакуйте ВЕСЬ ZIP в новый каталог, например D:\\AI_RESCUE_V7.
   Не запускайте BAT прямо внутри ZIP.
3. Двойной щелчок: TEST_V7_WINDOWS.bat.
   Успешная проверка должна вывести две строки SELFTEST PASS.
4. Двойной щелчок: RUN_V7_WINDOWS.bat для графического интерфейса.
   Tkinter входит в стандартный установщик Python для Windows.
5. Если графический интерфейс не запускается, пользуйтесь CMD:

   py -3 rescue-engine\\unified_v7.py selftest
   py -3 rescue-engine\\unified_v7.py doctor
   py -3 rescue-engine\\unified_v7.py status
   py -3 rescue-engine\\unified_v7.py backup
   py -3 rescue-engine\\unified_v7.py release
   py -3 rescue-engine\\unified_v7.py audit
   py -3 rescue-engine\\unified_v7.py queue EXAMPLE_JOB.json
   py -3 rescue-engine\\unified_v7.py worker-once

ИМПОРТ СТАРЫХ ВЕРСИЙ:
- Архивы V1–V6 лежат в папке legacy/ в исходном виде.
- Импорт внешнего ZIP НЕ исполняет его код:
   py -3 rescue-engine\\unified_v7.py legacy-import "D:\\old.zip"
- Перенос проекта без удаления/перезаписи файлов:
   py -3 rescue-engine\\unified_v7.py migrate-files "D:\\old\\workspace\\default\\files"
- Конфликты и отличающиеся файлы НЕ перезаписываются.
- Создаётся резервная копия до переноса.
- Оригиналы хранятся отдельно.

ПРОВЕРКА ЦЕЛОСТНОСТИ:
   py -3 rescue-engine\\unified_v7.py bundle-verify "D:\\download\\AI_RESCUE_FACTORY_V7_UNIFIED_CANDIDATE_WINDOWS.zip"
Проверяются CRC32, SHA256, пути файлов и состав манифеста.
Если архив повреждён — не используйте, скачайте его заново.

AI ANIME FACTORY:
Откройте вкладки в GUI или эти HTML:
   anime-factory\\v19\\AI_Anime_Factory_V19.html
   anime-factory\\v20\\AI_Anime_Factory_V20_3_PRESERVATION.html
V20.3 — экспериментальная восстановленная редакция поверх V19.
Графика остаётся процедурным 2D-аниматиком, это не готовый 3D-мультфильм.

СТРУКТУРА:
legacy/                 Неперезаписанные ZIP предыдущих версий
rescue-engine/          Движок, модули ИИ, импорт, проверка
anime-factory/          HTML V19 и V20.3
workspace/default/files Рабочий проект
backups/default/        Резервные ZIP проекта
releases/default/       Проверенные ZIP проекта
legacy-imports/         ZIP, сохранённые побайтово
tests/                  Python тесты

AI:
Входящий код ИИ сохраняется без автоматического выполнения.
Провайдеры Ollama и внешние API опциональны и не входят в ZIP.
Подписка ChatGPT Plus/Pro не заменяет оплату внешнего API.
Не пересылайте токены в открытый GitHub, не включайте секреты в ZIP.

ЗАВЕРШЕНИЕ:
Сначала тесты на GitHub Actions (Windows + Linux), потом статус
Verified Final. Пока тесты не завершились — это Candidate, а не Final.
"""

BAT_GUI = ('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
           'where py >nul 2>&1\r\n'
           'if errorlevel 1 (python gui_v7.py) else (py -3 gui_v7.py)\r\n'
           'echo.\r\npause\r\n')

BAT_TEST = ('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\n'
            'where py >nul 2>&1\r\n'
            'if errorlevel 1 (python rescue-engine\\engine.py selftest '
            '&& python rescue-engine\\unified_v7.py selftest) '
            'else (py -3 rescue-engine\\engine.py selftest '
            '&& py -3 rescue-engine\\unified_v7.py selftest)\r\n'
            'echo.\r\npause\r\n')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def prepare(root, source_dist):
    data = {}
    def add(rel, path):
        p = root / path
        if not p.is_file():
            raise FileNotFoundError("Missing source file " + str(p))
        data[rel] = p.read_bytes()

    for name in ("engine.py", "unified_v7.py", "launch.py", "ai_pipeline.py"):
        add("rescue-engine/" + name, "rescue-engine/" + name)
    for path in ("gui_v7.py", "tests/test_engine.py",
                 "tests/test_unified_v7.py",
                 "scripts/build_releases.py", "scripts/build_v7.py",
                 "anime-factory/v19/AI_Anime_Factory_V19.html",
                 "anime-factory/v20/patch_preserve.py",
                 "anime-factory/v20/story_v20.js",
                 "anime-factory/v21/visual_v21.js",
                 "anime-factory/v21/build_visual_v21.py",
                 "anime-factory/v21/README_RU.md",
                 "anime-factory/v20/build_story_v20.py",
                 "anime-factory/v20/README_RU.md",
                 "docs/RELEASE_HISTORY_AND_ASSETS_RU.md"):
        add(path, path)
    add("backup/AI_Anime_Factory_V19_ORIGINAL.html",
        "anime-factory/v19/AI_Anime_Factory_V19.html")

    patch_path = root / "anime-factory" / "v20" / "patch_preserve.py"
    spec = importlib.util.spec_from_file_location("anime_v20_preservation", patch_path)
    patch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch)
    original = (root / "anime-factory" / "v19" /
                "AI_Anime_Factory_V19.html").read_text(encoding="utf-8")
    data["anime-factory/v20/AI_Anime_Factory_V20_3_PRESERVATION.html"] = (
        patch.patch(original).encode("utf-8")
    )
    story_path = root / "anime-factory" / "v20" / "build_story_v20.py"
    story_spec = importlib.util.spec_from_file_location("anime_v20_story", story_path)
    story_builder = importlib.util.module_from_spec(story_spec)
    story_spec.loader.exec_module(story_builder)
    addon = (root / "anime-factory" / "v20" / "story_v20.js").read_text(encoding="utf-8")
    data["anime-factory/v20/AI_Anime_Factory_V20_STORY_COMBAT.html"] = (
        story_builder.patch(original, addon).encode("utf-8")
    )
    visual_path = root / "anime-factory" / "v21" / "build_visual_v21.py"
    visual_spec = importlib.util.spec_from_file_location("anime_v21_visual", visual_path)
    visual_builder = importlib.util.module_from_spec(visual_spec)
    visual_spec.loader.exec_module(visual_builder)
    data["anime-factory/v21/AI_Anime_Factory_V21_VISUAL_QUALITY.html"] = (
        visual_builder.build().encode("utf-8")
    )

    names = [
        f"AI_RESCUE_FACTORY_V{i}_WINDOWS.zip" for i in range(1, 7)
    ] + [
        "AI_ANIME_FACTORY_V19_REBUILT_WINDOWS.zip",
        "AI_ANIME_FACTORY_V20_3_REBUILT_WINDOWS.zip",
        "AI_ANIME_FACTORY_V20_STORY_COMBAT_WINDOWS.zip",
        "AI_ANIME_FACTORY_V21_VISUAL_QUALITY_WINDOWS.zip",
        "AI_RESCUE_ALL_SOURCES_V1_V6_AND_ANIME_V19.zip"
    ]
    for filename in names:
        source = source_dist / filename
        if not source.exists():
            raise FileNotFoundError("Missing verified legacy ZIP: " + str(source))
        with zipfile.ZipFile(source) as z:
            if z.testzip():
                raise ValueError("Legacy ZIP failed CRC check: " + filename)
        data["legacy/" + filename] = source.read_bytes()

    data["README_RU.txt"] = README_RU.encode("utf-8")
    data["RUN_V7_WINDOWS.bat"] = BAT_GUI.encode("utf-8")
    data["TEST_V7_WINDOWS.bat"] = BAT_TEST.encode("utf-8")
    data["EXAMPLE_JOB.json"] = json.dumps({
        "format": "ArtifactBridgeJob/1",
        "project": "AI Rescue Unified V7",
        "files": [{"path": "docs/Память_проекта.txt",
                   "content": "Сохранять сюжет, героев, способности и историю версий."}]
    }, ensure_ascii=False, indent=2).encode("utf-8")

    keys = {name.casefold() for name in data}
    if len(keys) != len(data) or META in data:
        raise ValueError("Duplicate or reserved V7 paths")
    if len(data) > MAX_FILES:
        raise ValueError("Too many files")
    return data


def check_zip(path):
    with zipfile.ZipFile(path) as z:
        rows = z.infolist()
        names = {i.filename for i in rows}
        if len(names) != len(rows) or META not in names:
            raise ValueError("Missing or duplicated entries")
        if z.testzip():
            raise ValueError("CRC32 failure")
        doc = json.loads(z.read(META))
        if doc.get("format") != "AIRescueUnified/7":
            raise ValueError("Unknown V7 format")
        listed = {row["path"] for row in doc["files"]}
        if listed != names - {META}:
            raise ValueError("V7 file inventory mismatch")
        for item in doc["files"]:
            content = z.read(item["path"])
            if len(content) != item["size"] or sha256(content) != item["sha256"]:
                raise ValueError("V7 SHA256 mismatch: " + item["path"])
        return len(listed)


def write_release(data, dest):
    if dest.exists():
        raise FileExistsError("Refusing to overwrite verified release")
    dest.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": "AIRescueUnified/7",
        "version": "7.0",
        "status": "Candidate - awaiting Windows and Linux CI verification",
        "contains": ["Core V1-V6", "Legacy ZIPs", "Optional AI Pipeline",
                     "V19 original HTML", "V20.3 rebuilt candidate", "Tk GUI"],
        "files": [
            {"path":name, "size":len(content), "sha256":sha256(content)}
            for name,content in sorted(data.items())
        ]
    }
    with tempfile.TemporaryDirectory(prefix="v7-build-", dir=dest.parent) as td:
        scratch = Path(td)/"release.zip"
        with zipfile.ZipFile(scratch,"w",compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6,allowZip64=True) as z:
            for name,contents in sorted(data.items()):
                z.writestr(name,contents)
            z.writestr(META,json.dumps(manifest,ensure_ascii=False,indent=2))
        count = check_zip(scratch)
        os.replace(scratch, dest)
        return count


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--out", default=str(ROOT / "dist"))
    cli.add_argument("--legacy", default=str(ROOT / "dist"))
    cli.add_argument("--verify")
    args = cli.parse_args()
    if args.verify:
        print("VALIDATED V7 PACKAGE", check_zip(args.verify))
        return
    files = prepare(ROOT, Path(args.legacy).resolve())
    dest = Path(args.out).resolve()
    release = dest / ARCHIVE_NAME
    number = write_release(files,release)
    print("BUILD V7",str(release),"files",number,"bytes",release.stat().st_size)
    assert check_zip(release) == number
    print("V7 PACKAGE INTEGRITY PASS")


if __name__ == "__main__":
    main()
