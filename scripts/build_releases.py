#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build reproducible source ZIPs for rescue editions V1..V6 and anime V19.
Do not claim these are bitwise-identical to prior browser downloads.
"""
import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESCUE = ROOT / "rescue-engine"
ANIME = ROOT / "anime-factory" / "v19"
VERSIONS = {
    1: "Base: offline files, status and release ZIP",
    2: "Backups: restore, SHA256 verification",
    3: "Safe job application: ArtifactBridgeJob/1",
    4: "Optional local Ollama and HTTPS-compatible AI proposal generation",
    5: "SQLite queue, crash recovery, durable jobs",
    6: "Remote GitHub Actions build, Windows/Linux tests and releases",
}
README = """AI RESCUE FACTORY v{n} — WINDOWS 10 x64
=====================================
A reconstructed release generated from reviewed source, not an exact copy
of the old ChatGPT browser-downloaded ZIP.

1. Install Python 3.10+ x64 from python.org if needed.
2. Extract the whole ZIP to a new folder (NTFS recommended).
3. Double-click TEST_WINDOWS.bat.
4. Double-click RUN_WINDOWS.bat.
5. See the command examples below.

Commands from CMD:
  py -3 launch.py selftest
  py -3 launch.py status
  py -3 launch.py release
  py -3 launch.py backup                  [edition V2+]
  py -3 launch.py verify "FILE.zip"       [edition V2+]
  py -3 launch.py job "EXAMPLE_JOB.json"  [edition V3+]
  py -3 launch.py ai TASK.txt --provider offline  [V4+]
  py -3 launch.py queue EXAMPLE_JOB.json  [V5+]
  py -3 launch.py once                    [V5+]

Generated project files: workspace/default/files/
Verified release ZIPs: releases/default/
Backup snapshots: backups/default/
Proposals: proposals/

