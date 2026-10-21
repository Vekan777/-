#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 additive editing/rendering layer over the audited V50.1 version."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V501=ROOT/"anime-factory/v50_1/build_cinematic_v501.py"
ART=Path(__file__).with_name("director_v502.js")
OUTPUT=ROOT/"dist/AI_Anime_Factory_V50_2_DIRECTOR_2D.html"
PANEL=r"""
<div class="card" id="v502-panel">
<h2>V50.2 · Кинорежиссура пилота и постановка боя</h2>
<p>Настоящие монтажные планы для двух первых серий: общий план,
крупный план каждого говорящего, реакция, деталь предательства,
слежение камеры и удар с отдачей в бою. Не меняет сюжет и старые
редакторы V19–V50.1. Это процедурная анимация, не финальная
рисованная аниме-серия; художественная приёмка по-прежнему обязательна.</p>
<label><input id="v502-enabled" type="checkbox" style="width:auto">
Использовать V50.2 для пилотных эпизодов 1–2</label>
<p class="muted">Отключение возвращает предыдущий V50.1 без потери сцен.
Для выразительных голосов можно заменить eSpeak записью на русском по
скрипту V50.2, но используйте лишь записи, на которые есть права.</p>
</div>
"""
def once(s,old,new):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"Expected exactly one V50.2 anchor {old[:70]!r}: {n}")
    return s.replace(old,new,1)
def build():
    spec=importlib.util.spec_from_file_location("v501_as_base_for_v502",V501)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    s=mod.build()
    for token in ("/* END V50.1 CINEMATIC */","function v501SceneDraw(",
                  "window.v501Visual","window.v50FinalQA","function v48Manifest("):
        if token not in s:raise RuntimeError("V50.1 base missing "+token)
    s=once(s,'<div class="card" id="v501-cinematic-settings">',
         '<div class="card" id="v501-cinematic-settings">') # check anchor, no mutation
    # The existing V50 QA page gets ONE additional visual control box.
    s=once(s,'<div class="card" id="v501-cinematic-settings">',
         '<div class="card" id="v501-cinematic-settings">'+PANEL)
    s=once(s,"/* END V50.1 CINEMATIC */",
         "/* END V50.1 CINEMATIC */\n"+
         ART.read_text(encoding="utf-8")+"\n/* END V50.2 DIRECTOR */")
    s=once(s,"v48Show();v49Show();v50Show();v501Settings();}",
           "v48Show();v49Show();v50Show();v501Settings();v502Settings();}")
    return s
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default=str(OUTPUT))
    parser.add_argument("--selftest",action="store_true")
    args=parser.parse_args()
    html=build()
    for token in ("v502Director=Object.freeze","function v502Scene(",
                  "id=\"v502-enabled\"","window.v501Visual","window.v50FinalQA"):
        if token not in html:raise RuntimeError("Output missing "+token)
    if args.selftest:
        print("V50.2 parent preserved; bytes",len(html.encode()),
              "sha256",hashlib.sha256(html.encode()).hexdigest())
        return
    dest=Path(args.output).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html,encoding="utf-8")
    print("V50.2 HTML",dest,len(html.encode()))
if __name__=="__main__":main()
