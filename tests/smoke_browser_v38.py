#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V38 real Chromium QA: compare same-timestamp grading, PNG sheet, V37 subtitles and V36 WebM audio."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
  f.writeframes(b"".join(struct.pack("<h",round(8500*math.sin(2*math.pi*440*i/rate)))
    for i in range(3*rate)))
def png_info(path):
 raw=path.read_bytes()
 if raw[:8]!=b"\x89PNG\r\n\x1a\n" or len(raw)<5000:raise AssertionError("Bad PNG "+str(path))
 return hashlib.sha256(raw).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--html",required=True)
 p.add_argument("--out",default="dist/V38_CINEMATIC_SAMPLES")
 args=p.parse_args()
 dst=Path(args.out).resolve();dst.mkdir(parents=True,exist_ok=True)
 wav=dst/"V38_TEST_VOICE.wav";tone(wav)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1460,"height":1100},
   accept_downloads=True,device_scale_factor=1)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v38-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="cinematic-v38"]').click()
   page.locator("#v38-save").click()
   baseline=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V38'))""")
   if baseline["version"]!=38 or not baseline["episodes"][0].get("storyV20"):
    raise AssertionError("V38 migration lost project or story")
   if not baseline["characters"][0].get("qualityV23"):
    raise AssertionError("Old character model missing")
   # Copy remains only in browser test storage, NEVER in the GitHub originals.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V38',data=JSON.parse(localStorage.getItem(key));
    data.episodes[0].scenes=data.episodes[0].scenes.slice(0,2);
    data.episodes[0].scenes.forEach(s=>s.duration=1.25);
    localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v38-episode')?.options.length>0",timeout=45000)
   # V37: sample a real subtitle — must remain crisp on top of V38 grading.
   page.locator('[data-page="subtitles-v37"]').click()
   page.locator("#v37-scene").select_option("0")
   page.locator("#v37-start").fill("0.1")
   page.locator("#v37-end").fill("0.9")
   page.locator("#v37-speaker").fill("Герой")
   page.locator("#v37-text").fill("Цвет и камера — сцена")
   page.locator("#v37-save").click()
   page.locator('[data-page="cinematic-v38"]').click()
   page.locator("#v38-scene").select_option("0")
   page.locator("#v38-preset").select_option("neutral")
   page.locator("#v38-zoomStart").fill("1")
   page.locator("#v38-zoomEnd").fill("1")
   page.locator("#v38-panStart").fill("0")
   page.locator("#v38-panEnd").fill("0")
   page.locator("#v38-save").click()
   with page.expect_download(timeout=20000) as dl:
    page.locator("#v38-json").click()
   plan=dst/"V38_CINEMATIC_FINISHING.json";dl.value.save_as(str(plan))
   manifest=json.loads(plan.read_text(encoding="utf-8"))
   if manifest["version"]!=38 or len(manifest["episodes"][0]["scenes"])!=2:
    raise AssertionError("Missing V38 timeline")
   duration=manifest["episodes"][0]["totalSeconds"]
   # Only one timepoint, so color/motion is the sole change between screenshots.
   seek=str(round(1000*.5/duration))
   page.locator("#v38-seek").fill(seek)
   neutral=dst/"V38_REAL_CANVAS_NEUTRAL.png"
   page.locator("#v38-preview").screenshot(path=str(neutral))
   neutral_hash=png_info(neutral)
   page.locator("#v38-preset").select_option("moonlight")
   page.locator("#v38-zoomStart").fill("1.05")
   page.locator("#v38-zoomEnd").fill("1.29")
   page.locator("#v38-panStart").fill("-1")
   page.locator("#v38-panEnd").fill("1")
   page.locator("#v38-letterbox").check()
   page.locator("#v38-save").click()
   page.locator("#v38-seek").fill(seek)
   treated=dst/"V38_REAL_CANVAS_CINEMATIC.png"
   page.locator("#v38-preview").screenshot(path=str(treated))
   if png_info(treated)==neutral_hash:
    raise AssertionError("No genuine pixel change after camera/grade")
   with page.expect_download(timeout=20000) as dl:
    page.locator("#v38-sheet").click()
   sheet=dst/"V38_FOUR_REAL_FRAMES.png";dl.value.save_as(str(sheet))
   png_info(sheet)
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V38'))""")
   for key in ("storyV20","title"):
    if current["episodes"][0].get(key)!=baseline["episodes"][0].get(key):
     raise AssertionError("Legacy story mutated: "+key)
   if current["characters"][0]["qualityV23"]!=baseline["characters"][0]["qualityV23"]:
    raise AssertionError("Character models mutated")
   for key in ("storyboardV34","assemblyV35","audioV36","choreographyV25"):
    if current["episodes"][0]["scenes"][0].get(key)!=baseline["episodes"][0]["scenes"][0].get(key):
     raise AssertionError("Earlier scene field mutated: "+key)
   if current["episodes"][0]["scenes"][0]["cameraV38"]["letterbox"] is not True:
    raise AssertionError("V38 camera saved incorrectly")
   if not current["episodes"][0]["scenes"][0].get("subtitlesV37",{}).get("cues"):
    raise AssertionError("Existing V37 subtitles missing")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v36-export").click()
   movie=dst/"V38_REAL_CINEMATIC_WITH_AUDIO_AND_SUBTITLES.webm"
   dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V38_CINEMATIC_EPISODE_"):
    raise AssertionError("Not the V38 image finishing recorder")
   if movie.stat().st_size<6000:raise AssertionError("Recorded WebM is too small")
   probe={}
   if shutil.which("ffprobe"):
    proc=subprocess.run(["ffprobe","-v","error","-show_entries",
     "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
     capture_output=True,text=True,check=True,timeout=30)
    probe=json.loads(proc.stdout)
    codecs={item["codec_type"] for item in probe.get("streams",[])}
    if not {"audio","video"}.issubset(codecs):
     raise AssertionError("Real V38 movie lost audio or video: "+str(codecs))
    if float(probe.get("format",{}).get("duration",0))<1:
     raise AssertionError("Truncated WebM duration")
   if errors:raise AssertionError("Chromium JS errors: "+"; ".join(errors[:5]))
   qa={"version":38,"same_timestamp_real_pixel_differential":True,
    "legacy_story_characters_scene_data_preserved":True,
    "v37_subtitles_preserved":True,"v38_movie_bytes":movie.stat().st_size,
    "four_frame_sheet_verified":True,"ffprobe":probe,"pageerrors":errors}
   (dst/"V38_BROWSER_QA.json").write_text(json.dumps(
    qa,ensure_ascii=False,indent=2),encoding="utf-8")
   print("V38 CHROMIUM PASS: real pixel grade, camera motion, subtitles, audio+WebM, story preserved")
  finally:browser.close()
if __name__=="__main__":main()
