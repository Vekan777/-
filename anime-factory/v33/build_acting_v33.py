#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V33 acting and facial expression on top of genuine V19–V32."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v32"/"build_keyframes_v32.py"
ADDON=Path(__file__).with_name("acting_v33.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V33_ACTING_EXPRESSION.html")
PANEL=r"""
<section class="page" id="page-acting-v33" hidden>
<div class="card">
 <h2>V33 — Актёрская игра, взгляд и эмоции</h2>
 <p class="muted">Направление взгляда, положение бровей и век, наклон головы, дыхание и движения кистей в существующем 2D-риге. Опирается на эмоции V22 и ключевые позы V32. Исходы боя и сюжет не переписываются.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v33-scene"></select></div>
  <div class="field"><label>Стиль</label><select id="v33-style">
   <option value="cinematic">Кинематографично</option>
   <option value="expressive">Выразительно</option>
   <option value="subtle">Сдержанно</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v33-enabled" checked> Включить актёрские движения V33</label>
 <div class="grid">
  <div class="field"><label>Направление взгляда <span id="v33-gaze-n">72</span>%</label><input id="v33-gaze" type="range" min="0" max="100"></div>
  <div class="field"><label>Эмоции бровей и глаз <span id="v33-emotion-n">79</span>%</label><input id="v33-emotion" type="range" min="0" max="100"></div>
  <div class="field"><label>Выразительность жестов <span id="v33-gesture-n">73</span>%</label><input id="v33-gesture" type="range" min="0" max="100"></div>
  <div class="field"><label>Естественное дыхание <span id="v33-breathing-n">51</span>%</label><input id="v33-breathing" type="range" min="0" max="100"></div>
  <div class="field"><label>Плавность переходов <span id="v33-transitions-n">76</span>%</label><input id="v33-transitions" type="range" min="0" max="100"></div>
 </div>
 <div class="flex">
  <button id="v33-preset">Профиль выразительной игры</button>
  <button class="accent" id="v33-save">Сохранить актёрскую игру</button>
 </div>
</div>
<div class="card">
 <h2>Настоящий рендер: V32 до / V33 после</h2>
 <div class="grid">
  <div class="field"><label>V32 — исходная сцена</label>
   <canvas id="v33-before" class="preview" width="640" height="360"></canvas></div>
  <div class="field"><label>V33 — направленный взгляд и жесты</label>
   <canvas id="v33-after" class="preview" width="640" height="360"></canvas></div>
 </div>
 <label>Позиция сцены <input type="range" id="v33-position" min="0" max="100" value="38"></label>
 <p id="v33-caption" class="muted"></p>
 <div class="flex">
  <button id="v33-sheet">Экспорт 4 PNG кадров</button>
  <button id="v33-plan">Экспорт плана эмоций TXT</button>
  <button id="v33-qa">Проверить сценический ритм</button>
 </div>
 <pre class="report" id="v33-report" style="white-space:pre-wrap;max-height:220px;overflow:auto"></pre>
</div>
<div class="card">
 <h2>Честные ограничения</h2>
 <p class="note">Это процедурная анимация 2D-рига, а не нейросетевая перерисовка, motion capture, lip-sync студийного уровня или 3D. Ваши PNG персонажей не изменяются. Автоматический анализ эмоции опирается на уже заданные настроения сцены и не понимает актёрский подтекст.</p>
</div>
</section>
"""
def once(txt,old,new):
 n=txt.count(old)
 if n!=1:raise ValueError("V33 integration anchor "+repr(old[:90])+" occurrences="+str(n))
 return txt.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("anime_v32_builder",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,addon):
 if "function v33Act(" in html or 'id="page-acting-v33"' in html:
  raise ValueError("Already integrated V33")
 for mark in ("function v32Pose(","function v32Face(","function v31Grade(",
              "function v30Audit(","function v22Mood(","function drawRigPerson("):
  if mark not in html:raise ValueError("Missing historical feature "+mark)
 html=once(html,'<button data-page="export">',
  '<button data-page="acting-v33">Актёрская игра V33</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V32';",
  "const storageKey='AI_ANIME_FACTORY_V33';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:32,",
  "P={format:'AIAnimeFactoryProject',version:33,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V31')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V32')||localStorage.getItem('AI_ANIME_FACTORY_V31')")
 html=once(html,"if(page==='keyframe-v32')v32Show();",
  "if(page==='keyframe-v32')v32Show();if(page==='acting-v33')v33Show();")
 html=once(html,"v30Run();v31UpdateUI();v32Show();}",
  "v30Run();v31UpdateUI();v32Show();v33Show();}")
 # Call one shared acting signal to apply synchronized wrists, head and gaze.
 html=once(html,
  "v29=v29Actor(s,t,role),v32=v32Pose(s,t,role);const d=rigDynamics(s,t,role),mood=",
  "v29=v29Actor(s,t,role),v32=v32Pose(s,t,role),v33=v33Act(s,t,role);const d=rigDynamics(s,t,role),mood=")
 html=once(html,
  "const leftElbow=[-54-attack*12+v32.elbowLX,-118-block*14-v25.guard*14+v32.elbowLY],leftHand=[-72-attack*17+v25.guard*8+v32.handLX,-97-block*46-v25.guard*33-v29.guardY+v32.handLY];",
  "const leftElbow=[-54-attack*12+v32.elbowLX+v33.elbowLX,-118-block*14-v25.guard*14+v32.elbowLY+v33.elbowLY],leftHand=[-72-attack*17+v25.guard*8+v32.handLX+v33.handLX,-97-block*46-v25.guard*33-v29.guardY+v32.handLY+v33.handLY];")
 html=once(html,
  "const rightElbow=[55+attack*17+v32.elbowRX,-121-attack*42+v32.elbowRY],rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32+v29.handX+v32.handRX,-104-attack*101-block*77-v24.handLift-v25.attack*25-v29.handY+v32.handRY];",
  "const rightElbow=[55+attack*17+v32.elbowRX+v33.elbowRX,-121-attack*42+v32.elbowRY+v33.elbowRY],rightHand=[76+attack*60-block*33+v24.handX+v25.attack*32+v29.handX+v32.handRX+v33.handRX,-104-attack*101-block*77-v24.handLift-v25.attack*25-v29.handY+v32.handRY+v33.handRY];")
 html=once(html,
  "g.rotate(lean);g.translate(v24.rootX+v25.step+v29.rootX+v32.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob+v29.rootY+v32.rootY);",
  "g.rotate(lean);g.translate(v24.rootX+v25.step+v29.rootX+v32.rootX+v33.rootX,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body+v24.bob+v29.rootY+v32.rootY+v33.rootY);")
 html=once(html,
  "const f=v32Face(s,t,role,v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role))));",
  "const f=v33Face(s,t,role,v32Face(s,t,role,v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role)))));")
 head="g.save();g.translate(0,-209);g.rotate(v32.headTilt);const hs="
 if html.count(head)!=2:
  raise ValueError("V33 face/hair head-tilt anchors not matched")
 html=html.replace(head,
  "g.save();g.translate(0,-209);g.rotate(v32.headTilt+v33.headTilt);const hs=",2)
 html=once(html,
  "v24.headX+v29.headX+v32.headX,-f.impact*2.8);",
  "v24.headX+v29.headX+v32.headX+v33.headX,-f.impact*2.8);")
 html=once(html,
  "'AI ANIME FACTORY V32  •  KEYFRAME READABILITY'",
  "'AI ANIME FACTORY V33  •  ACTING & EXPRESSION'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V32_KEYFRAME_READABILITY.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V33_ACTING_EXPRESSION.html',data:selfHTML()},"+
  "{name:'V33_ACTING_PLAN_RU.txt',data:v33Plan()},"+
  "{name:'V33_SCENE_ACTING.json',data:JSON.stringify(P.episodes.map(e=>"+
  "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,actingV33:v33Of(s)}))})),null,2)},")
 html=once(html,"'AI_Anime_Factory_V32_KEYFRAME_READABILITY_Offline.html'",
  "'AI_Anime_Factory_V33_ACTING_EXPRESSION_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<32)migrated.version=32;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<33)migrated.version=33;return migrated;}")
 anchor=("try{const old=localStorage.getItem(storageKey)||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V32')||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V31')||")
 html=once(html,anchor,"\n/* V33 ACTING AND EXPRESSION */\n"+
    addon.strip()+"\n/* END V33 */\n"+anchor)
 return html
def build():
 return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes()
 content=build()
 for mark in ('id="page-acting-v33"',"function v33Act(",
              "function v33Face(","function v33Signal(",
              "function v32Pose(","function v31Grade(","V33_SCENE_ACTING.json"):
  assert mark in content,mark
 assert V19.read_bytes()==original
 print("V33 ORIGINAL SOURCE PASS",len(content.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--selftest",action="store_true")
 parser.add_argument("--output",default=str(OUTPUT))
 args=parser.parse_args()
 if args.selftest:selftest();return
 dest=Path(args.output).resolve()
 if dest==V19.resolve():raise ValueError("Cannot overwrite original V19")
 dest.parent.mkdir(parents=True,exist_ok=True)
 body=build();dest.write_text(body,encoding="utf-8")
 print("V33 HTML BUILT",dest,dest.stat().st_size)
if __name__=="__main__":main()
