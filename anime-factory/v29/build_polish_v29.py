#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preserve original V19 and layer V29 temporal combat polish on V20–V28."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v28"/"build_interaction_v28.py"
ADDON=Path(__file__).with_name("polish_v29.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html")
PANEL=r"""
<section class="page" id="page-polish-v29" hidden>
<div class="card">
 <h2>V29 — Полировка анимации и боевого ритма</h2>
 <p class="muted">Одна шкала фаз управляет движением рук, корпуса, опорой ног и пылью. Подготовка — удар — защита/попадание — возврат. Исходы боя берутся из существующих событий V19/V17. Сюжет и редакторы V19–V28 сохранены.</p>
 <div class="grid">
  <div class="field"><label>Боевая сцена</label><select id="v29-scene"></select></div>
  <div class="field"><label>Манера анимации</label><select id="v29-style">
   <option value="natural">Естественная</option>
   <option value="action">Динамичная</option>
   <option value="subtle">Сдержанная</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v29-enabled" checked> Включить улучшенные движения V29</label>
 <div class="grid">
  <div class="field"><label>Синхронизация тайминга <span id="v29-timing-n">78</span>%</label><input type="range" id="v29-timing" min="0" max="100"></div>
  <div class="field"><label>Опора ног и баланс <span id="v29-stance-n">75</span>%</label><input type="range" id="v29-stance" min="0" max="100"></div>
  <div class="field"><label>Затухание движения <span id="v29-follow-n">64</span>%</label><input type="range" id="v29-follow" min="0" max="100"></div>
  <div class="field"><label>Сила реакции на контакт <span id="v29-impact-n">68</span>%</label><input type="range" id="v29-impact" min="0" max="100"></div>
  <div class="field"><label>Плавность и фиксация ног <span id="v29-smoothness-n">80</span>%</label><input type="range" id="v29-smoothness" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v29-preset">Профиль боевой анимации</button>
 <button class="accent" id="v29-save">Сохранить движения V29</button></div>
</div>
<div class="card">
 <h2>Сравнение одного кадра V28 / V29</h2>
 <div class="grid">
  <div class="field"><label>V28 — движение до полировки</label>
   <canvas class="preview" id="v29-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V29 — синхронные фазы</label>
   <canvas class="preview" id="v29-after" width="640" height="360"></canvas></div>
 </div>
 <label>Момент сцены <input type="range" id="v29-position" min="0" max="100" value="45"></label>
 <p class="muted" id="v29-caption"></p>
 <div class="flex"><button id="v29-sheet">Скачать 4 кадра PNG</button>
 <button id="v29-plan">Скачать фазы боя TXT</button></div>
</div>
<div class="card">
 <h2>Проверка согласованности</h2>
 <pre id="v29-qa" class="report" style="white-space:pre-wrap;max-height:260px;overflow:auto"></pre>
 <div class="note">Это процедурный 2D-риг, а не настоящая кинематографичная скелетная анимация. Фиксация стоп приближённая; авторские PNG не перерисовываются и события боя не переписываются.</div>
</div>
</section>
"""

def once(txt,old,new):
    n=txt.count(old)
    if n!=1:raise ValueError("V29 integration anchor "+repr(old[:100])+" occurrences="+str(n))
    return txt.replace(old,new,1)

