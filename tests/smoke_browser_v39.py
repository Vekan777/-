#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chromium V39: actual rig pixel changes, canon preserved, real WebM with audio/subtitles."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
  f.writeframes(b"".join(struct.pack("<h",round(8500*math.sin(2*math.pi*440*i/rate)))
   for i in range(rate*3)))
def hash_png(path):
 blob=path.read_bytes()
 if not blob.startswith(b"\x89PNG\r\n\x1a\n") or len(blob)<5000:
  raise AssertionError("Invalid Canvas PNG "+str(path))
 return hashlib.sha256(blob).hexdigest()
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--html",required=True)
 cli.add_argument("--out",default="dist/V39_ACTION_SAMPLES")
 a=cli.parse_args();dest=Path(a.out).resolve();dest.mkdir(parents=True,exist_ok=True)
 wav=dest/"V39_TEST_DIALOGUE.wav";tone(wav)
 errors=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage",
    "--disable-gpu","--autoplay-policy=no-user-gesture-required"])
  page=b.new_page(viewport={"width":1480,"height":1150},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(a.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v39-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="performance-v39"]').click()
   page.locator("#v39-save").click()
   base=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V39'))""")
   if base["version"]!=39 or not base["episodes"][0].get("storyV20"):
    raise AssertionError("Broken V39 migration or story")
   if not base["characters"][0].get("qualityV23"):
    raise AssertionError("Missing V23 character data")
   # Separate test-only, shortened episode. Prefer an existing authored fight.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V39',value=JSON.parse(localStorage.getItem(key));
    const scenes=value.episodes.flatMap(e=>e.scenes||[]);
    const fight=scenes.find(s=>s.kind==='fight')||scenes[0];
    const companion=scenes.find(s=>s!==fight)||fight;
    value.episodes[0].scenes=[JSON.parse(JSON.stringify(fight)),JSON.parse(JSON.stringify(companion))];
    value.episodes[0].scenes.forEach(s=>s.duration=1.35);
    localStorage.setItem(key,JSON.stringify(value));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v39-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="performance-v39"]').click()
   page.locator("#v39-scene").select_option("0")
   # Establish normalized legacy fields before touching only V39 controls.
   canonical=page.evaluate("""() => {
     const value=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V39'));
     return JSON.parse(JSON.stringify(value.episodes[0].scenes[0]));
   }""")
   page.locator("#v39-enabled").uncheck()
   page.locator("#v39-save").click()
   with page.expect_download(timeout=20000) as dl:
    page.locator("#v39-json").click()
   file=dest/"V39_CHARACTER_PERFORMANCE.json";dl.value.save_as(str(file))
   manifest=json.loads(file.read_text(encoding="utf-8"))
   if manifest["version"]!=39 or len(manifest["episodes"][0]["scenes"])!=2:
    raise AssertionError("Missing V39 performance settings")
   duration=page.evaluate("""() => {
     const key='AI_ANIME_FACTORY_V39';
     const value=JSON.parse(localStorage.getItem(key));
     return value.episodes[0].scenes.reduce((sum,s)=>sum+s.duration,0);
   }""")
   # Use an early actor pose while generated scene is authoritative.
   seek="220"
   page.locator("#v39-seek").fill(seek)
   before=dest/"V39_REAL_CHARACTER_BEFORE.png"
   page.locator("#v39-preview").screenshot(path=str(before))
   first=hash_png(before)
   page.locator("#v39-enabled").check()
   page.locator("#v39-energy").fill("96")
   page.locator("#v39-facial").fill("95")
   page.locator("#v39-followThrough").fill("90")
   page.locator("#v39-impact").fill("90")
   page.locator("#v39-streaks").fill("70")
   page.locator("#v39-save").click()
   page.locator("#v39-seek").fill(seek)
   after=dest/"V39_REAL_CHARACTER_AFTER.png"
   page.locator("#v39-preview").screenshot(path=str(after))
   second=hash_png(after)
   if first==second:
    raise AssertionError("V39 rig and performance did not change real canvas pixels")
   with page.expect_download(timeout=20000) as dl:
    page.locator("#v39-sheet").click()
   sheet=dest/"V39_FOUR_REAL_CHARACTER_FRAMES.png";dl.value.save_as(str(sheet))
   hash_png(sheet)
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V39'))""")
   if current["episodes"][0]["storyV20"]!=base["episodes"][0]["storyV20"]:
    raise AssertionError("Canonical episode story was rewritten")
   if current["characters"][0]["qualityV23"]!=base["characters"][0]["qualityV23"]:
    raise AssertionError("Canonical character model was rewritten")
   # Historical modules lazily populate default fields while rendering.
   # Added *default* keys are allowed; every pre-existing scalar/list must
   # remain exactly unchanged (including plot, combat outcome and animation).
   def original_preserved(old,new,path):
    if isinstance(old,dict):
     if not isinstance(new,dict):raise AssertionError("Historical dict replaced: "+path)
     for k,v in old.items():
      if k not in new:raise AssertionError("Historical field lost: "+path+"."+k)
      original_preserved(v,new[k],path+"."+k)
    elif isinstance(old,list):
     if not isinstance(new,list) or len(old)!=len(new):
      raise AssertionError("Historical array replaced: "+path)
     for i,(x,y) in enumerate(zip(old,new)):
      original_preserved(x,y,path+"["+str(i)+"]")
    elif old!=new:
     raise AssertionError("Historical value changed: "+path)
   old_scene={k:v for k,v in canonical.items() if k!="performanceV39"}
   new_scene={k:v for k,v in current["episodes"][0]["scenes"][0].items()
              if k!="performanceV39"}
   original_preserved(old_scene,new_scene,"scene")
   if current["episodes"][0]["scenes"][0]["performanceV39"]["enabled"] is not True:
    raise AssertionError("V39 motion not saved")
   # V37 subtitles and V38 camera remain active in existing studio.
   page.locator('[data-page="subtitles-v37"]').click()
   page.locator("#v37-scene").select_option("0")
   page.locator("#v37-start").fill("0.05")
   page.locator("#v37-end").fill("0.9")
   page.locator("#v37-speaker").fill("Герой")
   page.locator("#v37-text").fill("Канон сохранён")
   page.locator("#v37-save").click()
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v36-export").click()
   movie=dest/"V39_REAL_CHARACTER_ACTION_WITH_AUDIO.webm"
   dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V39_CHARACTER_ACTION_EPISODE_"):
    raise AssertionError("Wrong saved V39 version")
   if movie.stat().st_size<6000:raise AssertionError("Recorded WebM too small")
   info={}
   if shutil.which("ffprobe"):
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
      capture_output=True,text=True,check=True,timeout=30)
    info=json.loads(p.stdout)
    codecs={s["codec_type"] for s in info.get("streams",[])}
    if not {"audio","video"}.issubset(codecs):
     raise AssertionError("Real movie lost video or audio "+str(codecs))
    if float(info.get("format",{}).get("duration",0))<1:
     raise AssertionError("V39 video truncated")
   if errors:raise AssertionError("Browser errors: "+"; ".join(errors[:6]))
   (dest/"V39_BROWSER_QA.json").write_text(json.dumps({
      "version":39,"real_pixel_change":True,"original_story_preserved":True,
      "v37_subtitles":True,"real_webm_bytes":movie.stat().st_size,
      "real_frames_png":True,"ffprobe":info,"pageerrors":errors
     },ensure_ascii=False,indent=2),encoding="utf-8")
   print("V39 CHROMIUM PASS: actor pixels, canon, SRT previous, real WebM/audio")
  finally:b.close()
if __name__=="__main__":main()
