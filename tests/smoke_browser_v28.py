#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actual Chromium V28 scene effects A/B, confirmed hit gating, project reload, PNG."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def check_png(path):
 data=Path(path).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Invalid rendered PNG "+str(path))
 w,h=struct.unpack(">II",data[16:24])
 if w<250 or h<140:raise AssertionError("Invalid canvas dimensions")
 return {"name":path.name,"size":[w,h],"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--html",required=True)
 ap.add_argument("--out",default="dist/V28_INTERACTION_SAMPLES")
 cfg=ap.parse_args()
 html=Path(cfg.html).resolve()
 out=Path(cfg.out).resolve();out.mkdir(parents=True,exist_ok=True)
 frames=[];errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,
    args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1480,"height":1100},
      device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v28-scene')?.options.length>0",timeout=40000)
   page.locator('[data-page="interaction-v28"]').click()
   page.wait_for_function("() => !document.querySelector('#page-interaction-v28').hidden")
   page.locator("#v28-position").fill("38")
   before=out/"V28_V27_BASE.png";after=out/"V28_CHARACTER_WORLD.png"
   page.locator("#v28-before").screenshot(path=str(before))
   page.locator("#v28-after").screenshot(path=str(after))
   frames.extend((check_png(before),check_png(after)))
   if before.read_bytes()==after.read_bytes():
    raise AssertionError("Interaction effects did not alter actual frame")
   page.locator("#v28-style").select_option("dramatic")
   for key,value in (("footsteps","96"),("dust","86"),("bounce","92"),
                     ("scars","85"),("impactFX","89")):
    page.locator("#v28-"+key).fill(value)
   page.locator("#v28-save").click()
   newer=out/"V28_STRONG_CONTACT.png";page.locator("#v28-after").screenshot(path=str(newer))
   frames.append(check_png(newer))
   if newer.read_bytes()==after.read_bytes():
    raise AssertionError("Sliders did not change character/environment contact")
   pstate=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V28')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if pstate["version"]!=28 or not pstate["episodes"]:
    raise AssertionError("V28 project not persisted")
   scene=pstate["episodes"][0]["scenes"][0]
   if scene["interactionV28"]["dust"]!=86:
    raise AssertionError("Interaction not saved in the current scene")
   if not pstate["episodes"][0].get("storyV20") or not pstate["characters"][0].get("qualityV23"):
    raise AssertionError("Previous story or character design missing")
   for key in ("visualV21","actingV22","motionV24","choreographyV25",
               "cinemaV26","worldV27"):
    if key not in scene:raise AssertionError("Prior scene field lost: "+key)
   # Evaluate the exact V28 source function in an isolated browser scope.
   # The real editor keeps its IIFE functions private, so we do not poke
   # private state or mutate the project's authoritative combat timeline.
   gates=page.evaluate("""() => {
      const source=[...document.querySelectorAll('script')].map(s=>s.textContent).join('\\n');
      const matched=source.match(/function v28ImpactAt\\(s,t\\)\\{[\\s\\S]*?\\n\\}(?=\\nfunction v28CombatGround)/);
      if(!matched)throw new Error('V28 impact-gating function not found in generated JS');
      const limit=(v,a,b)=>Math.max(a,Math.min(b,v));
      function check(outcome){
       const runner=new Function('v25Contact','clamp',
           matched[0]+";return v28ImpactAt({kind:'fight'},2);");
       return runner(()=>({active:true,outcome,actor:'hero',contact:1}),limit);
      }
      return {miss:check('miss')===null,dodge:check('dodge')===null,
              hit:check('hit')?.kind,block:check('block')?.kind};
   }""")
   if gates!={"miss":True,"dodge":True,"hit":"hit","block":"block"}:
    raise AssertionError("V28 combat-gating failed: "+str(gates))
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v28-scene')?.options.length>0")
   reloaded=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V28')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if pstate!=reloaded:raise AssertionError("V28 reload changed previous story/characters")
   page.locator('[data-page="interaction-v28"]').click()
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v28-sheet").click()
   sheet=out/"V28_FOUR_INTERACTION_FRAMES.png"
   dl.value.save_as(sheet);frames.append(check_png(sheet))
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Chromium errors: "+" | ".join(errors[:7]))
   (out/"V28_BROWSER_QA.json").write_text(json.dumps({
    "version":28,"frames":frames,"gates":gates,
    "interaction":scene["interactionV28"],"errors":errors},
    ensure_ascii=False,indent=2),encoding="utf-8")
   print("V28 CHROMIUM PASS: A/B, actor contact, gated hits, V20–V28 JSON, PNG")
  finally:browser.close()
if __name__=="__main__":main()
