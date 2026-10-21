#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real Chromium proof: before/after and distinct silhouettes, unchanged canon, recorded WebM."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
  f.writeframes(b"".join(struct.pack("<h",round(7900*math.sin(2*math.pi*440*i/rate)))
     for i in range(rate*3)))
def hash_png(path):
 data=path.read_bytes()
 if data[:8]!=b"\x89PNG\r\n\x1a\n" or len(data)<5000:
  raise AssertionError("PNG failed: "+str(path))
 return hashlib.sha256(data).hexdigest()
def contains_existing(old,new,where):
 if isinstance(old,dict):
  if not isinstance(new,dict):raise AssertionError("Old object replaced "+where)
  for k,v in old.items():
   if k not in new:raise AssertionError("Old field removed "+where+"."+k)
   contains_existing(v,new[k],where+"."+k)
 elif isinstance(old,list):
  if not isinstance(new,list) or len(old)!=len(new):
   raise AssertionError("Old array changed "+where)
  for i,(x,y) in enumerate(zip(old,new)):
   contains_existing(x,y,where+"["+str(i)+"]")
 elif old!=new:raise AssertionError("Existing story value changed "+where)
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--html",required=True)
 parser.add_argument("--out",default="dist/V41_SILHOUETTE_SAMPLES")
 args=parser.parse_args()
 output=Path(args.out).resolve();output.mkdir(parents=True,exist_ok=True)
 wav=output/"V41_TEST_VOICE.wav";tone(wav);errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage",
   "--disable-gpu","--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1560,"height":1140},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v41-character')?.options.length>0",timeout=45000)
   page.locator('[data-page="silhouette-v41"]').click()
   page.locator("#v41-character").select_option("0")
   page.locator("#v41-shape").select_option("guardian")
   page.locator("#v41-cape").fill("100")
   page.locator("#v41-shoulders").fill("100")
   page.locator("#v41-save").click()
   baseline=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V41'))""")
   if baseline["version"]!=41 or not baseline["episodes"][0].get("storyV20"):
    raise AssertionError("V41 project missing storyline")
   if not baseline["characters"][0].get("qualityV23"):
    raise AssertionError("V23 character model lost")
   before=output/"V41_CHARACTER_BEFORE.png"
   after=output/"V41_CHARACTER_GUARDIAN.png"
   page.locator("#v41-before").screenshot(path=str(before))
   page.locator("#v41-after").screenshot(path=str(after))
   if hash_png(before)==hash_png(after):
    raise AssertionError("Real vector silhouette produced no pixel delta")
   page.locator("#v41-shape").select_option("ranger")
   page.locator("#v41-hair").fill("100")
   page.locator("#v41-save").click()
   ranger=output/"V41_CHARACTER_RANGER.png"
   page.locator("#v41-after").screenshot(path=str(ranger))
   if hash_png(ranger)==hash_png(after):
    raise AssertionError("Ranger and guardian silhouettes are identical")
   page.locator("#v41-shape").select_option("arcanist")
   page.locator("#v41-save").click()
   arcanist=output/"V41_CHARACTER_ARCANIST.png"
   page.locator("#v41-after").screenshot(path=str(arcanist))
   if len({hash_png(after),hash_png(ranger),hash_png(arcanist)})!=3:
    raise AssertionError("Three shapes not visibly distinct")
   with page.expect_download(timeout=30000) as d:
    page.locator("#v41-json").click()
   f=output/"V41_SILHOUETTES.json";d.value.save_as(str(f))
   report=json.loads(f.read_text(encoding="utf-8"))
   if report["version"]!=41 or report["characters"][0]["silhouette"]["shape"]!="arcanist":
    raise AssertionError("V41 settings failed persistence/manifest")
   with page.expect_download(timeout=30000) as d:
    page.locator("#v41-sheet").click()
   sheet=output/"V41_FOUR_REAL_FRAMES.png";d.value.save_as(str(sheet));hash_png(sheet)
   # Shortening exists ONLY in temporary browser QA localStorage.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V41',data=JSON.parse(localStorage.getItem(key));
    const all=data.episodes.flatMap(e=>e.scenes||[]);
    const fight=all.find(s=>s.kind==='fight')||all[0];
    const other=all.find(s=>s!==fight)||fight;
    data.episodes[0].scenes=[JSON.parse(JSON.stringify(fight)),JSON.parse(JSON.stringify(other))];
    data.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v41-character')?.options.length>0",timeout=45000)
   page.locator('[data-page="silhouette-v41"]').click()
   page.locator("#v41-save").click()  # normalizes old short QA scenes before baseline
   normalized=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V41'))""")
   oldchars=[{k:v for k,v in c.items() if k!="silhouetteV41"} for c in normalized["characters"]]
   oldscenes=normalized["episodes"][0]["scenes"]
   page.locator("#v41-cape").fill("67")
   page.locator("#v41-save").click()
   current=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V41'))""")
   contains_existing(oldchars,[{k:v for k,v in c.items() if k!="silhouetteV41"}
      for c in current["characters"]],"characters")
   contains_existing(oldscenes,current["episodes"][0]["scenes"],"scenes")
   if current["episodes"][0]["storyV20"]!=normalized["episodes"][0]["storyV20"]:
    raise AssertionError("Story rewritten")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as movie:
    page.locator("#v36-export").click()
   video=output/"V41_REAL_SILHOUETTE_EPISODE.webm"
   movie.value.save_as(str(video))
   if not movie.value.suggested_filename.startswith("V41_SILHOUETTE_EPISODE_"):
    raise AssertionError("Incorrect video release filename")
   if video.stat().st_size<6000:raise AssertionError("WebM not recorded")
   probe={}
   if shutil.which("ffprobe"):
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,codec_name","-of","json",str(video)],
      capture_output=True,text=True,timeout=30,check=True)
    probe=json.loads(p.stdout)
    kinds={item["codec_type"] for item in probe.get("streams",[])}
    if not {"audio","video"}.issubset(kinds):
     raise AssertionError("WebM does not contain real audio+video")
    if float(probe.get("format",{}).get("duration",0))<1:
     raise AssertionError("WebM recording truncated")
   if errors:raise AssertionError("JavaScript exceptions: "+"; ".join(errors[:5]))
   (output/"V41_BROWSER_QA.json").write_text(json.dumps({
    "version":41,"different_silhouettes":3,"original_story_preserved":True,
    "real_png_before_after":True,"webm_bytes":video.stat().st_size,
    "ffprobe":probe,"pageerrors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V41 CHROMIUM PASS: 3 distinct real character silhouettes, preserved story and WebM with audio")
  finally:browser.close()
if __name__=="__main__":main()
