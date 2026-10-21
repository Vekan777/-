#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actual Chromium V42: same timestamp lighting pixel proof, V41 retention, audio+video WebM."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as sound:
  sound.setnchannels(1);sound.setsampwidth(2);sound.setframerate(rate)
  sound.writeframes(b"".join(struct.pack("<h",round(8800*math.sin(2*math.pi*440*i/rate)))
    for i in range(rate*3)))
def png(path):
 raw=path.read_bytes()
 if raw[:8]!=b"\x89PNG\r\n\x1a\n" or len(raw)<5000:
  raise AssertionError("Not genuine Canvas PNG: "+str(path))
 return hashlib.sha256(raw).hexdigest()
def retained(old,new,where):
 if isinstance(old,dict):
  if not isinstance(new,dict):raise AssertionError("Previous object overwritten "+where)
  for key,value in old.items():
   if key not in new:raise AssertionError("Old field lost "+where+"."+key)
   retained(value,new[key],where+"."+key)
 elif isinstance(old,list):
  if not isinstance(new,list) or len(old)!=len(new):
   raise AssertionError("Previous list changed "+where)
  for i,(a,b) in enumerate(zip(old,new)):retained(a,b,where+"["+str(i)+"]")
 elif old!=new:
  raise AssertionError("Previous value changed "+where)
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--html",required=True)
 cli.add_argument("--out",default="dist/V42_STAGE_SAMPLES")
 args=cli.parse_args();output=Path(args.out).resolve()
 output.mkdir(parents=True,exist_ok=True)
 wav=output/"V42_TEST_VOICE.wav";tone(wav)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1480,"height":1120},accept_downloads=True)
  page.on("pageerror",lambda err:errors.append(str(err)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v42-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="stage-v42"]').click()
   page.locator("#v42-scene").select_option("0")
   page.locator("#v42-enabled").uncheck()  # onChange saves the disabled stage
   page.locator("#v42-seek").fill("200")
   before=output/"V42_SAME_TIME_LEGACY.png"
   page.locator("#v42-preview").screenshot(path=str(before))
   baseline=png(before)
   page.locator("#v42-preset").select_option("storm")
   page.locator("#v42-light").fill("95")
   page.locator("#v42-particles").fill("95")
   page.locator("#v42-depth").fill("95")
   page.locator("#v42-save").click()
   page.locator("#v42-seek").fill("200")
   storm=output/"V42_SAME_TIME_STORM.png"
   page.locator("#v42-preview").screenshot(path=str(storm))
   if png(storm)==baseline:
    raise AssertionError("V42 atmosphere did not change real pixels")
   page.locator("#v42-preset").select_option("ember")
   page.locator("#v42-light").fill("92")
   page.locator("#v42-save").click()
   page.locator("#v42-seek").fill("200")
   ember=output/"V42_SAME_TIME_EMBERS.png"
   page.locator("#v42-preview").screenshot(path=str(ember))
   if len({baseline,png(storm),png(ember)})!=3:
    raise AssertionError("Storm and ember styles did not produce distinct images")
   page.locator("#v42-audit").click()
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v42-json").click()
   manifest=output/"V42_STAGE_DEPTH.json";dl.value.save_as(str(manifest))
   settings=json.loads(manifest.read_text(encoding="utf-8"))
   if settings["version"]!=42 or settings["episodes"][0]["scenes"][0]["stage"]["preset"]!="ember":
    raise AssertionError("Stage timeline JSON did not save correct scene")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v42-sheet").click()
   sheet=output/"V42_FOUR_REAL_EPISODE_FRAMES.png"
   dl.value.save_as(str(sheet));png(sheet)
   fresh=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V42'))""")
   if fresh["version"]!=42 or not fresh["episodes"][0].get("storyV20"):
    raise AssertionError("Story or new version lost")
   if not fresh["characters"][0].get("silhouetteV41"):
    raise AssertionError("Character silhouettes V41 lost")
   # Browser-only two-scene sample shortens recording, never repository sources.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V42',data=JSON.parse(localStorage.getItem(key));
    const scenes=data.episodes[0].scenes;
    const next=scenes.length>1?scenes[1]:scenes[0];
    data.episodes[0].scenes=[JSON.parse(JSON.stringify(scenes[0])),
      JSON.parse(JSON.stringify(next))];
    data.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v42-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="stage-v42"]').click()
   page.locator("#v42-save").click()  # normalize old scene durations before baseline
   old=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V42'))""")
   old_scenes=old["episodes"][0]["scenes"]
   old_characters=old["characters"]
   page.locator("#v42-light").fill("61")
   page.locator("#v42-save").click()
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V42'))""")
   previous=[{k:v for k,v in c.items() if k!="stageV42"} for c in old_scenes]
   latest=[{k:v for k,v in c.items() if k!="stageV42"} for c in current["episodes"][0]["scenes"]]
   retained(previous,latest,"scenes")
   retained(old_characters,current["characters"],"characters")
   if old["episodes"][0]["storyV20"]!=current["episodes"][0]["storyV20"]:
    raise AssertionError("V42 changed storyline")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v36-export").click()
   movie=output/"V42_REAL_SCENE_WITH_AUDIO.webm";dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V42_STAGE_DEPTH_EPISODE_"):
    raise AssertionError("Wrong WebM version")
   if movie.stat().st_size<6000:raise AssertionError("No genuine WebM")
   probe={}
   if shutil.which("ffprobe"):
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
       "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
       check=True,capture_output=True,text=True,timeout=30)
    probe=json.loads(p.stdout)
    kinds={x["codec_type"] for x in probe.get("streams",[])}
    if not {"audio","video"}.issubset(kinds):
     raise AssertionError("WebM missing real audio or video: "+str(kinds))
    if float(probe.get("format",{}).get("duration",0))<1:
     raise AssertionError("WebM too short")
   if errors:raise AssertionError("Chromium exception: "+"; ".join(errors[:5]))
   (output/"V42_BROWSER_QA.json").write_text(json.dumps({
    "version":42,"real_same_timestamp_pixel_differential":True,
    "storm_and_ember_distinct":True,"old_characters_preserved":True,
    "old_scenes_preserved":True,"webm_bytes":movie.stat().st_size,
    "ffprobe":probe,"page_errors":errors
   },ensure_ascii=False,indent=2),encoding="utf-8")
   print("V42 CHROMIUM PASS: three authentic stage images, canon, audio and video")
  finally:browser.close()
if __name__=="__main__":main()
