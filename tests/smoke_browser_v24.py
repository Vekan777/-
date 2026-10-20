#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V24 actual Chromium Canvas, saved project roundtrip and PNG export QA."""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_info(path):
    payload=Path(path).read_bytes()
    if payload[:8]!=b"\x89PNG\r\n\x1a\n" or len(payload)<8000:
        raise AssertionError("Broken or blank PNG: "+str(path))
    w,h=struct.unpack(">II",payload[16:24])
    if w<300 or h<170:
        raise AssertionError("Invalid PNG dimensions")
    return {"filename":Path(path).name,"bytes":len(payload),
            "width":w,"height":h,"sha256":hashlib.sha256(payload).hexdigest()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--html",required=True)
    ap.add_argument("--out",default="dist/V24_CHARACTER_ANIMATION_SAMPLES")
    opt=ap.parse_args()
    html=Path(opt.html).resolve()
    out=Path(opt.out).resolve();out.mkdir(parents=True,exist_ok=True)
    errors=[];frames=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1440,"height":1040},
                              accept_downloads=True,device_scale_factor=1)
        page.on("pageerror",lambda error:errors.append(str(error)))
        try:
            page.goto(html.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function(
                "() => document.querySelector('#v24-scene')?.options.length>0",
                timeout=40000)
            page.locator('[data-page="animation-v24"]').click()
            page.wait_for_function(
                "() => !document.querySelector('#page-animation-v24').hidden")
            page.locator("#v24-playhead").fill("45")
            prior=out/"V24_BEFORE.png";after=out/"V24_AFTER.png"
            page.locator("#v24-before").screenshot(path=str(prior))
            page.locator("#v24-after").screenshot(path=str(after))
            frames.extend([png_info(prior),png_info(after)])
            if prior.read_bytes()==after.read_bytes():
                raise AssertionError("V24 procedural movement did not change Canvas")

            page.locator("#v24-style").select_option("cinematic")
            page.locator("#v24-stride").fill("95")
            page.locator("#v24-weight").fill("92")
            page.locator("#v24-anticipation").fill("94")
            page.locator("#v24-recoil").fill("88")
            page.locator("#v24-followThrough").fill("91")
            page.locator("#v24-save").click()
            adjusted=out/"V24_HIGH_MOTION.png"
            page.locator("#v24-after").screenshot(path=str(adjusted))
            frames.append(png_info(adjusted))
            if adjusted.read_bytes()==after.read_bytes():
                raise AssertionError("V24 sliders did not change animated pose")

            before_reload=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V24')||'null');
             return {version:p?.version,episodes:p?.episodes?.length,
                     characters:p?.characters?.length,scene:p?.episodes?.[0]?.scenes?.[0],
                     story:p?.episodes?.[0]?.storyV20,
                     quality:p?.characters?.[0]?.qualityV23,
                     lore:p?.lore};
            }""")
            if before_reload["version"]!=24 or before_reload["episodes"]<1:
                raise AssertionError("Project not saved as V24")
            if before_reload["scene"]["motionV24"]["stride"]!=95:
                raise AssertionError("Stride value not saved")
            for field in ("visualV21","actingV22","combatV17","motionV24"):
                if field not in before_reload["scene"]:
                    raise AssertionError("Prior scene data absent: "+field)
            if not before_reload["story"] or not before_reload["quality"]:
                raise AssertionError("V20 story or V23 character settings lost")

            page.reload(wait_until="load")
            page.wait_for_function(
                "() => document.querySelector('#v24-scene')?.options.length>0")
            restored=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V24')||'null');
             return {version:p?.version,scene:p?.episodes?.[0]?.scenes?.[0],
                     story:p?.episodes?.[0]?.storyV20,
                     quality:p?.characters?.[0]?.qualityV23,lore:p?.lore};
            }""")
            for name in ("scene","story","quality","lore"):
                if restored[name]!=before_reload[name]:
                    raise AssertionError("Save/reload modified "+name)

            page.locator('[data-page="animation-v24"]').click()
            with page.expect_download(timeout=60000) as d:
                page.locator("#v24-sheet").click()
            sheet=out/"V24_FOUR_MOTION_FRAMES.png"
            d.value.save_as(sheet);frames.append(png_info(sheet))
            for tab in ("story-v20","visual-v21","acting-v22",
                        "character-v23","impact-v19"):
                page.locator('[data-page="'+tab+'"]').click()
                page.wait_for_function(
                    "tab => !document.querySelector('#page-'+tab).hidden",
                    arg=tab)
            if errors:
                raise AssertionError("Browser JS errors: "+" | ".join(errors[:8]))
            (out/"V24_BROWSER_QA.json").write_text(json.dumps(
                {"frames":frames,"version":24,"persisted":restored["scene"]["motionV24"],
                 "errors":errors},ensure_ascii=False,indent=2),encoding="utf-8")
            print("V24 CHROMIUM PASS / A-B Canvas / sliders / save-reload / 4 PNGs")
        finally:
            browser.close()

if __name__=="__main__":main()
