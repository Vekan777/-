#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V47 Portable Voice and amplitude Lip Sync Studio on actual V46 renderer."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v46/build_animation_v46.py"
STUDIO=Path(__file__).with_name("portable_voice_v47.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V47_PORTABLE_VOICE.html")
PANEL=r"""
<section class="page" id="page-voice-v47" hidden>
<div class="card">
 <h2>V47 — Звуковая студия и переносимая озвучка</h2>
 <p class="muted">Загружайте WAV/MP3/OGG/WebM/M4A для голоса, музыки и эффектов. Реальные байты файла сохраняются прямо в полном JSON проекта и декодируются при следующем открытии. Есть настройка громкости, смещения, выбор говорящего, мимики и предпросмотр.</p>
 <div class="grid">
  <div class="field"><label>Эпизод</label><select id="v47-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v47-scene"></select></div>
  <div class="field"><label>Тип звука</label><select id="v47-slot">
   <option value="voice">Голос / реплика</option>
   <option value="music">Музыка</option><option value="fx">Эффекты</option>
  </select></div>
  <div class="field"><label>Говорящий (для рта)</label><select id="v47-speaker"></select></div>
 </div>
 <div class="flex">
  <button id="v47-choose" onclick="document.getElementById('v47-file').click()">Загрузить переносимый аудиофайл</button>
  <input id="v47-file" type="file" accept=".wav,.mp3,.ogg,.webm,.m4a,audio/*" hidden>
 </div>
 <p id="v47-state" class="muted"></p>
 <p class="note">Лимит одного клипа — 1,5 МБ: обычный Chrome/Edge часто выделяет локальному хранилищу около 5 МБ. Для длинной речи лучше сжатые OGG/MP3 и короткие сцены. Если квота превышена, приложение не обещает сохранность и сообщает об ошибке. Всегда экспортируйте полный JSON на диск.</p>
 <div class="grid">
  <div class="field"><label>Громкость / микшер 0–200%</label><input id="v47-gain" type="range" min="0" max="200" value="100"></div>
  <div class="field"><label>Задержка звука, сотые доли секунды</label><input id="v47-offset" type="range" min="0" max="300" value="0"></div>
  <div class="field"><label>Положение рта X</label><input id="v47-mouth-x" type="number" min="-45" max="45" value="0"></div>
  <div class="field"><label>Положение рта Y</label><input id="v47-mouth-y" type="number" min="-45" max="45" value="0"></div>
 </div>
 <label><input id="v47-mouth-on" type="checkbox" checked> Использовать движения рта по реальному уровню звука (для голоса)</label>
 <button class="accent" id="v47-save">Сохранить микшер и привязку говорящего</button>
 <p class="note">Амплитудный липсинк действительно синхронизирован с сохранённым звуком, но **это не распознавание фонем**. Для сложной речи, нескольких говорящих и художественно точных форм рта потребуется дополнительная ручная постановка, которую проверим в V50.</p>
</div>
<div class="card">
 <h2>Реальный предпросмотр озвученной сцены и движения рта</h2>
 <canvas id="v47-preview" class="preview" width="640" height="360"></canvas>
 <label>Фаза сцены <input id="v47-timeline" type="range" min="0" max="1000" value="300"></label>
 <p id="v47-time" class="muted"></p>
 <p class="note">Для прослушивания и записи целого эпизода со звуком используйте прежнюю вкладку «Звук / экспорт V36». V47 автоматически восстанавливает встроенные аудиофайлы перед началом воспроизведения и записи WebM.</p>
</div>
<div class="card">
 <h2>Перенос проекта и звуковой аудит</h2>
 <div class="flex">
  <button id="v47-project">Полный JSON со звуками и рисунками</button>
  <button id="v47-manifest">Отчёт об озвучке JSON</button>
  <button id="v47-audit">Проверка звуков</button>
 </div>
 <pre id="v47-report" class="report" style="white-space:pre-wrap;max-height:340px;overflow:auto"></pre>
 <p class="note">V19–V46 и сюжет/боевые исходы сохранены. V48 — очередь видео на серии, V49 — объединяющий интерфейс, V50 — глубокие проверки под ключ. 3D Edition начинается только после принятого 2D V50.</p>
</div>
</section>
"""
def once(src,a,b):
 n=src.count(a)
 if n!=1:raise ValueError("V47 expects one anchor got "+str(n)+": "+repr(a[:110]))
 return src.replace(a,b,1)
