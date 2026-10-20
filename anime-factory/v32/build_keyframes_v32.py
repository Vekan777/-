#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V32 — additive scene-specific keyframe and procedural character readability."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v31"/"build_visual_v31.py"
ADDON=Path(__file__).with_name("keyframes_v32.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V32_KEYFRAME_READABILITY.html")
PANEL=r"""
<section class="page" id="page-keyframe-v32" hidden>
<div class="card">
 <h2>V32 — Читаемые силуэты и ключевые позы</h2>
 <p class="muted">Четыре управляемых ключевых положения сцены. Плавная интерполяция жеста, локтей, кистей, стойки и эмоции лица. Сюжет, персонажи и выпуск V19–V31 сохранены; загруженные PNG не перерисовываются.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v32-scene"></select></div>
  <div class="field"><label>Манера анимации</label><select id="v32-style">
   <option value="readable">Читаемая</option><option value="subtle">Сдержанная</option><option value="action">Динамичная</option>
  </select></div>
 </div>
 <label><input id="v32-enabled" type="checkbox" checked> Улучшить процедурные позы V32</label>
 <div class="grid">
  <div class="field"><label>Ширина силуэта <span id="v32-silhouette-n">77</span>%</label><input id="v32-silhouette" type="range" min="0" max="100"></div>
  <div class="field"><label>Размах жеста <span id="v32-gesture-n">75</span>%</label><input id="v32-gesture" type="range" min="0" max="100"></div>
  <div class="field"><label>Выразительность лица <span id="v32-expression-n">70</span>%</label><input id="v32-expression" type="range" min="0" max="100"></div>
  <div class="field"><label>Фиксация ключевой позы <span id="v32-hold-n">70</span>%</label><input id="v32-hold" type="range" min="0" max="100"></div>
  <div class="field"><label>Подготовка к действию <span id="v32-anticipation-n">73</span>%</label><input id="v32-anticipation" type="range" min="0" max="100"></div>
 </div>
 <div class="grid">
  <div class="field"><label>Редактируемая ключевая поза</label><select id="v32-keyframe">
   <option value="0">1 — 12% сцены</option><option value="1">2 — 38% сцены</option>
   <option value="2">3 — 62% сцены</option><option value="3">4 — 86% сцены</option>
  </select></div>
  <div class="field"><label>Выразительность этого ключа <span id="v32-key-value-n">48</span>%</label><input type="range" id="v32-key-value" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v32-preset">Профиль выразительности</button>
  <button class="accent" id="v32-save">Сохранить ключевые позы V32</button></div>
</div>
<div class="card">
 <h2>Сравнение идентичного времени: V31 / V32</h2>
 <div class="grid">
  <div class="field"><label>V31 — исходная процедурная поза</label><canvas class="preview" id="v32-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V32 — читаемый силуэт и мимика</label><canvas class="preview" id="v32-after" width="640" height="360"></canvas></div>
 </div>
 <label>Позиция сцены <input type="range" id="v32-position" min="0" max="100" value="38"></label>
 <p class="muted" id="v32-caption"></p>
 <div class="flex"><button id="v32-sheet">Скачать 4 PNG ключевых поз</button>
  <button id="v32-plan">Скачать план ключевых поз TXT</button>
  <button id="v32-qa">Проверить выразительность</button></div>
 <pre class="report" id="v32-report" style="white-space:pre-wrap;max-height:220px;overflow:auto"></pre>
</div>
<div class="card">
 <h2>Область действия</h2>
 <p class="note">V32 улучшает геометрию <b>процедурных персонажей</b>. При использовании готового пользовательского PNG/портрета позиция может остаться прежней: источник изображения не меняется. Это 2D-аниматик с интерполяцией, не ручная покадровая анимация и не профессиональная 3D-система.</p>
</div>
</section>
"""

