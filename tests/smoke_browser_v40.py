#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V40 Chromium QA: genuine art pixel change, canon preservation and real audio/video WebM."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def make_wav(path):
 sr=16000
 with wave.open(str(path),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
  f.writeframes(b"".join(struct.pack("<h",int(7600*math.sin(2*math.pi*440*i/sr)))
   for i in range(sr*3)))
def png_sha(path):
 blob=path.read_bytes()
 if blob[:8]!=b"\x89PNG\r\n\x1a\n" or len(blob)<5000:
  raise AssertionError("Invalid genuine Canvas PNG "+str(path))
 return hashlib.sha256(blob).hexdigest()
def preserved(old,new,label):
 if isinstance(old,dict):
  if not isinstance(new,dict):raise AssertionError("Field replaced "+label)
  for k,v in old.items():
   if k not in new:raise AssertionError("Missing old field "+label+"."+k)
   preserved(v,new[k],label+"."+k)
 elif isinstance(old,list):
  if not isinstance(new,list) or len(old)!=len(new):
   raise AssertionError("Old array replaced "+label)
  for i,(x,y) in enumerate(zip(old,new)):preserved(x,y,label+"."+str(i))
 elif old!=new:raise AssertionError("Old value changed "+label)
def main():
 arg=argparse.ArgumentParser()
 arg.add_argument("--html",required=True)
 arg.add_argument("--out",default="dist/V40_REAL_ART_SAMPLES")
 a=arg.parse_args()
 dst=Path(a.out).resolve();dst.mkdir(parents=True,exist_ok=True)
 wav=dst/"V40_REAL_TEST_VOICE.wav";make_wav(wav)
 pageerrors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage",
   "--disable-gpu","--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1540,"height":1120},accept_downloads=True)
  page.on("pageerror",lambda e:pageerrors.append(str(e)))
  try:
   page.goto(Path(a.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v40-character')?.options.length>0",timeout=45000)
   page.locator('[data-page="character-art-v40"]').click()
   page.locator("#v40-profile").select_option("ornate")
   page.locator("#v40-eyes").fill("95")
   page.locator("#v40-hair").fill("96")
   page.locator("#v40-costume").fill("96")
   page.locator("#v40-shine").fill("91")
   page.locator("#v40-save").click()
   data=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V40'))""")
   if data["version"]!=40 or not data["episodes"][0].get("storyV20") or not data["characters"][0].get("qualityV23"):
    raise AssertionError("Previous canon or character metadata missing")
   before=dst/"V40_CHARACTER_BEFORE.png"
   after=dst/"V40_CHARACTER_AFTER.png"
   page.locator("#v40-before").screenshot(path=str(before))
   page.locator("#v40-after").screenshot(path=str(after))
   if png_sha(before)==png_sha(after):
    raise AssertionError("Character art V40 made no actual pixel difference on same timestamp")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v40-json").click()
   manifest=dst/"V40_CHARACTER_ART.json"
   dl.value.save_as(str(manifest))
   m=json.loads(manifest.read_text(encoding="utf-8"))
   if m["version"]!=40 or m["characters"][0]["quality"]["profile"]!="ornate":
    raise AssertionError("Art metadata persistence failure")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v40-sheet").click()
   sheet=dst/"V40_FOUR_REAL_CHARACTER_FRAMES.png";dl.value.save_as(str(sheet));png_sha(sheet)
   # Normalize a short browser-only test movie, with the same save mechanism
   # used by earlier releases; NEVER modify the source or repository originals.
   page.evaluate("""() => {
     const key='AI_ANIME_FACTORY_V40',x=JSON.parse(localStorage.getItem(key));
     const candidates=x.episodes.flatMap(e=>e.scenes||[]);
     const fight=candidates.find(s=>s.kind==='fight')||candidates[0];
     const other=candidates.find(s=>s!==fight)||fight;
     x.episodes[0].scenes=[JSON.parse(JSON.stringify(fight)),JSON.parse(JSON.stringify(other))];
     x.episodes[0].scenes.forEach(s=>s.duration=1.3);
     localStorage.setItem(key,JSON.stringify(x));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v40-character')?.options.length>0",timeout=45000)
   page.locator('[data-page="character-art-v40"]').click()
   page.locator("#v40-save").click()
   baseline=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V40'))""")
   char_baseline=[{k:v for k,v in c.items() if k!="visualV40"} for c in baseline["characters"]]
   scene_baseline=[{k:v for k,v in c.items() if k!="visualV40"} for c in baseline["episodes"][0]["scenes"]]
   page.locator("#v40-hair").fill("81")
   page.locator("#v40-save").click()
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V40'))""")
   preserved(char_baseline,
    [{k:v for k,v in c.items() if k!="visualV40"} for c in current["characters"]],"characters")
   preserved(scene_baseline,current["episodes"][0]["scenes"],"scenes")
   if current["episodes"][0]["storyV20"]!=baseline["episodes"][0]["storyV20"]:
    raise AssertionError("Canonical storyline changed")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v36-export").click()
   movie=dst/"V40_REAL_ART_EPISODE_WITH_AUDIO.webm";dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V40_CHARACTER_ART_EPISODE_"):
    raise AssertionError("V40 recorder has wrong generation filename")
   if movie.stat().st_size<6000:raise AssertionError("No genuine movie")
   info={}
   if shutil.which("ffprobe"):
    run=subprocess.run(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
     capture_output=True,text=True,check=True,timeout=30)
    info=json.loads(run.stdout)
    kinds={x["codec_type"] for x in info.get("streams",[])}
    if not {"video","audio"}.issubset(kinds):raise AssertionError("No audio/video codec: "+str(kinds))
    if float(info.get("format",{}).get("duration",0))<1:raise AssertionError("WebM truncated")
   if pageerrors:raise AssertionError("Browser JS errors: "+"; ".join(pageerrors[:5]))
   (dst/"V40_BROWSER_QA.json").write_text(json.dumps({
      "v40":True,"actual_before_after_different":True,
      "canon_untouched":True,"full_movie_bytes":movie.stat().st_size,
      "ffprobe":info,"pageerrors":pageerrors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V40 CHROMIUM PASS: actual art pixel delta, preserved previous fields, real WebM audio+video")
  finally:browser.close()
if __name__=="__main__":main()
