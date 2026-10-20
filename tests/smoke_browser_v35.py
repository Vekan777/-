#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V35 actual browser verifies adjacent scene compositing and timing."""
from __future__ import annotations
import argparse,hashlib,json,struct,time
from pathlib import Path
from playwright.sync_api import sync_playwright
def image_info(p):
 d=Path(p).read_bytes()
 if len(d)<8000 or d[:8]!=b"\x89PNG\r\n\x1a\n":raise AssertionError("Bad PNG "+str(p))
 w,h=struct.unpack(">II",d[16:24])
 if w<320 or h<180:raise AssertionError("Tiny frame")
 return {"name":p.name,"width":w,"height":h,"bytes":len(d),
   "sha256":hashlib.sha256(d).hexdigest()}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--html",required=True)
 parser.add_argument("--out",default="dist/V35_EPISODE_SAMPLES")
 c=parser.parse_args()
 out=Path(c.out).resolve();out.mkdir(parents=True,exist_ok=True)
 errs=[];frames=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1500,"height":1170},
   device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda err:errs.append(str(err)))
  try:
   page.goto(Path(c.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v35-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="assembly-v35"]').click()
   page.wait_for_function("() => !document.querySelector('#page-assembly-v35').hidden")
   if page.locator("#v35-sequence").inner_text().count(" · ")<3:
    raise AssertionError("Missing cumulative episode timeline")
   # Export real manifest and verify overlap math from saved project.
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v35-json").click()
   manifest=out/"V35_EPISODE_ASSEMBLY.json";dl.value.save_as(manifest)
   obj=json.loads(manifest.read_text(encoding="utf-8"))
   episode=obj["episodes"][0];shots=episode["scenes"]
   if len(shots)<2:raise AssertionError("Expected first episode to contain 2 scenes")
   for idx,s in enumerate(shots[:-1]):
    nxt=shots[idx+1]
    expected=s["startSeconds"]+s["durationSeconds"]-s["overlapSeconds"]
    if abs(expected-nxt["startSeconds"])>.00001:
     raise AssertionError("Broken cumulative timeline / overlap")
   if abs(episode["totalSeconds"]-shots[-1]["endSeconds"])>.00001:
    raise AssertionError("Wrong total episode runtime")
   total=episode["totalSeconds"]
   first=shots[0];second=shots[1]
   if first["overlapSeconds"]<=0:
    raise AssertionError("Default overlap unexpectedly disabled")
   cut=second["startSeconds"]
   # A/B actual frame screenshots at the different phases of a real dissolve.
   positions=[max(0,cut-.035),cut+first["overlapSeconds"]*.45,
              cut+first["overlapSeconds"]*.92]
   for i,t in enumerate(positions):
    pct=round(t/total*1000)
    page.locator("#v35-progress").fill(str(pct))
    p=out/("V35_REAL_COMPOSITE_"+str(i+1)+".png")
    page.locator("#v35-preview").screenshot(path=str(p))
    frames.append(image_info(p))
   if len({f["sha256"] for f in frames})!=3:
    raise AssertionError("Cumulative timeline composite did not change over dissolve")
   # Edit transition, verify saved scene durations and story data unchanged.
   page.locator("#v35-scene").select_option("0")
   page.locator("#v35-transition").fill("80")
   page.locator("#v35-save").click()
   saved=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V35')||'null');
    return {version:p?.version,characters:p?.characters,episodes:p?.episodes,
      lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if saved["version"]!=35 or not saved["episodes"]:
    raise AssertionError("Project not saved as V35")
   episode_data=saved["episodes"][0]
   if episode_data["scenes"][0]["assemblyV35"]["transition"]!=.8:
    raise AssertionError("Per scene crossfade not persisted")
   for i,s in enumerate(shots):
    if episode_data["scenes"][i]["duration"]!=s["durationSeconds"]:
     raise AssertionError("Original scene duration changed")
   if not episode_data.get("storyV20") or not saved["characters"][0].get("qualityV23"):
    raise AssertionError("Older plot or character model missing")
   for k in ("visualV21","actingV22","motionV24","choreographyV25",
             "cinemaV26","worldV27","interactionV28","polishV29",
             "finishV31","readabilityV32","actingV33","storyboardV34"):
    if k not in episode_data["scenes"][0]:
     raise AssertionError("Older scene setting missing "+k)
   # Verify actual continuous play advances and pause freezes time.
   page.locator("#v35-start").click()
   page.locator("#v35-play").click()
   page.wait_for_timeout(450)
   advancing=page.locator("#v35-progress").input_value()
   if int(advancing)<1:raise AssertionError("Playback timeline did not advance")
   page.locator("#v35-play").click()
   stopped=page.locator("#v35-progress").input_value()
   page.wait_for_timeout(140)
   if page.locator("#v35-progress").input_value()!=stopped:
    raise AssertionError("Episode play did not pause")
   page.locator("#v35-audit").click()
   if not page.locator("#v35-audit-result").inner_text():
    raise AssertionError("Empty production audit UI")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v35-report").click()
   report=out/"V35_EPISODE_ASSEMBLY_RU.txt";dl.value.save_as(report)
   if "Сборка" not in report.read_text(encoding="utf-8") and "СБОРКА" not in report.read_text(encoding="utf-8"):
    raise AssertionError("No production report")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v35-sheet").click()
   board=out/"V35_SIX_REAL_SCENE_FRAMES.png";dl.value.save_as(board)
   dims=image_info(board);frames.append(dims)
   if (dims["width"],dims["height"])!=(1920,720):
    raise AssertionError("Wrong 6-frame contact sheet layout")
   # Real project reload, historical tab navigation and full story equality.
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v35-episode')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V35')||'null');
    return {version:p?.version,characters:p?.characters,episodes:p?.episodes,
      lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if after!=saved:raise AssertionError("V19–V35 data lost on reload")
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
      "animation-v24","combat-v25","cinematic-v26","world-v27",
      "interaction-v28","polish-v29","review-v30","visual-v31",
      "keyframe-v32","acting-v33","storyboard-v34","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errs:raise AssertionError("Chromium JS errors: "+"; ".join(errs[:5]))
   (out/"V35_BROWSER_QA.json").write_text(json.dumps({
    "version":35,"frames":frames,"composite_verified":True,
    "scene_durations_preserved":True,"continuous_play_checked":True,
    "legacy_story_preserved":True,"errors":errs},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V35 CHROMIUM PASS: true episodes, dissolve, playback, 6 PNGs, preserved old story")
  finally:browser.close()
if __name__=="__main__":main()
