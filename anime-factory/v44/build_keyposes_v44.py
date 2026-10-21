#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V44 key-pose motion system, non-destructive addition over all V19–V43."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v43/build_director_v43.py"
ADDON=Path(__file__).with_name("keyposes_v44.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V44_TRUE_KEYPOSES.html")
PANEL=r"""
<section class="page" id="page-keyposes-v44" hidden>
<div class="card">
 <h2>V44 — Настоящие позы, стойка и движение конечностей</h2>
 <p class="muted">Новое дополнение к действующему процедурному 2D-ригу: опорные ноги, работа рук, перенос веса, боевая стойка, подготовка, выпад, защита и реакция. Преобразования применяются при реальном рисовании персонажей внутри функций V24/V39. Это не изображение эффекта поверх готового кадра и не создание новых боевых событий.</p>
 <div class="grid">
  <div class="field"><label>Эпизод</label><select id="v44-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v44-scene"></select></div>
  <div class="field"><label>Тип боевой пластики</label><select id="v44-profile">
   <option value="grounded">Устойчивая стойка</option>
   <option value="agile">Быстрый и подвижный</option>
   <option value="powerful">Тяжёлый удар</option>
  </select></div>
 </div>
 <label><input id="v44-enabled" type="checkbox" checked> Включить дополнительный риг V44</label>
 <div class="grid">
  <div class="field"><label>Опорная стойка <span id="v44-label-stance">85</span>%</label><input id="v44-stance" type="range" min="0" max="100"></div>
  <div class="field"><label>Размах и выпад рук <span id="v44-label-reach">58</span>%</label><input id="v44-reach" type="range" min="0" max="100"></div>
  <div class="field"><label>Защита и блок <span id="v44-label-guard">74</span>%</label><input id="v44-guard" type="range" min="0" max="100"></div>
  <div class="field"><label>Инерция после движения <span id="v44-label-recovery">64</span>%</label><input id="v44-recovery" type="range" min="0" max="100"></div>
  <div class="field"><label>Работа ног <span id="v44-label-steps">76</span>%</label><input id="v44-steps" type="range" min="0" max="100"></div>
  <div class="field"><label>Волосы и ткань <span id="v44-label-secondary">48</span>%</label><input id="v44-secondary" type="range" min="0" max="100"></div>
 </div>
 <button class="accent" id="v44-save">Сохранить настоящие позы сцены</button>
 <p class="note">V44 меняет только keyposesV44 в выбранной сцене. История, исходы боёв, данные V19–V43 и пользовательские PNG остаются нетронутыми. Статичная авторская PNG-картинка не становится автоматически скелетированной.</p>
</div>
<div class="card">
 <h2>Предпросмотр всей серии и живое движение рига</h2>
 <canvas class="preview" id="v44-preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v44-play">Воспроизвести</button><button id="v44-first">В начало</button></div>
 <label>Таймкод серии V35 <input id="v44-seek" type="range" min="0" max="1000" value="0"></label>
 <p class="muted" id="v44-time">Текущая сцена и подлинная оценка исхода боя</p>
 <p class="note">Возможность записать WebM со звуком сохранена во вкладке «Звук / экспорт V36». Кадры используют движения V44, V43 камеру, V42 свет, V41 модели и субтитры V37.</p>
</div>
<div class="card">
 <h2>До/после и контроль сценария</h2>
 <div class="flex">
  <button id="v44-sheet">PNG: две позы до и после</button>
  <button id="v44-json">Полный план V44 JSON</button>
  <button id="v44-audit">Проверка постановки</button>
 </div>
 <pre class="report" id="v44-report" style="white-space:pre-wrap;max-height:340px;overflow:auto"></pre>
 <p class="note">В PNG 2×2 на верхней строке одна поза до/после V44, на нижней — другая поза до/после. Рендер выполняется на настоящем Canvas с прежними эффектами.</p>
</div>
</section>
"""
def once(src,a,b):
 count=src.count(a)
 if count!=1:raise ValueError("V44 anchor count "+str(count)+": "+repr(a[:100]))
 return src.replace(a,b,1)
def previous():
 spec=importlib.util.spec_from_file_location("v43_keypose_parent",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,script):
 if "function v44Pose(" in html or 'id="page-keyposes-v44"' in html:
  raise ValueError("Duplicate V44")
 for term in ("function v24Dynamics(","function v24FootPose(","function v25Contact(",
  "function v35Plan(","function v36Schedule(","function v37Paint(",
  "function v39Move(","function v42Layers(","function v43Shot("):
  if term not in html:raise ValueError("Historical source missing: "+term)
 html=once(html,'<button data-page="export">',
  '<button data-page="keyposes-v44">Позы персонажей V44</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V43';",
  "const storageKey='AI_ANIME_FACTORY_V44';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:43,",
  "P={format:'AIAnimeFactoryProject',version:44,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V42')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V43')||localStorage.getItem('AI_ANIME_FACTORY_V42')")
 html=once(html,"if(page==='action-v43')v43Show();",
  "if(page==='action-v43')v43Show();if(page==='keyposes-v44')v44Show();")
 html=once(html,"v42Show();v43Show();}","v42Show();v43Show();v44Show();}")
 html=once(html,"function show(page){if(page!=='action-v43')v43Pause();",
  "function show(page){if(page!=='keyposes-v44')v44Pause();if(page!=='action-v43')v43Pause();")
 html=once(html,
  "'AI ANIME FACTORY V43  •  ACTION CAMERA DIRECTOR'",
  "'AI ANIME FACTORY V44  •  TRUE ACTOR KEYPOSES'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V43_ACTION_DIRECTOR.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V44_TRUE_KEYPOSES.html',data:selfHTML()},"+
  "{name:'V44_ACTOR_KEYPOSES.json',data:JSON.stringify(v44Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V43_ACTION_DIRECTOR_Offline.html'",
  "'AI_Anime_Factory_V44_TRUE_KEYPOSES_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<43)migrated.version=43;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<44)migrated.version=44;return migrated;}")
 html=once(html,"download('V43_ACTION_DIRECTOR_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V44_TRUE_KEYPOSES_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V43: постановка боевого кадра записана в WebM (",
  "V44: настоящие позы и работа ног записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V43 с постановкой боя</button>',
  '<button class="accent" id="v36-export">Записать V44 с позами персонажей</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V43')||"
 html=once(html,anchor,"\n/* V44 ACTOR RIG / TRUE DRAW-TIME KEYPOSES */\n"+
  script.strip()+"\n/* END V44 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();html=build()
 for term in ("function v44Pose(","v24Dynamics=function(","v24FootPose=function(",
  "function v43Shot(","function v42Layers(","function v39Move(",
  "function v35Plan(","AI_ANIME_FACTORY_V44",'id="page-keyposes-v44"'):
  assert term in html,term
 assert V19.read_bytes()==original
 print("V44 NON-DESTRUCTIVE BUILD",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--output",default=str(OUTPUT))
 a=p.parse_args()
 if a.selftest:selftest();return
 out=Path(a.output).resolve()
 if out==V19.resolve():raise ValueError("Will not overwrite source V19")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V44 HTML",out,out.stat().st_size)
if __name__=="__main__":main()
