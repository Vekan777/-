#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V25 choreography over the original V19→V20→V21→V22→V23→V24 pipeline."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE24=ROOT/"anime-factory"/"v24"/"build_animation_v24.py"
ADDON=Path(__file__).with_name("combat_v25.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html")

PANEL=r"""
<section class="page" id="page-combat-v25" hidden>
<div class="card">
 <h2>V25 — Боевая хореография: дистанция, атака, защита</h2>
 <p class="muted">Движения двух актёров согласованы по событиям боя V17/V19: удар, блок, уклонение и промах остаются разными результатами. Сюжет и предыдущие сцены сохраняются.</p>
 <div class="grid">
  <div class="field"><label>Боевая сцена</label><select id="v25-scene"></select></div>
  <div class="field"><label>Постановочный стиль</label><select id="v25-style">
   <option value="balanced">Сбалансированный</option>
   <option value="duel">Дуэль</option>
   <option value="defensive">Осторожный бой</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v25-enabled" checked> Включить хореографию V25</label>
 <div class="grid">
  <div class="field"><label>Контроль дистанции: <span id="v25-distance-n">65</span>%</label><input type="range" id="v25-distance" min="0" max="100"></div>
  <div class="field"><label>Перемещение в бою: <span id="v25-footwork-n">75</span>%</label><input type="range" id="v25-footwork" min="0" max="100"></div>
  <div class="field"><label>Защитная стойка: <span id="v25-guard-n">72</span>%</label><input type="range" id="v25-guard" min="0" max="100"></div>
  <div class="field"><label>Реакция на удар: <span id="v25-response-n">70</span>%</label><input type="range" id="v25-response" min="0" max="100"></div>
  <div class="field"><label>Ритм и выпады: <span id="v25-rhythm-n">62</span>%</label><input type="range" id="v25-rhythm" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v25-preset">Пресет дуэли</button>
 <button class="accent" id="v25-save">Сохранить V25</button></div>
</div>
<div class="card">
 <h2>Два бойца, один момент: до и после</h2>
 <div class="grid">
  <div class="field"><label>V24 — базовая сцена</label>
    <canvas class="preview" id="v25-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V25 — согласованные движения</label>
    <canvas class="preview" id="v25-after" width="640" height="360"></canvas></div>
 </div>
 <label>Время боя <input type="range" id="v25-position" min="0" max="100" value="45"></label>
 <p id="v25-status" class="muted"></p>
 <div class="flex"><button id="v25-sheet">Скачать 4 кадра боя PNG</button>
 <button id="v25-plan">Скачать постановку боя TXT</button></div>
</div>
<div class="card">
 <h2>Проверка постановки</h2>
 <pre class="report" id="v25-qa" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
 <div class="note">2D-постановка без физической симуляции столкновений. Событие «попадание» берётся из исходной разметки V19/V17 — хореография не превращает промах в удар.</div>
</div>
</section>
"""

def once(text,old,new):
    count=text.count(old)
    if count!=1:
        raise ValueError("V25 expected unique marker, got "+str(count)+": "+repr(old[:95]))
    return text.replace(old,new,1)

