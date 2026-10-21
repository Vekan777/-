#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V39 additive character-performance builder on tested V19–V38."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v38/build_cinematic_v38.py"
ADDON=Path(__file__).with_name("performance_v39.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V39_CHARACTER_ACTION.html")
PANEL=r"""
<section class="page" id="page-performance-v39" hidden>
<div class="card">
 <h2>V39 — Выразительность персонажей и бой</h2>
 <p class="muted">Изменяется настоящая анимация суставов 2D-рига, положение корпуса, экспрессия лица и ударные эффекты по установленным событиям боя V17/V19. Ни один новый удар, промах или победа не создаётся, сюжет и исходные длительности не переписываются.</p>
 <div class="grid">
  <div class="field"><label>Серия</label><select id="v39-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v39-scene"></select></div>
 </div>
 <label><input id="v39-enabled" type="checkbox" checked> Включить улучшенную постановку V39</label>
 <div class="grid">
  <div class="field"><label>Энергия движения <span id="v39-label-energy">65</span>%</label>
   <input id="v39-energy" type="range" min="0" max="100" value="65"></div>
  <div class="field"><label>Выразительность лица <span id="v39-label-facial">62</span>%</label>
   <input id="v39-facial" type="range" min="0" max="100" value="62"></div>
  <div class="field"><label>Подготовка к удару <span id="v39-label-anticipation">72</span>%</label>
   <input id="v39-anticipation" type="range" min="0" max="100" value="72"></div>
  <div class="field"><label>Инерция движения <span id="v39-label-followThrough">68</span>%</label>
   <input id="v39-followThrough" type="range" min="0" max="100" value="68"></div>
  <div class="field"><label>Сила визуального контакта <span id="v39-label-impact">70</span>%</label>
   <input id="v39-impact" type="range" min="0" max="100" value="70"></div>
  <div class="field"><label>Линии скорости <span id="v39-label-streaks">48</span>%</label>
   <input id="v39-streaks" type="range" min="0" max="100" value="48"></div>
 </div>
 <div class="flex">
  <button id="v39-preset">Пресет для сцены</button>
  <button class="accent" id="v39-save">Сохранить движения и экспрессию</button>
 </div>
 <p class="note">Авторские PNG-слои остаются нетронутыми. Реальные изменения суставов применяются к встроенному процедурному 2D-ригу; это не motion capture и не 3D. При включённых импортированных рисунках некоторых героев изменения поз могут быть незаметны.</p>
</div>
<div class="card">
 <h2>Непрерывный просмотр сцены и боя</h2>
 <canvas class="preview" id="v39-preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v39-play">Воспроизвести</button><button id="v39-first">В начало</button></div>
 <label>Таймкод всей серии <input id="v39-seek" type="range" min="0" max="1000" value="0"></label>
 <p class="muted" id="v39-time">Общая шкала V35</p>
 <p class="note">Кадр V39 включает прежнее цветовое оформление V38, субтитры V37 и все реальные сцены. При записи WebM со звуком через вкладку V36 используется этот же финальный рендер.</p>
</div>
<div class="card">
 <h2>Аудит постановки и контрольные материалы</h2>
 <div class="flex">
  <button id="v39-sheet">Скачать 4 настоящих кадра PNG</button>
  <button id="v39-json">Скачать настройки V39 JSON</button>
  <button id="v39-audit">Проверить сцены</button>
 </div>
 <pre class="report" id="v39-report" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
 <p class="muted">V39 не изменяет исход канонического боя. Эффекты «попадание» и «блок» рисуются только если событие уже присутствует в истории. Качественную 3D-анимацию требуется создавать отдельно.</p>
</div>
</section>
"""
def once(txt,needle,replacement):
 n=txt.count(needle)
 if n!=1:raise ValueError("V39 expected exactly 1 anchor, found "+str(n)+": "+repr(needle[:90]))
 return txt.replace(needle,replacement,1)
def previous():
 spec=importlib.util.spec_from_file_location("v38_builder",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,addon):
 if "function v39Move(" in html or 'id="page-performance-v39"' in html:
  raise ValueError("Already integrated V39")
 for old in ("function v24Dynamics(","function v13Face(","function v25Contact(",
  "function v35Plan(","function v36Schedule(","function v37Paint(",
  "function v38Frame(","function drawScene("):
  if old not in html:raise ValueError("V39 missing historical function "+old)
 html=once(html,'<button data-page="export">',
  '<button data-page="performance-v39">Персонажи и бой V39</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V38';",
  "const storageKey='AI_ANIME_FACTORY_V39';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:38,",
  "P={format:'AIAnimeFactoryProject',version:39,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V37')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V38')||localStorage.getItem('AI_ANIME_FACTORY_V37')")
 html=once(html,"if(page==='cinematic-v38')v38Show();",
  "if(page==='cinematic-v38')v38Show();if(page==='performance-v39')v39Show();")
 html=once(html,"v37Show();v38Show();}",
  "v37Show();v38Show();v39Show();}")
 html=once(html,
  "function show(page){if(page!=='cinematic-v38')v38Pause();",
  "function show(page){if(page!=='performance-v39')v39Pause();if(page!=='cinematic-v38')v38Pause();")
 html=once(html,"'AI ANIME FACTORY V38  •  CINEMATIC FINISHING'",
  "'AI ANIME FACTORY V39  •  CHARACTER ACTION / PERFORMANCE'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V38_CINEMATIC_FINISHING.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V39_CHARACTER_ACTION.html',data:selfHTML()},"+
  "{name:'V39_CHARACTER_PERFORMANCE.json',data:JSON.stringify(v39Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V38_CINEMATIC_FINISHING_Offline.html'",
  "'AI_Anime_Factory_V39_CHARACTER_ACTION_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<38)migrated.version=38;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<39)migrated.version=39;return migrated;}")
 # Canonical timeline and actual V36 recorder remain untouched. All animated
 # actors are generated by their historical render calls with V39 hooks.
 # Contact effects are inserted BEFORE V37 subtitles so text stays legible.
 html=once(html,
  "v37Paint(canvas,episode,sec);\n return state;",
  "v39Effects(ctx,state,w,h);\n v37Paint(canvas,episode,sec);\n return state;")
 html=once(html,
  "download('V38_CINEMATIC_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V39_CHARACTER_ACTION_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,
  "V38: кинематографическая серия WebM записана (",
  "V39: анимация персонажей и бой записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать кинематографическую серию V38</button>',
  '<button class="accent" id="v36-export">Записать V39 с движением персонажей</button>')
 # Declare v39 wrappers after all earlier functions and before project init.
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V38')||"
 html=once(html,anchor,"\n/* V39 TRUE CHARACTER RIG + ACTION */\n"+addon.strip()+
  "\n/* END V39 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();output=build()
 for token in ("function v39Move(","function v39Effects(","function v39Manifest(",
  "function v25Contact(","function v24Dynamics(","function v35Plan(",
  "function v38Frame(",'id="v39-preview"',"AI_ANIME_FACTORY_V39"):
  assert token in output,token
 assert V19.read_bytes()==original
 print("V39 BUILDER PASS",len(output.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--selftest",action="store_true")
 ap.add_argument("--output",default=str(OUTPUT))
 a=ap.parse_args()
 if a.selftest:selftest();return
 dst=Path(a.output).resolve()
 if dst==V19.resolve():raise ValueError("Refusing to overwrite original V19")
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(build(),encoding="utf-8")
 print("V39 HTML BUILT",dst,dst.stat().st_size)
if __name__=="__main__":main()
