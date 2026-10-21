#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 independent visual QA across 6 episodes: 18 real Chromium PNGs,
original first 2 story SHA, distinct action beats, toggle and audio guards.
This is technical smoke QA, not artistic approval.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,io
from pathlib import Path
from PIL import Image,ImageStat
from playwright.sync_api import sync_playwright
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--html',required=True,type=Path)
 p.add_argument('--project',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args()
 source=json.loads(a.project.read_text(encoding='utf-8'))
 assert len(source['episodes'])>=6 and source['seasonScriptV502']['newScriptedScenes']==24
 a.out.mkdir(parents=True,exist_ok=True)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
    '--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
  page=browser.new_page()
  page.on('pageerror',lambda e:errors.append(str(e)))
  try:
   page.goto(a.html.resolve().as_uri(),wait_until='load',timeout=60000)
   page.wait_for_function("""() =>
     window.v502PerformanceQA && window.v502SeasonStageQA && window.v502CleanCutsQA &&
     window.v502CleanCutsQA.loaded()===13""",timeout=45000)
   state=page.evaluate("""() => ({
     enabled:window.v502PerformanceQA.enabled(),
     count:window.v50FinalQA.currentProject().episodes.length,
     original:window.v50FinalQA.currentProject().seasonScriptV502.originalFirstTwoEpisodesSha256,
     loaded:window.v502CleanCutsQA.loaded(),
     errors:window.v50FinalQA.audit().errors })""")
   assert state['count']>=6 and state['enabled'] and state['loaded']==13,state
   assert state['original']==source['seasonScriptV502']['originalFirstTwoEpisodesSha256'],state
   assert not state['errors'],state['errors'][:6]
   rows=[];hashes=set()
   for ei in range(6):
    ep=source['episodes'][ei]
    assert len(ep['scenes'])==6
    for si in (0,2,4):
     sc=ep['scenes'][si]
     assert sc['pilotV50'] and len(sc['lines'])==2
     for track in ('voice','music','fx'):
      assert sc['audioV36'][track]['embeddedV47'].startswith('data:audio/mpeg;base64,')
     start=sum(float(s['duration'])-float(s.get('assemblyV35',{}).get('transition',.35))
               for s in ep['scenes'][:si])
     t=start+float(sc['duration'])*.70
     encoded=page.evaluate("([ei,t])=>window.v502PerformanceQA.frame(ei,t,640)",[ei,t])
     frame=base64.b64decode(encoded.split(',',1)[1])
     assert frame.startswith(b'\x89PNG\r\n\x1a\n')
     digest=hashlib.sha256(frame).hexdigest()
     assert digest not in hashes,(ei,si,'duplicate image')
     hashes.add(digest)
     light=sum(ImageStat.Stat(Image.open(io.BytesIO(frame)).convert('RGB')).mean)/3
     assert light>12,(ei,si,'black visual')
     name=f'ep{ei+1:02d}_scene{si+1:02d}.png'
     (a.out/name).write_bytes(frame)
     rows.append({'ep':ei+1,'scene':si+1,'digest':digest,'meanBrightness':round(light,2),
                  'file':name})
   t=sum(float(s['duration'])-.35 for s in source['episodes'][3]['scenes'][:2])+8.4
   page.evaluate('()=>window.v502PerformanceQA.setEnabled(false)')
   before=page.evaluate("t=>window.v502PerformanceQA.frame(3,t,640)",t)
   page.evaluate('()=>window.v502PerformanceQA.setEnabled(true)')
   after=page.evaluate("t=>window.v502PerformanceQA.frame(3,t,640)",t)
   assert before!=after,'Performance checkbox made no change'
   assert not errors,errors[:8]
   report={'schema':'AIAnimeFactory/V502/PerformanceTechnicalQA/1',
           'status':'TECHNICAL_PASS_HUMAN_ART_APPROVAL_PENDING',
           'sourceCanonSHA':state['original'],'scenes':rows,
           'jpegCount':13,'rollbackSwitchVerified':True,
           'artApproved':False,'naturalVoiceApproved':False,
           'fullEpisodesApproved':False}
   (a.out/'V502_PERFORMANCE_QA.json').write_text(
       json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
   print('V50.2 PERFORMANCE TECHNICAL PASS',len(rows),'different shots, 13 JPEG, 6 EP')
  finally:browser.close()
if __name__=='__main__':main()
