#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real Chromium smoke test of V21 Canvas, tab, scene save, PNG export.
CI dependency: pip install playwright; python -m playwright install chromium.
Not needed by end users to operate the editor.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright


def signature(path):
    contents=Path(path).read_bytes()
    if contents[:8]!=b"\x89PNG\r\n\x1a\n":
        raise AssertionError("PNG header missing")
    width,height=struct.unpack(">II",contents[16:24])
    if width<200 or height<100 or len(contents)<10000:
        raise AssertionError("PNG too small or empty")
    return {"width":width,"height":height,"size":len(contents),
            "sha256":hashlib.sha256(contents).hexdigest()}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",required=True)
    p.add_argument("--out",default="dist/V21_VISUAL_SAMPLES")
    opt=p.parse_args()
    source=Path(opt.html).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    out=Path(opt.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    report={"source":str(source.name),"samples":[],"errors":[]}

    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1400,"height":1000},
                              device_scale_factor=1,accept_downloads=True)
        page.on("pageerror",lambda error: report["errors"].append(str(error)))
        try:
            page.goto(source.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function(
                "() => document.querySelector('#v21-scene')?.options.length > 0",
                timeout=30000)
            page.locator('[data-page="visual-v21"]').click()
            page.wait_for_function(
                "() => !document.getElementById('page-visual-v21').hidden",
                timeout=10000)
            default_path=out/"V21_01_DEFAULT.png"
            page.locator("#v21-preview").screenshot(path=str(default_path),timeout=30000)
            report["samples"].append({"name":default_path.name,**signature(default_path)})

            page.locator("#v21-look").select_option("sunset")
            page.locator("#v21-weather").select_option("rain")
            page.locator("#v21-intensity").fill("90")
            page.locator("#v21-rim").fill("88")
            page.locator("#v21-save").click()
            page.wait_for_timeout(500)
            after=out/"V21_02_SUNSET_RAIN.png"
            page.locator("#v21-preview").screenshot(path=str(after),timeout=30000)
            report["samples"].append({"name":after.name,**signature(after)})
            if default_path.read_bytes()==after.read_bytes():
                raise AssertionError("Changing the palette and weather did not change the frame")

            stored=page.evaluate("""() => {
              const raw=localStorage.getItem('AI_ANIME_FACTORY_V21');
              const p=raw?JSON.parse(raw):null;
              return {version:p?.version, episodes:p?.episodes?.length,
                visual:p?.episodes?.[0]?.scenes?.[0]?.visualV21};
            }""")
            if stored["version"]!=21 or stored["episodes"]<1:
                raise AssertionError("V21 project not persisted")
            if stored["visual"]["weather"]!="rain" or stored["visual"]["look"]!="sunset":
                raise AssertionError("V21 color and weather settings missing from JSON")
            report["storage"]=stored

            with page.expect_download(timeout=60000) as info:
                page.locator("#v21-sheet").click()
            sample=out/"V21_03_FOUR_SHOT_CONTACT_SHEET.png"
            info.value.save_as(sample)
            report["samples"].append({"name":sample.name,**signature(sample)})

            page.locator('[data-page="story-v20"]').click()
            if page.locator("#v20-episode option").count()<1:
                raise AssertionError("V20 Story tab is broken")
            page.locator('[data-page="impact-v19"]').click()
            if page.locator("#impact19-profile").count()<1:
                raise AssertionError("V19 combat tab is broken")
            report["tabs"]=["V21 Visual Quality","V20 Story","V19 Impact"]
            if report["errors"]:
                raise AssertionError("JavaScript runtime errors: "+str(report["errors"]))
        except Exception:
            page.screenshot(path=str(out/"V21_BROWSER_FAILURE.png"),full_page=True)
            raise
        finally:
            browser.close()
    (out/"V21_BROWSER_SMOKE_REPORT.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V21 REAL BROWSER SMOKE PASS",json.dumps(
        {"frames":len(report["samples"]),"js_errors":len(report["errors"]),
         "tabs":len(report["tabs"])},ensure_ascii=False))


if __name__=="__main__":
    main()
