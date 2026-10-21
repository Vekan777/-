#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V40 genuine vector character artwork, layered on all original V19–V39 sources."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v39/build_performance_v39.py"
ADDON=Path(__file__).with_name("character_art_v40.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V40_CHARACTER_ART.html")
PANEL=r"""
<section class="page" id="page-character-art-v40" hidden>
<div class="card">
 <h2>V40 — Рисовка и художественные детали персонажей</h2>
 <p class="muted">Реальные изменения рисунка процедурных 2D-моделей: радужка глаз, блики, брови, форма прядей, воротник, защита плеч и костюмные элементы. Сохраняется канон персонажей V23, прежние движения V39, события боя, импортированные авторские PNG и история эпизодов.</p>
 <div class="grid">
  <div class="field"><label>Персонаж</label><select id="v40-character"></select></div>
  <div class="field"><label>Стиль рисовки</label><select id="v40-profile">
   <option value="dramatic">Кинематографичный</option>
   <option value="clean">Чистая аниме-линия</option>
   <option value="ornate">Детализированное фэнтези</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v40-enabled" checked> Включить улучшенную рисовку V40</label>
 <div class="grid">
  <div class="field"><label>Глаза и мимические детали <span id="v40-label-eyes">88</span>%</label><input type="range" id="v40-eyes" min="0" max="100"></div>
  <div class="field"><label>Пряди и движение волос <span id="v40-label-hair">82</span>%</label><input type="range" id="v40-hair" min="0" max="100"></div>
  <div class="field"><label>Детализация костюма <span id="v40-label-costume">78</span>%</label><input type="range" id="v40-costume" min="0" max="100"></div>
  <div class="field"><label>Контуры и читаемость <span id="v40-label-line">72</span>%</label><input type="range" id="v40-line" min="0" max="100"></div>
  <div class="field"><label>Световые акценты <span id="v40-label-shine">65</span>%</label><input type="range" id="v40-shine" min="0" max="100"></div>
 </div>
 <button class="accent" id="v40-save">Сохранить художественный стиль персонажа</button>
 <p class="note">Новые детали относятся только к встроенной векторной модели. Пользовательские PNG/PSD не изменяются и автоматически не превращаются в 3D или полноценный скелетный риг.</p>
</div>
<div class="card">
 <h2>Настоящее сравнение до / после</h2>
 <div class="grid">
  <div class="field"><label>Оригинальный векторный персонаж</label><canvas class="preview" id="v40-before" width="640" height="360"></canvas></div>
  <div class="field"><label>Улучшенная рисовка V40</label><canvas class="preview" id="v40-after" width="640" height="360"></canvas></div>
 </div>
 <label>Момент сцены <input id="v40-time" type="range" min="0" max="100" value="35"></label>
 <p class="muted" id="v40-caption">Выберите персонажа и сравните один таймкод.</p>
 <div class="flex">
  <button id="v40-sheet">Скачать 4 настоящих кадра PNG</button>
  <button id="v40-json">Скачать настройки персонажей JSON</button>
  <button id="v40-audit">Проверить рисовку</button>
 </div>
 <pre id="v40-report" class="report" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
 <p class="note">Реальное изображение V40 участвует в прежнем предпросмотре V35–V39 и в записи WebM через вкладку V36. Изменения ограничены поддерживаемыми зонами векторных моделей.</p>
</div>
</section>
"""
def once(txt,old,new):
 n=txt.count(old)
 if n!=1:raise ValueError("V40 expected one anchor, got "+str(n)+": "+repr(old[:100]))
 return txt.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("v39_builder",BASE)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def patch(html,addon):
 if 'id="page-character-art-v40"' in html or "function v40FaceInk(" in html:
  raise ValueError("Already V40")
 for mark in ("function v23FaceForm(","function v23HairForm(","function v23CostumeForm(",
  "function v39Move(","function v38Frame(","function v37Paint(",
  "function v36Schedule(","function v35Plan(","function drawScene("):
  if mark not in html:raise ValueError("Missing original historical module: "+mark)
 html=once(html,'<button data-page="export">',
  '<button data-page="character-art-v40">Рисовка V40</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V39';",
  "const storageKey='AI_ANIME_FACTORY_V40';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:39,",
  "P={format:'AIAnimeFactoryProject',version:40,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V38')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V39')||localStorage.getItem('AI_ANIME_FACTORY_V38')")
 html=once(html,"if(page==='performance-v39')v39Show();",
  "if(page==='performance-v39')v39Show();if(page==='character-art-v40')v40Show();")
 html=once(html,"v38Show();v39Show();}",
  "v38Show();v39Show();v40Show();}")
 html=once(html,
  "function show(page){if(page!=='performance-v39')v39Pause();",
  "function show(page){if(page!=='performance-v39')v39Pause();")
 html=once(html,"'AI ANIME FACTORY V39  •  CHARACTER ACTION / PERFORMANCE'",
  "'AI ANIME FACTORY V40  •  CHARACTER ART / DRAWING'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V39_CHARACTER_ACTION.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V40_CHARACTER_ART.html',data:selfHTML()},"+
  "{name:'V40_CHARACTER_ART.json',data:JSON.stringify(v40Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V39_CHARACTER_ACTION_Offline.html'",
  "'AI_Anime_Factory_V40_CHARACTER_ART_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<39)migrated.version=39;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<40)migrated.version=40;return migrated;}")
 html=once(html,
  "download('V39_CHARACTER_ACTION_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V40_CHARACTER_ART_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,
  "V39: анимация персонажей и бой записаны в WebM (",
  "V40: улучшенная рисовка персонажей записана в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V39 с движением персонажей</button>',
  '<button class="accent" id="v36-export">Записать V40 с улучшенной рисовкой</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V39')||"
 html=once(html,anchor,"\n/* V40 NEW VECTOR CHARACTER ART */\n"+addon.strip()+
  "\n/* END V40 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 before=V19.read_bytes();new=build()
 for mark in ("function v40FaceInk(","function v40HairInk(","function v40CostumeInk(",
  "function v39Move(","function v38Frame(","function v37Paint(",
  "function v35Plan(","AI_ANIME_FACTORY_V40",'id="v40-after"'):
  assert mark in new,mark
 assert before==V19.read_bytes()
 print("V40 BUILDER PASS",len(new.encode("utf-8")),hashlib.sha256(before).hexdigest())
def main():
 args=argparse.ArgumentParser()
 args.add_argument("--selftest",action="store_true")
 args.add_argument("--output",default=str(OUTPUT))
 a=args.parse_args()
 if a.selftest:selftest();return
 out=Path(a.output).resolve()
 if out==V19.resolve():raise ValueError("Refusing to overwrite V19")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V40 HTML BUILT",out,out.stat().st_size)
if __name__=="__main__":main()