def previous():
    spec=importlib.util.spec_from_file_location("anime_v28_builder",BASE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if "function v29Beat(" in html or 'id="page-polish-v29"' in html:
        raise ValueError("Already V29")
    for tag in ("function v28Footfall(","function v27Feet(","function v26Camera(",
                "function v25Actor(","function v24FootPose(","function v20CanonLines("):
        if tag not in html:raise ValueError("Missing previous module "+tag)
    html=once(html,'<button data-page="export">',
        '<button data-page="polish-v29">Анимация V29</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
        PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V28';",
        "const storageKey='AI_ANIME_FACTORY_V29';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:28,",
        "P={format:'AIAnimeFactoryProject',version:29,")
    html=once(html,
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V27')",
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V28')||localStorage.getItem('AI_ANIME_FACTORY_V27')")
    html=once(html,"if(page==='interaction-v28')v28Show();",
        "if(page==='interaction-v28')v28Show();if(page==='polish-v29')v29Show();")
    html=once(html,"v26Show();v27Show();v28Show();}",
        "v26Show();v27Show();v28Show();v29Show();}")
    html=once(html,
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA(),v27QA(),v28QA());",
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA(),v27QA(),v28QA(),v29QA());")
    # The same V19/V25 authoritative beat is used by the procedural rig and
    # by V28 dust; existing author-owned character art remains unmodified.
    html=once(html,
        "const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role);const d=rigDynamics(s,t,role),mood=",
        "const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role),v29=v29Actor(s,t,role);const d=rigDynamics(s,t,role),mood=")
    html=once(html,
        "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p+v24.lean+v25.lean;",
        "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p+v24.lean+v25.lean+v29.lean;")
    html=once(html,
        "leftHand=[-72-attack*17+v25.guard*8,-97-block*46-v25.guard*33];",
        "leftHand=[-72-attack*17+v25.guard*8,-97-block*46-v25.guard*33-v29.guardY];")
    html=once(html,
        "rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32,-104-attack*101-block*77-v24.handLift-v25.attack*25];",
        "rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32+v29.handX,-104-attack*101-block*77-v24.handLift-v25.attack*25-v29.handY];")
    html=once(html,
        "g.rotate(lean);g.translate(v24.rootX+v25.step,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob);",
        "g.rotate(lean);g.translate(v24.rootX+v25.step+v29.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob+v29.rootY);")
    html=once(html,
        "const footL=v24FootPose(s,t,role,'left',-36-steps*29,4-Math.max(0,steps)*10),footR=v24FootPose(s,t,role,'right',36+steps*29,4-Math.max(0,-steps)*10);",
        "const footL=v29FootPose(s,t,role,'left',v24FootPose(s,t,role,'left',-36-steps*29,4-Math.max(0,steps)*10)),footR=v29FootPose(s,t,role,'right',v24FootPose(s,t,role,'right',36+steps*29,4-Math.max(0,-steps)*10));")
    html=once(html,
        "g.translate(Math.sin(t*18)*f.impact*2.2+v24.headX,-f.impact*2.8);",
        "g.translate(Math.sin(t*18)*f.impact*2.2+v24.headX+v29.headX,-f.impact*2.8);")
    html=once(html,"const foot=v28Footfall(s,t,role);",
        "const foot=v29GroundPulse(s,t,role);")
    html=once(html,"'AI ANIME FACTORY V28  •  CHARACTER–ENVIRONMENT'",
        "'AI ANIME FACTORY V29  •  ANIMATION POLISH'")
    html=once(html,
        "const files=[{name:'AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html',data:selfHTML()},",
        "const files=[{name:'AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html',data:selfHTML()},"+
        "{name:'V29_COMBAT_TIMING_RU.txt',data:v29Plan()},"+
        "{name:'V29_MOTION_SETTINGS.json',data:JSON.stringify(P.episodes.map(e=>"+
        "({number:e.number,scenes:e.scenes.filter(s=>s.kind==='fight').map(s=>"+
        "({title:s.title,polishV29:v29Options(s)}))})),null,2)},")
    html=once(html,"'AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION_Offline.html'",
        "'AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH_Offline.html'")
    html=once(html,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<28)migrated.version=28;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<29)migrated.version=29;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V28')||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V27')||")
    html=once(html,anchor,
        "\n/* V29 ANIMATION & COMBAT POLISH */\n"+addon.strip()+
        "\n/* END V29 */\n"+anchor)
    return html

def build():
    return patch(previous().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    before=V19.read_bytes()
    content=build()
    for mark in ('id="page-polish-v29"',"function v29Beat(",
                 "function v29Actor(","function v29FootPose(",
                 "function v29GroundPulse(","function v28ImpactAt(",
                 "function v27Feet(","function v26Camera(",
                 "function v25PairPose(","function v20CanonLines(",
                 "V29_MOTION_SETTINGS.json"):
        assert mark in content,mark
    assert before==V19.read_bytes()
    print("V29 SOURCE PASS",len(content.encode("utf-8")),hashlib.sha256(before).hexdigest())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--output",default=str(OUTPUT))
    o=p.parse_args()
    if o.selftest:selftest();return
    target=Path(o.output).resolve()
    if target==V19.resolve():raise ValueError("Cannot overwrite V19")
    target.parent.mkdir(parents=True,exist_ok=True)
    payload=build();target.write_text(payload,encoding="utf-8")
    print("V29 HTML BUILT",target,"bytes",target.stat().st_size)

if __name__=="__main__":main()