def previous():
 spec=importlib.util.spec_from_file_location("anime_v46_portable_parent",BASE)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def patch(html,script):
 if 'id="page-voice-v47"' in html or "function v47RestoreEpisode(" in html:
  raise ValueError("V47 was already integrated")
 for old in ("function v36Start(","function v36Attach(","function v36Buffer(",
  "function mouth(","function drawProductionPerson(","function pose16Sample(",
  "function v46SaveClip(","function v45DrawBackground("):
  if old not in html:raise ValueError("Missing historical 2D function: "+old)
 html=once(html,'<button data-page="export">',
  '<button data-page="voice-v47">Озвучка и губы V47</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V46';",
  "const storageKey='AI_ANIME_FACTORY_V47';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:46,",
  "P={format:'AIAnimeFactoryProject',version:47,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V45')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V46')||localStorage.getItem('AI_ANIME_FACTORY_V45')")
 html=once(html,"if(page==='animation-v46')v46Show();",
  "if(page==='animation-v46')v46Show();if(page==='voice-v47')v47View();")
 html=once(html,"v45Show();v46Show();}","v45Show();v46Show();v47View();}")
 html=once(html,
  "'AI ANIME FACTORY V46  •  KEYFRAME ANIMATION ENGINE'",
  "'AI ANIME FACTORY V47  •  PORTABLE VOICE / LIP SYNC'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V46_ANIMATION_ENGINE.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V47_PORTABLE_VOICE.html',data:selfHTML()},"+
  "{name:'V47_AUDIO_LIPSYNC_MANIFEST.json',data:JSON.stringify(v36Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V46_ANIMATION_ENGINE_Offline.html'",
  "'AI_Anime_Factory_V47_PORTABLE_VOICE_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<46)migrated.version=46;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<47)migrated.version=47;return migrated;}")
 html=once(html,
  "download('V46_ANIMATION_ENGINE_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V47_PORTABLE_VOICE_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V46: анимационные ключи и клипы записаны в WebM (",
  "V47: переносимое аудио и движения рта записаны в WebM (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать V46 с настоящей анимацией</button>',
  '<button class="accent" id="v36-export">Записать V47 с озвучкой и губами</button>')
 # Guarantee V36 legacy export uses re-decoded data from the actual JSON
 # after the browser is restarted. Do not change the canonical timeline.
 html=once(html,
  "const ctx=v36Audio();\n  await ctx.resume();\n  await preloadArtwork();",
  "const ctx=v36Audio();\n  await ctx.resume();\n  await v47RestoreEpisode(ep);\n  await preloadArtwork();")
 # PNG face layers must also react to voice (not only the original procedural face).
 # Keep old V45 actor art and pivot drawing otherwise untouched.
 html=once(html,
  "g.drawImage(img,-PROD_ANCHOR.x/PROD_ANCHOR.scale,-PROD_ANCHOR.y/PROD_ANCHOR.scale,PROD_ANCHOR.width/PROD_ANCHOR.scale,PROD_ANCHOR.height/PROD_ANCHOR.scale);",
  "g.drawImage(img,-PROD_ANCHOR.x/PROD_ANCHOR.scale,-PROD_ANCHOR.y/PROD_ANCHOR.scale,PROD_ANCHOR.width/PROD_ANCHOR.scale,PROD_ANCHOR.height/PROD_ANCHOR.scale);"+
  "if(name==='face')v47PaintMouthOnCutout(g,s,c,t);")
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V46')||"
 html=once(html,anchor,
  "\n/* V47 FULLY PORTABLE AUDIO AND SOUND-BASED MOUTH */\n"+script.strip()+
  "\n/* END V47 */\n"+anchor)
 return html
def build():return patch(previous().build(),STUDIO.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();html=build()
 for term in ("function v47RestoreEpisode(","function v47Wave(",
  "mouth=function(s,c,sec)","v47PaintMouthOnCutout(g,s,c,t);",
  "await v47RestoreEpisode(ep);","function v46SaveClip(",
  "function v45DrawBackground(","AI_ANIME_FACTORY_V47",
  'id="page-voice-v47"'):
  assert term in html,term
 assert V19.read_bytes()==original
 print("V47 SELFTEST OK",len(html.encode()),hashlib.sha256(original).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--output",default=str(OUTPUT))
 a=p.parse_args()
 if a.selftest:selftest();return
 out=Path(a.output).resolve()
 if out==V19.resolve():raise ValueError("Cannot modify original V19")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V47 HTML",out,out.stat().st_size)
if __name__=="__main__":main()
