#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V48 deterministic episode studio builder over the complete V47 pipeline."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v47/build_voice_v47.py"
ADDON=Path(__file__).with_name("episode_engine_v48.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V48_EPISODE_ENGINE.html")
PANEL=r"""
<section class="page" id="page-episode-v48" hidden>
<div class="card">
 <h2>V48 — Episode Production Engine: готовый эпизод и сезон</h2>
 <p class="muted">Полные серии берутся из действующего V35 таймлайна со всеми моделями, ключевыми кадрами, фонами, V47 звуком, V37 субтитрами и камерой. Здесь настраиваются титры и план выпуска. Для автоматической очереди эпизодов, восстановления уже отрендеренных серий и MP4 используйте RUN_BATCH_WINDOWS.bat из комплекта; браузер записывает один эпизод за раз.</p>
 <div class="grid">
  <div class="field"><label>Выбранная серия</label><select id="v48-episode"></select></div>
  <div class="field"><label>Частота кадров WebM</label><select id="v48-fps">
   <option value="6">6 FPS — слабый ноутбук</option>
   <option value="12">12 FPS — баланс</option>
   <option value="24">24 FPS — мощный ПК</option>
  </select></div>
  <div class="field"><label>Ширина для настроек будущей сборки</label><select id="v48-width">
   <option value="640">640 × 360</option><option value="960">960 × 540</option>
   <option value="1280">1280 × 720</option>
  </select></div>
  <div class="field"><label>Длительность титров внутри конца серии</label>
   <input id="v48-credit-seconds" type="number" min=".5" max="8" step=".5" value="2"></div>
 </div>
 <label><input id="v48-credits" type="checkbox" checked> Показать финальную карточку с титрами</label>
 <div class="field"><label>Студия / имя в титрах</label><input id="v48-studio" placeholder="Название студии"></div>
 <button class="accent" id="v48-save">Сохранить параметры выпуска</button>
 <p class="note">Титры накладываются на последние секунды сцены, без изменения прежнего сюжета или длительности V35. В браузере запись ведётся в реальном времени: длинная серия занимает примерно столько же времени, сколько просмотр. Указанная ширина сохраняется для пакетного задания; базовый встроенный WebM использует 640×360, пока внешний рендер не подтвердил нужный пресет.</p>
</div>
<div class="card">
 <h2>Настоящий предпросмотр серии и титров</h2>
 <canvas id="v48-preview" class="preview" width="640" height="360"></canvas>
 <label>Таймкод всей серии <input id="v48-position" type="range" min="0" max="1000" value="0"></label>
 <p id="v48-timestamp" class="muted"></p>
 <div class="flex">
  <button id="v48-play">Воспроизвести</button><button id="v48-first">В начало</button>
  <button id="v48-frames">Контрольный PNG 4×</button>
 </div>
</div>
<div class="card">
 <h2>Профессиональные материалы выпуска</h2>
 <div class="flex">
  <button id="v48-srt">Субтитры SRT</button>
  <button id="v48-vtt">Субтитры VTT</button>
  <button id="v48-shot">Режиссёрский план JSON</button>
  <button id="v48-manifest">Паспорт сезона JSON</button>
  <button id="v48-project">Полный проект с артом и звуком</button>
 </div>
 <button class="accent" id="v48-record">Записать выбранную серию WebM с V47 звуком</button>
 <p class="note">Чтобы автоматически записать две или больше серий, сделать MP4 и продолжить после сбоя, положите скачанный полный проект под именем PROJECT_INPUT.json рядом с RUN_BATCH_WINDOWS.bat, установите Python/Playwright Chromium и FFmpeg через SETUP_BATCH_WINDOWS.bat, затем запустите пакетную обработку. Пропускаются только полностью проверенные сохранённые серии с верным SHA256. Это восстановление **по границе эпизода**, а не с точности последнего видеокадра.</p>
 <pre id="v48-report" class="report" style="white-space:pre-wrap;max-height:350px;overflow:auto"></pre>
 <p class="note">V49 — один объединённый интерфейс, V50 — глубокая художественная и техническая приёмка. Успешные автоматические тесты не равны профессиональному качеству аниме без качественных рисунков, режиссуры и ручной проверки звука.</p>
</div>
</section>
"""
def once(src,a,b):
 n=src.count(a)
 if n!=1:raise ValueError("V48 anchor "+str(n)+" "+repr(a[:110]))
 return src.replace(a,b,1)
