#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V33 authentic Chromium A/B face and gesture frames, edits, save, export."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright
def png(p):
 b=Path(p).read_bytes()
 if len(b)<8000 or b[:8]!=b"\x89PNG\r\n\x1a\n":raise AssertionError("Invalid PNG "+str(p))
 w,h=struct.unpack(">II",b[16:24])
 if w<250 or h<140:raise AssertionError("Bad PNG dimensions")
 return {"file":p.name,"size":[w,h],"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--html",required=True)
 a.add_argument("--out",default="dist/V33_ACTING_SAMPLES")
 cfg=a.parse_args()
 folder=Path(cfg.out).resolve();folder.mkdir(parents=True,exist_ok=True)
 errs=[];frames=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,
   args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1470,"height":1090},accept_downloads=True,device_scale_factor=1)
  page.on("pageerror",lambda e:errs.append(str(e)))
  try:
   page.goto(Path(cfg.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v33-scene')?.options.length>0",timeout=45000)
   page.locator('[data-page="acting-v33"]').click()
   page.wait_for_function("() => !document.querySelector('#page-acting-v33').hidden")
   old=folder/"V33_V32_BASE.png";new=folder/"V33_ACTING_FACE.png"
   changed=False
   for pct in ("12","38","62","86"):
    page.locator("#v33-position").fill(pct)
    page.locator("#v33-before").screenshot(path=str(old))
    page.locator("#v33-after").screenshot(path=str(new))
    if old.read_bytes()!=new.read_bytes():
     changed=True;break
   if not changed:raise AssertionError("V33 acting does not change actual procedurally rendered frames")
   frames.extend((png(old),png(new)))
   page.locator("#v33-enabled").check()
   page.locator("#v33-style").select_option("expressive")
   for key,value in (("gaze","99"),("emotion","95"),
                     ("gesture","96"),("breathing","89"),("transitions","97")):
    page.locator("#v33-"+key).fill(value)
   page.locator("#v33-save").click()
   strong=folder/"V33_EXPRESSIVE_ACTING.png"
   page.locator("#v33-after").screenshot(path=str(strong))
   frames.append(png(strong))
   if new.read_bytes()==strong.read_bytes():raise AssertionError("V33 sliders have no effect on actual frame")
   choice=page.locator("#v33-scene").input_value()
   i,j=(int(v) for v in choice.split(":"))
   before=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V33')||'null');
    return {version:p?.version,characters:p?.characters,episodes:p?.episodes,
      lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before["version"]!=33 or not before["episodes"] or not before["characters"]:
    raise AssertionError("V33 project not saved")
   s=before["episodes"][i]["scenes"][j]
   o=s.get("actingV33",{})
   if o.get("gaze")!=99 or o.get("emotion")!=95 or o.get("gesture")!=96:
    raise AssertionError("Scene-specific V33 settings missing")
   if not before["episodes"][i].get("storyV20") or not before["characters"][0].get("qualityV23"):
    raise AssertionError("Old story or character bible missing")
   for key in ("visualV21","actingV22","motionV24","choreographyV25",
               "cinemaV26","worldV27","interactionV28","polishV29",
               "finishV31","readabilityV32"):
    if key not in s:raise AssertionError("Missing historical field "+key)
   page.locator("#v33-qa").click()
   if not page.locator("#v33-report").inner_text():
    raise AssertionError("Acting diagnostics did not display")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v33-plan").click()
   plan=folder/"V33_ACTING_PLAN_RU.txt";dl.value.save_as(plan)
   if "Ключ" not in plan.read_text(encoding="utf-8"):raise AssertionError("No acting timeline in report")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v33-sheet").click()
   sheet=folder/"V33_FOUR_ACTING_FRAMES.png";dl.value.save_as(sheet)
   frames.append(png(sheet))
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v33-scene')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V33')||'null');
    return {version:p?.version,characters:p?.characters,episodes:p?.episodes,
      lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before!=after:raise AssertionError("V20–V33 JSON mutated on reload")
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26",
               "world-v27","interaction-v28","polish-v29",
               "review-v30","visual-v31","keyframe-v32","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errs:raise AssertionError("Chromium JS errors: "+" | ".join(errs[:8]))
   (folder/"V33_BROWSER_QA.json").write_text(json.dumps({
    "version":33,"scene":[i,j],"frames":frames,"settings":o,
    "original_plot_preserved":True,"errors":errs
   },ensure_ascii=False,indent=2),encoding="utf-8")
   print("V33 CHROMIUM PASS: genuine A/B facial gestures, saved sliders, V20–V33 JSON, PNG")
  finally:browser.close()
if __name__=="__main__":main()
