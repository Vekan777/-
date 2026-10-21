#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real headless-browser preview, NOT professional art or phoneme-sync signoff."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,base64,hashlib,json
def main():
 a=argparse.ArgumentParser()
 for key in ("html","out"):a.add_argument("--"+key,required=True)
 args=a.parse_args()
 output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
 failures=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
  page=b.new_page(viewport={"width":1200,"height":850})
  page.on("pageerror",lambda e:failures.append(str(e)))
  page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=70000)
  page.wait_for_function("()=>window.v502ActingQA&&window.v502PerformanceQA&&window.v50FinalQA",timeout=40000)
  state=page.evaluate("""()=>({
    enabled:!!window.v50FinalQA.currentProject()?.v502Acting?.enabled,
    eps:window.v50FinalQA.currentProject()?.episodes?.length,
    art:window.v502CleanCutsQA.loaded(),
    errors:window.v50FinalQA.audit().errors})""")
  assert state["eps"]==6 and state["art"]==13 and not state["errors"],state
  page.evaluate("()=>window.v502ActingQA.setEnabled(true)")
  hashes=[];records=[]
  for ei in range(6):
   scenes=page.evaluate("(e)=>window.v50FinalQA.currentProject().episodes[e].scenes",ei)
   for si in (0,1,2,3,4,5):
    t=sum(float(x["duration"])-.35 for x in scenes[:si])
    t+=scenes[si]["duration"]*(.705 if si==2 else (.32 if si%2==0 else .61))
    pic=page.evaluate("([e,t])=>window.v502ActingQA.frame(e,t,640)",[ei,t])
    raw=base64.b64decode(pic.split(",",1)[1])
    assert raw.startswith(bytes.fromhex("89504e470d0a1a0a"))
    hashval=hashlib.sha256(raw).hexdigest()
    hashes.append(hashval)
    name=f"EP{ei+1}_SC{si+1}.png";(output/name).write_bytes(raw)
    records.append(dict(episode=ei+1,scene=si+1,sha256=hashval))
  assert len(set(hashes))>=30
  # Earlier builds falsely passed because subtitle variations changed hashes,
  # although all six fights displayed the same reused battle illustration.
  from PIL import Image
  battle_center=[]
  for ei in range(1,7):
   image=Image.open(output/f"EP{ei}_SC3.png").convert("RGB")
   center=image.crop((40,38,600,300))
   battle_center.append(hashlib.sha256(center.tobytes()).hexdigest())
  assert len(set(battle_center))>=4,("Same still reused for all fights",battle_center)
  ep=page.evaluate("()=>window.v50FinalQA.currentProject().episodes[0]")
  t1=ep["scenes"][0]["duration"]*.29;t2=ep["scenes"][0]["duration"]*.65
  first=page.evaluate("([e,t])=>window.v502ActingQA.frame(e,t,640)",[0,t1])
  second=page.evaluate("([e,t])=>window.v502ActingQA.frame(e,t,640)",[0,t2])
  assert first!=second,"Speaker coverage didn't change"
  assert page.evaluate("(t)=>window.v502ActingQA.speaker(0,0,t)",t1)=="Акира"
  assert page.evaluate("(t)=>window.v502ActingQA.speaker(0,0,t)",t2)=="Сайра"
  with_overlay=page.evaluate("([e,t])=>window.v502ActingQA.frame(e,t,640)",[0,t1])
  page.evaluate("()=>window.v502ActingQA.setEnabled(false)")
  without=page.evaluate("([e,t])=>window.v502ActingQA.frame(e,t,640)",[0,t1])
  assert with_overlay!=without,"Original fallback mode didn't restore"
  page.evaluate("()=>window.v502ActingQA.setEnabled(true)")
  usage=page.evaluate("()=>window.v502ActingQA.stats()")
  assert usage["closeups"]>=8,usage
  assert len(usage["variants"])>=4,usage
  assert not failures,failures[:5]
  qa={"status":"TECHNICAL_PASS_NOT_PHONEME_OR_HUMAN_ART_APPROVED",
       "fullEpisodes":6,"differentFrames":len(set(hashes)),
       "portraitsUsed":usage["variants"],
       "actingCoverage":"VOICE_AMPLITUDE_NOT_PHONEME_SYNC",
       "speakerAlternation":True,"battleStillPhotoReplacement":False,
       "disabledModeRestore":True,"humanActingApproved":False,
       "neuralVoiceVerified":False,"results":records}
  (output/"ACTING_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
  print("PASS V50.2 ACTING:",len(hashes),"real frames",
        len(usage["variants"]),"painted variants, off/on fallback")
  b.close()
if __name__=="__main__":main()
