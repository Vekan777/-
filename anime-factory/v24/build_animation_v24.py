#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add V24 animation to the unmodified V19→V20→V21→V22→V23 build."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER23=ROOT/"anime-factory"/"v23"/"build_character_v23.py"
ADDON=Path(__file__).with_name("animation_v24.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V24_CHARACTER_ANIMATION.html")

PANEL=r"""
<section class="page" id="page-animation-v24" hidden>
<div class="card">
 <h2>V24 — Движение персонажей: шаг, вес, удар и реакция</h2>
 <p class="muted">Настройка пластики процедурных 2D-персонажей в одной сцене. Все серии, настройки V20–V23 и загруженные рисунки остаются на месте.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v24-scene"></select></div>
  <div class="field"><label>Стиль движения</label><select id="v24-style">
   <option value="auto">Автоматически по сцене</option>
   <option value="cinematic">Кинематографичный</option>
   <option value="subtle">Сдержанный</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v24-enabled" checked> Включить анимацию V24 для сцены</label>
 <div class="grid">
  <div class="field"><label>Шаг и постановка ног: <span id="v24-stride-n">68</span>%</label><input type="range" id="v24-stride" min="0" max="100"></div>
  <div class="field"><label>Перенос веса: <span id="v24-weight-n">70</span>%</label><input type="range" id="v24-weight" min="0" max="100"></div>
  <div class="field"><label>Подготовка к удару: <span id="v24-anticipation-n">78</span>%</label><input type="range" id="v24-anticipation" min="0" max="100"></div>
  <div class="field"><label>Реакция на удар: <span id="v24-recoil-n">66</span>%</label><input type="range" id="v24-recoil" min="0" max="100"></div>
  <div class="field"><label>Инерция после движения: <span id="v24-followThrough-n">64</span>%</label><input type="range" id="v24-followThrough" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v24-preset">Настроить по типу сцены</button>
 <button class="accent" id="v24-save">Сохранить движение V24</button></div>
</div>
<div class="card">
 <h2>До / После — один и тот же момент сцены</h2>
 <div class="grid">
  <div class="field"><label>V23 — до изменения движений</label>
    <canvas class="preview" id="v24-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V24 — движение с переносом веса</label>
    <canvas class="preview" id="v24-after" width="640" height="360"></canvas></div>
 </div>
 <label>Положение в сцене <input type="range" id="v24-playhead" min="0" max="100" value="45"></label>
 <p class="muted" id="v24-caption"></p>
 <div class="flex"><button id="v24-sheet">Скачать 4 кадра PNG</button>
 <button id="v24-plan">Скачать план движений TXT</button></div>
</div>
<div class="card">
 <h2>Контроль постановки движения</h2>
 <pre id="v24-qa" class="report" style="white-space:pre-wrap;max-height:260px;overflow:auto"></pre>
 <div class="note">Анимация основана на 2D-риге. Механика шагов приближённая, без физического IK и motion capture. Изображения PNG, загруженные пользователем, не изменяются.</div>
</div>
</section>
"""

def once(text,old,new):
    n=text.count(old)
    if n!=1:
        raise ValueError("V24: expected one stable integration marker, found "+str(n)+": "+repr(old[:105]))
    return text.replace(old,new,1)

