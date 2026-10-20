#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V30 real Chromium project audit, protected canon baseline, JSON and PNG exports."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_info(p):
 b=Path(p).read_bytes()
 if len(b)<8000 or b[:8]!=b"\x89PNG\r\n\x1a\n":raise AssertionError("Broken PNG "+str(p))
 w,h=struct.unpack(">II",b[16:24])
 if w<250 or h<140:raise AssertionError("Small PNG")
 return {"name":p.name,"width":w,"height":h,"bytes":len(b),
         "sha256":hashlib.sha256(b).hexdigest()}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--html",required=True)
 parser.add_argument("--out",default="dist/V30_UNIFIED_QA_SAMPLES")
 cfg=parser.parse_args()
 html=Path(cfg.html).resolve();out=Path(cfg.out).resolve();out.mkdir(parents=True,exist_ok=True)
 errors=[];screens=[]
 with sync_playwright() as pl:
  browser=pl.chromium.launch(headless=True,
   args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
  page=browser.new_page(viewport={"width":1480,"height":1110},
                       accept_downloads=True,device_scale_factor=1)
  page.on("pageerror",lambda err:errors.append(str(err)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v30-run') && !!localStorage.getItem('AI_ANIME_FACTORY_V30')",timeout=45000)
   page.locator('[data-page="review-v30"]').click()
   page.wait_for_function("() => !document.querySelector('#page-review-v30').hidden")
   page.locator("#v30-run").click()
   initial=page.locator("#v30-summary").inner_text()
   if "эталон: не создан" not in initial:raise AssertionError("Fresh project wrongly has saved canon baseline: "+initial)
   page.locator("#v30-snapshot").click()
   initial_after=page.locator("#v30-summary").inner_text()
   if "эталон: не создан" in initial_after:raise AssertionError("Checkpoint failed")
   baseline=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V30')||'null');
    return {version:p?.version,characters:p?.characters,
      episodes:p?.episodes,lore:p?.lore,checkpoint:p?.unifiedV30};
   }""")
   if baseline["version"]!=30 or not baseline["checkpoint"] or not baseline["episodes"]:
    raise AssertionError("Checkpoint not saved as V30")
   if not baseline["episodes"][0].get("storyV20") or not baseline["characters"][0].get("qualityV23"):
    raise AssertionError("Historic story or model settings missing")
   for k in ("visualV21","actingV22","motionV24","choreographyV25",
             "cinemaV26","worldV27","interactionV28","polishV29"):
    if k not in baseline["episodes"][0]["scenes"][0]:raise AssertionError("Missing "+k)
   # Export complete JSON before testing scenario changes.
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v30-backup").click()
   backup=out/"V30_COMPLETE_PROJECT_BACKUP.json"
   dl.value.save_as(backup);backed=json.loads(backup.read_text(encoding="utf-8"))
   if backed["version"]!=30 or backed["unifiedV30"]!=baseline["checkpoint"]:
    raise AssertionError("Full backup incomplete")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v30-manifest").click()
   manifest=out/"V30_INTEGRITY_REPORT.json";dl.value.save_as(manifest)
   checked=json.loads(manifest.read_text(encoding="utf-8"))
   if not checked["baseline"] or not checked["current"]:
    raise AssertionError("Baseline/current hashes missing")
   # Simulate a legitimate author revision through persisted local project
   # rather than deleting content or modifying the private app closure.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V30',p=JSON.parse(localStorage.getItem(key));
    p.episodes[0].scenes[0].title+=' — ИЗМЕНЕНИЕ ДЛЯ КОНТРОЛЯ';
    localStorage.setItem(key,JSON.stringify(p));
   }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v30-results')?.textContent.length>0")
   page.locator('[data-page="review-v30"]').click()
   page.locator("#v30-run").click()
   issues=page.locator("#v30-results").inner_text()
   if "Изменилась сцена" not in issues:
    raise AssertionError("Baseline failed to catch changed scene title: "+issues[:500])
   current=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V30'));
    return {version:p.version,title:p.episodes[0].scenes[0].title,
            baseline:p.unifiedV30,cast:p.characters.length,
            episodes:p.episodes.length};
   }""")
   if "ИЗМЕНЕНИЕ ДЛЯ КОНТРОЛЯ" not in current["title"] or current["baseline"]!=baseline["checkpoint"]:
    raise AssertionError("Audit edited user scene or removed protected checkpoint")
   page.locator("#v30-filter").select_option("warning")
   if "Изменилась сцена" not in page.locator("#v30-results").inner_text():
    raise AssertionError("Severity filtering lost scene issue")
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v30-report").click()
   report=out/"V30_AUDIT_RU.txt";dl.value.save_as(report)
   if "Изменилась сцена" not in report.read_text(encoding="utf-8"):
    raise AssertionError("Russian TXT report missing continuity issue")
   page.locator("#v30-position").fill("38")
   frame=out/"V30_VERIFIED_REAL_FRAME.png"
   page.locator("#v30-preview").screenshot(path=str(frame));screens.append(png_info(frame))
   with page.expect_download(timeout=60000) as dl:
    page.locator("#v30-sheet").click()
   sheet=out/"V30_FOUR_SCENE_FRAMES.png";dl.value.save_as(sheet);screens.append(png_info(sheet))
   # Crucial: all old editor UI pages remain accessible.
   for tab in ("story-v20","visual-v21","acting-v22","character-v23",
               "animation-v24","combat-v25","cinematic-v26","world-v27",
               "interaction-v28","polish-v29","impact-v19"):
    page.locator('[data-page="'+tab+'"]').click()
    page.wait_for_function("tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
   if errors:raise AssertionError("Browser JavaScript errors: "+"; ".join(errors[:8]))
   (out/"V30_BROWSER_QA.json").write_text(json.dumps({
    "version":30,"frames":screens,"baseline_preserved":True,
    "detected_scene_edit":True,"backup_bytes":backup.stat().st_size,
    "report_bytes":report.stat().st_size,"errors":errors
   },indent=2,ensure_ascii=False),encoding="utf-8")
   print("V30 CHROMIUM PASS: checkpoint, backup, detects scene edit, preserves old data, PNG")
  finally:browser.close()
if __name__=="__main__":main()
