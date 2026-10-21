#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one portable Windows V50.1 pilot ZIP with full HTML and batch tooling.
Only package after technical regression; never mark art as finished automatically.
"""
from pathlib import Path
import argparse,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
def add(z,file,name):
    if not file.is_file():raise FileNotFoundError(file)
    z.write(file,name)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",required=True)
    p.add_argument("--project")
    p.add_argument("--out",required=True)
    opt=p.parse_args()
    target=Path(opt.out).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    readme=ROOT/"anime-factory/v50_1/README_RU.md"
    name="AI_Anime_Factory_V50_1_CINEMATIC_2D.html"
    run="@echo off\r\nsetlocal\r\nstart \"\" \"%~dp0"+name+"\"\r\n"
    setup="@echo off\r\nsetlocal\r\npy -3 -m pip install playwright==1.56.0\r\npy -3 -m playwright install chromium\r\npause\r\n"
    render=("@echo off\r\nsetlocal\r\n"
      "cd /d \"%~dp0\"\r\n"
      "if exist \"tools\\ffmpeg\\bin\\ffmpeg.exe\" set \"PATH=%CD%\\tools\\ffmpeg\\bin;%PATH%\"\r\n"
      "if not exist \"PROJECT_INPUT.json\" (echo ERROR: Save the full project as PROJECT_INPUT.json & pause & exit /b 1)\r\n"
      "py -3 render_anime_v48.py --html "+name+
      " --project PROJECT_INPUT.json --out OUTPUT --episodes 1,2 --fps 6 --mp4\r\n"
      "pause\r\n")
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        add(z,Path(opt.html).resolve(),name)
        add(z,readme,"README_RU.md")
        add(z,ROOT/"anime-factory/v50_1/cinematic_pilot_v501.js","SOURCE/cinematic_pilot_v501.js")
        add(z,ROOT/"anime-factory/v50_1/build_cinematic_v501.py","SOURCE/build_cinematic_v501.py")
        add(z,ROOT/"scripts/render_anime_v48.py","render_anime_v48.py")
        add(z,ROOT/"scripts/produce_2d_pilot_v50.py","SOURCE/produce_2d_pilot_v50.py")
        add(z,ROOT/"scripts/produce_2d_pilot_v501.py","SOURCE/produce_2d_pilot_v501.py")
        add(z,ROOT/"anime-factory/production_v50/PILOT_EP01_EP02_RU.json","SOURCE/PILOT_EP01_EP02_RU.json")
        z.writestr("RUN_WINDOWS.bat",run)
        z.writestr("SETUP_BATCH_WINDOWS.bat",setup)
        z.writestr("RUN_BATCH_WINDOWS.bat",render)
        z.writestr("tools/ffmpeg/bin/PUT_FFMPEG_EXE_HERE.txt",
            "Распакуйте имеющийся FFmpeg 9.0.2 сюда: ffmpeg.exe и ffprobe.exe.\n")
        z.writestr("PROJECT_INPUT_INSTRUCTIONS_RU.txt",
            "Откройте редактор V50.1, импортируйте JSON пилота, затем сохраните полный "
            "проект как PROJECT_INPUT.json в эту папку. Пример JSON прилагается.\n")
        if opt.project:
            add(z,Path(opt.project).resolve(),"PROJECT_PILOT_V501.json")
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert "RUN_WINDOWS.bat" in z.namelist()
    print("V50.1 WINDOWS ZIP",target,target.stat().st_size,
          hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=="__main__":main()