def previous():
 sp=importlib.util.spec_from_file_location("v47_episode_parent",BASE)
 m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def patch(html,addon):
 if 'id="page-episode-v48"' in html or "function v48Manifest(" in html:
  raise ValueError("Duplicate V48")
 for old in ("function v47RestoreEpisode(","function v35Plan(",
  "function v35Frame(","function v36Start(","function v37SubtitleFile(",
  "function v46ApplyClip(","function v45DrawBackground(","function v25Contact("):
  if old not in html:raise ValueError("Missing original stage "+old)
 html=once(html,'<button data-page="export">',
  '<button data-page="episode-v48">Монтаж серий V48</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V47';",
  "const storageKey='AI_ANIME_FACTORY_V48';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:47,",
  "P={format:'AIAnimeFactoryProject',version:48,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V46')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V47')||localStorage.getItem('AI_ANIME_FACTORY_V46')")
 html=once(html,"if(page==='voice-v47')v47View();",
  "if(page==='voice-v47')v47View();if(page==='episode-v48')v48Show();")
 html=once(html,"v46Show();v47View();}","v46Show();v47View();v48Show();}")
 html=once(html,"function show(page){if(page!=='animation-v46')v46Pause();",
  "function show(page){if(page!=='episode-v48')v48Pause();if(page!=='animation-v46')v46Pause();")
 html=once(html,
  "'AI ANIME FACTORY V47  •  PORTABLE VOICE / LIP SYNC'",
  "'AI ANIME FACTORY V48  •  EPISODE PRODUCTION ENGINE'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V47_PORTABLE_VOICE.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V48_EPISODE_ENGINE.html',data:selfHTML()},"+
  "{name:'V48_EPISODE_PRODUCTION_MANIFEST.json',data:JSON.stringify(v48Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V47_PORTABLE_VOICE_Offline.html'",
  "'AI_Anime_Factory_V48_EPISODE_ENGINE_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<47)migrated.version=47;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<48)migrated.version=48;return migrated;}")
 html=once(html,
  "download('V47_PORTABLE_VOICE_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V48_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V47: переносимое аудио и движения рта записаны в WebM (",
  "V48: реальная серия WebM с музыкой и титрами записана (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V47 с озвучкой и губами</button>',
  '<button class="accent" id="v36-export">Записать серию V48 с V47 звуком</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V47')||"
 html=once(html,anchor,
  "\n/* V48 SEASON EDITOR + EPISODE TITLE CARD */\n"+addon.strip()+
  "\n/* END V48 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 orig=V19.read_bytes();html=build()
 for term in ("function v48Manifest(","function v48DrawCredits(",
  "v35Frame=function(canvas,episode,sec)","function v47RestoreEpisode(",
  "function v37SubtitleFile(","V48_EPISODE_",
  "AI_ANIME_FACTORY_V48",'id="page-episode-v48"'):
  assert term in html,term
 assert orig==V19.read_bytes()
 print("V48 BUILD OK",len(html.encode()),hashlib.sha256(orig).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--output",default=str(OUTPUT))
 a=p.parse_args()
 if a.selftest:selftest();return
 dst=Path(a.output).resolve()
 if dst==V19.resolve():raise ValueError("Original V19 cannot be overwritten")
 dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(build(),encoding="utf-8")
 print("V48 HTML",dst,dst.stat().st_size)
if __name__=="__main__":main()
