#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V43: additive action camera direction atop V42 and all original V19–V41."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v42/build_stage_v42.py"
ADDON=Path(__file__).with_name("director_v43.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V43_ACTION_DIRECTOR.html")
PANEL=r"""
<section class="page" id="page-action-v43" hidden>
<div class="card">
 <h2>V43 — Режиссура камеры и читаемость боевых сцен</h2>
 <p class="muted">Новый реальный кадрирующий 2D-режиссёр использует уже существующие события боя V25: подготовка, удар, блок, уклонение. Действия, результат попадания, длительности, герои и история неизменны. Камера может приблизиться, сместить центр внимания и слегка наклониться на подтверждённом событии. Субтитры остаются сверху и не наклоняются вместе с кадром.</p>
 <div class="grid">
  <div class="field"><label>Эпизод</label><select id="v43-episode"></select></div>
  <div class="field"><label>Сцена (ищите «Бой»)</label><select id="v43-scene"></select></div>
  <div class="field"><label>Режиссёрский профиль</label><select id="v43-profile">
   <option value="duel">Классическая дуэль</option>
   <option value="heroic">Героическая динамика</option>
   <option value="wide">Общий план боя</option>
  </select></div>
  <div class="field"><label>Крупность кадра</label><select id="v43-shot">
   <option value="wide">Общий план</option>
   <option value="medium">Средний план</option>
   <option value="close">Крупный план</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v43-enabled" checked> Включить V43 на выбранной сцене</label>
 <label><input type="checkbox" id="v43-reduced"> Уменьшение движения камеры (без тряски и наклонов)</label>
 <div class="grid">
  <div class="field"><label>Динамическое приближение <span id="v43-label-zoom">53</span>%</label><input id="v43-zoom" type="range" min="0" max="100"></div>
  <div class="field"><label>Акцент на участнике <span id="v43-label-focus">57</span>%</label><input id="v43-focus" type="range" min="0" max="100"></div>
  <div class="field"><label>Реакция камеры на попадание <span id="v43-label-recoil">40</span>%</label><input id="v43-recoil" type="range" min="0" max="100"></div>
  <div class="field"><label>Ритм наезда <span id="v43-label-tempo">62</span>%</label><input id="v43-tempo" type="range" min="0" max="100"></div>
  <div class="field"><label>Наклон при подтверждённом событии <span id="v43-label-tilt">18</span>%</label><input id="v43-tilt" type="range" min="0" max="100"></div>
 </div>
 <button class="accent" id="v43-save">Сохранить режиссуру сцены</button>
 <p class="note">Только кадрирование 2D сцены, не автоматическая новая анимация, не 3D и не генерация ударов. На диалогах V43 не меняет изображение: это специальный режиссёр для сцен вида «Бой».</p>
</div>
<div class="card">
 <h2>Настоящий предпросмотр целого эпизода</h2>
 <canvas class="preview" id="v43-preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v43-play">Воспроизвести</button><button id="v43-first">В начало</button></div>
 <label>Реальный таймкод V35 <input id="v43-seek" type="range" min="0" max="1000" value="0"></label>
 <p id="v43-time" class="muted">Таймкод эпизода</p>
 <p class="note">Полный видеорендер со звуком по-прежнему выполняется во вкладке «Звук / экспорт V36». Запись включает V43 движение кадра, V42 атмосферу, V41 рисунок персонажей и V37 субтитры.</p>
</div>
<div class="card">
 <h2>Контроль боя, экспорт и резерв</h2>
 <div class="flex">
  <button id="v43-sheet">Четыре настоящих кадра PNG</button>
  <button id="v43-json">Режиссёрский план JSON</button>
  <button id="v43-audit">Проверка комфорта просмотра</button>
 </div>
 <pre id="v43-report" class="report" style="white-space:pre-wrap;max-height:320px;overflow:auto"></pre>
</div>
</section>
"""
def once(src,a,b):
 n=src.count(a)
 if n!=1:raise ValueError("V43 anchor occurrences "+str(n)+": "+repr(a[:95]))
 return src.replace(a,b,1)
def previous():
 spec=importlib.util.spec_from_file_location("v42_base_builder",BASE)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def patch(html,script):
 if "function v43Shot(" in html or 'id="page-action-v43"' in html:
  raise ValueError("V43 applied twice")
 for old in ("function v25Contact(","function v35Plan(","function v36Schedule(",
   "function v37Paint(","function v38Frame(","function v39Move(",
   "function v40FaceInk(","function v41Cape(","function v42Layers("):
  if old not in html:raise ValueError("Missing original V19–V42 function "+old)
 html=once(html,'<button data-page="export">',
  '<button data-page="action-v43">Режиссёр боя V43</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V42';",
  "const storageKey='AI_ANIME_FACTORY_V43';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:42,",
  "P={format:'AIAnimeFactoryProject',version:43,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V41')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V42')||localStorage.getItem('AI_ANIME_FACTORY_V41')")
 html=once(html,"if(page==='stage-v42')v42Show();",
  "if(page==='stage-v42')v42Show();if(page==='action-v43')v43Show();")
 html=once(html,"v41Show();v42Show();}","v41Show();v42Show();v43Show();}")
 html=once(html,"function show(page){if(page!=='stage-v42')v42Pause();",
  "function show(page){if(page!=='action-v43')v43Pause();if(page!=='stage-v42')v42Pause();")
 html=once(html,
  "'AI ANIME FACTORY V42  •  SCENE DEPTH / LIGHTING'",
  "'AI ANIME FACTORY V43  •  ACTION CAMERA DIRECTOR'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V42_STAGE_DEPTH.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V43_ACTION_DIRECTOR.html',data:selfHTML()},"+
  "{name:'V43_ACTION_CAMERA.json',data:JSON.stringify(v43Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V42_STAGE_DEPTH_Offline.html'",
  "'AI_Anime_Factory_V43_ACTION_DIRECTOR_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<42)migrated.version=42;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<43)migrated.version=43;return migrated;}")
 html=once(html,"download('V42_STAGE_DEPTH_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V43_ACTION_DIRECTOR_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V42: свет и глубина окружения записаны в WebM (",
  "V43: постановка боевого кадра записана в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V42 с атмосферой и светом</button>',
  '<button class="accent" id="v36-export">Записать V43 с постановкой боя</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V42')||"
 html=once(html,anchor,"\n/* V43 ORIGINAL CANON ACTION CAMERA */\n"+script.strip()+
  "\n/* END V43 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();html=build()
 for term in ("function v43Shot(","function v43DirectorState(","v38Frame=function(",
  "function v42Layers(","function v41Cape(","function v39Move(",
  "function v37Paint(","AI_ANIME_FACTORY_V43",'id="page-action-v43"'):
  assert term in html,term
 assert original==V19.read_bytes()
 print("V43 BUILD PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--output",default=str(OUTPUT))
 args=p.parse_args()
 if args.selftest:selftest();return
 out=Path(args.output).resolve()
 if out==V19.resolve():raise ValueError("Refusing original V19 overwrite")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V43 HTML BUILT",out,out.stat().st_size)
if __name__=="__main__":main()
