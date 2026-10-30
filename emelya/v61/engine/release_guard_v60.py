"""Fail-closed release gate: only fresh Chromium captures for the current release.
  Usage: python engine/release_guard_v60.py --screens /path/screens --sites /path/sites
  Does NOT imply pixel-perfect reference reconstruction or Windows acceptance.
"""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
from PIL import Image
from design_autopilot import source_contract,MODES


def filehash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_release(root,shots,sites,previous=None):
 root=Path(root);shots=Path(shots);sites=Path(sites)
 report={'version':'V61','source_contract':source_contract(root),'screens':[], 'sites':[], 'failures':[], 'notes':['Browser screenshots are separate from artistic concept images','Windows 10 and HTTPS not accepted by this gate']}
 if not report['source_contract']['pass']:report['failures']+=report['source_contract']['errors']
 for mode in MODES:
  site=sites/mode
  if not site.is_dir():report['failures'].append('missing site '+mode);continue
  for needed in ['server.py','site.css','site.js','premium.css','art_direction_v61.css','project.json','DESIGN_AUTOPILOT_PLAN.json','APPROVED_ASSET_PROVENANCE.json','APPROVED_DESIGNS_V61/'+mode+'_PC.png']:
   if not (site/needed).exists():report['failures'].append('missing '+mode+'/'+needed)
  # Different creative banners only if owner has not replaced the banner.
  plan=json.loads((site/'DESIGN_AUTOPILOT_PLAN.json').read_text('utf8'))
  report['sites'].append({'mode':mode,'layout':plan['layout'],'files':len([p for p in site.rglob('*') if p.is_file()]),'plan_sha256':filehash(site/'DESIGN_AUTOPILOT_PLAN.json')})
  for dev in ['PC','MOBILE']:
   for page in ['HOME','CATALOG']:
    name=f'V61_{mode}_{dev}_{page}.png';file=shots/name
    if not file.is_file():report['failures'].append('missing screenshot '+name);continue
    with Image.open(file) as im:
     im.verify()
    with Image.open(file) as im:w,h=im.size
    is_device_correct=(w==1440 if dev=='PC' else w==390)
    same_as_reference=filehash(file)==filehash(root/'APPROVED_DESIGNS_V61'/f'{mode}_{dev if dev=="PC" else "MOBILE"}.png')
    old_file=Path(previous)/f'V60_1_{mode}_{dev}_{page}.png' if previous else None
    same_as_old=bool(old_file and old_file.exists() and filehash(file)==filehash(old_file))
    if not is_device_correct or same_as_reference or same_as_old or h<=600:report['failures'].append('invalid or stale screen '+name)
    if page=='HOME':
     preview=root/'previews'/'premium'/(mode+'.png' if dev=='PC' else mode+'-mobile.png')
     if not preview.is_file() or filehash(preview)!=filehash(file):report['failures'].append('stale factory premium preview '+mode+'/'+dev)
    report['screens'].append({'name':name,'width':w,'height':h,'sha256':filehash(file),'render_source':'Chromium HTML/CSS/JS','not_concept':not same_as_reference,'not_previous_release':not same_as_old,'pass':is_device_correct and not same_as_reference and not same_as_old and h>600})
 report['success']=not report['failures'] and len(report['screens'])==12 and len(report['sites'])==3
 return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--screens',required=True);parser.add_argument('--sites',required=True);parser.add_argument('--previous');parser.add_argument('--output');args=parser.parse_args()
 r=verify_release(Path(__file__).resolve().parent.parent,args.screens,args.sites,args.previous)
 if args.output:Path(args.output).write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8')
 print(json.dumps({'success':r['success'],'screens':len(r['screens']),'failed':r['failures']},ensure_ascii=False))
 raise SystemExit(0 if r['success'] else 1)