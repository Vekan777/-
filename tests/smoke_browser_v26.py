#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real Chromium V26 camera A/B frames, settings, story preservation and PNG export."""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png(path):
 data=Path(path).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Missing or invalid PNG: "+str(path))
 w,h=struct.unpack(">II",data[16:24])
 if w<250 or h<140:raise AssertionError("Broken Canvas dimensions")
 return {"name":Path(path).name,"bytes":len(data),"width":w,"height":h,
         "sha256":hashlib.sha256(data).hexdigest()}

def main():
 arg=argparse.ArgumentParser()
 arg.add_argument("--html",required=True)
 arg.add_argument("--out",default="dist/V26_CINEMATIC_SAMPLES")
 opts=arg.parse_args()
 html=Path(opts.html).resolve()
 dest=Path(opts.out).resolve();dest.mkdir(parents=True,exist_ok=True)
 frames=[];errors=[]
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,
      args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1470,"height":1050},
      accept_downloads=True,device_scale_factor=1)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v26-scene')?.options.length>0",timeout=40000)
   page.locator('[data-page="cinematic-v26"]').click()
   page.wait_for_function("() => !document.querySelector('#page-cinematic-v26').hidden")
   selected=page.locator("#v26-scene").input_value()
   ep_i,sc_i=(int(v) for v in selected.split(':'))
   page.locator("#v26-position").fill("48")
   first=dest/"V26_V25_BASELINE.png";second=dest/"V26_CINEMATIC.png"
   page.locator("#v26-before").screenshot(path=str(first))
   page.locator("#v26-after").screenshot(path=str(second))
   frames.extend((png(first),png(second)))
   if first.read_bytes()==second.read_bytes():
    raise AssertionError("Cinematography did not alter actual Canvas frame")
   page.locator("#v26-style").select_option("close")
   for key,value in (("intensity","95"),("tracking","87"),
                     ("impactFocus","93"),("letterbox","90"),("transitions","70")):
    page.locator("#v26-"+key).fill(value)
   page.locator("#v26-save").click()
   third=dest/"V26_CLOSE_UP.png";page.locator("#v26-after").screenshot(path=str(third))
   frames.append(png(third))
   if second.read_bytes()==third.read_bytes():
    raise AssertionError("Camera settings did not change shot")
   before=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V26')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,
            lore:p?.lore};
   }""")
   if before["version"]!=26 or len(before["episodes"])<1:
    raise AssertionError("V26 project not persisted")
   episode=before["episodes"][ep_i];scene=episode["scenes"][sc_i]
   if scene["kind"]!="fight" or scene["cinemaV26"]["intensity"]!=95:
    raise AssertionError("Per-scene V26 camera settings lost")
   if not episode.get("storyV20") or not before["characters"][0].get("qualityV23"):
    raise AssertionError("Story or character design lost")
   for key in ("visualV21","actingV22","combatV17","motionV24","choreographyV25"):
    if key not in scene:raise AssertionError("Missing previous scene setting "+key)
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v26-scene')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V26')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,
            lore:p?.lore};
   }""")
   if before!=after:raise AssertionError("Reload corrupted V20–V26 project")
   page.locator('[data-page="cinematic-v26"]').click()
   with page.expect_download(timeout=60000) as download:
    page.locator("#v26-sheet").click()
   output=dest/"V26_FOUR_SHOTS.png"
   download.value.save_as(output);frames.append(png(output))
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Chromium JS: "+" / ".join(errors[:8]))
   (dest/"V26_BROWSER_QA.json").write_text(json.dumps(
    {"version":26,"scene":[ep_i,sc_i],"frames":frames,"js_errors":errors},
    ensure_ascii=False,indent=2),encoding="utf-8")
   print("V26 CHROMIUM PASS: A/B camera, settings, V19–V25 preservation, PNG")
  finally:browser.close()
if __name__=="__main__":main()
