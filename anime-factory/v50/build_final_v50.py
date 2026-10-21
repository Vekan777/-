#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final V50 QA overlay on actual V49 unified editor and all V19–V48 code."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v49/build_unified_v49.py"
ADDON=Path(__file__).with_name("deep_qa_v50.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V50_FINAL_2D.html")
PANEL=r"""
<section class="page" id="page-final-v50" hidden>
<div class="card">
 <h2>AI ANIME FACTORY V50 FINAL — заключительная проверка 2D</h2>
 <p>Эта версия завершает согласованный план V45–V50: аудит сценария, персонажей, анимации, звука, субтитров, экспорта и сохранения предыдущих данных. Поиск ошибок автоматизирован, но профессиональное художественное качество требует просмотра человеком. Формальная отметка «проверено» не удаляет обнаруженные ошибки.</p>
 <p id="v50-summary" class="muted"></p>
 <div class="field"><label>Серия</label><select id="v50-episode"></select></div>
 <p id="v50-status" class="note"></p>
 <pre id="v50-evidence" class="report" style="white-space:pre-wrap"></pre>
 <div class="flex">
  <button class="accent" id="v50-full-backup">Скачать ВЕСЬ проект JSON: сюжет + рисунки + движения + голоса</button>
  <button id="v50-import">Восстановить полный проект из JSON</button>
  <button id="v50-export">Скачать отчёт углублённой QA</button>
 </div>
 <p class="note">Перед исправлениями обязательно экспортируйте резерв JSON на диск. Браузерный localStorage не является надёжным долговременным архивом аудио и изображений.</p>
</div>
<div class="card">
 <h2>Чек-лист фактической приёмки выбранной серии</h2>
 <div id="v50-checklist"></div>
 <p id="v50-signoff" class="muted"></p>
 <p class="note">Проверяйте художественные сцены в масштабе 100%, сюжетные переходы, движения корпуса/рук, положение рта, голос, музыку и полный экспорт MP4. Отдельно проверяйте письменные права на весь используемый арт и звук. Эти поля заполняются только ВАМИ, не тестами.</p>
 <div class="flex"><button id="v50-go-stages">Открыть все шесть редакторов V49</button>
 <button id="v50-go-render" class="accent">Открыть настоящий рендер V48</button></div>
</div>
<div class="card">
 <h2>Обнаруженные проблемы и режиссёрские заметки</h2>
 <pre id="v50-report" class="report" style="white-space:pre-wrap;max-height:440px;overflow:auto"></pre>
 <div class="field">
  <label>Мои замечания по финальной приёмке, необходимые исправления, права</label>
  <textarea id="v50-notes" rows="5" placeholder="Проверено в браузере и на Windows: монтаж, персонажи, звук, локации, оружие, дружба, предательство, любовь, титры; какие недостатки остались"></textarea>
 </div>
 <button id="v50-notes-save">Сохранить итоговые замечания</button>
</div>
<div class="card">
 <h2>Реальные пределы итоговой версии</h2>
 <p>**V50 FINAL — это итог сборки и глубокой технической QA**, а не доказательство, что случайные процедурные круги или простой Canvas-cutout стали профессиональной 2D-аниме-сериалом студийного уровня. Художники, озвучка, монтаж и лицензированные материалы всё равно нужны. Собственная 3D Edition — следующий отдельный проект только после подтверждённой ручной приёмки 2D.</p>
 <p>Пакетные MP4 доступны через RUN_BATCH_WINDOWS.bat, Python, Chromium Playwright и FFmpeg. Проверка SHA256 позволяет продолжить с последней завершённой серии. Сохранение аудио V47 ограничено квотой браузера; для большого сезона используйте короткие сжатые клипы и внешний архив файлов.</p>
</div>
</section>
"""
def once(src,a,b):
 count=src.count(a)
 if count!=1:raise ValueError("V50 builder expected one anchor, got "+str(count)+": "+repr(a[:105]))
 return src.replace(a,b,1)
def previous():
 sp=importlib.util.spec_from_file_location("v49_final_parent",BASE)
 m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def patch(html,addon):
 if 'id="page-final-v50"' in html or "function v50AuditProject(" in html:
  raise ValueError("Duplicate V50")
 for token in ("function v49Audit(","function v48Manifest(","function v47RestoreEpisode(",
  "function v46LayerMotion(","function v45DrawBackground(",
  "function v37SubtitleFile(","function v35Plan(","function v25Contact("):
  if token not in html:raise ValueError("Original functionality removed: "+token)
 html=once(html,'<button data-page="export">',
  '<button data-page="final-v50">ФИНАЛЬНАЯ QA V50</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V49';",
  "const storageKey='AI_ANIME_FACTORY_V50';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:49,",
  "P={format:'AIAnimeFactoryProject',version:50,")
 html=once(html,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V48')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V49')||localStorage.getItem('AI_ANIME_FACTORY_V48')")
 html=once(html,"if(page==='unified-v49')v49Show();",
  "if(page==='unified-v49')v49Show();if(page==='final-v50')v50Show();")
 html=once(html,"v48Show();v49Show();}","v48Show();v49Show();v50Show();}")
 html=once(html,"'AI ANIME FACTORY V49  •  UNIFIED 2D PRODUCTION STUDIO'",
  "'AI ANIME FACTORY V50  •  FINAL 2D / DEEP QUALITY ASSURANCE'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V49_UNIFIED_STUDIO.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V50_FINAL_2D.html',data:selfHTML()},"+
  "{name:'V50_FINAL_DEEP_QA_REPORT.json',data:JSON.stringify(v50Report(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V49_UNIFIED_STUDIO_Offline.html'",
  "'AI_Anime_Factory_V50_FINAL_2D_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<49)migrated.version=49;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<50)migrated.version=50;return migrated;}")
 html=once(html,
  "download('V49_UNIFIED_EPISODE_'+slug(ep.title)+'.webm',blob);",
  "download('V50_FINAL_EPISODE_'+slug(ep.title)+'.webm',blob);")
 html=once(html,"V49: серия и звук записаны единым движком (",
  "V50: серия со звуком записана финальным движком (")
 html=once(html,
  '<button class="accent" id="v36-export">Записать серию V49 с V47 звуком</button>',
  '<button class="accent" id="v36-export">Записать серию V50 со звуком V47</button>')
 anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V49')||"
 html=once(html,anchor,
  "\n/* V50 DETERMINISTIC NONDESTRUCTIVE DEEP QA */\n"+addon.strip()+
  "\n/* END V50 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();html=build()
 for token in ("function v50AuditProject(","window.v50FinalQA=Object.freeze",
  "function v49Audit(","function v48Manifest(","AI_ANIME_FACTORY_V50",
  'id="page-final-v50"'):
  assert token in html,token
 assert original==V19.read_bytes()
 print("V50 FINAL BUILD PASSED",len(html.encode()),hashlib.sha256(original).hexdigest())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--selftest",action="store_true")
 ap.add_argument("--output",default=str(OUTPUT))
 a=ap.parse_args()
 if a.selftest:selftest();return
 target=Path(a.output).resolve()
 if target==V19.resolve():raise ValueError("Refuse to overwrite V19 original")
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(build(),encoding="utf-8")
 print("V50 HTML",target,target.stat().st_size)
if __name__=="__main__":main()
