#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build actual V45 cutout art editor + modular shared engine over V44."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v44/build_keyposes_v44.py"
STUDIO=Path(__file__).with_name("art_assets_v45.js")
ENGINE=ROOT/"anime-factory/engine/anime_production_engine_v45.js"
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V45_ART_ENGINE.html")
PANEL=r"""
<section class="page" id="page-art-assets-v45" hidden>
<div class="card">
 <h2>V45 — Аниме-художник: многослойные 2D-персонажи</h2>
 <p class="muted">Создайте реальный PNG-комплект из 7 частей существующего персонажа либо импортируйте собственные прозрачные PNG/WebP/JPEG. Каждая часть может перемещаться, поворачиваться и имеет редактируемую точку поворота. Сохранённые слои используются в общем рендере V19–V44, а не только в отдельном предпросмотре.</p>
 <div class="grid">
  <div class="field"><label>Персонаж</label><select id="v45-character"></select></div>
  <div class="field"><label>Слой</label><select id="v45-layer">
   <option value="legs">Ноги</option><option value="cape">Ткань / плащ</option>
   <option value="torso">Корпус и одежда</option><option value="arms">Руки</option>
   <option value="face">Лицо и рот</option><option value="hair">Волосы</option>
   <option value="weapon">Оружие / предмет</option>
  </select></div>
 </div>
 <div class="flex">
  <button class="accent" id="v45-make">Создать 7 прозрачных PNG из встроенного рига</button>
  <button id="v45-import" onclick="document.getElementById('v45-file').click()">Импорт PNG/WebP/JPEG слоя</button>
  <input id="v45-file" type="file" accept=".png,.webp,.jpg,.jpeg,image/png,image/webp,image/jpeg" hidden>
 </div>
 <div class="field"><label>Автор и право на иллюстрации</label><input id="v45-rights" placeholder="Авторская работа / источник и лицензия"></div>
 <div class="grid">
  <div class="field"><label>Смещение слоя X</label><input id="v45-x" type="number" min="-100" max="100" value="0"></div>
  <div class="field"><label>Смещение слоя Y</label><input id="v45-y" type="number" min="-100" max="100" value="0"></div>
  <div class="field"><label>Масштаб (0.5–1.5)</label><input id="v45-scale" type="number" min=".5" max="1.5" step=".05" value="1"></div>
  <div class="field"><label>Поворот слоя (градусы)</label><input id="v45-angle" type="number" min="-45" max="45" value="0"></div>
  <div class="field"><label>Точка поворота X</label><input id="v45-pivot-x" type="number" min="-125" max="125" value="0"></div>
  <div class="field"><label>Точка поворота Y</label><input id="v45-pivot-y" type="number" min="-260" max="260" value="0"></div>
  <div class="field"><label>Доп. угол вокруг точки</label><input id="v45-pivot-angle" type="number" min="-120" max="120" value="0"></div>
 </div>
 <button class="accent" id="v45-save">Сохранить слой и точку поворота</button>
 <p id="v45-status" class="muted"></p>
 <p class="note">PNG хранятся внутри экспортируемого JSON как данные. Исходный формат импортируемого изображения переводится в PNG 640×960. Важен комплект отдельных изображений: одна плоская PNG не превращается автоматически в полностью анимированного персонажа.</p>
</div>
<div class="card">
 <h2>Локации, фоны и художественная постановка</h2>
 <div class="field"><label>Выберите конкретную сцену для фона и предпросмотра</label><select id="v45-scene"></select></div>
 <p>Смените текущую сцену в прежнем редакторе «Сценарии» или «Анимация», затем загрузите фон; импорт встроен в рендер всех эпизодов.</p>
 <div class="flex">
  <button id="v45-bg-import" onclick="document.getElementById('v45-bg-file').click()">Загрузить фон PNG/WebP/JPEG</button>
  <input id="v45-bg-file" type="file" accept=".png,.webp,.jpg,.jpeg,image/png,image/webp,image/jpeg" hidden>
 </div>
 <label><input id="v45-use-bg" type="checkbox"> Использовать импортированный фон</label>
 <div class="field"><label>Автор / лицензия фонового изображения</label><input id="v45-background-rights" placeholder="Мой фон / CC BY с указанием автора"></div>
 <button id="v45-bg-save">Сохранить оформление фона</button>
 <p id="v45-background-status" class="muted"></p>
</div>
<div class="card">
 <h2>Настоящие кадры и переносимый проект</h2>
 <canvas class="preview" id="v45-preview" width="640" height="360"></canvas>
 <label>Фаза сцены <input id="v45-time" type="range" min="0" max="100" value="30"></label>
 <p id="v45-timestamp" class="muted"></p>
 <div class="flex">
  <button id="v45-frame">Четыре реальных кадра PNG</button>
  <button id="v45-project">Скачать ПОЛНЫЙ JSON с изображениями</button>
  <button id="v45-plan">Паспорт Anime Production Engine</button>
  <button id="v45-audit">Аудит персонажей и событий</button>
 </div>
 <pre id="v45-report" class="report" style="white-space:pre-wrap;max-height:360px;overflow:auto"></pre>
 <p class="note">На данном этапе ядро движка планирует сценарии, миры, взаимоотношения, боевые события и ракурсы. Полноценная покадровая анимация V46, переносимая озвучка V47 и сборка сезонов V48 планируются далее. Профессиональное качество арта требует авторских материалов и ручной проверки.</p>
</div>
</section>
"""
def once(s,needle,replacement):
 count=s.count(needle)
 if count!=1:raise ValueError("V45 anchor occurrences "+str(count)+": "+repr(needle[:105]))
 return s.replace(needle,replacement,1)
