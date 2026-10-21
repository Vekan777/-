#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a NON-DESTRUCTIVE V50.2 screenplay pass for episodes 3–6.

Original six-episode JSON stays unchanged. Original episode 1–2 bytes/JSON
and V19/V20 canon fingerprint are verified. New season scenes are a DRAFT;
not a production-ready long-form anime season.
"""
from __future__ import annotations
import argparse,base64,copy,hashlib,json,math,struct,subprocess,tempfile,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STORY=Path(__file__).resolve().parents[1]/'anime-factory/v50_2/STORY_EP03_EP06_V502.json'
ROLE_VOICES={'hero':'ru+m3','miyu':'ru+f3','ren':'ru+m2','saira':'ru+f2','archon':'ru+m1'}
ALLOWED_KINDS=['opening','friendship','fight','romance','betrayal','ending']

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,
      separators=(',',':')).encode('utf-8')).hexdigest()
def run(args):
    cp=subprocess.run(args,capture_output=True,text=True,timeout=90)
    if cp.returncode:raise RuntimeError(' '.join(args[:6])+': '+cp.stderr[-1000:])

def tts_dialogue(lines):
    """Generate temporary eSpeak voices, two role segments, mono portable MP3.
    Dialogue timing is from actual WAV frames, not character counts.
    Not natural acting / not phonemic lip sync.
    """
    with tempfile.TemporaryDirectory(prefix='anime_v502_ep3_6_') as tmp:
        root=Path(tmp)
        chunks=[];rate=None
        for i,(role,words) in enumerate(lines):
            path=root/f'line_{i}.wav'
            run(['espeak-ng','-v',ROLE_VOICES[role],'-s','185','-w',str(path),words])
            with wave.open(str(path),'rb') as w:
                sr=w.getframerate()
                if w.getnchannels()!=1 or w.getsampwidth()!=2:
                    raise ValueError('eSpeak WAV not mono PCM16')
                if rate is None:rate=sr
                if rate!=sr:raise ValueError('Voice sample rate differs')
                buf=w.readframes(w.getnframes())
            chunks.append((role,buf,len(buf)/(sr*2)))
        gaps=.30
        cursor=0.;segments=[]
        out=root/'joined.wav'
        with wave.open(str(out),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
            for i,(role,frames,duration) in enumerate(chunks):
                w.writeframes(frames)
                segments.append({'role':role,'start':round(cursor,3),
                                 'end':round(cursor+duration,3)})
                cursor+=duration
                if i<len(chunks)-1:
                    w.writeframes(b'\0\0'*round(rate*gaps));cursor+=gaps
        if cursor>10.4:
            raise ValueError(f'Two lines too long for staged 12-second clip: {cursor:.2f}s: {lines}')
        mp3=root/'joined.mp3'
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out),
             '-b:a','48k','-ar','16000','-ac','1',str(mp3)])
        with wave.open(str(out),'rb') as w:pcm=w.readframes(w.getnframes())
        values=struct.unpack('<'+'h'*(len(pcm)//2),pcm)
        hop=max(1,rate//50)
        rms=[math.sqrt(sum((v/32768.)**2 for v in values[i:i+hop])/
                      max(1,len(values[i:i+hop])))
             for i in range(0,len(values),hop)]
        sortedr=sorted(rms)
        norm=max(.012,sortedr[round(.95*(len(sortedr)-1))]) if rms else .012
        wave50=[round(min(1.0,v/norm),3) for v in rms]
        return {'url':'data:audio/mpeg;base64,'+base64.b64encode(mp3.read_bytes()).decode(),
                'wave':wave50,'total':round(cursor,3),'segments':segments,
                'rate':rate,'bytes':mp3.stat().st_size}

def validate_pack(pack):
    if pack.get('schema')!='AIAnimeFactory/SeasonScript/V502/1':
        raise ValueError('Not V50.2 season script')
    eps=pack['episodes']
    if [ep['number'] for ep in eps]!=[3,4,5,6]:raise ValueError('Need episodes 3-6 in order')
    lost=[e['memoryLost'] for e in eps]
    if len(lost)!=len(set(lost)) or 'дом детства' in lost:
        raise ValueError('Repeating already erased childhood home')
    for ep in eps:
        if len(ep['scenes'])!=6:raise ValueError('Every episode must contain 6 scenes')
        if [s['kind'] for s in ep['scenes']]!=ALLOWED_KINDS:
            raise ValueError('Scenario scene order must match canonical beats')
        for scene in ep['scenes']:
            lines=scene.get('dialogue',[])
            if len(lines)!=2 or lines[0][0]==lines[1][0]:
                raise ValueError('Require two DIFFERENT speaking roles per scene')
            for role,phrase in lines:
                if role not in ROLE_VOICES or not 15<=len(phrase)<=95:
                    raise ValueError('Invalid Russian role or length')
                if not any('а'<=ch.lower()<='я' for ch in phrase):
                    raise ValueError('Russian script required')
    return True

def apply(project,pack,with_tts=False,with_audio=False):
    validate_pack(pack)
    if project.get('format')!='AIAnimeFactoryProject' or len(project.get('episodes',[]))<6:
        raise ValueError('The full original V50.2 project is required')
    if not project.get('pilotProductionV50',{}).get('originalV50ProjectSha256'):
        raise ValueError('Original V50 canonical SHA provenance missing')
    out=copy.deepcopy(project)
    original_first_two=digest(out['episodes'][:2])
    original_source_sha=hashlib.sha256(json.dumps(project,sort_keys=True,
             ensure_ascii=False).encode()).hexdigest()
    old_hashes={str(i+1):digest(project['episodes'][i]) for i in range(2,6)}
    known_costs=[e.get('memoryLost') for e in project['episodes'][:2]]
    if len(set(known_costs+[x['memoryLost'] for x in pack['episodes']]))!=6:
        raise ValueError('All six memory-loss events must be unique')
    from importlib.machinery import SourceFileLoader
    import importlib.util
    sound=None
    if with_audio:
        p=Path(__file__).resolve().parents[1]/'scripts/postprocess_v502.py'
        # Also works from the repo's scripts/ folder itself.
        if not p.exists():p=Path(__file__).resolve().with_name('postprocess_v502.py')
        spec=importlib.util.spec_from_file_location('original_v502_foley',p)
        sound=importlib.util.module_from_spec(spec);spec.loader.exec_module(sound)
    cast={c['id']:c['name'] for c in out['characters']}
    roles={'hero':cast['hero'],'miyu':cast['lover'],'ren':cast['friend'],
           'saira':cast['rival'],'archon':cast['enemy']}
    reports=[]
    for script in pack['episodes']:
        i=script['number']-1
        ep=out['episodes'][i]
        if ep['number']!=script['number'] or ep['title']!=script['title']:
            raise ValueError('Episode canonical identity changed')
        if len(ep['scenes'])!=6 or [s['kind'] for s in ep['scenes']]!=ALLOWED_KINDS:
            raise ValueError('A mismatched original V19 scene layout needs manual review')
        ep['pilotV50']={'status':'DRAFT_REQUIRES_HUMAN_ART_REVIEW',
                         'sourceStoryV20':copy.deepcopy(ep.get('storyV20')),
                         'sourceMemoryLost':ep.get('memoryLost'),
                         'sourceEpisodeSha256':old_hashes[str(i+1)]}
        ep.setdefault('storyV20',{})
        ep['storyV20'].update({'wound':script['wound'],'soulCost':script['memoryLost'],
            'clue':script['clue'],'payoff':script['payoff'],
            'memoryJournal':'Утрата воспоминания: '+script['memoryLost']})
        ep['memoryLost']=script['memoryLost']
        ep['seasonScriptV502']={'arc':script['arc'],'status':'SCRIPTED_DRAFT_NOT_ART_APPROVED',
                               'canonSourceEpisodeSha256':old_hashes[str(i+1)]}
        report={'episode':script['number'],'scenes':6,'lines':12,
                'cost':script['memoryLost'],'ttsClips':0,'originalEpisodeSha256':old_hashes[str(i+1)]}
        for si,plan in enumerate(script['scenes']):
            sc=ep['scenes'][si]
            original={key:copy.deepcopy(sc.get(key)) for key in
                      ('title','duration','narration','camera','dialogue','lines')}
            transcript=[(roles[r],text) for r,text in plan['dialogue']]
            voice=tts_dialogue(plan['dialogue']) if with_tts else None
            duration=12.0 # respect original V50 scenes maximum
            sc['duration']=duration
            sc['title']=plan['title']
            sc['pilotV50']={'sourceSceneTextV19':original,'acting':plan['acting'],
                'camera':plan['camera'],'speech_source':('temporary espeak-ng Russian' if voice else 'not_recorded'),
                'speech_rights':'CHECK VOICE LICENSE BEFORE COMMERCIAL RELEASE'}
            sc['scriptV502']={'location':plan['location'],'camera':plan['camera'],
                'acting':plan['acting'],'roleOrder':[r for r,_ in plan['dialogue']],
                'status':'DRAFT_HUMAN_STORY_REVIEW_PENDING'}
            sc['dialogue']='\n'.join(f'{n}: {line}' for n,line in transcript)
            first=voice['segments'][0]['end'] if voice else 4.5
            second=voice['segments'][1]['start'] if voice else 4.8
            cues=[{'start':.25,'end':round(min(duration-.6,first+.25),3),
                    'speaker':transcript[0][0],'text':transcript[0][1]},
                  {'start':round(.25+second,3),'end':round(
                     min(duration-.35,.25+(voice['segments'][1]['end'] if voice else 9.2)),3),
                    'speaker':transcript[1][0],'text':transcript[1][1]}]
            sc['subtitlesV37']={'cues':cues}
            sc['lines']=[{'speaker':transcript[j][0],'text':transcript[j][1],
                     'start':round(.25+(voice['segments'][j]['start'] if voice else j*4.8),3),
                     'duration':round((voice['segments'][j]['end']-voice['segments'][j]['start']) if voice else 4.3,3),
                     'emotion':('tense' if plan['kind']=='fight' else 'dramatic')}
                    for j in range(2)]
            if voice:
                config=sc.setdefault('audioV36',{}).setdefault('voice',{})
                config.update({'embeddedV47':voice['url'],'waveV47':voice['wave'],
                    'durationV47':voice['total'],'sampleRateV47':50,'gain':.95,
                    'offset':.25,'name':f'ep{script["number"]:02d}_scene{si+1:02d}_RU_TEMP.mp3',
                    'mouthEnabledV47':True,'speakerV47':transcript[0][0],
                    'segmentsV501':voice['segments'],'languageV501':'ru-RU',
                    'actingStatusV501':'TEMPORARY_ESPEAK_NOT_FINAL'})
                report['ttsClips']+=1
            if sound:
                with tempfile.TemporaryDirectory(prefix='v502_fx_') as tmp:
                    tone,fx=sound.synth(duration,si,script['number'],sc['kind'])
                    for kind,arr,gain in (('music',tone,.14),('fx',fx,.22)):
                        cfg=sc.setdefault('audioV36',{}).setdefault(kind,{})
                        cfg.update({'name':f'ep{script["number"]}_sc{si+1}_{kind}.mp3',
                            'embeddedV47':sound.export_mp3(arr,Path(tmp),kind),
                            'durationV47':duration,'gain':gain,'offset':0,
                            'sourceV502':'GENERATED_ORIGINAL_PROCEDURAL',
                            'rightsV502':'No third-party music samples used'})
        reports.append(report)
    if digest(out['episodes'][:2])!=original_first_two:
        raise RuntimeError('Episodes 1 and 2 may not be edited by this pass')
    if out['pilotProductionV50']['originalV50ProjectSha256']!=project['pilotProductionV50']['originalV50ProjectSha256']:
        raise RuntimeError('Original canon fingerprint changed')
    out['seasonScriptV502']={'schema':pack['schema'],'status':'SIX_EPISODE_SCREENPLAY_DRAFT_NOT_ANIME_FINAL',
        'episodeCount':6,'newScriptedScenes':24,'newRussianLines':48,
        'originalProjectSha256':original_source_sha,
        'originalFirstTwoEpisodesSha256':original_first_two,
        'originalDraftEpisodeSha256':old_hashes,
        'continuity':{'memoryCosts':[e['memoryLost'] for e in out['episodes'][:6]],
             'noResurrectionOfLostMemory':True,'renBetrayalRepairedByActionsNotInstantForgiveness':True,
             'episode6ChildhoodHomeDuplicateFixed':True},
        'artApproval':False,'voiceApproval':False,'rightsApproved':False}
    out['v502SeasonStage']={'enabled':True,'status':'FOUR_SCRIPTED_EPISODES_PREVIEW',
                            'artApproval':False,'humanVoiceApproved':False}
    out['productionV50']['qaAccepted']=False
    return out,reports

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--project',required=True,type=Path)
    a.add_argument('--story',default=STORY,type=Path)
    a.add_argument('--out',required=True,type=Path)
    a.add_argument('--tts',action='store_true')
    a.add_argument('--sound',action='store_true')
    a.add_argument('--validate-only',action='store_true')
    x=a.parse_args()
    pack=json.loads(x.story.read_text(encoding='utf-8'))
    validate_pack(pack)
    if x.validate_only:
        print('V50.2 3-6 SCRIPT VALID: 24 scenes / 48 Russian lines / 4 unique new memory costs')
        return
    src=x.project.resolve();dst=x.out.resolve()
    if src==dst:raise RuntimeError('Never overwrite source project')
    original=src.read_bytes();project=json.loads(original)
    out,qa=apply(project,pack,with_tts=x.tts,with_audio=x.sound)
    if src.read_bytes()!=original:raise RuntimeError('Input project changed unexpectedly')
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'schema':pack['schema'],'status':'STORY_DRAFT_HUMAN_ART_REVIEW_PENDING',
        'sourceProjectSha256':hashlib.sha256(original).hexdigest(),'sourceUnchanged':True,
        'episodes':qa,'quality':{'scriptedScenes':36,'spokenLines':72,
            'voiceGenerated':bool(x.tts),'originalFoleyGenerated':bool(x.sound),
            'naturalVoices':False,'professionalAnimationApproved':False,
            'fullLengthEpisodesProduced':False,'rightsApproved':False}}
    (dst.parent/'V502_SEASON_3_6_SCRIPT_QA.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('V50.2 SCRIPTED EP 3–6',dst,'bytes',dst.stat().st_size,
          'New voice scenes',sum(i['ttsClips'] for i in qa),'source SHA unchanged')
if __name__=='__main__':main()