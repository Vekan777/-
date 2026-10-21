#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V44 headless Chromium: authentic action camera, canon invariants, WebM with audio."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as sound:
  sound.setnchannels(1);sound.setsampwidth(2);sound.setframerate(rate)
  sound.writeframes(b"".join(struct.pack("<h",round(8600*math.sin(2*math.pi*440*i/rate)))
    for i in range(rate*3)))
def png_digest(file):
 raw=file.read_bytes()
 if raw[:8]!=b"\x89PNG\r\n\x1a\n" or len(raw)<5000:
  raise AssertionError("Not real image: "+str(file))
 return hashlib.sha256(raw).hexdigest()
def preserved(old,new,path):
 if isinstance(old,dict):
  if not isinstance(new,dict):raise AssertionError("Previous dict overwritten "+path)
  for k,v in old.items():
   if k not in new:raise AssertionError("Old field missing "+path+"."+k)
   preserved(v,new[k],path+"."+k)
 elif isinstance(old,list):
  if not isinstance(new,list) or len(old)!=len(new):
   raise AssertionError("Previous list altered "+path)
  for i,(a,b) in enumerate(zip(old,new)):
   preserved(a,b,path+"["+str(i)+"]")
 elif old!=new:raise AssertionError("Previous value altered "+path)
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--html",required=True)
 cli.add_argument("--out",default="dist/V44_TRUE_RIG_SAMPLES")
 args=cli.parse_args()
 dst=Path(args.out).resolve();dst.mkdir(parents=True,exist_ok=True)
 wav=dst/"V44_TEST_VOICE.wav";tone(wav)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1480,"height":1130},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v44-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="action-v44"]').click()
   # Legacy editor keeps P private in an IIFE: rely on public saved JSON,
   # never attempt to access a private JavaScript symbol from page.evaluate.
   page.locator("#v44-save").click()
   scene=page.evaluate("""() => {
    const stored=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V44'));
    for(let i=0;i<stored.episodes.length;i++)
     for(let j=0;j<stored.episodes[i].scenes.length;j++)
      if(stored.episodes[i].scenes[j].kind==='fight')return {episode:i,scene:j};
    return null;
   }""")
   if not scene:raise AssertionError("No real authored fight scene found")
   page.locator("#v44-episode").select_option(str(scene["episode"]))
   page.locator("#v44-scene").select_option(str(scene["scene"]))
   page.locator("#v44-enabled").uncheck()
   page.locator("#v44-save").click()
   # Both screenshots use the same V35 timeline camera position, untouched by settings.
   before=dst/"V44_ACTOR_KEYPOSES_OFF.png"
   page.locator("#v44-preview").screenshot(path=str(before))
   old_pixels=png_digest(before)
   page.locator("#v44-enabled").check()
   page.locator("#v44-profile").select_option("powerful")
   page.locator("#v44-reach").fill("98")
   page.locator("#v44-stance").fill("95")
   page.locator("#v44-steps").fill("95")
   page.locator("#v44-save").click()
   after=dst/"V44_ACTOR_KEYPOSES_ON.png"
   page.locator("#v44-preview").screenshot(path=str(after))
   if png_digest(after)==old_pixels:
    raise AssertionError("V44 rig produced unchanged pixels with V44 on")
   result=page.evaluate("""({episode,scene}) => {
    const data=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V44'));
    const s=data.episodes[episode].scenes[scene];
    return {kind:s.kind,enabled:s.keyposesV44?.enabled,
      reach:s.keyposesV44?.reach,stance:s.keyposesV44?.stance,
      steps:s.keyposesV44?.steps,profile:s.keyposesV44?.profile};
   }""",scene)
   if result["kind"]!="fight" or not result["enabled"] or result["reach"]<95 or result["profile"]!="powerful":
    raise AssertionError("V44 true rig pose controls did not persist")
   # Distinct pose time, same actor and scene, genuine 2D rendered pixels.
   page.locator("#v44-seek").fill("450")
   moved=dst/"V44_TRUE_RIG_LATER_FRAME.png"
   page.locator("#v44-preview").screenshot(path=str(moved))
   if png_digest(moved)==png_digest(after):
    raise AssertionError("V44 rig produced static actor frames at distinct times")
   page.locator("#v44-seek").fill("320")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v44-json").click()
   manifest=dst/"V44_ACTOR_KEYPOSES.json";dl.value.save_as(str(manifest))
   report=json.loads(manifest.read_text(encoding="utf-8"))
   if report["version"]!=43 or report["episodes"][scene["episode"]]["scenes"][scene["scene"]]["keyposes"]["enabled"] is not True:
    raise AssertionError("V44 true rig pose JSON not persisted")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v44-sheet").click()
   sheet=dst/"V44_FOUR_REAL_KEYPOSES.png";dl.value.save_as(str(sheet))
   png_digest(sheet)
   original=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V44'))""")
   if original["version"]!=43 or not original["characters"][0].get("silhouetteV41"):
    raise AssertionError("V41 actors lost")
   if not original["episodes"][0].get("storyV20"):
    raise AssertionError("Original storyline lost")
   # Browser-only short sample; repo scenes are NEVER changed.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V44',data=JSON.parse(localStorage.getItem(key));
    const target=data.episodes.flatMap(ep=>ep.scenes).find(s=>s.kind==='fight');
    const rest=data.episodes.flatMap(ep=>ep.scenes).find(s=>s!==target)||target;
    data.episodes[0].scenes=[
      JSON.parse(JSON.stringify(target)),JSON.parse(JSON.stringify(rest))
    ];
    data.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v44-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="action-v44"]').click()
   page.locator("#v44-save").click() # normalize synthetic duration before old baseline
   old=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V44'))""")
   page.locator("#v44-reach").fill("72")
   page.locator("#v44-save").click()
   fresh=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V44'))""")
   prior=[{k:v for k,v in s.items() if k!="keyposesV44"} for s in old["episodes"][0]["scenes"]]
   latest=[{k:v for k,v in s.items() if k!="keyposesV44"} for s in fresh["episodes"][0]["scenes"]]
   preserved(prior,latest,"original-scene-fields")
   preserved(old["characters"],fresh["characters"],"original-character-fields")
   if old["episodes"][0]["storyV20"]!=fresh["episodes"][0]["storyV20"]:
    raise AssertionError("Story was rewritten by camera")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v36-export").click()
   movie=dst/"V44_REAL_DIRECTED_ACTION_WITH_AUDIO.webm"
   dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V44_TRUE_KEYPOSES_EPISODE_"):
    raise AssertionError("Wrong V44 recording filename")
   if movie.stat().st_size<6500:raise AssertionError("No real movie")
   probe={}
   if shutil.which("ffprobe"):
    process=subprocess.run(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
      text=True,capture_output=True,timeout=30,check=True)
    probe=json.loads(process.stdout)
    tracks={s["codec_type"] for s in probe.get("streams",[])}
    if not {"audio","video"}.issubset(tracks):
     raise AssertionError("Real WebM lost audio/video: "+str(tracks))
    if float(probe.get("format",{}).get("duration",0))<1:
     raise AssertionError("Real WebM truncated")
   if errors:raise AssertionError("JavaScript errors: "+"; ".join(errors[:5]))
   (dst/"V44_BROWSER_QA.json").write_text(json.dumps({
    "version":43,"true_rig_pixel_change":True,
    "two_pose_timestamps_checked":True,"story_characters_preserved":True,
    "webm_bytes":movie.stat().st_size,"ffprobe":probe,
    "pageerrors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V44 CHROMIUM PASS: true procedural rig posing, two timestamps, preserved canon, audio WebM")
  finally:browser.close()
if __name__=="__main__":main()
