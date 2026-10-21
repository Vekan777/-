#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build FULL existing V19–V50.2 editor + optional storyboard for episodes 3–6.
Only additive JS on top of reproducible V50.2. Old projects preserve prior flow.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'anime-factory/v50_2/build_complete_v502.py'
ART=ROOT/'anime-factory/v50_2/season_stage_v502.js'
MARKER='/* END V50.2 REPRODUCIBLE ART AND MOTION */'

def build(project=None):
    if not BASE.is_file() or not ART.is_file():
        raise FileNotFoundError('Requires full GitHub V50.2 builder and story-stage JS')
    spec=importlib.util.spec_from_file_location('v502_complete_for_season',BASE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    data=None
    if project:
        data=json.loads(Path(project).read_text(encoding='utf-8'))
        if data.get('seasonScriptV502',{}).get('newScriptedScenes')!=24:
            raise ValueError('Need exactly 24 additional V50.2 season scenes')
        if not data.get('v502SeasonStage',{}).get('enabled'):
            raise ValueError('Enable V502 season stage only in working project JSON')
    html,meta=mod.build(project)
    if html.count(MARKER)!=1:raise RuntimeError('Missing V50.2 art/motion insertion anchor')
    html=html.replace(MARKER,MARKER+'\n'+ART.read_text(encoding='utf-8')+
                      '\n/* END SEASON 03–06 STORY STAGE */',1)
    if 'window.v502SeasonStageQA' not in html:raise RuntimeError('Story-stage loader missing')
    return html,meta

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--project',type=Path)
    cli.add_argument('--out',required=True,type=Path)
    cli.add_argument('--selftest',action='store_true')
    a=cli.parse_args()
    html,meta=build(a.project)
    if a.selftest:
        print('PASS additive season stage bytes',len(html.encode()),'13 existing images')
        return
    dest=a.out.resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html,encoding='utf-8')
    print('V50.2 SIX EPISODE STORY STUDIO',dest,len(html.encode()),
          hashlib.sha256(dest.read_bytes()).hexdigest(),meta['artCount'])
if __name__=='__main__':main()