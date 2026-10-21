#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep V50.2 story continuity checks, no bogus artistic sign-off."""
from __future__ import annotations
import argparse,copy,importlib.util,json
from pathlib import Path

def load_builder():
    path=Path(__file__).resolve().parents[1]/'scripts/expand_season_v502.py'
    spec=importlib.util.spec_from_file_location('v502_season',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def verify(project,source):
    m=load_builder()
    assert len(project['episodes'])==len(source['episodes'])==6
    assert m.digest(project['episodes'][:2])==m.digest(source['episodes'][:2])
    assert project['pilotProductionV50']==source['pilotProductionV50']
    assert project['seasonScriptV502']['newScriptedScenes']==24
    assert not project['productionV50']['qaAccepted']
    costs=[ep['memoryLost'] for ep in project['episodes']]
    assert len(costs)==len(set(costs))==6
    assert costs==['дом детства','первую встречу с Мию','имя старого наставника',
                   'свою клятву','голос матери','воспоминание о первой дружбе с Рэном']
    assert project['episodes'][5]['pilotV50']['sourceMemoryLost']=='дом детства'
    assert project['episodes'][5]['storyV20']['soulCost']==costs[5]
    for e in project['episodes'][2:]:
        assert all(e['storyV20'].get(k) for k in ('wound','clue','payoff','memoryJournal'))
        assert len(e['scenes'])==6 and all(s['kind']==kind for s,kind in
                   zip(e['scenes'],m.ALLOWED_KINDS))
        assert ('левое плечо' in e['storyV20']['wound'].lower() or
                'левого плеча' in e['storyV20']['wound'].lower())
        for s in e['scenes']:
            assert len(s['lines'])==2 and len(s['subtitlesV37']['cues'])==2
            assert s['pilotV50']['sourceSceneTextV19']['title']
            assert s['pilotV50']['sourceSceneTextV19']['narration']
            assert s['scriptV502']['status']=='DRAFT_HUMAN_STORY_REVIEW_PENDING'
            assert s['subtitlesV37']['cues'][0]['start']<s['subtitlesV37']['cues'][1]['start']
    dialogue=' '.join(x['text'] for ep in project['episodes'][2:] for s in ep['scenes'] for x in s['lines'])
    for clue in ('Совет','сестру','памяти','мост','песни','простить','клятва'):
        assert clue.lower() in dialogue.lower(),clue
    assert 'Из-за тебя' in dialogue and 'не отменяет вред' in dialogue
    assert project['seasonScriptV502']['artApproval'] is False
    assert project['seasonScriptV502']['voiceApproval'] is False
    assert project['seasonScriptV502']['rightsApproved'] is False
    return {'episodes':6,'newScenes':24,'newLines':48,'totalScenes':36,
            'totalLines':72,'uniqueMemoryCosts':6,'originalEp01Ep02Kept':True,
            'renMotivationKept':True,'automaticForgiveness':False,
            'artApproval':False,'voiceApproval':False}

def browser_frames(html,project,out):
    from playwright.sync_api import sync_playwright
    import base64,hashlib,os,shutil
    out.mkdir(parents=True,exist_ok=True)
    errors=[];shots=[];hashes=set()
    with sync_playwright() as pw:
        executable=os.environ.get('V502_CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        browser=pw.chromium.launch(headless=True,args=[
            '--no-sandbox','--disable-gpu','--disable-dev-shm-usage'],
            **({'executable_path':executable} if executable else {}))
        page=browser.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        try:
            page.goto(html.resolve().as_uri(),wait_until='load',timeout=60000)
            # The six-episode project contains 36 embedded sound scenes and
            # exceeds Chrome's ~5MB localStorage quota. It must be pre-embedded
            # into the fully offline HTML by build_season_v502.py.
            page.wait_for_function('() => window.v502Motion && window.v50FinalQA && window.v502SeasonStageQA',timeout=30000)
            page.wait_for_function('() => window.v502CleanCutsQA.loaded()===13',timeout=30000)
            state=page.evaluate("""() =>({episodeCount:window.v50FinalQA.currentProject().episodes.length,
                     stage:window.v502SeasonStageQA.active(),
                     sourceSHA:window.v50FinalQA.currentProject().seasonScriptV502?.originalFirstTwoEpisodesSha256,
                     errors:window.v50FinalQA.audit().errors})""")
            assert state['episodeCount']==6 and state['stage'] and not state['errors'],state
            assert state['sourceSHA']==project['seasonScriptV502']['originalFirstTwoEpisodesSha256'],state
            for ei in range(2,6):
                ep=project['episodes'][ei]
                for si,scene in enumerate(ep['scenes']):
                    start=sum(float(s['duration'])-.35 for s in ep['scenes'][:si])
                    time=start+float(scene['duration'])*.53
                    blob=page.evaluate('([ei,t])=>window.v502Motion.sceneFrame(ei,t,640)',[ei,time])
                    data=base64.b64decode(blob.split(',',1)[1])
                    assert data.startswith(b'\x89PNG\r\n\x1a\n')
                    dig=hashlib.sha256(data).hexdigest();hashes.add(dig)
                    name=f'EP{ei+1:02d}_SCENE{si+1:02d}.png'
                    (out/name).write_bytes(data)
                    shots.append({'episode':ei+1,'scene':si+1,'image':name,'sha256':dig})
            assert len(hashes)>=20,'Insufficient variety in 24 scene renders'
            assert not errors,errors[:6]
        finally:browser.close()
    data={'newPilotEpisodeCount':4,'sceneFrames':len(shots),
          'distinctFrameSha256':len(hashes),'humanArtApproved':False,
          'screenshots':shots}
    (out/'V502_EP03_EP06_BROWSER_QA.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--project',required=True,type=Path)
    p.add_argument('--html',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    source=json.loads(a.source.read_text(encoding='utf-8'))
    project=json.loads(a.project.read_text(encoding='utf-8'))
    result=verify(project,source)
    print('STORY QA PASS',json.dumps(result,ensure_ascii=False))
    if a.html:
        if not a.out:raise ValueError('--out required with --html')
        art=browser_frames(a.html,project,a.out)
        print('BROWSER EP 3–6 QA PASS',json.dumps({k:v for k,v in art.items() if k!='screenshots'},ensure_ascii=False))
if __name__=='__main__':main()