def once(s,old,new):
 n=s.count(old)
 if n!=1:raise ValueError("V32 expected one integration anchor "+repr(old[:100])+" count="+str(n))
 return s.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("v31_builder",BASE)
 obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def patch(html,addon):
 if "function v32Pose(" in html or 'id="page-keyframe-v32"' in html:
  raise ValueError("V32 already integrated")
 for key in ("function v31Grade(","function v30Audit(","function v29Actor(",
             "function v24FootPose(","function v23HeadScale(",
             "function v20CanonLines(","function drawRigPerson("):
  if key not in html:raise ValueError("Missing retained original source "+key)
 html=once(html,'<button data-page="export">',
    '<button data-page="keyframe-v32">Ключевые позы V32</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
    PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V31';",
    "const storageKey='AI_ANIME_FACTORY_V32';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:31,",
    "P={format:'AIAnimeFactoryProject',version:32,")
 html=once(html,
    "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V30')",
    "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V31')||localStorage.getItem('AI_ANIME_FACTORY_V30')")
 html=once(html,"if(page==='visual-v31')v31UpdateUI();",
    "if(page==='visual-v31')v31UpdateUI();if(page==='keyframe-v32')v32Show();")
 html=once(html,"v29Show();v30Run();v31UpdateUI();}",
    "v29Show();v30Run();v31UpdateUI();v32Show();}")
 # Update actual articulated anatomy and face within the existing procedural
 # drawRigPerson rather than drawing a cosmetic overlay over the scene.
 html=once(html,
    "const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role),v29=v29Actor(s,t,role);const d=rigDynamics(s,t,role),mood=",
    "const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role),v29=v29Actor(s,t,role),v32=v32Pose(s,t,role);const d=rigDynamics(s,t,role),mood=")
 html=once(html,
    "v24.lean+v25.lean+v29.lean;",
    "v24.lean+v25.lean+v29.lean+v32.lean;")
 html=once(html,
    "const leftElbow=[-54-attack*12,-118-block*14-v25.guard*14],leftHand=[-72-attack*17+v25.guard*8,-97-block*46-v25.guard*33-v29.guardY];",
    "const leftElbow=[-54-attack*12+v32.elbowLX,-118-block*14-v25.guard*14+v32.elbowLY],leftHand=[-72-attack*17+v25.guard*8+v32.handLX,-97-block*46-v25.guard*33-v29.guardY+v32.handLY];")
 html=once(html,
    "const rightElbow=[55+attack*17,-121-attack*42],rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32+v29.handX,-104-attack*101-block*77-v24.handLift-v25.attack*25-v29.handY];",
    "const rightElbow=[55+attack*17+v32.elbowRX,-121-attack*42+v32.elbowRY],rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32+v29.handX+v32.handRX,-104-attack*101-block*77-v24.handLift-v25.attack*25-v29.handY+v32.handRY];")
 html=once(html,
    "g.rotate(lean);g.translate(v24.rootX+v25.step+v29.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob+v29.rootY);",
    "g.rotate(lean);g.translate(v24.rootX+v25.step+v29.rootX+v32.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob+v29.rootY+v32.rootY);")
 html=once(html,
    "const footL=v29FootPose(s,t,role,'left',v24FootPose(s,t,role,'left',-36-steps*29,4-Math.max(0,steps)*10)),footR=v29FootPose(s,t,role,'right',v24FootPose(s,t,role,'right',36+steps*29,4-Math.max(0,-steps)*10));",
    "const footL=v32Foot(s,t,role,'left',v29FootPose(s,t,role,'left',v24FootPose(s,t,role,'left',-36-steps*29,4-Math.max(0,steps)*10))),footR=v32Foot(s,t,role,'right',v29FootPose(s,t,role,'right',v24FootPose(s,t,role,'right',36+steps*29,4-Math.max(0,-steps)*10)));")
 html=once(html,
    "const f=v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role)));g.translate(Math.sin(t*18)*f.impact*2.2+v24.headX+v29.headX,-f.impact*2.8);",
    "const f=v32Face(s,t,role,v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role))));g.translate(Math.sin(t*18)*f.impact*2.2+v24.headX+v29.headX+v32.headX,-f.impact*2.8);")
 head="g.save();g.translate(0,-209);const hs="
 if html.count(head)!=2:raise ValueError("Face and hair transforms diverged; V32 cannot safely apply shared tilt")
 html=html.replace(head,"g.save();g.translate(0,-209);g.rotate(v32.headTilt);const hs=",2)
 html=once(html,"'AI ANIME FACTORY V31  •  VISUAL PRODUCTION'",
    "'AI ANIME FACTORY V32  •  KEYFRAME READABILITY'")
 html=once(html,
    "const files=[{name:'AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html',data:selfHTML()},",
    "const files=[{name:'AI_Anime_Factory_V32_KEYFRAME_READABILITY.html',data:selfHTML()},"+
    "{name:'V32_KEYFRAME_PLAN_RU.txt',data:v32Plan()},"+
    "{name:'V32_SCENE_POSES.json',data:JSON.stringify(P.episodes.map(e=>"+
    "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,readabilityV32:v32Of(s)}))})),null,2)},")
 html=once(html,"'AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW_Offline.html'",
    "'AI_Anime_Factory_V32_KEYFRAME_READABILITY_Offline.html'")
 html=once(html,
    "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<31)migrated.version=31;return migrated;}",
    "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<32)migrated.version=32;return migrated;}")
 anchor=("try{const old=localStorage.getItem(storageKey)||"+
    "localStorage.getItem('AI_ANIME_FACTORY_V31')||"+
    "localStorage.getItem('AI_ANIME_FACTORY_V30')||")
 html=once(html,anchor,"\n/* V32 KEYFRAME READABILITY */\n"+
    addon.strip()+"\n/* END V32 */\n"+anchor)
 return html
def build():
 return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes()
 html=build()
 for mark in ('id="page-keyframe-v32"',"function v32Pose(","function v32Foot(",
    "function v32Face(","function v31Grade(","function v30Audit(",
    "function v29Actor(","V32_SCENE_POSES.json"):
  assert mark in html,mark
 assert original==V19.read_bytes()
 print("V32 BUILDER PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--output",default=str(OUTPUT));p.add_argument("--selftest",action="store_true")
 a=p.parse_args()
 if a.selftest:selftest();return
 out=Path(a.output).resolve()
 if out==V19.resolve():raise ValueError("Refusing V19 overwrite")
 out.parent.mkdir(parents=True,exist_ok=True)
 result=build();out.write_text(result,encoding="utf-8")
 print("V32 HTML BUILT",out,out.stat().st_size)
if __name__=="__main__":main()
