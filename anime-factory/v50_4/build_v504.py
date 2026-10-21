#!/usr/bin/env python3
"""V50.4 complete additive offline editor: six original episodes preserved;
five-cast Russian project gets opt-in layered face animation for episodes 1–2.
"""
import argparse,hashlib,importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'anime-factory/v50_2/build_acting_v502.py'
PATCH=Path(__file__).with_name('facial_layers_v504.js')
def build(project_path):
 spec=importlib.util.spec_from_file_location('anime_v502_base',BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 p=json.loads(Path(project_path).read_text(encoding='utf-8'))
 if len(p.get('episodes',[]))!=6 or not p.get('v504FiveCast'):
  raise ValueError('Expected 6-episode V50.4 five-cast project')
 if p.get('v504FiveCast',{}).get('commercialRightsApproved') is not False:
  raise ValueError('Never mislabel Silero as commercial-approved')
 p['v504Face']={'enabled':True,'exactLipSync':False,'artApproved':False}
 with tempfile.TemporaryDirectory() as t:
  temp=Path(t)/'temporary_copy.json'
  temp.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8')
  html,_=mod.build(temp)
 marker='/* END V50.2 ACTING PASS */'
 if html.count(marker)!=1:raise RuntimeError('Missing V50.2 acting insertion')
 html=html.replace(marker,marker+'\n'+PATCH.read_text(encoding='utf8')+
                   '\n/* END V50.4 FIVE-CAST FACIAL PREVIEW */',1)
 if 'window.v504FacialQA' not in html:raise RuntimeError('V50.4 not installed')
 return html,p
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--project',required=True)
 ap.add_argument('--out',required=True)
 ap.add_argument('--project-out')
 args=ap.parse_args()
 raw=Path(args.project).read_bytes()
 html,p=build(args.project)
 target=Path(args.out).resolve();target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(html,encoding='utf-8')
 if args.project_out:
  Path(args.project_out).write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
 if Path(args.project).read_bytes()!=raw:raise RuntimeError('Source project mutated')
 print('V50.4 unified HTML',target,len(html.encode()),hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
