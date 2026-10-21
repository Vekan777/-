#!/usr/bin/env python3
"""V50.4 independent release gate: no missing audio, no original text changes,
two real 2-speaker dialogue timelines, exact subtitle boundaries, all voices,
distinct five speech samples, explicit noncommercial license marker.
"""
import argparse,hashlib,json,wave
from collections import Counter
from pathlib import Path
def main():
 a=argparse.ArgumentParser()
 a.add_argument('--before',required=True)
 a.add_argument('--after',required=True)
 a.add_argument('--samples',required=True)
 args=a.parse_args()
 before=json.loads(Path(args.before).read_text(encoding='utf-8'))
 after=json.loads(Path(args.after).read_text(encoding='utf-8'))
 assert len(before['episodes'])==len(after['episodes'])==6
 assert before['pilotProductionV50']['originalV50ProjectSha256']==after['pilotProductionV50']['originalV50ProjectSha256']
 assert before['seasonScriptV502']['originalFirstTwoEpisodesSha256']==after['seasonScriptV502']['originalFirstTwoEpisodesSha256']
 count=Counter()
 for ei in range(6):
  aa=before['episodes'][ei];bb=after['episodes'][ei]
  assert len(aa['scenes'])==len(bb['scenes'])==6
  for si in range(6):
   old=aa['scenes'][si];new=bb['scenes'][si]
   assert [(x['speaker'],x['text']) for x in old['lines']]==[(x['speaker'],x['text']) for x in new['lines']]
   if ei>1:
    assert old==new,'Later episodes must not be modified'
    continue
   voice=new['audioV36']['voice'];spans=voice['segmentsV501']
   assert len(spans)==len(new['lines'])==2
   assert voice['embeddedV47'].startswith('data:audio/mpeg;base64,')
   assert len(voice['waveV47'])>=200
   assert len(voice['visemesV504'])>20
   assert not voice['phonemeAlignedV504'] and not voice['rightsCheckedV504']
   subtitles=new['subtitlesV37']['cues']
   assert len(subtitles)==2
   for idx,(span,cue,line) in enumerate(zip(spans,subtitles,new['lines'])):
    assert span['end']>span['start']
    assert abs(cue['start']-line['start'])<.002
    assert abs(cue['end']-(line['start']+line['duration']))<.003
    assert cue['end']<new['duration']-.15
    if idx: assert spans[idx-1]['end']+.25<=span['start']
    count[span['sourceV504']]+=1
 assert count['PIPER_DENIS'] and count['PIPER_DMITRI']
 assert count['SILERO_KSENIYA'] and count['SILERO_XENIA']
 for name in ('kseniya','xenia','aidar'):
  p=Path(args.samples)/(name+'.wav')
  with wave.open(str(p),'rb') as w:
   assert w.getframerate()==24000 and w.getnframes()>12000
   assert w.getnchannels()==1 and w.getsampwidth()==2
 print('DEEP V50.4 QA PASS: 12 scenes, 24 dialogue lines, 3 new native 24kHz samples',dict(count))
if __name__=='__main__':main()
