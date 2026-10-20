#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V27 real Chromium: world A/B, scene palette changes, reload, legacy and PNG."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_info(path):
 data=Path(path).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Missing/invalid PNG: "+str(path))
 w,h=struct.unpack(">II",data[16:24])
 if w<250 or h<140:raise AssertionError("Tiny rendered PNG")
 return {"name":Path(path).name,"bytes":len(data),"size":[w,h],
         "sha256":hashlib.sha256(data).hexdigest()}

def main():
 args=argparse.ArgumentParser()
 args.add_argument("--html",required=True)
 args.add_argument("--out",default="dist/V27_WORLD_SAMPLES")
 cfg=args.parse_args()
 html=Path(cfg.html).resolve()
 dest=Path(cfg.out).resolve();dest.mkdir(parents=True,exist_ok=True)
 errors=[];frames=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1450,"height":1010},
                        device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda exc:errors.append(str(exc)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v27-scene')?.options.length>0",timeout=40000)
   page.locator('[data-page="world-v27"]').click()
   page.wait_for_function("() => !document.querySelector('#page-world-v27').hidden")
   page.locator("#v27-position").fill("38")
   before=dest/"V27_V26_BASE.png";after=dest/"V27_WORLD.png"
   page.locator("#v27-before").screenshot(path=str(before))
   page.locator("#v27-after").screenshot(path=str(after))
   frames.extend((png_info(before),png_info(after)))
   if before.read_bytes()==after.read_bytes():
    raise AssertionError("New world depth did not alter actual scene")
   page.locator("#v27-biome").select_option("forest")
   for key,value in (("depth","96"),("lighting","87"),("grounding","90"),
                     ("atmosphere","79"),("foreground","82")):
    page.locator("#v27-"+key).fill(value)
   page.locator("#v27-save").click()
   updated=dest/"V27_FOREST_WORLD.png"
   page.locator("#v27-after").screenshot(path=str(updated))
   frames.append(png_info(updated))
   if updated.read_bytes()==after.read_bytes():
    raise AssertionError("Scene biome and sliders did not change the world frame")
   state=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V27')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if state["version"]!=27 or not state["episodes"]:
    raise AssertionError("V27 JSON not saved")
   s=state["episodes"][0]["scenes"][0]
   if s["worldV27"]["biome"]!="forest" or s["worldV27"]["depth"]!=96:
    raise AssertionError("World settings not written in scene")
   if not state["episodes"][0].get("storyV20") or not state["characters"][0].get("qualityV23"):
    raise AssertionError("Prior story/characters missing")
   for key in ("visualV21","actingV22","motionV24","choreographyV25","cinemaV26"):
    if key not in s:raise AssertionError("Prior scene field missing "+key)
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v27-scene')?.options.length>0")
   again=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V27')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if again!=state:raise AssertionError("Reload mutated legacy plot, characters or world")
   page.locator('[data-page="world-v27"]').click()
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v27-sheet").click()
   sheet=dest/"V27_FOUR_WORLD_FRAMES.png"
   dl.value.save_as(sheet);frames.append(png_info(sheet))
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Chromium JS errors: "+" | ".join(errors[:7]))
   (dest/"V27_BROWSER_QA.json").write_text(json.dumps({
    "frames":frames,"version":27,"world":state["episodes"][0]["scenes"][0]["worldV27"],
    "js_errors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V27 CHROMIUM PASS: A/B world, biome, saved V20–V27 story and PNG")
  finally:browser.close()
if __name__=="__main__":main()
