#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V49 single consolidated workflow over unchanged V19–V48 production modules."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v48/build_episode_v48.py"
JS=Path(__file__).with_name("unified_studio_v49.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V49_UNIFIED_STUDIO.html")
PANEL=r"""
<section class="page" id="page-unified-v49" hidden>
<div class="card">
  <h2>AI Anime Factory V49 — единая производственная студия 2D</h2>
  <p>Один маршрут: <strong>сценарий → персонажи и миры → анимация → звук → субтитры → выпуск</strong>. Это полноценный рабочий интерфейс к настоящим редакторам V19–V48, а не имитация рендера.</p>
  <p id="v49-summary" class="muted"></p>
  <div class="grid">
    <div class="field"><label>Серия для контроля</label><select id="v49-episode"></select></div>
  </div>
  <p id="v49-readiness" class="note"></p>
  <div class="flex">
    <button class="accent" id="v49-export-project">Скачать ПОЛНЫЙ резерв JSON (арт + звук + сюжет)</button>
    <button id="v49-import-project">Импортировать сохранённый проект</button>
    <button id="v49-export-checklist">Скачать технический аудит JSON</button>
  </div>
  <p class="note">В браузере хранилище ограничено и не является архивом. До редактирования и перед каждым выпуском скачивайте полный JSON на диск. Импорт использует прежний проверенный обработчик, который сохраняет совместимость со старыми проектами.</p>
</div>
<div class="card">
  <h2>Шесть производственных этапов — один проект</h2>
  <div id="v49-stage-list"></div>
  <p class="note">Отметка «Я проверил» — только ваша ручная приёмка. Программа не ставит её автоматически и не выдаёт зелёный список за профессиональную художественную экспертизу. Замечания не исчезают от ручной отметки.</p>
</div>
<div class="card">
  <h2>Отчёт о готовности выбранной серии</h2>
  <pre id="v49-report" class="report" style="white-space:pre-wrap;max-height:360px;overflow:auto"></pre>
  <div class="field">
    <label>Режиссёрские замечания / незавершённые сцены / договорённости по правам</label>
    <textarea id="v49-notes" rows="5" placeholder="Что проверить до публикации: герои, лица, бой, дыхание, эмоции, звук, сюжет, источники изображения."></textarea>
  </div>
  <div class="flex"><button id="v49-save-notes">Сохранить заметки в проект</button>
    <button class="accent" id="v49-record">Перейти к настоящей записи серии</button></div>
  <p class="note">Нажатие перехода не создаёт видео само: оно открывает настоящий монтаж V48 с выбранной серией. Для WebM нажмите запись V48, для MP4 и очереди серий используйте RUN_BATCH_WINDOWS.bat + FFmpeg.</p>
</div>
<div class="card">
  <h2>Что ещё нужно перед V50 FINAL</h2>
  <p>V49 объединяет редакторы, резервирование, журнал ручной приёмки и проверку ошибок. На V50 остаются углублённая проверка происхождения материалов, история сериалов, качество синхронизации звука, художественная связность, тесты восстановления и итоговый отчёт о реальной готовности. 3D — отдельный проект только после проверки 2D V50.</p>
</div>
</section>
"""
def once(s,a,b):
 count=s.count(a)
 if count!=1:raise ValueError("V49 expected 1 anchor, got "+str(count)+": "+repr(a[:110]))
 return s.replace(a,b,1)
def previous():
 spec=importlib.util.spec_from_file_location("v48_unified_parent",BASE)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def patch(html,addon):
 if 'id="page-unified-v49"' in html or "function v49Audit(" in html:
  raise ValueError("V49 duplicated")
 for token in ("function v48Manifest(","function v47RestoreEpisode(",
  "function v46LayerMotion(","function v45DrawBackground(",
  "function v37SubtitleFile(","function v35Plan(","function v25Contact("):
  if token not in html:raise ValueError("History missing "+token)
 html=once(html,'<button data-page="export">',
   '<button data-page="unified-v49">Единая студия V49</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
   PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V48';",
   "const storageKey='AI_ANIME_FACTORY_V49';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:48,",
   "P={format:'AIAnimeFactoryProject',version:49,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V47')",
   "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V48')||localStorage.getItem('AI_ANIME_FACTORY_V47')")
 html=once(html,"if(page==='episode-v48')v48Show();",
   "if(page==='episode-v48')v48Show();if(page==='unified-v49')v49Show();")
 html=once(html,"v47View();v48Show();}","v47View();v48Show();v49Show();}")
 html=once(html,
   "'AI ANIME FACTORY V48  •  EPISODE PRODUCTION ENGINE'",
   "'AI ANIME FACTORY V49  •  UNIFIED 2D PRODUCTION STUDIO'")
 html=once(html,
   "const files=[{name:'AI_Anime_Factory_V48_EPISODE_ENGINE.html',data:selfHTML()},",
   "const files=[{name:'AI_Anime_Factory_V49_UNIFIED_STUDIO.html',data:selfHTML()},"+
   "{name:'V49_TECHNICAL_READINESS.json',data:JSON.stringify(v49Audit(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V48_EPISODE_ENGINE_Offline.html'",
   "'AI_Anime_Factory_V49_UNIFIED_STUDIO_Offline.html'")
 html=once(html,
   "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<48)migrated.version=48;return migrated;}",
   "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<49)migrated.version=49;return migrated;}")
 html=once(html,
   "download('V48_EPISODE_'+slug(ep.title)+'.webm',blob);",
   "download('V49_UNIFIED_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V48: реальная серия WebM с музыкой и титрами записана (",
   "V49: серия и звук записаны единым движком (")
 html=once(html,
   '<button class="accent" id="v36-export">Записать серию V48 с V47 звуком</button>',
   '<button class="accent" id="v36-export">Записать серию V49 с V47 звуком</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V48')||"
 html=once(html,anchor,
   "\n/* V49 UNIFIED 2D PRODUCTION WORKFLOW */\n"+addon.strip()+
   "\n/* END V49 */\n"+anchor)
 return html
def build():return patch(previous().build(),JS.read_text(encoding="utf-8"))
def selftest():
 before=V19.read_bytes();html=build()
 for term in ("function v49Audit(","function v49Backup(","window.v49UnifiedBridge=",
  'id="page-unified-v49"',"function v48Manifest(",
  "function v47RestoreEpisode(","AI_ANIME_FACTORY_V49"):
  assert term in html,term
 assert before==V19.read_bytes()
 print("V49 UNIFIED BUILD OK",len(html.encode()),hashlib.sha256(before).hexdigest())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--selftest",action="store_true")
 ap.add_argument("--output",default=str(OUTPUT))
 a=ap.parse_args()
 if a.selftest:selftest();return
 out=Path(a.output).resolve()
 if out==V19.resolve():raise ValueError("Refuse to overwrite historical V19")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(build(),encoding="utf-8")
 print("V49 HTML",out,out.stat().st_size)
if __name__=="__main__":main()
