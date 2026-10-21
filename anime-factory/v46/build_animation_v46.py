#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V46 Animation Engine build atop verified V45. Original V19–V45 preserved."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v45/build_art_engine_v45.py"
STUDIO=Path(__file__).with_name("animation_engine_v46.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V46_ANIMATION_ENGINE.html")
PANEL=r"""
<section class="page" id="page-animation-v46" hidden>
<div class="card">
 <h2>V46 — Animation Engine: настоящий таймлайн 2D-рига</h2>
 <p class="muted">Рисуемые слои персонажа V45 теперь имеют самостоятельные ключевые кадры и анимационные клипы. Вы управляете частью тела, ролью, точным временем, смещением, поворотом и масштабом. Все изменения попадают в исходный Canvas-рендер, экспорт PNG и WebM, не только в отдельную демо-вкладку. Поддержка рук, ног, головы, волос, плаща, корпуса и оружия.</p>
 <div class="grid">
  <div class="field"><label>Эпизод</label><select id="v46-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v46-scene"></select></div>
  <div class="field"><label>Анимируемый участник</label><select id="v46-role"><option value="hero">Главный персонаж</option><option value="partner">Второй персонаж</option></select></div>
  <div class="field"><label>Слой модели</label><select id="v46-part">
   <option value="arms">Руки</option><option value="legs">Ноги</option>
   <option value="torso">Корпус / одежда</option><option value="face">Голова / лицо</option>
   <option value="hair">Волосы</option><option value="cape">Ткань / плащ</option>
   <option value="weapon">Предмет / оружие</option>
  </select></div>
 </div>
 <label><input id="v46-enabled" type="checkbox" checked> Включить анимацию V46 для выбранной сцены</label>
 <div class="grid">
  <div class="field"><label>Готовое движение</label><select id="v46-action">
   <option value="walk">Ходьба</option><option value="guard">Защита</option>
   <option value="strike">Взмах / атака</option><option value="bow">Поклон</option>
   <option value="warmth">Тёплый жест / дружба</option>
  </select></div>
 </div>
 <button id="v46-action-apply" class="accent">Создать 35 настоящих ключей для выбранного персонажа</button>
 <p class="note">Анимационные жесты не создают сюжетные события, настоящие попадания или романтические решения. Исходы боя и отношения остаются определены предыдущими редакторами.</p>
</div>
<div class="card">
 <h2>Ключевой кадр — редактирование</h2>
 <label>Таймкод сцены <input id="v46-position" type="range" min="0" max="1000" value="0"></label>
 <p id="v46-key-count" class="muted">0 ключей</p>
 <label>Существующие ключи <select id="v46-key-list"></select></label>
 <div class="grid">
  <div class="field"><label>Смещение X</label><input id="v46-x" type="number" min="-70" max="70" step=".5" value="0"></div>
  <div class="field"><label>Смещение Y</label><input id="v46-y" type="number" min="-70" max="70" step=".5" value="0"></div>
  <div class="field"><label>Угол (градусы)</label><input id="v46-angle" type="number" min="-100" max="100" step=".5" value="0"></div>
  <div class="field"><label>Масштаб</label><input id="v46-scale" type="number" min=".6" max="1.4" step=".05" value="1"></div>
  <div class="field"><label>Интерполяция</label><select id="v46-ease">
   <option value="smooth">Плавно</option><option value="linear">Линейно</option><option value="hold">Удержание кадра</option>
  </select></div>
 </div>
 <div class="flex">
  <button id="v46-key-save" class="accent">Записать / обновить ключ</button>
  <button id="v46-key-remove">Удалить ключ на этом времени</button>
 </div>
</div>
<div class="card">
 <h2>Библиотека повторно используемых анимаций</h2>
 <div class="grid">
  <div class="field"><label>Название нового клипа</label><input id="v46-clip-name" placeholder="Поклон героя / ходьба / дружеский жест"></div>
  <div class="field"><label>Выбрать сохранённый клип</label><select id="v46-clip"></select></div>
 </div>
 <p id="v46-clip-count" class="muted">0 клипов</p>
 <div class="flex"><button id="v46-clip-save">Сохранить движения в библиотеку</button>
 <button id="v46-clip-apply">Применить клип к текущей сцене</button></div>
 <p class="note">Клип сохраняется в проекте как 7 независимых массивов ключей выбранного персонажа. Его можно перенести в другую сцену без перезаписи остальных персонажей и сюжета.</p>
</div>
<div class="card">
 <h2>Настоящий предпросмотр с соседними кадрами (onion skin)</h2>
 <canvas id="v46-preview" class="preview" width="640" height="360"></canvas>
 <label><input id="v46-onion" type="checkbox"> Показывать соседние реальные кадры полупрозрачно</label>
 <p id="v46-timestamp" class="muted"></p>
 <div class="flex"><button id="v46-play">Воспроизвести</button><button id="v46-first">В начало</button></div>
 <div class="flex">
  <button id="v46-frame">Четыре подлинные позы PNG</button>
  <button id="v46-json">Скачать библиотеку и ключи JSON</button>
  <button id="v46-audit">Проверить ключи</button>
 </div>
 <pre id="v46-report" class="report" style="white-space:pre-wrap;max-height:280px;overflow:auto"></pre>
 <p class="note">V46 — редактируемый cutout-аниматор и библиотека клипов. Полноценные фонемы и переносимые голоса — этап V47; массовый выпуск серий — V48; V49 UNIFIED; V50 глубокая QA. Это не 3D, не нейросетевое создание покадрового арта.</p>
</div>
</section>
"""
def once(src,a,b):
 count=src.count(a)
 if count!=1:raise ValueError("V46 builder expected 1 anchor, got "+str(count)+": "+repr(a[:110]))
 return src.replace(a,b,1)