Limits: This edition is an offline build utility, not a full anime renderer.
V19 anime studio is packaged separately, and historical V20 browser-only
versions must not be described as complete verified releases.
Provider API secrets should be kept only in local environment variables.
This release does NOT bypass ChatGPT subscriptions/quotas or install programs.
Version description: {description}
"""

def bat(command):
    return ('@echo off\r\ncd /d "%~dp0"\r\nwhere py >nul 2>&1\r\n'
            'if errorlevel 1 (python launch.py ' + command +
            ') else (py -3 launch.py ' + command + ')\r\npause\r\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def make_zip(destination, files):
    if destination.exists():
        destination.unlink()
    manifest = {"schema":"RescueDistribution/1",
                "files":[{"path":p,"sha256":sha(b),"size":len(b)}
                         for p,b in sorted(files.items())]}
    files["DISTRIBUTION_MANIFEST.json"] = json.dumps(
        manifest,ensure_ascii=False,indent=2).encode("utf-8")
    with zipfile.ZipFile(destination,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6,allowZip64=True) as z:
        for name, body in sorted(files.items()):
            zi=zipfile.ZipInfo(name,(2020,1,1,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=0o100644<<16
            z.writestr(zi,body)
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        md=json.loads(z.read("DISTRIBUTION_MANIFEST.json"))
        assert set(z.namelist())==set(files)
        for f in md["files"]:
            assert len(z.read(f["path"]))==f["size"]
            assert sha(z.read(f["path"]))==f["sha256"]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(ROOT/"dist"))
    args=parser.parse_args()
    output=Path(args.out).resolve()
    output.mkdir(parents=True,exist_ok=True)
    print("BUILD DIRECTORY:",output)

    core=(RESCUE/"engine.py").read_bytes()
    launcher=(RESCUE/"launch.py").read_bytes()
    ai=(RESCUE/"ai_pipeline.py").read_bytes()
    example=json.dumps({"format":"ArtifactBridgeJob/1","project":"AI Rescue",
                        "files":[{"path":"docs/hello.txt","content":"Привет из V6"}]},
                       ensure_ascii=False,indent=2).encode("utf-8")
    index=[]
    for n,description in VERSIONS.items():
        files={
            "engine.py":core,"launch.py":launcher,
            "edition.json":json.dumps({"version":n,"description":description},
                                      ensure_ascii=False,indent=2).encode("utf-8"),
            "README_RU.txt":README.format(n=n,description=description).encode("utf-8"),
            "RUN_WINDOWS.bat":bat("status").encode("utf-8"),
            "TEST_WINDOWS.bat":bat("selftest").encode("utf-8"),
            "EXAMPLE_JOB.json":example,
            "TASK.txt":"Создай простой Python-проект.\n".encode("utf-8")
        }
        if n>=4: files["ai_pipeline.py"]=ai
        name=f"AI_RESCUE_FACTORY_V{n}_WINDOWS.zip"
        make_zip(output/name,files)
        index.append((name,(output/name).stat().st_size))
        print("BUILT:",name,index[-1][1],"bytes")

    studio=ANIME/"AI_Anime_Factory_V19.html"
    if not studio.exists():
        raise SystemExit("V19 ORIGINAL SOURCE MISSING")
    v19={
        "AI_Anime_Factory_V19.html":studio.read_bytes(),
        "RUN_V19_WINDOWS.bat":('@echo off\r\ncd /d "%~dp0"\r\n'
                               'start "" "AI_Anime_Factory_V19.html"\r\n').encode("utf-8"),
        "README_RU.txt":("AI Anime Factory V19 — восстановленный дистрибутив HTML.\n"
            "Откройте HTML в Chrome/Edge. Это версия 2D-аниматика, а не 3D-фильм.\n"
            "Исходный ZIP V19 из Library не копируется побайтово.\n").encode("utf-8")
    }
    make_zip(output/"AI_ANIME_FACTORY_V19_REBUILT_WINDOWS.zip",v19)
    import importlib.util
    patch_file=ROOT/"anime-factory"/"v20"/"patch_preserve.py"
    spec=importlib.util.spec_from_file_location("anime_v20_patch",patch_file)
    patch_module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch_module)
    patched=patch_module.patch(studio.read_text(encoding="utf-8"))
    v20={
        "AI_Anime_Factory_V20_3_PRESERVATION.html":patched.encode("utf-8"),
        "backup/AI_Anime_Factory_V19_ORIGINAL.html":studio.read_bytes(),
        "RUN_WINDOWS.bat":('@echo off\r\ncd /d "%~dp0"\r\n'
                           'start "" "AI_Anime_Factory_V20_3_PRESERVATION.html"\r\n').encode("utf-8"),
        "README_RU.txt":("V20.3 REBUILT CANDIDATE: patch over original V19.\n"
                         "Nonstandard JSON fields are preserved; V19 2D renderer remains.\n"
                         "Not yet verified in actual Windows browsers.\n").encode("utf-8")
    }
    make_zip(output/"AI_ANIME_FACTORY_V20_3_REBUILT_WINDOWS.zip",v20)
    index.append(("AI_ANIME_FACTORY_V20_3_REBUILT_WINDOWS.zip",
                  (output/"AI_ANIME_FACTORY_V20_3_REBUILT_WINDOWS.zip").stat().st_size))
    index.append(("AI_ANIME_FACTORY_V19_REBUILT_WINDOWS.zip",
                  (output/"AI_ANIME_FACTORY_V19_REBUILT_WINDOWS.zip").stat().st_size))
    all_source={
        "rescue-engine/engine.py":core,
        "rescue-engine/launch.py":launcher,
        "rescue-engine/ai_pipeline.py":ai,
        "anime-factory/v19/AI_Anime_Factory_V19.html":studio.read_bytes(),
        "tests/test_engine.py":(ROOT/"tests/test_engine.py").read_bytes(),
        "anime-factory/v20/patch_preserve.py":patch_file.read_bytes(),
        "scripts/build_releases.py":Path(__file__).read_bytes()
    }
    make_zip(output/"AI_RESCUE_ALL_SOURCES_V1_V6_AND_ANIME_V19.zip",all_source)
    index.append(("AI_RESCUE_ALL_SOURCES_V1_V6_AND_ANIME_V19.zip",
                  (output/"AI_RESCUE_ALL_SOURCES_V1_V6_AND_ANIME_V19.zip").stat().st_size))
    (output/"RELEASE_INDEX.json").write_text(
        json.dumps([{"name":n,"bytes":s} for n,s in index],
                   ensure_ascii=False,indent=2),encoding="utf-8")
    print("DONE",len(index),"ZIP archives")

if __name__=="__main__":
    main()
