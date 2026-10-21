#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 cinematic cuts + original sound regression in real Chromium.
We test diversity/camera geometry and media structure, not art signoff.
"""
import argparse,base64,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    p=argparse.ArgumentParser()
    for key in ("html","project","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    data=json.loads(Path(a.project).read_text(encoding="utf-8"))
    assert data["v502Director"]["enabled"] and not data["v502Director"]["approval"]
    assert data["v501Visual"]["language"]=="ru-RU"
    assert len(data["episodes"])>=2
    for episode in data["episodes"][:2]:
        for scene in episode["scenes"]:
            assert scene.get("pilotV50")
            for kind in ("voice","music","fx"):
                s=scene["audioV36"][kind]
                assert s.get("embeddedV47","").startswith("data:audio/mpeg;base64,")
                assert float(s["gain"])>0 and float(s["gain"])<=1
            assert scene["audioV36"]["voice"]["segmentsV501"]
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
        page=browser.new_page(viewport={"width":1300,"height":900})
        page.on("pageerror",lambda x:errors.append(str(x)))
        try:
            page.goto(Path(a.html).resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => window.v502Director && window.v501Visual && window.v50FinalQA")
            page.evaluate("""p=>localStorage.setItem('AI_ANIME_FACTORY_V50',JSON.stringify(p))""",data)
            page.reload(wait_until="load")
            page.wait_for_function("() => window.v502Director && window.v501Visual && window.v50FinalQA")
            checks=page.evaluate("""() => ({
                enabled:window.v50FinalQA.currentProject().v502Director.enabled,
                allVersions:['v35Frame','v48Manifest','v50AuditProject','v502Director'].map(
                   n=>typeof window[n]!=='undefined'),
                errors:window.v50FinalQA.audit().errors})""")
            assert checks["enabled"] and all(checks["allVersions"]),checks
            assert not checks["errors"],checks["errors"][:8]
            rows=[];digests=[]
            for episode in range(2):
                for scene in range(6):
                    sc=data["episodes"][episode]["scenes"][scene]
                    times=(.08,.33,.57,.86)
                    starts=sum(s["duration"]-.35 for s in data["episodes"][episode]["scenes"][:scene])
                    for phase,fraction in enumerate(times):
                        t=float(sc["duration"])*fraction
                        blob=page.evaluate("""([e,t])=>window.v502Director.frame(e,t)""",
                                           [episode,starts+t])
                        payload=base64.b64decode(blob.split(",",1)[1])
                        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
                        digest=hashlib.sha256(payload).hexdigest()
                        digests.append(digest)
                        shot=page.evaluate("""([e,s,t]) => window.v502Director.active(e,s,t)""",
                                [episode,scene,t])
                        name=f"e{episode+1}_s{scene+1}_cut{phase+1}_{shot}.png"
                        (out/name).write_bytes(payload)
                        rows.append({"episode":episode+1,"scene":scene+1,
                                     "shot":shot,"sha256":digest,"frame":name})
            unique={r["shot"] for r in rows}
            required={"wide","hero","partner","over","detail","impact"}
            assert required.issubset(unique),sorted(unique)
            assert len(set(digests))>=40,"Too few distinct cinematic frames"
            assert len({x["sha256"] for x in rows[:4]})>=3,"No opening editorial cuts"
            assert not errors,errors[:8]
            qa={"status":"TECHNICAL_PASS_ART_REVIEW_PENDING",
                "version":"50.2-draft","screenCaptures":len(rows),
                "distinctFrameHashes":len(set(digests)),"shots":sorted(unique),
                "twoCompletePilotScriptsPreserved":True,
                "russianVoiceMode":data["v502Director"]["voiceMode"],
                "originalFoleyMusicSlots":24,
                "cues":rows,"humanArtApproved":False,
                "actorPerformancesApproved":False,"rightsApproved":False}
            (out/"V502_CAMERA_SOUND_QA.json").write_text(
              json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
            print("V50.2 BROWSER CAMERA QA PASS:",len(rows),
                  "actual frames",len(set(digests)),"distinct hashes",
                  "shot types",sorted(unique))
        finally:browser.close()
if __name__=="__main__":main()