def previous():
 spec=importlib.util.spec_from_file_location("v44_art_parent",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,engine,studio):
 if "function v45DrawBackground(" in html or 'id="page-art-assets-v45"' in html:
  raise ValueError("Duplicate V45 integration")
 for item in ("function drawScene(","function drawProductionPerson(",
  "function v24Dynamics(","function v35Plan(","function v36Schedule(",
  "function v44Pose(","function productionOf(","function drawBG("):
  if item not in html:raise ValueError("Missing historical rendering function "+item)
 html=once(html,'<button data-page="export">',
  '<button data-page="art-assets-v45">2D Арт и движок V45</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V44';",
  "const storageKey='AI_ANIME_FACTORY_V45';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:44,",
  "P={format:'AIAnimeFactoryProject',version:45,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V43')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V44')||localStorage.getItem('AI_ANIME_FACTORY_V43')")
 html=once(html,"if(page==='keyposes-v44')v44Show();",
  "if(page==='keyposes-v44')v44Show();if(page==='art-assets-v45')v45Show();")
 html=once(html,"v43Show();v44Show();}","v43Show();v44Show();v45Show();}")
 html=once(html,
  "'AI ANIME FACTORY V44  •  TRUE ACTOR KEYPOSES'",
  "'AI ANIME FACTORY V45  •  ART ASSETS / PRODUCTION ENGINE'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V44_TRUE_KEYPOSES.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V45_ART_ENGINE.html',data:selfHTML()},"+
  "{name:'V45_ENGINE_PRODUCTION_PLAN.json',data:JSON.stringify(v45EngineSnapshot(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V44_TRUE_KEYPOSES_Offline.html'",
  "'AI_Anime_Factory_V45_ART_ENGINE_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<44)migrated.version=44;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<45)migrated.version=45;return migrated;}")
 html=once(html,"download('V44_TRUE_KEYPOSES_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V45_ART_ENGINE_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V44: настоящие позы и работа ног записаны в WebM (",
  "V45: многослойные персонажи и фон записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V44 с позами персонажей</button>',
  '<button class="accent" id="v36-export">Записать V45 с настоящими 2D-слоями</button>')
 # Actual painted frame: use imported background before V19 near/far effects.
 html=once(html,
  "drawBG(g,w,h,s.background,sec,q.lighting,q.effects);cin14Layers(g,w,h,s,sec,'far');",
  "if(!v45DrawBackground(g,w,h,s,sec))drawBG(g,w,h,s.background,sec,q.lighting,q.effects);cin14Layers(g,w,h,s,sec,'far');")
 # Only injected in the true V15 cutout drawing path; modifies actual PNG layer pivot.
 html=once(html,
  "g.translate(ox+(Number(p.x)||0),oy+(Number(p.y)||0));g.rotate(rot);const k=clamp(Number(p.scale)||1,.5,1.5);g.scale(k,k);g.translate(-ox,-oy);",
  "g.translate(ox+(Number(p.x)||0),oy+(Number(p.y)||0));g.rotate(rot);"+
  "const pv45=v45PivotFor(c,name);g.translate(pv45.x,pv45.y);"+
  "g.rotate(pv45.angle*Math.PI/180);g.translate(-pv45.x,-pv45.y);"+
  "const k=clamp(Number(p.scale)||1,.5,1.5);g.scale(k,k);g.translate(-ox,-oy);")
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V44')||"
 html=once(html,anchor,
  "\n/* V45 MODULAR ANIME PRODUCTION ENGINE */\n"+engine.strip()+
  "\n/* V45 ASSET STUDIO / TRUE CUTOUT RENDER */\n"+studio.strip()+
  "\n/* END V45 */\n"+anchor)
 return html
def build():
 return patch(previous().build(),
  ENGINE.read_text(encoding="utf-8"),STUDIO.read_text(encoding="utf-8"))
def selftest():
 old=V19.read_bytes();result=build()
 for name in ("function v45DrawBackground(","const AnimeProductionEngineV45=",
  "function v45GenerateLayers(","function v44Pose(","function v25Contact(",
  "if(!v45DrawBackground(","v45PivotFor(c,name)","AI_ANIME_FACTORY_V45",
  'id="page-art-assets-v45"'):
  assert name in result,name
 assert V19.read_bytes()==old
 print("V45 ADDITIVE BUILD",len(result.encode()),hashlib.sha256(old).hexdigest())
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--selftest",action="store_true")
 parser.add_argument("--output",default=str(OUTPUT))
 args=parser.parse_args()
 if args.selftest:selftest();return
 target=Path(args.output).resolve()
 if target==V19.resolve():raise ValueError("Refuse to overwrite V19")
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(build(),encoding="utf-8")
 print("V45 HTML",target,target.stat().st_size)
if __name__=="__main__":main()