def base23():
    spec=importlib.util.spec_from_file_location("anime_v23_builder",BUILDER23)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,extension):
    if 'id="page-animation-v24"' in html:
        raise ValueError("V24 already integrated")
    for marker in ("function v23TorsoForm(", "function v22Mood(",
                   "function v20CanonLines(", "function impact19State("):
        if marker not in html:
            raise ValueError("Missing previous version: "+marker)
    html=once(html,'<button data-page="export">',
              '<button data-page="animation-v24">Анимация V24</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
              PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V23';",
              "const storageKey='AI_ANIME_FACTORY_V24';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:23,",
              "P={format:'AIAnimeFactoryProject',version:24,")
    html=once(html,
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V22')",
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V23')||localStorage.getItem('AI_ANIME_FACTORY_V22')")
    html=once(html,"if(page==='character-v23')v23Show();",
              "if(page==='character-v23')v23Show();if(page==='animation-v24')v24Show();")
    html=once(html,"v21RenderPanel();v22Show();v23Show();}",
              "v21RenderPanel();v22Show();v23Show();v24Show();}")
    html=once(html,"concat(v21VisualQA(),v22ActingQA(),v23CharacterQA());",
              "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA());")
    # Modify existing joint/limb motion rather than painting extra geometry.
    html=once(html,"const d=rigDynamics(s,t,role),mood=",
              "const v24=v24Dynamics(s,t,role);const d=rigDynamics(s,t,role),mood=")
    html=once(html,"const attack=d.attack*p,block=d.block*p,steps=d.steps*p,wind=",
              "const attack=d.attack*p+v24.strike*.25,block=d.block*p+v24.guard*.22,steps=d.steps*p+v24.step*.45,wind=")
    html=once(html,
       "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p;",
       "const lean=(d.preset==='dodge'?Math.sin(t*2.8)*.17:combat?attack*.12-block*.07:Math.sin(t*.7)*.014)*p+v24.lean;")
    html=once(html,
       "const rightElbow=[55+attack*17,-121-attack*42],rightHand=[76+attack*60-block*33,-104-attack*101-block*77];",
       "const rightElbow=[55+attack*17,-121-attack*42],rightHand=[76+attack*60-block*33+v24.handX,-104-attack*101-block*77-v24.handLift];")
    html=once(html,
       "g.rotate(lean);g.translate(0,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body);",
       "g.rotate(lean);g.translate(v24.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob);")
    html=once(html,
       "const footL=[-36-steps*29,4-Math.max(0,steps)*10],footR=[36+steps*29,4-Math.max(0,-steps)*10];",
       "const footL=v24FootPose(s,t,role,'left',-36-steps*29,4-Math.max(0,steps)*10),footR=v24FootPose(s,t,role,'right',36+steps*29,4-Math.max(0,-steps)*10);")
    html=once(html,
       "const f=v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role)));g.translate(Math.sin(t*18)*f.impact*2.2,-f.impact*2.8);",
       "const f=v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role)));g.translate(Math.sin(t*18)*f.impact*2.2+v24.headX,-f.impact*2.8);")
    html=once(html,
       "const attack=d.attack*p+v24.strike*.25,block=d.block*p+v24.guard*.22,steps=d.steps*p+v24.step*.45,wind=(Math.sin(t*4.2-1.1)+.7*d.attack-1.5*d.block)*d.hair+v23Secondary(s,c,t,role).hair,cloth=(Math.sin(t*2.7-.6)+1.4*d.attack-d.recover)*d.cloth+v23Secondary(s,c,t,role).cloth;",
       "const attack=d.attack*p+v24.strike*.25,block=d.block*p+v24.guard*.22,steps=d.steps*p+v24.step*.45,wind=(Math.sin(t*4.2-1.1)+.7*d.attack-1.5*d.block)*d.hair+v23Secondary(s,c,t,role).hair+v24.hair,cloth=(Math.sin(t*2.7-.6)+1.4*d.attack-d.recover)*d.cloth+v23Secondary(s,c,t,role).cloth+v24.cloth;")
    html=once(html,
       "'AI ANIME FACTORY V23  •  CHARACTER QUALITY'",
       "'AI ANIME FACTORY V24  •  CHARACTER ANIMATION'")
    html=once(html,
       "const files=[{name:'AI_Anime_Factory_V23_CHARACTER_QUALITY.html',data:selfHTML()},",
       "const files=[{name:'AI_Anime_Factory_V24_CHARACTER_ANIMATION.html',data:selfHTML()},"+
       "{name:'V24_MOTION_PLAN_RU.txt',data:v24Plan()},"+
       "{name:'V24_SCENE_MOTION.json',data:JSON.stringify(P.episodes.map(e=>"+
       "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,motionV24:v24Options(s)}))})),null,2)},")
    html=once(html,
       "'AI_Anime_Factory_V23_CHARACTER_QUALITY_Offline.html'",
       "'AI_Anime_Factory_V24_CHARACTER_ANIMATION_Offline.html'")
    html=once(html,
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<23)migrated.version=23;return migrated;}",
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<24)migrated.version=24;return migrated;}")
    start=("try{const old=localStorage.getItem(storageKey)||"+
       "localStorage.getItem('AI_ANIME_FACTORY_V23')||"+
       "localStorage.getItem('AI_ANIME_FACTORY_V22')||")
    html=once(html,start,"\n/* V24 CHARACTER ANIMATION */\n"+extension.strip()+
                "\n/* END V24 */\n"+start)
    return html

def build():
    return patch(base23().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    html=build()
    for marker in ('id="page-animation-v24"', "function v24Dynamics(",
                   "function v24FootPose(", "function v24Preview(", "function v24MotionQA(",
                   "function v23HeadScale(", "function v22Mood(", "function v20CanonLines(",
                   "function combat18Sim(", "function exportEpisode()", "V24_SCENE_MOTION.json"):
        assert marker in html,marker
    assert V19.read_bytes()==original
    print("V24 SOURCE PASS",len(html.encode("utf-8")),
          hashlib.sha256(original).hexdigest())

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--selftest",action="store_true")
    cli.add_argument("--output",default=str(OUTPUT))
    o=cli.parse_args()
    if o.selftest:selftest();return
    target=Path(o.output).resolve()
    if target==V19.resolve():raise ValueError("Refusing V19 overwrite")
    target.parent.mkdir(parents=True,exist_ok=True)
    content=build()
    target.write_text(content,encoding="utf-8")
    print("V24 HTML BUILT",target,"bytes",target.stat().st_size)

if __name__=="__main__":
    main()
