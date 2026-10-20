#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chromium V34: real camera frames, next-shot continuity audit, PNG and JSON."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png(p):
 data=Path(p).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("No real PNG "+str(p))
 w,h=struct.unpack(">II",data[16:24])
 if w<300 or h<180:raise AssertionError("Bad output dimensions")
 return {"name":p.name,"width":w,"height":h,"bytes":len(data),
         "sha256":hashlib.sha256(data).hexdigest()}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--html",required=True)
 parser.add_argument("--out",default="dist/V34_STORYBOARD_SAMPLES")
 opts=parser.parse_args()
 out=Path(opts.out).resolve();out.mkdir(parents=True,exist_ok=True)
 errors=[];frames=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1460,"height":1080},
   device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(opts.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v34-scene')?.options.length>0",timeout=45000)
   page.locator('[data-page="storyboard-v34"]').click()
   page.wait_for_function("() => !document.querySelector('#page-storyboard-v34').hidden")
   before=out/"V34_V33_CAMERA_BASE.png";after=out/"V34_SHOT_CAMERA.png"
   changed=False
   for pos in ("12","50","88"):
    page.locator("#v34-position").fill(pos)
    page.locator("#v34-before").screenshot(path=str(before))
    page.locator("#v34-after").screenshot(path=str(after))
    if before.read_bytes()!=after.read_bytes():changed=True;break
   if not changed:raise AssertionError("Storyboard camera does not alter real scene frames")
   frames.extend((png(before),png(after)))
   page.locator("#v34-enabled").check()
   page.locator("#v34-focus").select_option("hero")
   page.locator("#v34-axis").select_option("left")
   page.locator("#v34-beat").select_option("1")
   page.locator("#v34-shot").select_option("close")
   for k,v in (("strength","99"),("tracking","88"),("smoothness","95")):
    page.locator("#v34-"+k).fill(v)
   page.locator("#v34-save").click()
   refined=out/"V34_EDITED_SHOT.png"
   page.locator("#v34-after").screenshot(path=str(refined));frames.append(png(refined))
   if refined.read_bytes()==after.read_bytes():
    raise AssertionError("New camera plan or sliders do not affect actual frame")
   svalue=page.locator("#v34-scene").input_value()
   i,j=[int(v) for v in svalue.split(":")]
   saved=page.evaluate("""() => {
     const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V34')||'null');
     return {version:p?.version,episodes:p?.episodes,characters:p?.characters,
             lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if saved["version"]!=34 or not saved["episodes"]:
    raise AssertionError("V34 project not saved")
   record=saved["episodes"][i]["scenes"][j].get("storyboardV34",{})
   if record.get("shots",[None]*3)[1]!="close" or record.get("axis")!="left" or record.get("strength")!=99:
    raise AssertionError("V34 per-scene shot settings lost")
   if not saved["episodes"][i].get("storyV20") or not saved["characters"][0].get("qualityV23"):
    raise AssertionError("Historic plot or hero data lost")
   for key in ("visualV21","actingV22","motionV24","choreographyV25",
     "cinemaV26","worldV27","interactionV28","polishV29",
     "finishV31","readabilityV32","actingV33"):
    if key not in saved["episodes"][i]["scenes"][j]:
     raise AssertionError("Historical field lost: "+key)
   # Create a *known* unsafe edit in persisted JSON and prove that the
   # continuity audit flags it, without mutating app private state.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V34',p=JSON.parse(localStorage.getItem(key));
    if(p.episodes[0].scenes.length<2)throw new Error('Need 2 scenes for axis test');
    p.episodes[0].scenes[0].storyboardV34={enabled:true,axis:'left',
     focus:'center',shots:['wide','medium','close'],strength:90,tracking:50,smoothness:80};
    p.episodes[0].scenes[1].storyboardV34={enabled:true,axis:'right',
     focus:'center',shots:['wide','medium','close'],strength:90,tracking:50,smoothness:80};
    localStorage.setItem(key,JSON.stringify(p));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v34-scene')?.options.length>0")
   page.locator('[data-page="storyboard-v34"]').click()
   page.locator("#v34-audit").click()
   warnings=page.locator("#v34-report").inner_text()
   if "ось 180°" not in warnings:
    raise AssertionError("V34 did not detect adjacent-axis flip: "+warnings[:300])
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v34-plan").click()
   report=out/"V34_SHOT_CONTINUITY_RU.txt";dl.value.save_as(report)
   if "ПРОВЕРКА СТЫКОВ СЦЕН" not in report.read_text(encoding="utf-8"):
    raise AssertionError("Shot continuity TXT report missing")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v34-sheet").click()
   sheet=out/"V34_SIX_SHOTS_STORYBOARD.png";dl.value.save_as(sheet)
   image=png(sheet);frames.append(image)
   if image["width"]!=1920 or image["height"]!=720:
    raise AssertionError("Contact sheet should be 3 × 2 real frames")
   last=page.evaluate("""() => {
     const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V34'));
     return {version:p.version,episodes:p.episodes,characters:p.characters,
              lore:p.lore,checkpoint:p.unifiedV30};
   }""")
   page.reload(wait_until="load")
   reloaded=page.evaluate("""() => {
     const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V34'));
     return {version:p.version,episodes:p.episodes,characters:p.characters,
              lore:p.lore,checkpoint:p.unifiedV30};
   }""")
   if last!=reloaded:raise AssertionError("V34 story or metadata changed after reload")
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27",
               "interaction-v28","polish-v29","review-v30",
               "visual-v31","keyframe-v32","acting-v33","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Browser JS errors: "+"; ".join(errors[:5]))
   (out/"V34_BROWSER_QA.json").write_text(json.dumps({
     "version":34,"axis_change_detected":True,"frames":frames,
     "historical_project_preserved":True,"errors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V34 CHROMIUM PASS: A/B real camera, per-scene shots, axis flip, six PNGs, old project")
  finally:browser.close()
if __name__=="__main__":main()
