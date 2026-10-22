#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.1 browser acceptance: actual visual evidence and Russian dialogue.
A passing visual-difference test is NOT an artistic-quality sign-off.
"""
import argparse,base64,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser()
    for key in ("html","project","out"):
        parser.add_argument("--"+key,required=True)
    x=parser.parse_args()
    data=json.loads(Path(x.project).read_text(encoding="utf-8"))
    assert data["v501Visual"]["enabled"] is True
    assert data["v501Visual"]["language"]=="ru-RU"
    allscenes=sum((ep["scenes"] for ep in data["episodes"][:2]),[])
    assert len(allscenes)==12
    for scene in allscenes:
        v=scene["audioV36"]["voice"]
        seg=v["segmentsV501"]
        assert len(seg)==2 and seg[0]["role"]!=seg[1]["role"],seg
        assert v["languageV501"]=="ru-RU"
        assert all(len(s["text"])>20 and any("а"<=c.lower()<="я" for c in s["text"])
                   for s in scene["lines"]),scene["title"]
        assert v["embeddedV47"].startswith("data:audio/mpeg;base64,")
        assert v["waveV47"] and seg[0]["end"]<seg[1]["start"]
    out=Path(x.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page(viewport={"width":1440,"height":1000})
        page.on("pageerror",lambda e:errors.append(str(e)))
        try:
            page.goto(Path(x.html).resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => window.v501Visual && window.v50FinalQA",
                                   timeout=30000)
            page.evaluate("""project => {
              localStorage.setItem('AI_ANIME_FACTORY_V50',JSON.stringify(project));
            }""",data)
            page.reload(wait_until="load")
            page.wait_for_function("() => window.v501Visual && window.v50FinalQA",
                                   timeout=30000)
            conf=page.evaluate("""() => ({
              profiles:window.v501Visual.profiles,
              enabled:window.v50FinalQA.currentProject().v501Visual.enabled,
              audit:window.v50FinalQA.audit()})""")
            assert conf["enabled"] and len(conf["profiles"])>=6,conf
            assert not conf["audit"]["errors"],conf["audit"]["errors"][:6]
            for ep_id in (0,1):
                for scene_id in range(6):
                    blob=page.evaluate("""([ei,si]) => {
                       const ep=window.v50FinalQA.currentProject().episodes[ei];
                       const start=ep.scenes.slice(0,si).reduce((t,s)=>t+s.duration-.35,0);
                       return window.v501Visual.frame(ei,start+ep.scenes[si].duration/2);
                    }""",[ep_id,scene_id])
                    image=base64.b64decode(blob.split(",",1)[1])
                    assert image.startswith(b"\x89PNG\r\n\x1a\n")
                    (out/f"episode_{ep_id+1:02d}_scene_{scene_id+1:02d}.png").write_bytes(image)
            ep0=data["episodes"][0]
            # For choreography, never accept 9 identical battle frames.
            fightStart=sum(s["duration"]-.35 for s in ep0["scenes"][:2])
            duration=ep0["scenes"][2]["duration"]
            digests=[]
            for i,fraction in enumerate((.04,.15,.26,.37,.48,.59,.70,.81,.93)):
                blob=page.evaluate("""([start,t]) => window.v501Visual.frame(0,start+t)""",
                        [fightStart,duration*fraction])
                pixels=base64.b64decode(blob.split(",",1)[1])
                (out/f"battle_beat_{i+1:02d}.png").write_bytes(pixels)
                digests.append(hashlib.sha256(pixels).hexdigest())
            assert len(set(digests))>=8,"Combat choreography is visually frozen"
            if errors:raise AssertionError("V50.1 browser JS: "+"; ".join(errors[:8]))
            result={"schema":"AIAnimeFactory/V501/BrowserPilotQA/1",
                    "status":"TECHNICAL_PASS_ARTISTIC_REVIEW_REQUIRED",
                    "russianLanguage":"ru-RU","voicesWithSpeakerSegments":12,
                    "firstTwoEpisodesWithSceneFrames":2,"sceneFrameCount":12,
                    "combatFrames":9,"distinctCombatFrameDigests":len(set(digests)),
                    "characters":conf["profiles"],"v50DeepErrorCount":0,
                    "professionalArtworkApproved":False,
                    "naturalHumanDubApproved":False,
                    "commercialRightsApproved":False}
            (out/"V501_BROWSER_QA.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),
                                                      encoding="utf-8")
            print("V50.1 BROWSER VERIFIED:",json.dumps(result,ensure_ascii=False))
        finally:browser.close()
if __name__=="__main__":main()
