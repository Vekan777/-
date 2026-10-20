#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer V31 pixel-based visual production checks over preserved V19–V30."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v30"/"build_unified_v30.py"
ADDON=Path(__file__).with_name("visual_v31.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html")

PANEL=r"""
<section class="page" id="page-visual-v31" hidden>
<div class="card">
 <h2>V31 — Качество реального кадра и выпуск аниматика</h2>
 <p class="muted">Анализ Canvas-пикселей: яркость, контраст, глубокие тени, пересвет, читаемость центральной области и перепады освещения. Это измерения, не выдуманные рейтинги красоты персонажа.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v31-scene"></select></div>
  <div class="field"><label>Время кадра</label>
   <input type="range" id="v31-position" min="0" max="100" value="38"></div>
 </div>
 <label><input type="checkbox" id="v31-enabled" checked> Цветокоррекция V31 для этой сцены</label>
 <div class="grid">
  <div class="field"><label>Экспозиция <span id="v31-exposure-n">51</span>%</label><input type="range" id="v31-exposure" min="0" max="100"></div>
  <div class="field"><label>Контраст <span id="v31-contrast-n">54</span>%</label><input type="range" id="v31-contrast" min="0" max="100"></div>
  <div class="field"><label>Насыщенность <span id="v31-saturation-n">55</span>%</label><input type="range" id="v31-saturation" min="0" max="100"></div>
  <div class="field"><label>Виньетка <span id="v31-vignette-n">22</span>%</label><input type="range" id="v31-vignette" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v31-preset">Мягкий кинопрофиль</button>
  <button class="accent" id="v31-save">Сохранить качество кадра</button></div>
</div>
<div class="card">
 <h2>Один и тот же кадр — V30 против V31</h2>
 <div class="grid">
  <div class="field"><label>V30 — исходный рендер</label>
   <canvas class="preview" id="v31-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V31 — корректировка цвета</label>
   <canvas class="preview" id="v31-after" width="640" height="360"></canvas></div>
 </div>
 <p class="muted" id="v31-caption"></p>
 <div class="flex"><button id="v31-analyze">Анализ 4 кадров сцены</button>
   <button id="v31-all">Анализ первых 24 сцен сезона</button></div>
 <pre class="report" id="v31-result" style="white-space:pre-wrap;max-height:290px;overflow:auto"></pre>
 <div class="flex"><button id="v31-report">Скачать отчёт TXT</button>
   <button id="v31-json">Скачать метрики JSON</button>
   <button id="v31-sheet">Скачать 4 кадра PNG</button></div>
</div>
<div class="card">
 <h2>Ограничения автоматического анализа</h2>
 <p class="note">Алгоритм считает яркость и контраст пикселей, а не распознаёт лица. Он не знает сюжетного значения темноты, художественного стиля или драматической паузы. Проверка первых 24 сцен ограничивает нагрузку на старые ноутбуки. При импорте внешних изображений с запрещённым доступом к Canvas анализ сообщит об ошибке.</p>
 <p class="muted">Сюжет, 2D-позы, эффекты V19–V30 и авторские PNG не заменяются. V31 не является 3D, нейрорендером или готовым профессиональным сериалом.</p>
</div>
</section>
"""

def once(t,old,new):
 n=t.count(old)
 if n!=1:raise ValueError("V31 integration anchor "+repr(old[:90])+" count="+str(n))
 return t.replace(old,new,1)

def previous():
 spec=importlib.util.spec_from_file_location("v30_builder",BASE)
 m=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(m)
 return m

def patch(html,js):
 if "function v31Grade(" in html or 'id="page-visual-v31"' in html:
  raise ValueError("V31 already included")
 for item in ("function v30Audit(","function v29Actor(","function v28Ground(",
              "function v25PairPose(","function v20CanonLines("):
  if item not in html:raise ValueError("Previous version missing "+item)
 html=once(html,'<button data-page="export">',
           '<button data-page="visual-v31">Контроль кадра V31</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
           PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V30';",
           "const storageKey='AI_ANIME_FACTORY_V31';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:30,",
           "P={format:'AIAnimeFactoryProject',version:31,")
 html=once(html,
   "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V29')",
   "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V30')||localStorage.getItem('AI_ANIME_FACTORY_V29')")
 html=once(html,"if(page==='review-v30')v30Run();",
           "if(page==='review-v30')v30Run();if(page==='visual-v31')v31UpdateUI();")
 html=once(html,"v28Show();v29Show();v30Run();}",
           "v28Show();v29Show();v30Run();v31UpdateUI();}")
 # One final pixel pass used by normal preview AND existing PNG/video export.
 html=once(html,
   "cin14Post(g,w,h,s,sec);v26FinishFrame(g,w,h,s,sec);",
   "cin14Post(g,w,h,s,sec);v26FinishFrame(g,w,h,s,sec);v31Grade(g,w,h,s);")
 html=once(html,"'AI ANIME FACTORY V30  •  UNIFIED QUALITY REVIEW'",
           "'AI ANIME FACTORY V31  •  VISUAL PRODUCTION'")
 html=once(html,
   "const files=[{name:'AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html',data:selfHTML()},",
   "const files=[{name:'AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW.html',data:selfHTML()},"+
   "{name:'V31_VISUAL_REPORT.json',data:JSON.stringify(v31ReviewProject(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW_Offline.html'",
           "'AI_Anime_Factory_V31_VISUAL_PRODUCTION_REVIEW_Offline.html'")
 html=once(html,
   "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<30)migrated.version=30;return migrated;}",
   "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<31)migrated.version=31;return migrated;}")
 anchor=("try{const old=localStorage.getItem(storageKey)||"+
         "localStorage.getItem('AI_ANIME_FACTORY_V30')||"+
         "localStorage.getItem('AI_ANIME_FACTORY_V29')||")
 html=once(html,anchor,"\n/* V31 VISUAL PRODUCTION REVIEW */\n"+
           js.strip()+"\n/* END V31 */\n"+anchor)
 return html

def build():
 return patch(previous().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
 original=V19.read_bytes()
 html=build()
 for k in ('id="page-visual-v31"',"function v31Grade(","function v31Metrics(",
           "function v31ReviewProject(","function v30Audit(","function v29Actor(",
           "v26FinishFrame(g,w,h,s,sec);v31Grade(g,w,h,s);"):
  assert k in html,k
 assert V19.read_bytes()==original
 print("V31 BUILDER PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--selftest",action="store_true")
 p.add_argument("--output",default=str(OUTPUT))
 o=p.parse_args()
 if o.selftest:selftest();return
 dst=Path(o.output).resolve()
 if dst==V19.resolve():raise ValueError("Never overwrite V19")
 dst.parent.mkdir(parents=True,exist_ok=True)
 result=build();dst.write_text(result,encoding="utf-8")
 print("V31 HTML BUILT",dst,dst.stat().st_size)

if __name__=="__main__":main()
