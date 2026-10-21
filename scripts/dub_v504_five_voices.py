#!/usr/bin/env python3
"""V50.4 Russian 5-cast pilot: Piper Denis/Akira and Dmitri/Ren;
Silero v5_5_ru kseniya/Miyu, xenia/Saira, aidar/Archon.
PRIVATE, NON-COMMERCIAL ANIMATIC. Silero is CC BY-NC-SA.
Lip cues are estimated from letters/speech durations, NOT forced alignment.
"""
from __future__ import annotations
import argparse,base64,copy,hashlib,json,math,subprocess,tempfile,wave
from pathlib import Path
import numpy as np
import torch

PIPER={'Акира':'denis','Рэн':'dmitri'}
SILERO={'Мию':'kseniya','Сайра':'xenia','Архонт':'aidar'}
ROLE={'Акира':'hero','Рэн':'ren','Мию':'miyu','Сайра':'saira','Архонт':'archon'}
SR=24000
def call(argv,stdin=None):
 p=subprocess.run(list(map(str,argv)),input=stdin,capture_output=True,timeout=240)
 if p.returncode:raise RuntimeError(str(argv[:5])+' '+p.stderr.decode(errors='replace')[-800:])
 return p.stdout
def convert(buf,rate):
 data=np.asarray(buf,dtype='<f4')
 if rate!=SR:
  raw=call(['ffmpeg','-loglevel','error','-f','f32le','-ar',rate,'-ac',1,'-i','pipe:0',
      '-f','f32le','-ar',SR,'-ac',1,'pipe:1'],data.tobytes())
  data=np.frombuffer(raw,dtype='<f4').copy()
 if len(data)<SR*.2 or float(np.sqrt(np.mean(data*data)))<.003:
  raise ValueError('Empty or silent voice')
 return data
def say_piper(binary,model,text,folder):
 output=folder/'voice.wav';output.unlink(missing_ok=True)
 call([binary,'--model',model,'--output_file',output],(text+'\n').encode())
 with wave.open(str(output)) as r:
  if r.getnchannels()!=1 or r.getsampwidth()!=2:raise ValueError('Piper format mismatch')
  rate=r.getframerate();samples=np.frombuffer(r.readframes(r.getnframes()),dtype='<i2').astype('<f4')/32768
 return convert(samples,rate)
def say_silero(model,speaker,text):
 with torch.inference_mode():a=model.apply_tts(text=text,speaker=speaker,sample_rate=SR)
 return convert(a.detach().cpu().numpy() if hasattr(a,'detach') else a,SR)
def encode(audio):
 out=call(['ffmpeg','-loglevel','error','-f','f32le','-ar',SR,'-ac',1,'-i','pipe:0',
         '-codec:a','libmp3lame','-b:a','64k','-f','mp3','pipe:1'],audio.astype('<f4').tobytes())
 return 'data:audio/mpeg;base64,'+base64.b64encode(out).decode()
def envelope(audio):
 hop=SR//50
 rms=np.array([np.sqrt(np.mean(x*x)) for x in (audio[j:j+hop] for j in range(0,len(audio),hop))])
 norm=max(.008,float(np.quantile(rms,.97)))
 return [round(float(min(1,x/norm)),3) for x in rms]
def lip_shapes(text,begin,length,speaker):
 # Syllabic estimate from written Russian, not exact acoustic alignment.
 tags=[]
 for ch in text.lower():
  if ch in 'аыя':tags.append(('A',1.2))
  elif ch in 'оё':tags.append(('O',1.2))
  elif ch in 'эеи':tags.append(('I',1.2))
  elif ch in 'ую':tags.append(('U',1.2))
  elif ch in 'пбмвф':tags.append(('M',.65))
  elif ch in 'жшщчсз':tags.append(('E',.7))
  elif ch.isalpha():tags.append(('C',.55))
  elif ch==' ':tags.append(('REST',.3))
 if not tags:return []
 total=sum(w for _,w in tags);pos=begin;out=[]
 for shape,weight in tags:
  end=pos+length*weight/total
  out.append({'start':round(pos,4),'end':round(end,4),'shape':shape,'speaker':speaker})
  pos=end
 return out
