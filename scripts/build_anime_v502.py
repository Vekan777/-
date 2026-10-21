#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 self-contained Windows editing/export package with 24 voiced lines.
The pre-generated project is optional; if present it is kept intact.
No fonts, model weights, or unsigned binaries are bundled.
"""
import argparse,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME="AI_Anime_Factory_V50_2_DIRECTOR_2D.html"
README=ROOT/"anime-factory/v50_2/README_RU.md"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",required=True)
    p.add_argument("--project")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    target=Path(a.out).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        z.write(Path(a.html).resolve(),NAME)
        z.write(README,"README_RU.md")
        for path in ("anime-factory/v50_2/build_director_v502.py",
                     "anime-factory/v50_2/director_v502.js",
                     "anime-factory/v50_1/build_cinematic_v501.py",
                     "anime-factory/v50_1/cinematic_pilot_v501.js",
                     "scripts/produce_2d_pilot_v50.py",
                     "scripts/produce_2d_pilot_v501.py",
                     "scripts/postprocess_v502.py",
                     "scripts/render_anime_v48.py",
                     "anime-factory/production_v50/PILOT_EP01_EP02_RU.json"):
            path=Path(path);z.write(ROOT/path,"SOURCE/"+path.name)
        # Source assets are supplemental; user runs editor without Python.
        z.write(ROOT/"scripts/render_anime_v48.py","render_anime_v48.py")
        z.write(ROOT/"scripts/postprocess_v502.py","postprocess_v502.py")
        z.writestr("RUN_WINDOWS.bat",f'@echo off\r\nstart "" "%~dp0{NAME}"\r\n')
        z.writestr("SETUP_WINDOWS.bat",
                  '@echo off\r\npy -3 -m pip install playwright==1.56.0\r\n'
                  'py -3 -m playwright install chromium\r\npause\r\n')
        z.writestr("GENERATE_MP4_WINDOWS.bat",
                  '@echo off\r\ncd /d "%~dp0"\r\n'
                  'if exist "tools\\ffmpeg\\bin\\ffmpeg.exe" set "PATH=%CD%\\tools\\ffmpeg\\bin;%PATH%"\r\n'
                  'if not exist "PROJECT_V502.json" (echo No PROJECT_V502.json & pause & exit /b 1)\r\n'
                  f'py -3 render_anime_v48.py --html "{NAME}" --project PROJECT_V502.json '
                  '--out OUTPUT --episodes 1,2 --fps 6 --mp4\r\npause\r\n')
        z.writestr("tools/ffmpeg/bin/PUT_FFMPEG_HERE.txt",
                   "Из вашего ffmpeg-9.0.2-full_build.zip распакуйте ffmpeg.exe и ffprobe.exe.\n")
        z.writestr("ACTOR_VOICES/README_RU.txt",
                  "24 WAV: e01_s01_l01.wav, e01_s01_l02.wav, ... e02_s06_l02.wav;\n"
                  "16-bit PCM, mono/stereo, recorded by Russian speakers with signed consent.\n"
                  "py -3 postprocess_v502.py --project PROJECT_PILOT_V501.json "
                  "--actor-voices ACTOR_VOICES --output PROJECT_V502.json\n"
                  "Потребуются FFmpeg и все 24 записи, без неполного микса.\n")
        if a.project:z.write(Path(a.project).resolve(),"PROJECT_V502.json")
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert NAME in z.namelist()
        assert "PROJECT_V502.json" in z.namelist() if a.project else True
    print("V50.2 WINDOWS ZIP",target,target.stat().st_size,
          hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=="__main__":main()
