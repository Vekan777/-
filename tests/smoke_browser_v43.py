#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V43 headless Chromium: authentic action camera, canon invariants, WebM with audio."""
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
 cli.add_argument("--out",default="dist/V43_DIRECTOR_SAMPLES")
 args=cli.parse_args()
 dst=Path(args.out).resolve();dst.mkdir(parents=True,exist_ok=True)
 wav=dst/"V43_TEST_VOICE.wav";tone(wav)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1480,"height":1130},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v43-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="action-v43"]').click()
   scene=page.evaluate("""() => {
    for(let i=0;i<P.episodes.length;i++)
     for(let j=0;j<P.episodes[i].scenes.length;j++)
      if(P.episodes[i].scenes[j].kind==='fight')return {episode:i,scene:j};
    return null;
   }""")
   if not scene:raise AssertionError("No real authored fight scene found")
   page.locator("#v43-episode").select_option(str(scene["episode"]))
   page.locator("#v43-scene").select_option(str(scene["scene"]))
   page.locator("#v43-enabled").uncheck()
   page.locator("#v43-save").click()
   # Both screenshots use the same V35 timeline camera position, untouched by settings.
   before=dst/"V43_ACTION_CAMERA_OFF.png"
   page.locator("#v43-preview").screenshot(path=str(before))
   old_pixels=png_digest(before)
   page.locator("#v43-enabled").check()
   page.locator("#v43-profile").select_option("heroic")
   page.locator("#v43-shot").select_option("close")
   page.locator("#v43-zoom").fill("98")
   page.locator("#v43-focus").fill("89")
   page.locator("#v43-save").click()
   after=dst/"V43_ACTION_CAMERA_ON.png"
   page.locator("#v43-preview").screenshot(path=str(after))
   if png_digest(after)==old_pixels:
    raise AssertionError("V43 rendered the same Canvas pixels when enabled")
   result=page.evaluate("""() => {
    const s=v43Scene(),d=v43DirectorState(s,s.duration*.36);
    return {enabled:d.enabled,zoom:d.zoom,reducedMotion:v43Of(s).reducedMotion,
      kind:s.kind,event:d.event};
   }""")
   if result["kind"]!="fight" or result["zoom"]<=1 or not result["enabled"]:
    raise AssertionError("V43 genuine fight camera transform absent")
   page.locator("#v43-reduced").check()
   page.locator("#v43-save").click()
   reduced=page.evaluate("""() => {
    const s=v43Scene(),o=v43DirectorState(s,s.duration*.36);
    return {angle:o.angle,shiftY:o.shiftY,reducedMotion:v43Of(s).reducedMotion};
   }""")
   if reduced["angle"]!=0 or reduced["shiftY"]!=0 or not reduced["reducedMotion"]:
    raise AssertionError("Reduced-motion accessibility mode not functional")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v43-json").click()
   manifest=dst/"V43_ACTION_CAMERA.json";dl.value.save_as(str(manifest))
   report=json.loads(manifest.read_text(encoding="utf-8"))
   if report["version"]!=43 or report["episodes"][scene["episode"]]["scenes"][scene["scene"]]["direction"]["enabled"] is not True:
    raise AssertionError("V43 director JSON not persisted")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v43-sheet").click()
   sheet=dst/"V43_FOUR_REAL_ACTION_FRAMES.png";dl.value.save_as(str(sheet))
   png_digest(sheet)
   original=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V43'))""")
   if original["version"]!=43 or not original["characters"][0].get("silhouetteV41"):
    raise AssertionError("V41 actors lost")
   if not original["episodes"][0].get("storyV20"):
    raise AssertionError("Original storyline lost")
   # Browser-only short sample; repo scenes are NEVER changed.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V43',data=JSON.parse(localStorage.getItem(key));
    const target=data.episodes.flatMap(ep=>ep.scenes).find(s=>s.kind==='fight');
    const rest=data.episodes.flatMap(ep=>ep.scenes).find(s=>s!==target)||target;
    data.episodes[0].scenes=[
      JSON.parse(JSON.stringify(target)),JSON.parse(JSON.stringify(rest))
    ];
    data.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(key,JSON.stringify(data));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v43-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="action-v43"]').click()
   page.locator("#v43-save").click() # normalize synthetic duration before old baseline
   old=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V43'))""")
   page.locator("#v43-zoom").fill("72")
   page.locator("#v43-save").click()
   fresh=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V43'))""")
   prior=[{k:v for k,v in s.items() if k!="directorV43"} for s in old["episodes"][0]["scenes"]]
   latest=[{k:v for k,v in s.items() if k!="directorV43"} for s in fresh["episodes"][0]["scenes"]]
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
   movie=dst/"V43_REAL_DIRECTED_ACTION_WITH_AUDIO.webm"
   dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V43_ACTION_DIRECTOR_EPISODE_"):
    raise AssertionError("Wrong V43 recording filename")
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
   (dst/"V43_BROWSER_QA.json").write_text(json.dumps({
    "version":43,"real_pixel_camera_change":True,
    "reduced_motion_checked":True,"story_characters_preserved":True,
    "webm_bytes":movie.stat().st_size,"ffprobe":probe,
    "pageerrors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V43 CHROMIUM PASS: real camera crop, reduced motion, preserved canon, audio WebM")
  finally:browser.close()
if __name__=="__main__":main()
