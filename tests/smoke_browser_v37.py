#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V37 real Chromium: subtitle timestamps, PNG proof, legacy preservation, WebM with sound."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright

def audio(path):
 rate=16000
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes(b"".join(struct.pack("<h",round(8500*math.sin(2*math.pi*440*i/rate)))
    for i in range(rate*3)))
def png(path):
 data=path.read_bytes()
 if data[:8]!=b"\x89PNG\r\n\x1a\n" or len(data)<4000:raise AssertionError("Bad PNG "+str(path))
 return hashlib.sha256(data).hexdigest()
def main():
 args=argparse.ArgumentParser()
 args.add_argument("--html",required=True)
 args.add_argument("--out",default="dist/V37_SUBTITLE_SAMPLES")
 opt=args.parse_args()
 dest=Path(opt.out).resolve();dest.mkdir(parents=True,exist_ok=True)
 wav=dest/"V37_TEST_440HZ.wav";audio(wav)
 errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage",
     "--disable-gpu","--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1480,"height":1140},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(opt.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v37-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-save").click()
   baseline=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V37'))""")
   if not baseline or baseline["version"]!=37:raise AssertionError("Not V37 storage")
   if not baseline["episodes"][0].get("storyV20") or not baseline["characters"][0].get("qualityV23"):
    raise AssertionError("Canonical story or model missing")
   # Shorten ONLY in-memory test project for feasible real-time WebM capture.
   page.evaluate("""() => {
     const key='AI_ANIME_FACTORY_V37',data=JSON.parse(localStorage.getItem(key));
     data.episodes[0].scenes=data.episodes[0].scenes.slice(0,2);
     data.episodes[0].scenes.forEach(s=>s.duration=1.2);
     localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v37-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="subtitles-v37"]').click()
   page.locator("#v37-scene").select_option("0")
   page.locator("#v37-start").fill("0.15")
   page.locator("#v37-end").fill("0.85")
   page.locator("#v37-speaker").fill("Герой")
   page.locator("#v37-text").fill("Сюжет сохранён")
   page.locator("#v37-save").click()
   page.locator("#v37-audit").click()
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v37-srt").click()
   srt=dest/"V37_REAL_EPISODE.srt";dl.value.save_as(str(srt))
   srtext=srt.read_text(encoding="utf-8")
   if "00:00:00,150 --> 00:00:00,850" not in srtext or "Герой: Сюжет сохранён" not in srtext:
    raise AssertionError("Wrong timed SRT: "+srtext[:400])
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v37-vtt").click()
   vtt=dest/"V37_REAL_EPISODE.vtt";dl.value.save_as(str(vtt))
   if not vtt.read_text(encoding="utf-8").startswith("WEBVTT\n"):
    raise AssertionError("Invalid WebVTT format")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v37-json").click()
   manifest=dest/"V37_SUBTITLE_DELIVERY.json";dl.value.save_as(str(manifest))
   doc=json.loads(manifest.read_text(encoding="utf-8"))
   if doc["version"]!=37 or len(doc["episodes"][0]["cues"])!=1:
    raise AssertionError("Incorrect V37 JSON or cues")
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V37'))""")
   for field in ("storyV20","title"):
    if current["episodes"][0].get(field)!=baseline["episodes"][0].get(field):
     raise AssertionError("Old story rewritten: "+field)
   if current["characters"][0]["qualityV23"]!=baseline["characters"][0]["qualityV23"]:
    raise AssertionError("Character model overwritten")
   for key in ("assemblyV35","audioV36","storyboardV34","choreographyV25"):
    if current["episodes"][0]["scenes"][0].get(key)!=baseline["episodes"][0]["scenes"][0].get(key):
     raise AssertionError("Legacy scene changed: "+key)
   # Same exact timestamp, with subtitle and after removing cue:
   # visual evidence is pixel-level change, not a fake placeholder.
   page.locator("#v37-seek").fill("380")
   with_text=dest/"V37_REAL_CANVAS_WITH_SUBTITLE.png"
   page.locator("#v37-preview").screenshot(path=str(with_text))
   sha_text=png(with_text)
   page.locator("#v37-cue").select_option("0")
   page.locator("#v37-remove").click()
   page.locator("#v37-seek").fill("380")
   without=dest/"V37_REAL_CANVAS_NO_SUBTITLE.png"
   page.locator("#v37-preview").screenshot(path=str(without))
   if sha_text==png(without):raise AssertionError("Caption did not alter real canvas pixels")
   # Restore cue for movie proof.
   page.locator("#v37-start").fill("0.15")
   page.locator("#v37-end").fill("0.85")
   page.locator("#v37-speaker").fill("Герой")
   page.locator("#v37-text").fill("Сюжет сохранён")
   page.locator("#v37-save").click()
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=50000) as dl:
    page.locator("#v36-export").click()
   webm=dest/"V37_REAL_EPISODE_WITH_AUDIO_AND_SUBTITLES.webm"
   dl.value.save_as(str(webm))
   if not dl.value.suggested_filename.startswith("V37_EPISODE_SUBTITLES_"):
    raise AssertionError("Recorder exported wrong generation")
   if webm.stat().st_size<6000:raise AssertionError("Not a real WebM movie")
   probe={}
   if shutil.which("ffprobe"):
    proc=subprocess.run(["ffprobe","-v","error","-show_entries",
     "format=duration:stream=codec_type,codec_name","-of","json",str(webm)],
     capture_output=True,text=True,check=True,timeout=30)
    probe=json.loads(proc.stdout)
    types={s["codec_type"] for s in probe.get("streams",[])}
    if not {"audio","video"}.issubset(types):raise AssertionError("Missing audio or video: "+str(types))
    if float(probe["format"].get("duration",0))<1:raise AssertionError("Video truncated")
   if errors:raise AssertionError("Chromium errors: "+"; ".join(errors[:5]))
   (dest/"V37_BROWSER_QA.json").write_text(json.dumps({
    "version":37,"real_caption_canvas_verified":True,
    "srt_timestamps_verified":True,"vtt_verified":True,
    "old_story_preserved":True,"audio_video_webm_bytes":webm.stat().st_size,
    "ffprobe":probe,"errors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V37 CHROMIUM PASS: pixels, SRT/VTT, preserved canon, genuine video+audio WebM")
  finally:browser.close()
if __name__=="__main__":main()
