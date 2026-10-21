#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optional licensed Piper Russian-voice replacement (per character, per line).
Needs local piper binary and user-provided .onnx + .onnx.json voice.
Never rewrites source; preserves story and does not fake phoneme alignment.
"""
import argparse,base64,hashlib,json,subprocess,tempfile,wave
from pathlib import Path
import numpy as np

SR=22050
CAST={'Акира':'hero','Мию':'miyu','Рэн':'ren','Сайра':'saira','Архонт':'archon'}
def call(argv,data=None):
 p=subprocess.run(argv,input=data,capture_output=True,timeout=150)
 if p.returncode:raise RuntimeError(' '.join(map(str,argv[:4]))+
                                    ': '+p.stderr.decode(errors='replace')[-1000:])
 return p.stdout
def decode(encoded):
 if not encoded.startswith('data:audio/mpeg;base64,'):raise ValueError('Expected embedded MP3')
 data=base64.b64decode(encoded.split(',',1)[1])
 raw=call(['ffmpeg','-hide_banner','-loglevel','error','-i','pipe:0',
  '-f','s16le','-ac','1','-ar',str(SR),'pipe:1'],data)
 return np.frombuffer(raw,dtype='<i2').copy()
def encode(pcm):
 raw=call(['ffmpeg','-hide_banner','-loglevel','error','-f','s16le',
  '-ar',str(SR),'-ac','1','-i','pipe:0','-c:a','libmp3lame',
  '-b:a','64k','-f','mp3','pipe:1'],pcm.tobytes())
 return 'data:audio/mpeg;base64,'+base64.b64encode(raw).decode()
def piper_speak(binary,model,words,folder):
 target=folder/'voice.wav'
 call([binary,'--model',str(model),'--output_file',str(target)],
      (words.strip()+'\n').encode())
 with wave.open(str(target),'rb') as w:
  if (w.getframerate(),w.getnchannels(),w.getsampwidth())!=(SR,1,2):
   raise ValueError('Piper must output 22050Hz mono 16-bit PCM WAV')
  samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
 return samples
def scene_voice(scene,models,binary):
 v=scene['audioV36']['voice']
 segments=v['segmentsV501'];lines=scene['lines']
 if len(segments)!=2 or len(lines)!=2:raise ValueError('Expected 2 scripted lines')
 old=decode(v['embeddedV47']);offset=float(v.get('offset',0))
 output=np.zeros(max(1,round((float(scene['duration'])-offset)*SR)),dtype='<i2')
 changed=[]
 with tempfile.TemporaryDirectory() as folder:
  tmp=Path(folder)
  for idx,(line,span) in enumerate(zip(lines,segments)):
   role=CAST[line['speaker']]
   if span['role']!=role:raise ValueError('Speaker/canon role mismatch')
   start=max(0,round(span['start']*SR))
   end=min(len(output),round(span['end']*SR))
   if end<=start:raise ValueError('Empty voice interval')
   if role in models:
    samples=piper_speak(binary,models[role],line['text'],tmp)
    if len(samples)>end-start:
     raise ValueError(f'Neural line too long ({len(samples)/SR:.2f} seconds '
                      f'for {(end-start)/SR:.2f} seconds). Edit timing; do not clip.')
    changed.append(role)
   else:samples=old[start:min(end,len(old))]
   output[start:start+min(len(samples),end-start)]=samples[:end-start]
 if not changed:return False
 hop=SR//50
 env=[float(np.sqrt(np.mean((output[n:n+hop].astype(np.float64)/32768)**2)))
       for n in range(0,len(output),hop)]
 high=max(.008,float(np.percentile(env,97)))
 v.update({'embeddedV47':encode(output),'waveV47':[round(min(1,e/high),3) for e in env],
  'durationV47':round(len(output)/SR,3),'sampleRateV47':50,
  'neuralRolesV502':sorted(set(changed)),
  'actingStatusV501':'PIPER_NEURAL_RUSSIAN_PARTIAL_LICENSE_REVIEW_REQUIRED',
  'phonemeAlignedV502':False,'commercialRightsCheckedV502':False})
 return True
def main():
 a=argparse.ArgumentParser()
 a.add_argument('--project',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True)
 a.add_argument('--model',action='append',required=True,help='hero=/.../ru_RU-dmitri-medium.onnx')
 a.add_argument('--piper-bin',default='piper')
 a.add_argument('--episode',type=int,action='append')
 a.add_argument('--scene',type=int,action='append')
 x=a.parse_args()
 if x.project.resolve()==x.out.resolve():raise ValueError('Never modify original project')
 models={}
 for spec in x.model:
  role,_,path=spec.partition('=')
  p=Path(path).resolve()
  if role not in CAST.values() or not p.is_file() or not Path(str(p)+'.json').is_file():
   raise ValueError('Need role=model.onnx and matching .onnx.json: '+spec)
  models[role]=p
 orig=x.project.read_bytes();d=json.loads(orig)
 if len(d['episodes'])<6:raise ValueError('Expected all 6 episodes')
 canon=d['pilotProductionV50']['originalV50ProjectSha256']
 count=0
 for ei,ep in enumerate(d['episodes']):
  if x.episode and ei+1 not in x.episode:continue
  for si,sc in enumerate(ep['scenes']):
   if x.scene and si+1 not in x.scene:continue
   count+=scene_voice(sc,models,x.piper_bin)
 if count==0:raise RuntimeError('No speech matched configured role')
 if d['pilotProductionV50']['originalV50ProjectSha256']!=canon:
  raise RuntimeError('Original plot changed')
 d['v502NeuralVoice']={'status':'PARTIAL_LICENSE_REVIEW_REQUIRED',
  'roles':sorted(models),'scenesUpdated':count,'phonemeAligned':False,
  'commercialRightsVerified':False,'originalProjectSha256':hashlib.sha256(orig).hexdigest()}
 x.out.parent.mkdir(parents=True,exist_ok=True)
 x.out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 assert x.project.read_bytes()==orig
 print('V50.2 neural voice',count,'scenes, original untouched, licensing not approved')
if __name__=='__main__':main()
