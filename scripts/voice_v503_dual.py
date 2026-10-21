#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Anime Factory V50.3: actual two-model Russian Piper dubbing.
Non-destructive extension to the original V50.2 6-episode project.
Men: Akira -> Denis, Ren/Archon -> Dmitri. Female voices stay preview.
Speech is never silently cut: scene duration/subtitles move with samples.
"""
import argparse,hashlib,json,tempfile
from pathlib import Path
import numpy as np
import upgrade_ru_voice_v502 as audio

MAP={'Акира':'denis','Рэн':'dmitri','Архонт':'dmitri'}
CAST=audio.CAST
RATE=audio.SR

def handle(scene,voices,piper,scene_key):
    lines=scene['lines']
    conf=scene['audioV36']['voice']
    old=audio.decode(conf['embeddedV47'])
    spans=conf['segmentsV501']
    if len(lines)!=2 or len(spans)!=2:raise ValueError('Unscripted '+scene_key)
    samples=[];sources=[]
    with tempfile.TemporaryDirectory() as tmp:
      for idx,(line,span) in enumerate(zip(lines,spans)):
        who=line['speaker']
        if who not in CAST or CAST[who]!=span['role']:
            raise ValueError('Speaker mismatch '+scene_key)
        model=MAP.get(who)
        if model in voices:
          # Original helper writes one WAV per call, serial here by design.
          pcm=audio.piper_speak(piper,voices[model],line['text'],Path(tmp))
          source='PIPER_'+model.upper()
        else:
          a=round(float(span['start'])*RATE)
          b=round(float(span['end'])*RATE)
          pcm=old[max(0,a):max(0,b)].copy()
          source='ESPEAK_PREVIEW_UNCHANGED'
        if len(pcm)<int(.15*RATE):raise ValueError('Empty speech '+scene_key)
        samples.append(pcm);sources.append(source)
    offset=float(conf.get('offset',.25))
    gap=.33;tail=.70
    # Original Russian text stays unchanged; extend visuals if necessary.
    length=max(float(scene['duration']),
       round(offset+sum(len(p) for p in samples)/RATE+gap+tail,3))
    if length>24:raise ValueError('Speech >24s; edit scene manually: '+scene_key)
    pcm=np.zeros(round((length-offset)*RATE),dtype=np.int16)
    position=0;new_spans=[];cues=[]
    for i,(line,source,part) in enumerate(zip(lines,sources,samples)):
      end=position+len(part)
      if end>len(pcm):raise ValueError('Scene overrun '+scene_key)
      pcm[position:end]=part
      begin=round(position/RATE,3);finish=round(end/RATE,3)
      line['start']=round(offset+begin,3)
      line['duration']=round(len(part)/RATE,3)
      new_spans.append({'role':CAST[line['speaker']],'start':begin,
                        'end':finish,'sourceV503':source})
      cues.append({'start':line['start'],'end':round(offset+finish,3),
                   'text':line['text'],'speaker':line['speaker']})
      position=end+round(gap*RATE)
    hop=RATE//50
    envelope=[float(np.sqrt(np.mean((pcm[n:n+hop].astype(float)/32768)**2)))
              for n in range(0,len(pcm),hop)]
    high=max(.007,float(np.percentile(envelope,97)))
    conf.update({'name':scene_key+'_V503_NEURAL_MALE.mp3',
                 'embeddedV47':audio.encode(pcm),
                 'waveV47':[round(min(1,e/high),3) for e in envelope],
                 'sampleRateV47':50,'offset':offset,
                 'durationV47':round(len(pcm)/RATE,3),
                 'segmentsV501':new_spans,
                 'actingStatusV501':'MALE_PIPER_FEMALE_PREVIEW_NOT_FINAL',
                 'phonemeAlignedV503':False,'rightsCheckedV503':False})
    scene['duration']=round(length,3)
    scene['subtitlesV37']={'cues':cues}
    scene['neuralV503']={'sources':sources,'sceneLength':length,
        'humanAudioReviewRequired':True}
    return sources,length

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--project',required=True,type=Path)
    a.add_argument('--out',required=True,type=Path)
    a.add_argument('--piper-bin',required=True)
    a.add_argument('--voices-dir',required=True,type=Path)
    a.add_argument('--episodes',default='1,2,3,4,5,6')
    a.add_argument('--only-scenes',default='')
    opts=a.parse_args()
    if opts.project.resolve()==opts.out.resolve():
        raise ValueError('Refusing source project overwrite')
    source=opts.project.read_bytes()
    project=json.loads(source)
    if len(project.get('episodes',[]))!=6:raise ValueError('6 episodes required')
    canon=project['pilotProductionV50']['originalV50ProjectSha256']
    pilot=project['seasonScriptV502']['originalFirstTwoEpisodesSha256']
    original_text=[[(line['speaker'],line['text']) for sc in ep['scenes']
                    for line in sc['lines']] for ep in project['episodes']]
    models={}
    for role in ('denis','dmitri'):
      model=opts.voices_dir/f'ru_RU-{role}-medium.onnx'
      config=Path(str(model)+'.json')
      if not model.is_file() or model.stat().st_size<30_000_000 or not config.is_file():
        raise FileNotFoundError('Voice model or config missing: '+str(model))
      cfg=json.loads(config.read_text(encoding='utf-8'))
      if cfg['language']['code']!='ru_RU' or cfg['dataset']!=role or cfg['audio']['sample_rate']!=22050:
        raise ValueError('Wrong model JSON: '+role)
      models[role]=model
    eps={int(x) for x in opts.episodes.split(',')}
    scenes={int(x) for x in opts.only_scenes.split(',')} if opts.only_scenes else None
    rows=[];num=0
    for ei,ep in enumerate(project['episodes'],1):
      if ei not in eps:continue
      for si,sc in enumerate(ep['scenes'],1):
        if scenes and si not in scenes:continue
        src,length=handle(sc,models,opts.piper_bin,f'E{ei:02d}_S{si:02d}')
        rows.append({'episode':ei,'scene':si,'seconds':length,'sources':src})
        num+=sum(x.startswith('PIPER') for x in src)
        print('V50.3 real Piper',ei,si,src,round(length,2),flush=True)
    if num==0:raise ValueError('No male voices were synthesized')
    current_text=[[(line['speaker'],line['text']) for sc in ep['scenes']
                   for line in sc['lines']] for ep in project['episodes']]
    assert original_text==current_text
    assert project['pilotProductionV50']['originalV50ProjectSha256']==canon
    assert project['seasonScriptV502']['originalFirstTwoEpisodesSha256']==pilot
    project['v503NeuralDub']={'status':'PARTIAL_MALE_NEURAL_PREVIEW',
      'maleNeuralLines':num,'scenesProcessed':len(rows),'femaleActorsStillEspeak':True,
      'phonemeAligned':False,'actorApproval':False,'rightsApproval':False,
      'sourceSha256':hashlib.sha256(source).hexdigest()}
    opts.out.parent.mkdir(parents=True,exist_ok=True)
    opts.out.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
    (opts.out.parent/'V503_VOICE_QA.json').write_text(
      json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    assert opts.project.read_bytes()==source
    print('PASS: real Piper, no changed dialogue, output',opts.out)
if __name__=='__main__':main()
