#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actual Chromium V25 dual-actor combat, A/B frames, persistence, exports."""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path
from playwright.sync_api import sync_playwright

def png_check(path):
    data=Path(path).read_bytes()
    if len(data)<8000 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("Missing/non-PNG rendered output: "+str(path))
    w,h=struct.unpack(">II",data[16:24])
    if w<250 or h<140:raise AssertionError("Too small Canvas")
    return {"name":path.name,"width":w,"height":h,"bytes":len(data),
            "sha256":hashlib.sha256(data).hexdigest()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--html",required=True)
    parser.add_argument("--out",default="dist/V25_COMBAT_SAMPLES")
    cfg=parser.parse_args()
    html=Path(cfg.html).resolve()
    out=Path(cfg.out).resolve();out.mkdir(parents=True,exist_ok=True)
    frames=[];errors=[]
    with sync_playwright() as browser_tool:
        browser=browser_tool.chromium.launch(headless=True,
          args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1450,"height":1050},
                              accept_downloads=True,device_scale_factor=1)
        page.on("pageerror",lambda e:errors.append(str(e)))
        try:
            page.goto(html.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => document.querySelector('#v25-scene')?.options.length>0",timeout=35000)
            page.locator('[data-page="combat-v25"]').click()
            page.wait_for_function("() => !document.querySelector('#page-combat-v25').hidden")
            # The first option is a real fight scene; every option is filtered to kind=fight.
            selected=page.locator("#v25-scene").input_value()
            ep_i,sc_i=(int(v) for v in selected.split(':'))
            page.locator("#v25-position").fill("42")
            before=out/"V25_V24_BEFORE.png";after=out/"V25_DUEL_AFTER.png"
            page.locator("#v25-before").screenshot(path=str(before))
            page.locator("#v25-after").screenshot(path=str(after))
            frames.extend([png_check(before),png_check(after)])
            if before.read_bytes()==after.read_bytes():
                raise AssertionError("Choreography does not alter dual-actor Canvas")

            page.locator("#v25-style").select_option("duel")
            for key,value in (("distance","92"),("footwork","92"),
                              ("guard","90"),("response","92"),("rhythm","94")):
                page.locator("#v25-"+key).fill(value)
            page.locator("#v25-save").click()
            improved=out/"V25_STRONG_DUEL.png"
            page.locator("#v25-after").screenshot(path=str(improved))
            frames.append(png_check(improved))
            if after.read_bytes()==improved.read_bytes():
                raise AssertionError("Choreography settings did not affect the fight frame")

            stored=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V25')||'null');
             return {version:p?.version,characters:p?.characters,
                     lore:p?.lore,episodes:p?.episodes};
            }""")
            if stored["version"]!=25 or not stored["episodes"] or len(stored["characters"])<2:
                raise AssertionError("Project did not save in V25")
            ep=stored["episodes"][ep_i];sc=ep["scenes"][sc_i]
            if sc["kind"]!="fight" or sc["choreographyV25"]["distance"]!=92:
                raise AssertionError("Combat scene setting not saved")
            for key in ("storyV20",):
                if key not in ep:raise AssertionError("Missing "+key)
            for key in ("motionV24","actingV22","visualV21","combatV17"):
                if key not in sc:raise AssertionError("Missing "+key)
            if not stored["characters"][0].get("qualityV23"):
                raise AssertionError("V23 character detail lost")

            page.reload(wait_until="load")
            page.wait_for_function("() => document.querySelector('#v25-scene')?.options.length>0")
            restored=page.evaluate("""() => {
             const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V25')||'null');
             return {version:p?.version,characters:p?.characters,lore:p?.lore,episodes:p?.episodes};
            }""")
            if stored!=restored:
                raise AssertionError("V25 JSON roundtrip changed story, actors, or choreography")

            page.locator('[data-page="combat-v25"]').click()
            with page.expect_download(timeout=60000) as download:
                page.locator("#v25-sheet").click()
            sheet=out/"V25_FOUR_COMBAT_FRAMES.png"
            download.value.save_as(sheet);frames.append(png_check(sheet))
            for tab in ("story-v20","visual-v21","acting-v22",
                        "character-v23","animation-v24","impact-v19"):
                page.locator('[data-page="'+tab+'"]').click()
                page.wait_for_function(
                    "tab => !document.querySelector('#page-'+tab).hidden",arg=tab)
            if errors:raise AssertionError("Chromium JS errors: "+"; ".join(errors[:8]))
            (out/"V25_BROWSER_QA.json").write_text(json.dumps({
                "frames":frames,"selected_fight":[ep_i,sc_i],
                "saved_version":stored["version"],"errors":errors},
                ensure_ascii=False,indent=2),encoding="utf-8")
            print("V25 CHROMIUM PASS: paired fighter Canvas, controls, V19–V24 persistence, PNG")
        finally:browser.close()

if __name__=="__main__":main()
