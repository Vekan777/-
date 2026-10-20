#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V32 Chromium: actual procedural joint difference, keyframes, JSON and PNG."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png(p):
 b=Path(p).read_bytes()
 if len(b)<8000 or b[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Missing rendered PNG "+str(p))
 w,h=struct.unpack(">II",b[16:24])
 if min(w,h)<140:raise AssertionError("Tiny frame")
 return {"file":p.name,"dimensions":[w,h],"bytes":len(b),
         "sha256":hashlib.sha256(b).hexdigest()}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--html",required=True)
 ap.add_argument("--out",default="dist/V32_KEYFRAME_SAMPLES")
 cfg=ap.parse_args()
 html=Path(cfg.html).resolve()
 folder=Path(cfg.out).resolve();folder.mkdir(parents=True,exist_ok=True)
 errs=[];frames=[]
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,args=[
    "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1490,"height":1150},
    device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda x:errs.append(str(x)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v32-scene')?.options.length>0",timeout=45000)
   page.locator('[data-page="keyframe-v32"]').click()
   page.wait_for_function("() => !document.querySelector('#page-keyframe-v32').hidden")
   a=folder/"V32_V31_BASE.png";b=folder/"V32_READABLE_POSE.png"
   difference=False
   for pct in ["12","38","62","86"]:
    page.locator("#v32-position").fill(pct)
    page.locator("#v32-before").screenshot(path=str(a))
    page.locator("#v32-after").screenshot(path=str(b))
    if a.read_bytes()!=b.read_bytes():
     difference=True;break
   if not difference:
    raise AssertionError("New keyframes don't change actual rig silhouette")
   frames.extend((png(a),png(b)))
   page.locator("#v32-style").select_option("action")
   page.locator("#v32-keyframe").select_option("1")
   page.locator("#v32-key-value").fill("8")
   for k,v in (("silhouette","97"),("gesture","93"),
               ("expression","90"),("hold","88"),("anticipation","84")):
    page.locator("#v32-"+k).fill(v)
   page.locator("#v32-save").click()
   c=folder/"V32_EDITED_KEYFRAME.png"
   page.locator("#v32-after").screenshot(path=str(c))
   frames.append(png(c))
   if c.read_bytes()==b.read_bytes():
    raise AssertionError("Edited keyframe intensity did not change live frame")
   choice=page.locator("#v32-scene").input_value()
   i,j=[int(x) for x in choice.split(':')]
   before=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V32')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,
            lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before["version"]!=32 or not before["episodes"]:
    raise AssertionError("V32 version or story missing")
   scene=before["episodes"][i]["scenes"][j]
   if scene["readabilityV32"]["keyframes"][1]!=8 or scene["readabilityV32"]["silhouette"]!=97:
    raise AssertionError("Per-scene keyframe values not persisted")
   if not before["episodes"][i].get("storyV20") or not before["characters"][0].get("qualityV23"):
    raise AssertionError("V20 story or V23 character source lost")
   for key in ("visualV21","actingV22","motionV24","choreographyV25",
               "cinemaV26","worldV27","interactionV28","polishV29","finishV31"):
    if key not in scene:raise AssertionError("Lost legacy field "+key)
   # Four cue samples must stay smooth and bounded when shot time changes.
   page.locator("#v32-qa").click()
   if not page.locator("#v32-report").inner_text():
    raise AssertionError("Keyframe diagnostics did not render")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v32-plan").click()
   plan=folder/"V32_KEYFRAME_PLAN_RU.txt";dl.value.save_as(plan)
   if "ключевые кадры" not in plan.read_text(encoding="utf-8"):
    raise AssertionError("Export plan missing actual keyframes")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v32-sheet").click()
   sheet=folder/"V32_FOUR_KEY_POSES.png";dl.value.save_as(sheet)
   frames.append(png(sheet))
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v32-scene')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V32')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,
            lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before!=after:raise AssertionError("Reload modified V20–V32 story or keyframes")
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27",
               "interaction-v28","polish-v29","review-v30","visual-v31","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errs:raise AssertionError("Chromium errors: "+" | ".join(errs[:6]))
   (folder/"V32_BROWSER_QA.json").write_text(json.dumps({
     "version":32,"scene":[i,j],"frames":frames,
     "keyframes":scene["readabilityV32"]["keyframes"],
     "legacy_preserved":True,"js_errors":errs
   },indent=2,ensure_ascii=False),encoding="utf-8")
   print("V32 CHROMIUM PASS: real rig A/B, edited key poses, V20–V32 data, PNG")
  finally:browser.close()
if __name__=="__main__":main()
