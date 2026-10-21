#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.1 is an ADDITIVE visual production overlay on frozen V50.
All versions V19-V50 and their data are retained. No silent scene replacement.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"anime-factory/v50/build_final_v50.py"
ART=Path(__file__).with_name("cinematic_pilot_v501.js")
OUTPUT=ROOT/"dist/AI_Anime_Factory_V50_1_CINEMATIC_2D.html"
PANEL="""<div class="card" id="v501-cinematic-settings">
<h2>V50.1 · Кинографика и постановка двух серий</h2>
<p>Это улучшенный иллюстративный 2D-рендер для пилотов 1–2: шесть
различимых персонажей, особые костюмы и оружие, разные сцены,
девятифазный бой и сохранение канона V50. Работает только с JSON
из AI Anime Factory Pilot V50.1 и не меняет остальные проекты.</p>
<label><input type="checkbox" id="v501-enabled" style="width:auto">
Включить/выключить улучшенную рисовку V50.1</label>
<p class="muted">Это авторская процедурная 2D-иллюстрация, не
нейросетевая студийная покадровая анимация. Временный русский
голос eSpeak не заменяет работу актёра. Сохраните JSON перед экспортом.</p>
</div>"""
def once(text,old,new):
    n=text.count(old)
    if n!=1:raise ValueError(f"V50.1 expected exactly one patch anchor: {old[:90]!r}, got {n}")
    return text.replace(old,new,1)
def build():
    sp=importlib.util.spec_from_file_location("anime_v50_final_for_v501",BASE)
    mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    html=mod.build()
    for required in ("/* END V50 */","function v50AuditProject(","function v48Manifest(",
                     "function v46LayerMotion(","function v35Frame("):
        if required not in html:raise ValueError("V50 original missing "+required)
    html=once(html,'<section class="page" id="page-final-v50" hidden>',
        '<section class="page" id="page-final-v50" hidden>\n'+PANEL)
    html=once(html,"/* END V50 */","/* END V50 */\n"+
        ART.read_text(encoding="utf-8")+"\n/* END V50.1 CINEMATIC */")
    html=once(html,"v48Show();v49Show();v50Show();}",
        "v48Show();v49Show();v50Show();v501Settings();}")
    return html
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default=str(OUTPUT))
    p.add_argument("--selftest",action="store_true")
    args=p.parse_args()
    html=build()
    for text in ('id="v501-enabled"','v501Profiles=Object.freeze','function v501Battle(',
        'v501SceneDraw(','window.v50FinalQA','window.v501Visual','function v48Manifest('):
        assert text in html,text
    if args.selftest:
        print("V50.1 PRESERVES V19-V50 / HTML bytes",len(html.encode()),
              "SHA256",hashlib.sha256(html.encode()).hexdigest())
        return
    out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding="utf-8")
    print("V50.1 CINEMATIC HTML",out,len(html.encode()))
if __name__=="__main__":main()
