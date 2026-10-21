#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Additive V38 camera + color finishing layered on original V19–V37 HTML."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v37"/"build_subtitles_v37.py"
ADDON=Path(__file__).with_name("cinematic_v38.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V38_CINEMATIC_FINISHING.html")
PANEL=r"""
<section class="page" id="page-cinematic-v38" hidden>
<div class="card">
 <h2>V38 — Кинематографическая камера и цвет</h2>
 <p class="muted">Настоящее увеличение/панорамирование и цветокоррекция кадров Canvas. Настройки каждой сцены хранятся отдельно в cameraV38 — без изменения оригинальных персонажей, боя, сюжета, звука, длительности и субтитров.</p>
 <div class="grid">
  <div class="field"><label>Серия</label><select id="v38-episode"></select></div>
  <div class="field"><label>Кадр/сцена</label><select id="v38-scene"></select></div>
  <div class="field"><label>Цветовой пресет</label><select id="v38-preset">
   <option value="cinematic">Аниме-кино</option>
   <option value="neutral">Нейтральный</option>
   <option value="sunset">Закат</option>
   <option value="moonlight">Лунный свет</option>
   <option value="vivid">Яркий аниме-кадр</option>
  </select></div>
 </div>
 <p class="note">Измените нужный параметр и нажмите «Сохранить кадр». Пресет цвета применяется сразу к выбранной сцене.</p>
 <div class="grid">
  <div class="field"><label>Крупность камеры — начало <span id="v38-n-zoomStart"></span></label><input type="range" id="v38-zoomStart" min="1" max="1.3" step=".01"></div>
  <div class="field"><label>Крупность камеры — конец <span id="v38-n-zoomEnd"></span></label><input type="range" id="v38-zoomEnd" min="1" max="1.3" step=".01"></div>
  <div class="field"><label>Панорамирование — начало <span id="v38-n-panStart"></span></label><input type="range" id="v38-panStart" min="-1" max="1" step=".05"></div>
  <div class="field"><label>Панорамирование — конец <span id="v38-n-panEnd"></span></label><input type="range" id="v38-panEnd" min="-1" max="1" step=".05"></div>
  <div class="field"><label>Яркость <span id="v38-n-brightness"></span></label><input type="range" id="v38-brightness" min=".6" max="1.5" step=".01"></div>
  <div class="field"><label>Контраст <span id="v38-n-contrast"></span></label><input type="range" id="v38-contrast" min=".6" max="1.5" step=".01"></div>
  <div class="field"><label>Насыщенность <span id="v38-n-saturation"></span></label><input type="range" id="v38-saturation" min="0" max="2" step=".02"></div>
  <div class="field"><label>Температура цвета <span id="v38-n-warmth"></span></label><input type="range" id="v38-warmth" min="-50" max="50" step="2"></div>
  <div class="field"><label>Затемнение краёв <span id="v38-n-vignette"></span></label><input type="range" id="v38-vignette" min="0" max=".65" step=".01"></div>
 </div>
 <label><input id="v38-letterbox" type="checkbox"> Киношные полосы (2.39:1 приближённо)</label>
 <button class="accent" id="v38-save">Сохранить камеру и цвет сцены</button>
</div>
<div class="card">
 <h2>Реальный предпросмотр кинематографической серии</h2>
 <canvas id="v38-preview" class="preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v38-play">Воспроизвести</button><button id="v38-first">В начало</button></div>
 <label>Положение на общей шкале V35 <input id="v38-seek" type="range" min="0" max="1000" value="0"></label>
 <p id="v38-time" class="muted">Выберите серию</p>
 <p class="note">Финальная картинка V38 используется и в записываемом WebM вкладки «Звук / экспорт V36». Субтитры V37 накладываются после обработки цвета — текст сохраняет читаемость. Для MP4 используйте FFmpeg из инструкции.</p>
</div>
<div class="card">
 <h2>Контроль изображения и технической сборки</h2>
 <div class="flex">
  <button id="v38-sheet">Скачать 4 реальных кадра PNG</button>
  <button id="v38-json">Скачать JSON-план V38</button>
  <button id="v38-audit">Проверить кинематографию</button>
 </div>
 <pre id="v38-report" class="report" style="white-space:pre-wrap;max-height:310px;overflow:auto"></pre>
 <p class="muted">Функции V38 создают движение виртуальной камеры в процедурном 2D-кадре. Это не профессиональный 3D-рендер и не нейросетевое улучшение нарисованных персонажей. Художественный результат нужно оценивать по настоящим кадрам.</p>
</div>
</section>
"""
def once(body,old,new):
 if body.count(old)!=1:raise ValueError("V38 anchor count "+str(body.count(old))+": "+old[:95])
 return body.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("anime_v37_builder",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,addon):
 if "function v38Frame(" in html or 'id="page-cinematic-v38"' in html:
  raise ValueError("Already applied V38")
 for mark in ("function v37Paint(","function v37DrawFrame(","function v36Schedule(",
  "function v35Frame(","function v35Plan(","function v34Review(",
  "function v33Act(","function drawScene("):
  if mark not in html:raise ValueError("Previous feature absent: "+mark)
 html=once(html,'<button data-page="export">',
  '<button data-page="cinematic-v38">Кинокамера V38</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V37';",
  "const storageKey='AI_ANIME_FACTORY_V38';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:37,",
  "P={format:'AIAnimeFactoryProject',version:38,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V36')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V37')||localStorage.getItem('AI_ANIME_FACTORY_V36')")
 html=once(html,
  "if(page==='subtitles-v37')v37Show();",
  "if(page==='subtitles-v37')v37Show();if(page==='cinematic-v38')v38Show();")
 html=once(html,"v36Show();v37Show();}",
  "v36Show();v37Show();v38Show();}")
 html=once(html,
  "function show(page){if(page!=='subtitles-v37')v37Pause();",
  "function show(page){if(page!=='cinematic-v38')v38Pause();if(page!=='subtitles-v37')v37Pause();")
 html=once(html,"'AI ANIME FACTORY V37  •  SUBTITLES / DELIVERY'",
  "'AI ANIME FACTORY V38  •  CINEMATIC FINISHING'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V38_CINEMATIC_FINISHING.html',data:selfHTML()},"+
  "{name:'V38_CINEMATIC_FINISHING.json',data:JSON.stringify(v38Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V37_SUBTITLES_DELIVERY_Offline.html'",
  "'AI_Anime_Factory_V38_CINEMATIC_FINISHING_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<37)migrated.version=37;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<38)migrated.version=38;return migrated;}")
 # Reuse the genuine V36 mixer/recorder and make V38 image finishing the only
 # final image compositor; V37 subtitles are still applied after grading.
 html=once(html,"const state=v37DrawFrame($('v36-preview'),ep,v36At);",
  "const state=v38Frame($('v36-preview'),ep,v36At);")
 html=once(html,"const current=v37DrawFrame($('v37-preview'),ep,v37At);",
  "const current=v38Frame($('v37-preview'),ep,v37At);")
 html=once(html,
  "download('V37_EPISODE_SUBTITLES_'+slug(ep.title)+'.webm',blob);",
  "download('V38_CINEMATIC_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,
  "V37: серия WebM с субтитрами записана (",
  "V38: кинематографическая серия WebM записана (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать WebM с субтитрами V37</button>',
  '<button class="accent" id="v36-export">Записать кинематографическую серию V38</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V37')||"
 html=once(html,anchor,"\n/* V38 CINEMATIC CAMERA AND COLOR */\n"+addon.strip()+
  "\n/* END V38 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();result=build()
 for mark in ("function v38Frame(","function v38Manifest(","function v37Paint(",
  "function v36Schedule(","function v35Plan(","function v30Audit(",
  'id="v38-preview"',"AI_ANIME_FACTORY_V38"):
  assert mark in result,mark
 assert V19.read_bytes()==original
 print("V38 BUILDER PASS",len(result.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--selftest",action="store_true")
 ap.add_argument("--output",default=str(OUTPUT))
 args=ap.parse_args()
 if args.selftest:selftest();return
 out=Path(args.output).resolve()
 if out==V19.resolve():raise ValueError("Refuse original V19 overwrite")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V38 HTML BUILT",out,out.stat().st_size)
if __name__=="__main__":main()
