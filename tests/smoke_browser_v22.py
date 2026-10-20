#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chromium smoke QA for actual integrated V22 actor UI and Canvas PNG.
Requires Playwright in CI only; end users need no Playwright.
"""
from __future__ import annotations
import argparse
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright


def png_info(path):
    a=Path(path).read_bytes()
    if a[:8]!=b"\x89PNG\r\n\x1a\n" or len(a)<9000:
        raise AssertionError("Missing/empty PNG")
    w,h=struct.unpack(">II",a[16:24])
    if w<250 or h<150:
        raise AssertionError("Bad PNG dimensions")
    return {"name":Path(path).name,"width":w,"height":h,"bytes":len(a)}


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--html",required=True)
    arg.add_argument("--out",default="dist/V22_ACTING_SAMPLES")
    opt=arg.parse_args()
    html=Path(opt.html).resolve()
    out=Path(opt.out).resolve();out.mkdir(parents=True,exist_ok=True)
    errors=[];report={"source":html.name,"frames":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1360,"height":980},accept_downloads=True,device_scale_factor=1)
        page.on("pageerror",lambda e:errors.append(str(e)))
        try:
            page.goto(html.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => document.querySelector('#v22-scene')?.options.length > 0",timeout=30000)
            page.locator('[data-page="acting-v22"]').click()
            page.wait_for_function("() => !document.querySelector('#page-acting-v22').hidden",timeout=15000)

            page.locator("#v22-playhead").fill("75")
            before=out/"V22_BEFORE.png"
            page.locator("#v22-preview").screenshot(path=str(before))
            report["frames"].append(png_info(before))

            page.locator("#v22-faceStrength").fill("96")
            page.locator("#v22-breathing").fill("74")
            page.locator("#v22-save").click()
            page.locator("#v22-playhead").fill("50")
            page.locator("#v22-new").click()
            page.locator("#v22-hero").select_option("shocked")
            page.locator("#v22-partner").select_option("sad")
            page.locator("#v22-save-beat").click()
            page.locator("#v22-playhead").fill("75")
            after=out/"V22_AFTER_SHOCK.png"
            page.locator("#v22-preview").screenshot(path=str(after))
            report["frames"].append(png_info(after))
            if before.read_bytes()==after.read_bytes():
                raise AssertionError("V22 acting changes did not modify Canvas output")

            stored=page.evaluate("""() => {
              const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V22')||'null');
              const s=p?.episodes?.[0]?.scenes?.[0];
              return {version:p?.version, episodes:p?.episodes?.length,
                      v22:s?.actingV22, hasV21:!!s?.visualV21, hasV20:!!p?.episodes?.[0]?.storyV20};
            }""")
            if stored["version"]!=22 or stored["episodes"]<1:
                raise AssertionError("V22 project version/persistence failed: "+str(stored))
            if not stored["v22"] or not stored["v22"].get("beats"):
                raise AssertionError("V22 acting key was not persisted")
            if stored["v22"]["beats"][-1]["hero"]!="shocked":
                raise AssertionError("V22 selected expression not saved")
            report["storage"]=stored

            with page.expect_download(timeout=60000) as d:
                page.locator("#v22-contact").click()
            contact=out/"V22_FOUR_ACTING_FRAMES.png"
            d.value.save_as(contact)
            report["frames"].append(png_info(contact))

            page.locator('[data-page="visual-v21"]').click()
            page.wait_for_function("() => !document.querySelector('#page-visual-v21').hidden",timeout=10000)
            page.locator('[data-page="story-v20"]').click()
            page.wait_for_function("() => !document.querySelector('#page-story-v20').hidden",timeout=10000)
            page.locator('[data-page="impact-v19"]').click()
            page.wait_for_function("() => !document.querySelector('#page-impact-v19').hidden",timeout=10000)
            if errors:
                raise AssertionError("Browser JavaScript errors: "+str(errors))
        except Exception:
            page.screenshot(path=str(out/"V22_BROWSER_FAILURE.png"),full_page=True)
            raise
        finally:
            browser.close()
    report["errors"]=errors
    (out/"V22_BROWSER_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V22 BROWSER SMOKE PASS: PNG frames",len(report["frames"]),"V22 saved, V19/V20/V21 tabs available")


if __name__=="__main__":main()
