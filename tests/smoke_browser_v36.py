#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V36 Chromium smoke: real WAV playback, timeline manifest and recorded WebM."""
from __future__ import annotations
import argparse
import json
import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from playwright.sync_api import sync_playwright

def tone(path):
    sr=16000
    with wave.open(str(path),"wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(sr)
        samples=b"".join(struct.pack("<h",int(8000*math.sin(2*math.pi*440*i/sr)))
                         for i in range(int(sr*2)))
        out.writeframes(samples)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",required=True)
    p.add_argument("--out",default="dist/V36_AUDIO_SAMPLES")
    args=p.parse_args()
    folder=Path(args.out).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    wav=folder/"V36_TEST_AUDIO.wav"
    tone(wav)
    errors=[]
    with sync_playwright() as play:
        browser=play.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
            "--autoplay-policy=no-user-gesture-required"])
        page=browser.new_page(viewport={"width":1460,"height":1120},accept_downloads=True)
        page.on("pageerror",lambda error:errors.append(str(error)))
        try:
            page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => document.querySelector('#v36-episode')?.options.length>0",timeout=45000)
            page.locator('[data-page="audio-v36"]').click()
            page.wait_for_function("() => !document.querySelector('#page-audio-v36').hidden")
            before=page.evaluate("""() => ({
               version:P.version,plot:P.episodes[0].storyV20,
               hero:P.characters[0].qualityV23,
               previous:P.episodes[0].scenes[0].assemblyV35,
               oldDuration:P.episodes[0].scenes[0].duration
            })""")
            if before["version"]!=36 or not before["plot"] or not before["hero"]:
                raise AssertionError("V36 lost canonical V20/V23 content")
            page.locator("#v36-slot").select_option("voice")
            page.locator("#v36-audiofile").set_input_files(str(wav))
            page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
            page.locator("#v36-gain").fill("75")
            page.locator("#v36-offset").fill("25")
            page.locator("#v36-save").click()
            with page.expect_download(timeout=20000) as download:
                page.locator("#v36-json").click()
            manifest=folder/"V36_AUDIO_EPISODE.json"
            download.value.save_as(str(manifest))
            data=json.loads(manifest.read_text(encoding="utf-8"))
            slot=data["audio"][0]["scenes"][0]["slots"]["voice"]
            if slot["name"]!=wav.name or not slot["loadedInBrowser"]:
                raise AssertionError("Audio metadata/attachment missing")
            if abs(slot["gain"]-.75)>1e-5 or abs(slot["offsetSeconds"]-.25)>1e-5:
                raise AssertionError("Volume or offset not saved")
            after=page.evaluate("""() => ({
                duration:P.episodes[0].scenes[0].duration,
                plot:P.episodes[0].storyV20,
                hero:P.characters[0].qualityV23,
                previous:P.episodes[0].scenes[0].assemblyV35,
                audio:P.episodes[0].scenes[0].audioV36
            })""")
            for k,past in (("duration","oldDuration"),("plot","plot"),
                           ("hero","hero"),("previous","previous")):
                if after[k]!=before[past]:
                    raise AssertionError("Existing story or V35 timing rewritten: "+k)
            # Reduce runtime ONLY in the browser test's in-memory copy; source files unaffected.
            page.evaluate("""() => {
              P.episodes[0].scenes=P.episodes[0].scenes.slice(0,2);
              P.episodes[0].scenes.forEach(s=>{s.duration=1.1;});
              v36Scenes();
            }""")
            page.locator("#v36-play").click()
            page.wait_for_function("() => v36Active",timeout=20000)
            page.wait_for_timeout(400)
            clock=page.locator("#v36-clock").inner_text()
            if "сцена" not in clock:raise AssertionError("No audio-visual clock")
            page.locator("#v36-play").click()
            page.wait_for_function("() => !v36Active",timeout=15000)
            with page.expect_download(timeout=45000) as movie:
                page.locator("#v36-export").click()
            video=folder/"V36_REAL_AUDIO_EPISODE.webm"
            movie.value.save_as(str(video))
            if video.stat().st_size<6000:
                raise AssertionError("Actual WebM too small: "+str(video.stat().st_size))
            probe={}
            if shutil.which("ffprobe"):
                outcome=subprocess.run(
                 ["ffprobe","-v","error","-show_entries",
                  "format=duration:stream=codec_type,codec_name",
                  "-of","json",str(video)],
                 capture_output=True,text=True,timeout=30,check=True)
                probe=json.loads(outcome.stdout)
                kinds={s["codec_type"] for s in probe.get("streams",[])}
                if not {"audio","video"}.issubset(kinds):
                    raise AssertionError("Recorded WebM must contain audio and video: "+str(kinds))
                if float(probe.get("format",{}).get("duration",0))<1:
                    raise AssertionError("Video duration unexpectedly short")
            if errors:raise AssertionError("Browser JS errors: "+"; ".join(errors[:5]))
            (folder/"V36_BROWSER_QA.json").write_text(
              json.dumps({"v36":True,"legacy_preserved":True,
               "actual_webm_bytes":video.stat().st_size,
               "wav_attached":True,"audio_video_clock":True,
               "ffprobe":probe,"pageerrors":errors},ensure_ascii=False,indent=2),
              encoding="utf-8")
            print("V36 CHROMIUM PASS: audio upload, project unchanged, actual WebM with audio/video")
        finally:
            browser.close()

if __name__=="__main__":main()
