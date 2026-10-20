#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V29 real Chromium timeline, A/B changes, old project fields and gate checks."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_info(path):
 data=Path(path).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Invalid PNG "+str(path))
 w,h=struct.unpack(">II",data[16:24])
 if w<250 or h<140:raise AssertionError("Bad PNG shape")
 return {"name":path.name,"size":[w,h],"bytes":len(data),
         "sha256":hashlib.sha256(data).hexdigest()}

def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--html",required=True)
 cli.add_argument("--out",default="dist/V29_POLISH_SAMPLES")
 o=cli.parse_args();html=Path(o.html).resolve()
 folder=Path(o.out).resolve();folder.mkdir(parents=True,exist_ok=True)
 errors=[];frames=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,
   args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1450,"height":1040},
   device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v29-scene')?.options.length>0",timeout=40000)
   page.locator('[data-page="polish-v29"]').click()
   page.wait_for_function("() => !document.querySelector('#page-polish-v29').hidden")
   selection=page.locator("#v29-scene").input_value()
   i,j=(int(n) for n in selection.split(':'))
   baseline=folder/"V29_V28_BASE.png";improved=folder/"V29_SYNC_RIG.png"
   different=False
   for pct in ["25","38","50","62","75"]:
    page.locator("#v29-position").fill(pct)
    page.locator("#v29-before").screenshot(path=str(baseline))
    page.locator("#v29-after").screenshot(path=str(improved))
    if baseline.read_bytes()!=improved.read_bytes():
     different=True;break
   if not different:raise AssertionError("V29 animation does not change an actual fight frame")
   frames.extend((png_info(baseline),png_info(improved)))
   page.locator("#v29-style").select_option("action")
   for key,value in (("timing","96"),("stance","94"),
                     ("follow","90"),("impact","88"),("smoothness","93")):
    page.locator("#v29-"+key).fill(value)
   page.locator("#v29-save").click()
   strong=folder/"V29_BALANCED_CONTACT.png"
   page.locator("#v29-after").screenshot(path=str(strong))
   frames.append(png_info(strong))
   if improved.read_bytes()==strong.read_bytes():
    raise AssertionError("V29 sliders do not alter stance, limbs or effect timing")
   before=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V29')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if before["version"]!=29 or not before["episodes"]:
    raise AssertionError("V29 project not saved")
   s=before["episodes"][i]["scenes"][j]
   if s["kind"]!="fight" or s["polishV29"]["stance"]!=94:
    raise AssertionError("V29 scene polish settings lost")
   if not before["episodes"][i].get("storyV20") or not before["characters"][0].get("qualityV23"):
    raise AssertionError("Old plot or character attributes missing")
   for key in ("visualV21","actingV22","motionV24","choreographyV25",
               "cinemaV26","worldV27","interactionV28"):
    if key not in s:raise AssertionError("Old scene field missing: "+key)
   # Execute one authentic beat function in isolation; no private editor
   # closure is mutated, no synthetic result is added to the real project.
   outcomes=page.evaluate("""() => {
    const scripts=[...document.querySelectorAll('script')].map(x=>x.textContent).join('\\n');
    const m=scripts.match(/function v29Beat\\(s,t\\)\\{[\\s\\S]*?\\n\\}(?=\\nfunction v29Actor)/);
    if(!m)throw new Error('V29 beat source missing');
    const limit=(a,b,c)=>Math.max(b,Math.min(c,a));
    const evaluate=(outcome)=>{
     const f=new Function('v25Contact','clamp',
      m[0]+";return v29Beat({kind:'fight'},2);");
     return f(()=>({active:true,outcome,actor:'hero',anticipation:.3,
      release:.7,contact:1,defense:.9}),limit);
    };
    const miss=evaluate('miss'),dodge=evaluate('dodge'),
          hit=evaluate('hit'),block=evaluate('block');
    return {miss:miss.contact===0&&miss.guard===0,
            dodge:dodge.contact===0&&dodge.dodge>.8,
            hit:hit.contact===1&&hit.outcome==='hit',
            block:block.guard>.8&&block.contact===1};
   }""")
   if not all(outcomes.values()):raise AssertionError("False hit/block gating: "+str(outcomes))
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v29-scene')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V29')||'null');
    return {version:p?.version,episodes:p?.episodes,characters:p?.characters,lore:p?.lore};
   }""")
   if before!=after:raise AssertionError("V29 JSON reload changed historical project fields")
   page.locator('[data-page="polish-v29"]').click()
   with page.expect_download(timeout=60000) as dl:page.locator("#v29-sheet").click()
   sheet=folder/"V29_FOUR_ACTION_BEATS.png"
   dl.value.save_as(sheet);frames.append(png_info(sheet))
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27",
               "interaction-v28","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Chromium errors: "+" | ".join(errors[:6]))
   (folder/"V29_BROWSER_QA.json").write_text(json.dumps(
     {"version":29,"scene":[i,j],"frames":frames,"gates":outcomes,"errors":errors},
     indent=2,ensure_ascii=False),encoding="utf-8")
   print("V29 CHROMIUM PASS: synchronized A/B rig, controls, hit/miss, V20–V29 JSON, PNG")
  finally:browser.close()
if __name__=="__main__":main()
