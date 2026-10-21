#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Anime Factory V42 stage depth/light/weather, non-destructive V19–V41 extension."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v41/build_silhouette_v41.py"
ADDON=Path(__file__).with_name("stage_v42.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V42_STAGE_DEPTH.html")
PANEL=r"""
<section class="page" id="page-stage-v42" hidden>
<div class="card">
 <h2>V42 — Глубина окружения, свет и атмосфера сцены</h2>
 <p class="muted">Настоящие 2D-слои дальнего окружения, направленный свет, атмосферная дымка и частицы, привязанные к таймкоду эпизода. Эффекты боевого контакта возникают только при существующем попадании или блоке V25. Персонажи V41, сюжет и аудио остаются неизменными.</p>
 <div class="grid">
  <div class="field"><label>Серия</label><select id="v42-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v42-scene"></select></div>
  <div class="field"><label>Свет и погода</label><select id="v42-preset">
   <option value="dawn">Рассвет и тёплый свет</option>
   <option value="storm">Гроза и дождь</option>
   <option value="ember">Тлеющие угли</option>
   <option value="moon">Лунная ночь</option>
  </select></div>
 </div>
 <label><input id="v42-enabled" type="checkbox" checked> Включить V42 оформление сцены</label>
 <div class="grid">
  <div class="field"><label>Глубина слоёв <span id="v42-label-depth">48</span>%</label><input id="v42-depth" type="range" min="0" max="100"></div>
  <div class="field"><label>Направленный свет <span id="v42-label-light">65</span>%</label><input id="v42-light" type="range" min="0" max="100"></div>
  <div class="field"><label>Атмосфера и дымка <span id="v42-label-atmosphere">24</span>%</label><input id="v42-atmosphere" type="range" min="0" max="100"></div>
  <div class="field"><label>Дождь / искры <span id="v42-label-particles">16</span>%</label><input id="v42-particles" type="range" min="0" max="100"></div>
  <div class="field"><label>Сила ветра <span id="v42-label-wind">22</span>%</label><input id="v42-wind" type="range" min="0" max="100"></div>
 </div>
 <button class="accent" id="v42-save">Сохранить постановку сцены</button>
 <p class="note">Настройки сохраняются только в stageV42 конкретной сцены. Сюжет, импортированные PNG, персонажи, музыка и субтитры не переписываются. Это 2D-свет/атмосфера поверх готового кадра, не настоящий 3D-рендер.</p>
</div>
<div class="card">
 <h2>Непрерывный предпросмотр на общей шкале серии</h2>
 <canvas class="preview" id="v42-preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v42-play">Воспроизвести</button><button id="v42-first">В начало</button></div>
 <label>Таймкод <input id="v42-seek" type="range" min="0" max="1000" value="0"></label>
 <p class="muted" id="v42-time">Реальное время из сборки V35</p>
 <p class="note">Все V42 эффекты входят в реальное WebM со звуком при записи на вкладке «Звук / экспорт V36». Текст субтитров V37 дополнительно рисуется поверх атмосферы, чтобы оставаться читаемым.</p>
</div>
<div class="card">
 <h2>Аудит и настоящие контрольные кадры</h2>
 <div class="flex">
  <button id="v42-sheet">Скачать 4 реальных кадра PNG</button>
  <button id="v42-json">Скачать JSON V42</button>
  <button id="v42-audit">Проверить читаемость</button>
 </div>
 <pre id="v42-report" class="report" style="white-space:pre-wrap;max-height:320px;overflow:auto"></pre>
</div>
</section>
"""
def once(body,needle,replacement):
 n=body.count(needle)
 if n!=1:raise ValueError("V42 expected 1 anchor, got "+str(n)+": "+repr(needle[:105]))
 return body.replace(needle,replacement,1)
def previous():
 spec=importlib.util.spec_from_file_location("v41_stage_base",BASE)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module
def patch(html,addon):
 if "function v42Layers(" in html or 'id="page-stage-v42"' in html:
  raise ValueError("Already patched V42")
 for token in ("function v25Contact(","function v35Plan(","function v36Schedule(",
  "function v37Paint(","function v38Frame(","function v39Move(",
  "function v40FaceInk(","function v41Cape(","function drawScene("):
  if token not in html:raise ValueError("Original V19–V41 lost: "+token)
 html=once(html,'<button data-page="export">',
  '<button data-page="stage-v42">Свет и атмосфера V42</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V41';",
  "const storageKey='AI_ANIME_FACTORY_V42';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:41,",
  "P={format:'AIAnimeFactoryProject',version:42,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V40')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V41')||localStorage.getItem('AI_ANIME_FACTORY_V40')")
 html=once(html,"if(page==='silhouette-v41')v41Show();",
  "if(page==='silhouette-v41')v41Show();if(page==='stage-v42')v42Show();")
 html=once(html,"v40Show();v41Show();}","v40Show();v41Show();v42Show();}")
 html=once(html,
  "function show(page){if(page!=='performance-v39')v39Pause();",
  "function show(page){if(page!=='stage-v42')v42Pause();if(page!=='performance-v39')v39Pause();")
 html=once(html,"'AI ANIME FACTORY V41  •  CHARACTER SILHOUETTES / COSTUMES'",
  "'AI ANIME FACTORY V42  •  SCENE DEPTH / LIGHTING'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V42_STAGE_DEPTH.html',data:selfHTML()},"+
  "{name:'V42_STAGE_DEPTH.json',data:JSON.stringify(v42Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V41_SILHOUETTE_STUDIO_Offline.html'",
  "'AI_Anime_Factory_V42_STAGE_DEPTH_Offline.html'")
 html=once(html,"function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<41)migrated.version=41;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<42)migrated.version=42;return migrated;}")
 html=once(html,"download('V41_SILHOUETTE_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V42_STAGE_DEPTH_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V41: новый силуэт персонажей записан в WebM (",
  "V42: свет и глубина окружения записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V41 с силуэтами и костюмами</button>',
  '<button class="accent" id="v36-export">Записать V42 с атмосферой и светом</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V41')||"
 html=once(html,anchor,"\n/* V42 STAGE LIGHTING AND ATMOSPHERE */\n"+addon.strip()+
  "\n/* END V42 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 old=V19.read_bytes();new=build()
 for token in ("function v42Layers(","v38Frame=function(",
  "function v41Cape(","function v40FaceInk(","function v39Move(",
  "function v37Paint(","function v35Plan(","AI_ANIME_FACTORY_V42",
  'id="page-stage-v42"'):
  assert token in new,token
 assert V19.read_bytes()==old
 print("V42 NON-DESTRUCTIVE BUILD",len(new.encode("utf-8")),hashlib.sha256(old).hexdigest())
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--selftest",action="store_true")
 parser.add_argument("--output",default=str(OUTPUT))
 args=parser.parse_args()
 if args.selftest:selftest();return
 dest=Path(args.output).resolve()
 if dest==V19.resolve():raise ValueError("Cannot modify original V19")
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(build(),encoding="utf-8")
 print("V42 HTML BUILT",dest,dest.stat().st_size)
if __name__=="__main__":main()