def previous():
 spec=importlib.util.spec_from_file_location("v45_animation_parent",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,addon):
 if "function v46LayerMotion(" in html or 'id="page-animation-v46"' in html:
  raise ValueError("Duplicate V46")
 for term in ("function pose16Sample(","function drawProductionPerson(",
  "function v45GenerateLayers(","function v25Contact(","function v35Plan(",
  "function v36Schedule(","function v37Paint(","function v44Pose("):
  if term not in html:raise ValueError("Original V19–V45 missing: "+term)
 html=once(html,'<button data-page="export">',
  '<button data-page="animation-v46">2D Анимация V46</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V45';",
  "const storageKey='AI_ANIME_FACTORY_V46';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:45,",
  "P={format:'AIAnimeFactoryProject',version:46,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V44')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V45')||localStorage.getItem('AI_ANIME_FACTORY_V44')")
 html=once(html,"if(page==='art-assets-v45')v45Show();",
  "if(page==='art-assets-v45')v45Show();if(page==='animation-v46')v46Show();")
 html=once(html,"v44Show();v45Show();}","v44Show();v45Show();v46Show();}")
 html=once(html,"function show(page){if(page!=='keyposes-v44')v44Pause();",
  "function show(page){if(page!=='animation-v46')v46Pause();if(page!=='keyposes-v44')v44Pause();")
 html=once(html,
  "'AI ANIME FACTORY V45  •  ART ASSETS / PRODUCTION ENGINE'",
  "'AI ANIME FACTORY V46  •  KEYFRAME ANIMATION ENGINE'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V45_ART_ENGINE.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V46_ANIMATION_ENGINE.html',data:selfHTML()},"+
  "{name:'V46_ANIMATION_LIBRARY.json',data:JSON.stringify(v46Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V45_ART_ENGINE_Offline.html'",
  "'AI_Anime_Factory_V46_ANIMATION_ENGINE_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<45)migrated.version=45;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<46)migrated.version=46;return migrated;}")
 html=once(html,
  "download('V45_ART_ENGINE_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V46_ANIMATION_ENGINE_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V45: многослойные персонажи и фон записаны в WebM (",
  "V46: анимационные ключи и клипы записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V45 с настоящими 2D-слоями</button>',
  '<button class="accent" id="v36-export">Записать V46 с настоящей анимацией</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V45')||"
 html=once(html,anchor,
  "\n/* V46 TRUE POSE16 KEYFRAME ADDITIVE ENGINE */\n"+addon.strip()+
  "\n/* END V46 */\n"+anchor)
 return html
def build():return patch(previous().build(),STUDIO.read_text(encoding="utf-8"))
def selftest():
 orig=V19.read_bytes();html=build()
 for token in ("function v46LayerMotion(","pose16Sample=function(s,role,part,sec)",
  "function v46PresetAnimation(","function v46SaveClip(",
  "function v45DrawBackground(","function v25Contact(","AI_ANIME_FACTORY_V46",
  'id="page-animation-v46"'):
  assert token in html,token
 assert orig==V19.read_bytes()
 print("V46 HTML BUILD PASS",len(html.encode("utf-8")),hashlib.sha256(orig).hexdigest())
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--selftest",action="store_true")
 parser.add_argument("--output",default=str(OUTPUT))
 args=parser.parse_args()
 if args.selftest:selftest();return
 out=Path(args.output).resolve()
 if out==V19.resolve():raise ValueError("Refuse to overwrite V19")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V46 HTML",out,out.stat().st_size)
if __name__=="__main__":main()
