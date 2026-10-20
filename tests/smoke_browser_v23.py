#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actual Chromium V23 image/persistence smoke test (CI only)."""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_info(p):
    data=Path(p).read_bytes()
    if len(data)<8000 or data[:8]!=b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Missing/broken Canvas screenshot: "+str(p))
    w,h=struct.unpack(">II",data[16:24])
    if w<250 or h<150:
        raise AssertionError("Tiny rendered frame")
    return {"file":Path(p).name,"bytes":len(data),"size":[w,h],
            "sha256":hashlib.sha256(data).hexdigest()}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--html",required=True)
    cli.add_argument("--out",default="dist/V23_CHARACTER_SAMPLES")
    a=cli.parse_args()
    html=Path(a.html).resolve()
    dest=Path(a.out).resolve();dest.mkdir(parents=True,exist_ok=True)
    errors=[];frames=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,
           args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1360,"height":980},
                              device_scale_factor=1,accept_downloads=True)
        page.on("pageerror",lambda e:errors.append(str(e)))
        try:
            page.goto(html.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => document.querySelector('#v23-character')?.options.length>0")
            page.locator('[data-page="character-v23"]').click()
            page.wait_for_function("() => !document.querySelector('#page-character-v23').hidden")
            page.locator("#v23-playhead").fill("40")
            before=dest/"V23_BASE.png"
            page.locator("#v23-preview").screenshot(path=str(before))
            frames.append(png_info(before))

            # First change only appearance controls. The resulting frame must change.
            page.locator("#v23-profile").select_option("heroic")
            page.locator("#v23-anatomy").fill("97")
            page.locator("#v23-hairDetail").fill("95")
            page.locator("#v23-costumeDetail").fill("90")
            page.locator("#v23-secondaryMotion").fill("87")
            page.locator("#v23-save").click()
            after=dest/"V23_HEROIC.png"
            page.locator("#v23-preview").screenshot(path=str(after))
            frames.append(png_info(after))
            if before.read_bytes()==after.read_bytes():
                raise AssertionError("Character quality sliders did not affect the rendered Canvas")

            # Save V22 acting and ensure these settings survive reload into V23.
            page.locator('[data-page="acting-v22"]').click()
            page.locator("#v22-preset").click()
            page.locator('[data-page="character-v23"]').click()
            before_reload=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V23')||'null');
             return {version:p?.version,episodes:p?.episodes?.length,
                     characters:p?.characters?.length,quality:p?.characters?.[0]?.qualityV23,
                     acts:p?.episodes?.[0]?.scenes?.[0]?.actingV22,
                     visual:p?.episodes?.[0]?.scenes?.[0]?.visualV21,
                     story:p?.episodes?.[0]?.storyV20};
            }""")
            if before_reload["version"]!=23 or before_reload["characters"]<2:
                raise AssertionError("V23 project not saved")
            if before_reload["quality"].get("profile")!="heroic":
                raise AssertionError("Appearance not saved")
            if not before_reload["acts"] or not before_reload["acts"].get("beats"):
                raise AssertionError("V22 acting tracks were lost")
            if not before_reload["visual"] or not before_reload["story"]:
                raise AssertionError("V20/V21 persistent fields were lost")

            page.reload(wait_until="load")
            page.wait_for_function("() => document.querySelector('#v23-character')?.options.length>0")
            restored=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V23')||'null');
             return {version:p?.version,quality:p?.characters?.[0]?.qualityV23,
                     acts:p?.episodes?.[0]?.scenes?.[0]?.actingV22,
                     visual:p?.episodes?.[0]?.scenes?.[0]?.visualV21,
                     story:p?.episodes?.[0]?.storyV20};
            }""")
            for key in ("quality","acts","visual","story"):
                if restored[key]!=before_reload[key]:
                    raise AssertionError("Reload destroyed "+key+" settings")

            page.locator('[data-page="character-v23"]').click()
            with page.expect_download(timeout=60000) as d:
                page.locator("#v23-sheet").click()
            sheet=dest/"V23_CHARACTER_FOUR_FRAMES.png"
            d.value.save_as(sheet)
            frames.append(png_info(sheet))
            for tab in ("story-v20","visual-v21","acting-v22","impact-v19"):
                page.locator('[data-page="'+tab+'"]').click()
                page.wait_for_function(
                   "tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
            if errors:
                raise AssertionError("JavaScript browser errors: "+"; ".join(errors[:8]))
            (dest/"V23_QA.json").write_text(json.dumps(
                {"frames":frames,"before_reload":before_reload,
                 "after_reload":restored,"errors":errors},
                ensure_ascii=False,indent=2),encoding="utf-8")
            print("V23 CHROMIUM PASS",len(frames),"PNGs; V20–V23 persisted through reload")
        finally:
            browser.close()

if __name__=="__main__":
    main()