def process_scene(scene,ei,si,binary,models,silero,folder):
 lines=scene['lines']
 if len(lines)!=2:raise ValueError('Expected exactly two lines')
 voice=scene['audioV36']['voice'];offset=float(voice.get('offset',.25))
 samples=[];labels=[]
 for ln in lines:
  who=ln['speaker']
  if who in PIPER:
   k=PIPER[who];audio=say_piper(binary,models[k],ln['text'],folder);tag='PIPER_'+k.upper()
  elif who in SILERO:
   k=SILERO[who];audio=say_silero(silero,k,ln['text']);tag='SILERO_'+k.upper()
  else:raise ValueError('Unknown actor '+who)
  if len(audio)/SR>18:raise ValueError('Speech too long: '+who)
  samples.append(audio);labels.append(tag)
 gap=int(.35*SR);size=max(int(scene['duration']*SR),round(offset*SR)+sum(map(len,samples))+gap+int(.75*SR))
 if size/SR>27:raise ValueError('Scene too long, human director must split')
 mix=np.zeros(size-round(offset*SR),dtype='<f4');pos=0;spans=[];cues=[];vis=[]
 for ln,audio,tag in zip(lines,samples,labels):
  end=pos+len(audio)
  mix[pos:end]=audio
  start=round(pos/SR,4);stop=round(end/SR,4)
  ln['start']=round(offset+start,4);ln['duration']=round(len(audio)/SR,4)
  role=ROLE[ln['speaker']]
  spans.append({'role':role,'start':start,'end':stop,'sourceV504':tag})
  cues.append({'start':ln['start'],'end':round(offset+stop,4),
               'speaker':ln['speaker'],'text':ln['text']})
  vis.extend(lip_shapes(ln['text'],ln['start'],ln['duration'],role))
  pos=end+gap
 voice.update({'embeddedV47':encode(mix),'waveV47':envelope(mix),'sampleRateV47':50,
               'offset':offset,'segmentsV501':spans,'durationV47':round(len(mix)/SR,4),
               'visemesV504':vis,'name':f'V504_e{ei:02d}_s{si:02d}.mp3',
               'actingStatusV501':'NONCOMMERCIAL_NEURAL_TEST_NOT_HUMAN_PERFORMANCE',
               'phonemeAlignedV504':False,'rightsCheckedV504':False})
 scene['subtitlesV37']={'cues':cues};scene['duration']=round(size/SR,4)
 scene['v504Voice']={'sources':labels,'exactLipAlignment':False,
                      'naturalActorPerformanceApproved':False}
 return {'episode':ei,'scene':si,'duration':scene['duration'],'sources':labels,'cues':len(cues)}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--project',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 ap.add_argument('--piper',required=True)
 ap.add_argument('--models-dir',type=Path,required=True)
 ap.add_argument('--silero',type=Path,required=True)
 ap.add_argument('--samples',type=Path)
 ap.add_argument('--episodes',default='1,2')
 args=ap.parse_args()
 if args.project.resolve()==args.out.resolve():raise ValueError('Never overwrite original')
 origin=args.project.read_bytes();project=json.loads(origin)
 assert len(project['episodes'])==6
 before=[[(x['speaker'],x['text']) for s in ep['scenes'] for x in s['lines']] for ep in project['episodes']]
 models={}
 for v in ('denis','dmitri'):
  model=args.models_dir/f'ru_RU-{v}-medium.onnx'
  cfg=Path(str(model)+'.json')
  if not model.is_file() or model.stat().st_size<30000000 or not cfg.is_file():raise FileNotFoundError(model)
  meta=json.loads(cfg.read_text());assert meta['dataset']==v and meta['language']['code']=='ru_RU'
  models[v]=model
 if args.silero.stat().st_size<20000000:raise ValueError('Silero .pt too small')
 torch.set_num_threads(2)
 silero=torch.package.PackageImporter(str(args.silero)).load_pickle('tts_models','model')
 silero.to(torch.device('cpu'))
 selected={int(i) for i in args.episodes.split(',')}
 rows=[]
 with tempfile.TemporaryDirectory() as td:
  folder=Path(td)
  for ei,ep in enumerate(project['episodes'],1):
   if ei not in selected:continue
   for si,scene in enumerate(ep['scenes'],1):
    r=process_scene(scene,ei,si,args.piper,models,silero,folder)
    rows.append(r);print('DONE',r,flush=True)
  if args.samples:
   args.samples.mkdir(parents=True,exist_ok=True)
   for who,txt in {'Мию':'Ты не один. Я запишу всё, что важно для нас.',
                   'Сайра':'Оружие опусти. Сначала защити остальных.',
                   'Архонт':'Цена твоей силы будет выше, чем ты думаешь.'}.items():
    a=say_silero(silero,SILERO[who],txt)
    with wave.open(str(args.samples/(SILERO[who]+'.wav')),'wb') as f:
     f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR)
     f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
 after=[[(x['speaker'],x['text']) for s in ep['scenes'] for x in s['lines']] for ep in project['episodes']]
 if before!=after or args.project.read_bytes()!=origin:raise RuntimeError('Original text/file mutated')
 labels=[a for r in rows for a in r['sources']]
 if 'SILERO_KSENIYA' not in labels or 'SILERO_XENIA' not in labels:
  raise ValueError('Both female cast voices must be synthesized')
 project['v504FiveCast']={'status':'NONCOMMERCIAL_STORYBOARD_ONLY',
  'voicesUsed':sorted(set(labels)),'testedScenes':len(rows),'sourceSHA256':hashlib.sha256(origin).hexdigest(),
  'humanPerformanceApproved':False,'exactPhonemeSync':False,'artApproved':False,
  'commercialRightsApproved':False}
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
 (args.out.parent/'V504_VOICE_QA.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 print('V504 SUBTITLE/SCRIPT QA DONE',len(rows),'scenes')
if __name__=='__main__':main()
