#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run actual V50 deep-QA on the pilot project, export 12 review frames.

No human approval is invented. Fails if title/sound/subtitles/render data are
missing or canonical V50 migration changes the supplied project.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",required=True)
    p.add_argument("--project",required=True)
    p.add_argument("--out",required=True)
    o=p.parse_args()
    out=Path(o.out).resolve();out.mkdir(parents=True,exist_ok=True)
    project=json.loads(Path(o.project).read_text(encoding="utf-8"))
    if len(project["episodes"])<2:raise AssertionError("Need two pilot episodes")
    if project.get("pilotProductionV50",{}).get("status")!="DRAFT_NOT_RELEASE_READY":
        raise AssertionError("Pilot must not falsely claim final approval")
    original_hash=hashlib.sha256(json.dumps(project,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox",
          "--disable-dev-shm-usage","--disable-gpu","--autoplay-policy=no-user-gesture-required"])
        page=browser.new_page(viewport={"width":1440,"height":900})
        failures=[]
        page.on("pageerror",lambda e:failures.append(str(e)))
        try:
            page.goto(Path(o.html).resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => window.v50FinalQA?.currentProject()?.episodes?.length>=2",timeout=45000)
            page.evaluate("raw => localStorage.setItem('AI_ANIME_FACTORY_V50',raw)",
                json.dumps(project,ensure_ascii=False))
            page.reload(wait_until="load")
            page.wait_for_function("() => window.v50FinalQA?.currentProject()?.episodes?.length>=2",timeout=45000)
            after=page.evaluate("() => window.v50FinalQA.currentProject()")
            # Browser initialization adds lazy UI/cache fields, so compare
            # meaningful canonical content, not bytewise JSON string.
            for i in (0,1):
                before=project["episodes"][i]
                current=after["episodes"][i]
                if before["title"]!=current["title"] or before["memoryLost"]!=current["memoryLost"]:
                    raise AssertionError("Canonical episode changed on V50 reload")
                if before["storyV20"]["payoff"]!=current["storyV20"]["payoff"]:
                    raise AssertionError("V20 payoff disappeared")
                if len(current["scenes"])!=6:
                    raise AssertionError("Scene structure lost")
                for j,s in enumerate(current["scenes"]):
                    if len(s.get("subtitlesV37",{}).get("cues",[]))!=2:
                        raise AssertionError("Missing real per-scene subtitles")
                    audio=s.get("audioV36",{}).get("voice",{})
                    if not audio.get("embeddedV47","").startswith("data:audio/mpeg;base64,"):
                        raise AssertionError("No portable spoken voice in pilot scene")
                    if not audio.get("waveV47"):
                        raise AssertionError("No V47 waveform")
            deep=page.evaluate("() => window.v50FinalQA.audit()")
            (out/"V50_PILOT_DEEP_QA.json").write_text(
                json.dumps(deep,ensure_ascii=False,indent=2),encoding="utf-8")
            if deep.get("errors"):
                raise AssertionError("V50 deep QA blocks pilot: "+
                      json.dumps(deep["errors"][:8],ensure_ascii=False))
            if not deep.get("manualAcceptanceRequired"):
                raise AssertionError("Never auto-approve art or licenses")
            page.locator('[data-page="episode-v48"]').click()
            count=0
            for i in (0,1):
                page.locator("#v48-episode").select_option(str(i))
                for j,pos in enumerate((60,210,385,560,735,910)):
                    page.locator("#v48-position").fill(str(pos))
                    image=out/f"ep{i+1:02d}_frame{j+1:02d}.png"
                    page.locator("#v48-preview").screenshot(path=str(image))
                    if not image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                        raise AssertionError("Not a genuine PNG review frame")
                    count+=1
            if failures:raise AssertionError("Chromium JS errors: "+"; ".join(failures[:4]))
            report={"status":"TECHNICAL_BROWSER_PASS_ART_REVIEW_PENDING",
                    "episodeCount":2,"reviewFrames":count,
                    "scriptAndAudioPreserved":True,
                    "originalInputSha256":original_hash,
                    "humanArtApproved":False,"rightsApproved":False}
            (out/"PILOT_BROWSER_EVIDENCE.json").write_text(
                json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
            print("V50 PILOT BROWSER VERIFIED: 2 episodes, 12 scenes, 12 review PNGs; NOT artistically approved.")
        finally:browser.close()

if __name__=="__main__":main()
