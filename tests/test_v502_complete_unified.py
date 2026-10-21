#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real V50.2 FULL-SOURCE Chromium checks: 13 JPEG, 6 episodes, source canon,
12 scenes, 10 motion beats, illustrated/fallback toggle. Technical QA only.
"""
import argparse,base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser()
    for key in ("html","out"):parser.add_argument("--"+key,required=True)
    a=parser.parse_args()
    dest=Path(a.out).resolve();dest.mkdir(parents=True,exist_ok=True)
    script=Path(a.html).resolve()
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=[
            "--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])
        page=browser.new_page(viewport={"width":1280,"height":780})
        page.on("pageerror",lambda e:errors.append(str(e)))
        try:
            page.goto(script.as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("""() =>
              window.v502Motion && window.v502CleanCutsQA && window.v50FinalQA""",
              timeout=45000)
            page.wait_for_function(
                "() => window.v502CleanCutsQA.loaded()===13",timeout=45000)
            state=page.evaluate("""() => {
              const p=window.v50FinalQA.currentProject();
              return {eps:p?.episodes?.length,
                canon:p?.pilotProductionV50?.originalV50ProjectSha256,
                actor:p?.characters?.map(a=>a.id),
                rig:p?.v502MotionRig?.enabled,
                clean:p?.v502CleanCuts?.enabled,
                art:p?.v502Art?.enabled,
                director:p?.v502Director?.enabled,
                images:window.v502CleanCutsQA.loaded(),
                failed:window.v502CleanCutsQA.failed(),
                errors:window.v50FinalQA.audit().errors};
            }""")
            assert state["eps"]>=6 and len(state["canon"])==64,state
            assert state["rig"] and state["art"] and state["clean"] and state["director"],state
            assert state["images"]==13 and state["failed"]==0,state
            assert not state["errors"],state["errors"][:10]
            assert {"hero","lover","friend","rival","enemy"}.issubset(state["actor"]),state
            proj=page.evaluate("() => window.v50FinalQA.currentProject()")
            shots=[];actual=set()
            for ei in (0,1):
                episode=proj["episodes"][ei]
                assert len(episode["scenes"])==6
                for si,scene in enumerate(episode["scenes"]):
                    assert scene.get("pilotV50") and len(scene.get("lines",[]))==2
                    clip=scene["audioV36"]["voice"]
                    assert clip["embeddedV47"].startswith("data:audio/mpeg;base64,")
                    assert len(clip["segmentsV501"])==2
                    begin=sum(float(s["duration"])-.35 for s in episode["scenes"][:si])
                    t=begin+float(scene["duration"])*(
                        .72 if scene["kind"]=="fight" else .42)
                    image=page.evaluate(
                        "([i,t])=>window.v502Motion.sceneFrame(i,t,640)",[ei,t])
                    binary=base64.b64decode(image.split(",",1)[1])
                    assert binary.startswith(b"\x89PNG\r\n\x1a\n")
                    digest=hashlib.sha256(binary).hexdigest()
                    actual.add(digest)
                    (dest/f"ep{ei+1:02d}_scene{si+1:02d}.png").write_bytes(binary)
                    shots.append({"episode":ei+1,"scene":si+1,"sha256":digest})
            assert len(actual)==12,"12 different scene compositions expected"
            beats=[]
            ep=proj["episodes"][0]
            offset=sum(float(sc["duration"])-.35 for sc in ep["scenes"][:2])
            for n,f in enumerate((.06,.16,.24,.37,.49,.59,.70,.74,.84,.96)):
                t=offset+float(ep["scenes"][2]["duration"])*f
                src=page.evaluate(
                    "([i,t])=>window.v502Motion.sceneFrame(i,t,640)",[0,t])
                binary=base64.b64decode(src.split(",",1)[1])
                shot_image=Image.open(io.BytesIO(binary)).convert("RGB")
                center=shot_image.crop((180,90,470,265))
                brightness=sum(ImageStat.Stat(center).mean)/3
                # A fully opaque fade previously produced empty shot_03
                # (old center mean 10). Fail on a blank transition.
                assert brightness>25,(n,f,round(brightness,1),"black frame on cut")
                beats.append(hashlib.sha256(binary).hexdigest())
                (dest/f"fight_{n:02d}.png").write_bytes(binary)
            assert len(set(beats))>=9,"Fight animation not moving enough"
            # Check a visually identifiable portrait actually changes after
            # disabling CLEAN CUTS, and restore the original toggle.
            time=sum(float(s["duration"])-.35 for s in ep["scenes"][:3])
            time+=ep["scenes"][3]["duration"]*.4
            original=page.evaluate(
                "([e,t])=>window.v502Motion.sceneFrame(e,t,640)",[0,time])
            page.evaluate("() => window.v502CleanCutsQA.setEnabled(false)")
            fallback=page.evaluate(
                "([e,t])=>window.v502Motion.sceneFrame(e,t,640)",[0,time])
            page.evaluate("() => window.v502CleanCutsQA.setEnabled(true)")
            assert original!=fallback,"CLEAN CUTS has no effect / failed fallback"
            assert not errors,errors[:8]
            info={"schema":"AIAnimeFactory/V502/UnifiedBrowserQA/1",
                  "status":"TECHNICAL_PASS_REQUIRES_ARTISTIC_REVIEW",
                  "completeSeasonEpisodes":state["eps"],"originalCanonSHA":state["canon"],
                  "actorIDs":state["actor"],"jpegCount":state["images"],
                  "twoPilotEpisodes":True,"sceneScreenshots":len(shots),
                  "uniqueSceneScreenshots":len(actual),"fightShots":len(beats),
                  "differentFightFrames":len(set(beats)),
                  "rollbackSwitchTest":"PASS",
                  "humanArtApproved":False,"humanVoiceApproved":False,
                  "rightsVerified":False,"clips":shots}
            (dest/"V502_COMPLETE_BROWSER_QA.json").write_text(json.dumps(
                info,ensure_ascii=False,indent=2),encoding="utf-8")
            print("V50.2 REPRODUCIBLE BROWSER QA PASS:",len(actual),
                  "unique scenes and",len(set(beats)),"fight shots; 13 JPEG; canon intact")
        finally:browser.close()

if __name__=="__main__":main()