def builder24():
    spec=importlib.util.spec_from_file_location("anime_v24_builder",BASE24)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if 'id="page-combat-v25"' in html or "function v25PairPose(" in html:
        raise ValueError("Already V25")
    for token in ("function v24Dynamics(","function v23HeadScale(",
                  "function v22Mood(","function v20CanonLines(","function combat17State("):
        if token not in html:raise ValueError("Previous integrated version missing "+token)
    html=once(html,'<button data-page="export">',
              '<button data-page="combat-v25">Хореография V25</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
              PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V24';",
              "const storageKey='AI_ANIME_FACTORY_V25';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:24,",
              "P={format:'AIAnimeFactoryProject',version:25,")
    html=once(html,
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V23')",
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V24')||localStorage.getItem('AI_ANIME_FACTORY_V23')")
    html=once(html,"if(page==='animation-v24')v24Show();",
              "if(page==='animation-v24')v24Show();if(page==='combat-v25')v25Show();")
    html=once(html,"v22Show();v23Show();v24Show();}",
              "v22Show();v23Show();v24Show();v25Show();}")
    html=once(html,
       "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA());",
       "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA());")
    # Pairwise position edit is shared by preview and exported frames.
    html=once(html,
       "const impactV19=impact19State(s,sec);impact19Modify(poses,impactV19,s);",
       "const impactV19=impact19State(s,sec);impact19Modify(poses,impactV19,s);v25PairPose(s,sec,poses,combat17,impactV19);")
    # Limb choreography applies only to the procedural rig. The art and PNG
    # production paths continue returning without these changes.
    html=once(html,
       "const v24=v24Dynamics(s,t,role);const d=rigDynamics(s,t,role),mood=",
       "const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role);const d=rigDynamics(s,t,role),mood=")
    html=once(html,
       "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p+v24.lean;",
       "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p+v24.lean+v25.lean;")
    html=once(html,
       "const leftElbow=[-54-attack*12,-118-block*14],leftHand=[-72-attack*17,-97-block*46];",
       "const leftElbow=[-54-attack*12,-118-block*14-v25.guard*14],leftHand=[-72-attack*17+v25.guard*8,-97-block*46-v25.guard*33];")
    html=once(html,
       "const rightElbow=[55+attack*17,-121-attack*42],rightHand=[76+attack*60-block*33+v24.handX,-104-attack*101-block*77-v24.handLift];",
       "const rightElbow=[55+attack*17,-121-attack*42],rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32,-104-attack*101-block*77-v24.handLift-v25.attack*25];")
    html=once(html,
       "g.rotate(lean);g.translate(v24.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob);",
       "g.rotate(lean);g.translate(v24.rootX+v25.step,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob);")
    html=once(html,"'AI ANIME FACTORY V24  •  CHARACTER ANIMATION'",
              "'AI ANIME FACTORY V25  •  COMBAT CHOREOGRAPHY'")
    html=once(html,
       "const files=[{name:'AI_Anime_Factory_V24_CHARACTER_ANIMATION.html',data:selfHTML()},",
       "const files=[{name:'AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html',data:selfHTML()},"+
       "{name:'V25_COMBAT_PLAN_RU.txt',data:v25Plan()},"+
       "{name:'V25_CHOREOGRAPHY.json',data:JSON.stringify(P.episodes.map(e=>"+
       "({number:e.number,scenes:e.scenes.filter(s=>s.kind==='fight').map(s=>"+
       "({title:s.title,choreographyV25:v25Options(s)}))})),null,2)},")
    html=once(html,"'AI_Anime_Factory_V24_CHARACTER_ANIMATION_Offline.html'",
              "'AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY_Offline.html'")
    html=once(html,
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<24)migrated.version=24;return migrated;}",
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<25)migrated.version=25;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
       "localStorage.getItem('AI_ANIME_FACTORY_V24')||"+
       "localStorage.getItem('AI_ANIME_FACTORY_V23')||")
    html=once(html,anchor,
              "\n/* V25 COMBAT CHOREOGRAPHY */\n"+addon.strip()+
              "\n/* END V25 */\n"+anchor)
    return html

def build():
    return patch(builder24().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    before=V19.read_bytes()
    content=build()
    for mark in ('id="page-combat-v25"',"function v25PairPose(",
                 "function v25Contact(","function v25Actor(",
                 "function v24Dynamics(","function v23HeadScale(",
                 "function v22Mood(","function v20CanonLines(",
                 "function combat18Sim(","V25_CHOREOGRAPHY.json"):
        assert mark in content,mark
    assert V19.read_bytes()==before
    print("V25 PATCH SELFTEST PASS",len(content.encode("utf-8")),
          hashlib.sha256(before).hexdigest())

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",default=str(OUTPUT))
    cli.add_argument("--selftest",action="store_true")
    arg=cli.parse_args()
    if arg.selftest:selftest();return
    path=Path(arg.output).resolve()
    if path==V19.resolve():raise ValueError("V19 must never be overwritten")
    path.parent.mkdir(parents=True,exist_ok=True)
    html=build();path.write_text(html,encoding="utf-8")
    print("V25 HTML BUILT",path,"bytes",path.stat().st_size)

if __name__=="__main__":
    main()
