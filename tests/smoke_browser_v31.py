#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V31 genuine Chromium A/B pixels, metrics, export, V20–V31 and thresholds."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png(path):
 data=Path(path).read_bytes()
 if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
  raise AssertionError("Invalid PNG "+str(path))
 w,h=struct.unpack(">II",data[16:24])
 if w<250 or h<140:raise AssertionError("Invalid frame dimensions")
 return {"file":path.name,"width":w,"height":h,"bytes":len(data),
  "sha256":hashlib.sha256(data).hexdigest()}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--html",required=True)
 parser.add_argument("--out",default="dist/V31_VISUAL_PRODUCTION_SAMPLES")
 args=parser.parse_args()
 html=Path(args.html).resolve()
 out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
 errors=[];frames=[]
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,
   args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1500,"height":1090},
   device_scale_factor=1,accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v31-scene')?.options.length>0",timeout=45000)
   page.locator('[data-page="visual-v31"]').click()
   page.wait_for_function("() => !document.querySelector('#page-visual-v31').hidden")
   baseline=out/"V31_V30_BASE_FRAME.png"
   grade=out/"V31_GRADED_FRAME.png"
   page.locator("#v31-position").fill("45")
   page.locator("#v31-before").screenshot(path=str(baseline))
   page.locator("#v31-after").screenshot(path=str(grade))
   frames.extend([png(baseline),png(grade)])
   if baseline.read_bytes()==grade.read_bytes():
    raise AssertionError("V31 final grading didn't change the actual rendered frame")
   page.locator("#v31-enabled").check()
   for key,value in (("exposure","70"),("contrast","70"),
                     ("saturation","72"),("vignette","53")):
    page.locator("#v31-"+key).fill(value)
   page.locator("#v31-save").click()
   stronger=out/"V31_NEW_GRADE.png"
   page.locator("#v31-after").screenshot(path=str(stronger))
   frames.append(png(stronger))
   if grade.read_bytes()==stronger.read_bytes():
    raise AssertionError("V31 grade slider changes didn't affect Canvas pixels")
   selected=page.locator("#v31-scene").input_value()
   i,j=[int(x) for x in selected.split(':')]
   before=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V31')||'null');
    return {version:p?.version,characters:p?.characters,
            episodes:p?.episodes,lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before["version"]!=31 or not before["episodes"]:
    raise AssertionError("V31 project not persisted")
   s=before["episodes"][i]["scenes"][j]
   if s["finishV31"]["exposure"]!=70:
    raise AssertionError("V31 grade scene changes not saved")
   if not before["episodes"][i].get("storyV20") or not before["characters"][0].get("qualityV23"):
    raise AssertionError("Historic story or character detail was lost")
   for k in ("visualV21","actingV22","motionV24","choreographyV25",
             "cinemaV26","worldV27","interactionV28","polishV29"):
    if k not in s:raise AssertionError("Lost older scene attribute "+k)
   page.locator("#v31-analyze").click()
   selected_metrics=page.locator("#v31-result").inner_text()
   if "яркость" not in selected_metrics or "контраст" not in selected_metrics:
    raise AssertionError("Real Canvas metrics missing")
   page.locator("#v31-all").click()
   if "Изучено сцен" not in page.locator("#v31-result").inner_text():
    raise AssertionError("Project-level visual QA not completed")
   # Exact detector function called in isolation with deliberately dark and
   # bright frame metrics; this does not mutate any private project closure.
   thresholds=page.evaluate("""() => {
    const src=[...document.querySelectorAll('script')].map(x=>x.textContent).join('\\n');
    const match=src.match(/function v31Assess\\(metrics\\)\\{[\\s\\S]*?\\n\\}(?=\\nfunction v31SceneReview)/);
    if(!match)throw new Error('Actual V31 threshold source missing');
    const assess=new Function('metrics',match[0]+';return v31Assess(metrics);');
    const dark=assess([{mean:30,contrast:12,dark:.75,bright:0,center:20,edges:.002}]);
    const bright=assess([{mean:240,contrast:12,dark:0,bright:.8,center:230,edges:.002}]);
    return {dark:dark.some(x=>x.includes('низкая яркость')),
            bright:bright.some(x=>x.includes('пересветка'))};
   }""")
   if not all(thresholds.values()):
    raise AssertionError("V31 pixels do not flag known dark/bright frames "+str(thresholds))
   with page.expect_download(timeout=60000) as d:
    page.locator("#v31-json").click()
   mfile=out/"V31_VISUAL_PRODUCTION_METRICS.json"
   d.value.save_as(mfile)
   metrics=json.loads(mfile.read_text(encoding="utf-8"))
   if metrics["sampled"]<1 or not metrics["scenes"] or len(metrics["scenes"][0]["metrics"])!=4:
    raise AssertionError("Report failed to analyze four true frames")
   with page.expect_download(timeout=60000) as d:
    page.locator("#v31-report").click()
   txt=out/"V31_VISUAL_QA_RU.txt";d.value.save_as(txt)
   if "Кадр 1" not in txt.read_text(encoding="utf-8"):
    raise AssertionError("Missing per-frame report")
   with page.expect_download(timeout=60000) as d:
    page.locator("#v31-sheet").click()
   sheet=out/"V31_FOUR_FRAMES.png";d.value.save_as(sheet)
   frames.append(png(sheet))
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v31-scene')?.options.length>0")
   after=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V31')||'null');
    return {version:p?.version,characters:p?.characters,
            episodes:p?.episodes,lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if before!=after:raise AssertionError("V20–V31 JSON changed after browser reload")
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27",
               "interaction-v28","polish-v29","review-v30","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Browser exceptions: "+" | ".join(errors[:5]))
   (out/"V31_BROWSER_QA.json").write_text(json.dumps({
    "version":31,"frames":frames,"threshold_tests":thresholds,
    "review_scenes":metrics["sampled"],"js_errors":errors
   },ensure_ascii=False,indent=2),encoding="utf-8")
   print("V31 CHROMIUM PASS: actual graded pixels, thresholds, JSON persistence and PNG")
  finally:browser.close()
if __name__=="__main__":main()
