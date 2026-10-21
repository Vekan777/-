#!/usr/bin/env python3
"""V50.4: real Silero CIS Base Russian dubbing for five distinct characters.
Source story, dialogue and original project bytes are immutable.
Audio timing is measured from synthesized waveform frames; phonemes are NOT
forced-aligned and final art/acting/licensing approval is NOT asserted.
"""
from __future__ import annotations
import argparse,base64,copy,hashlib,json,math,subprocess,sys
from pathlib import Path
import numpy as np
RATE=24000
CAST={'Акира':'hero','Мию':'miyu','Рэн':'ren','Сайра':'saira','Архонт':'archon'}
VOICES={'Акира':'ru_roman','Мию':'ru_ekaterina','Рэн':'ru_dmitriy',
        'Сайра':'ru_karina','Архонт':'ru_eduard'}
def run(cmd,raw=None):
 p=subprocess.run(cmd,input=raw,capture_output=True,timeout=180)
 if p.returncode:raise RuntimeError(str(cmd[:5])+': '+p.stderr.decode(errors='replace')[-900:])
 return p.stdout
def as_mp3(a):
 raw=np.clip(a,-1,1).astype('<f4').tobytes()
 mp3=run(['ffmpeg','-hide_banner','-loglevel','error','-f','f32le',
          '-ar',str(RATE),'-ac','1','-i','pipe:0','-c:a','libmp3lame',
          '-b:a','64k','-f','mp3','pipe:1'],raw)
 return 'data:audio/mpeg;base64,'+base64.b64encode(mp3).decode()
def wave50(a):
 hop=RATE//50
 v=[float(np.sqrt(np.mean(piece.astype('float64')**2)))
    for i in range(0,len(a),hop) if len(piece:=a[i:i+hop])]
 ref=max(.007,float(np.percentile(v,97))) if v else .007
 return [round(min(1,x/ref),3) for x in v]
def real_silero(model):
 import torch
 torch.set_num_threads(2)
 if Path(model).stat().st_size<20000000:raise ValueError('Silero model missing')
 t=torch.package.PackageImporter(str(model)).load_pickle('tts_models','model')
 t.to(torch.device('cpu'))
 def synth(text,voice):
  out=t.apply_tts(text=text,speaker=voice,sample_rate=RATE)
  if hasattr(out,'detach'):out=out.detach().cpu().numpy()
  audio=np.asarray(out,dtype=np.float32).reshape(-1)
  if len(audio)<RATE*.15 or not np.isfinite(audio).all() or float(np.max(np.abs(audio)))<.005:
   raise ValueError('Invalid real speech '+voice)
  return audio
 return synth
def dub(src,dest,synth,episodes):
 path=Path(src).resolve();output=Path(dest).resolve()
 if path==output:raise ValueError('Cannot overwrite source')
 before=path.read_bytes();project=json.loads(before)
 if len(project.get('episodes',[]))!=6:raise ValueError('6 staged episodes required')
 canon=project['pilotProductionV50']['originalV50ProjectSha256']
 old2=project['seasonScriptV502']['originalFirstTwoEpisodesSha256']
 original=[[(l['speaker'],l['text']) for sc in ep['scenes'] for l in sc['lines']]
           for ep in project['episodes']]
 new=copy.deepcopy(project);rows=[];utterances=0
 for ei,ep in enumerate(new['episodes']):
  if ei+1 not in episodes:continue
  if len(ep['scenes'])!=6:raise ValueError('6 scenes missing')
  for si,scene in enumerate(ep['scenes']):
   if len(scene['lines'])!=2:raise ValueError('2 lines missing')
   recordings=[]
   for line in scene['lines']:
    if line['speaker'] not in VOICES:raise ValueError('Unknown actor')
    audio=synth(line['text'],VOICES[line['speaker']])
    recordings.append(np.asarray(audio,dtype=np.float32))
   gap=round(RATE*.33);duration_audio=sum(map(len,recordings))+gap
   offset=.25;minend=offset+duration_audio/RATE+.65
   scene_duration=round(max(float(scene['duration']),minend),3)
   if scene_duration>30:raise ValueError('Scene too long, re-edit by hand')
   audio=np.zeros(math.ceil((scene_duration-offset)*RATE),dtype=np.float32)
   cursor=0;segments=[];cues=[]
   for i,line in enumerate(scene['lines']):
    part=recordings[i];start=cursor;end=start+len(part)
    audio[start:end]=part
    s=round(start/RATE,3);e=round(end/RATE,3)
    segments.append({'role':CAST[line['speaker']],'start':s,'end':e,
                     'voiceV504':VOICES[line['speaker']]})
    line['start']=round(offset+s,3)
    line['duration']=round(len(part)/RATE,3)
    cues.append({'speaker':line['speaker'],'text':line['text'],
                 'start':line['start'],'end':round(offset+e,3)})
    cursor=end+gap;utterances+=1
   v=scene['audioV36']['voice']
   v.update({'embeddedV47':as_mp3(audio),'name':f'V504_E{ei+1:02d}_S{si+1:02d}.mp3',
       'gain':.95,'offset':offset,'segmentsV501':segments,
       'waveV47':wave50(audio),'sampleRateV47':50,
       'durationV47':round(len(audio)/RATE,3),'mouthEnabledV47':True,
       'languageV501':'ru-RU','phonemeAlignedV504':False,
       'actingStatusV501':'SILERO_CIS_BASE_DISTINCT_NEURAL_RU_NOT_HUMAN'})
   scene['duration']=scene_duration
   scene['subtitlesV37']={'cues':cues}
   scene['neuralV504']={'voices':[x['voiceV504'] for x in segments],
      'isPhonemeAligned':False,'humanVoiceApproved':False}
   rows.append({'episode':ei+1,'scene':si+1,'seconds':scene_duration,
                'voices':[x['voiceV504'] for x in segments]})
 now=[[(l['speaker'],l['text']) for sc in ep['scenes'] for l in sc['lines']]
      for ep in new['episodes']]
 if now!=original or new['pilotProductionV50']['originalV50ProjectSha256']!=canon or new['seasonScriptV502']['originalFirstTwoEpisodesSha256']!=old2:
  raise RuntimeError('Original canonical dialogue was changed')
 new['v504NeuralDub']={'status':'FIVE_NEURAL_VOICES_ART_REVIEW_PENDING','voices':VOICES,
      'scenes':len(rows),'utterances':utterances,'episodes':sorted(episodes),
      'sourceSHA256':hashlib.sha256(before).hexdigest(),'originalCanonSHA':canon,
      'phonemeAligned':False,'humanPerformanceApproved':False,'rightsReviewed':False}
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
 (output.parent/'V504_DUB_QA.json').write_text(
    json.dumps({'status':'TECHNICAL_NEURAL_ONLY','scenes':rows,'voices':VOICES,
    'utterances':utterances,'originalUnchanged':True,'phonemeAligned':False},
    ensure_ascii=False,indent=2),encoding='utf-8')
 assert before==path.read_bytes()
 print('V50.4 REAL RU',len(rows),'scenes',utterances,'utterances; no story mutation')
 return new
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--project',required=True)
 p.add_argument('--output',required=True)
 p.add_argument('--model',required=True)
 p.add_argument('--episodes',default='1,2,3,4,5,6')
 a=p.parse_args()
 eps={int(x) for x in a.episodes.split(',')}
 if not eps<=set(range(1,7)):raise ValueError('Only 1 through 6')
 dub(a.project,a.output,real_silero(a.model),eps)
if __name__=='__main__':main()
