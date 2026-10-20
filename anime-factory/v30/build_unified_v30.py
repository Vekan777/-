#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V30 unified QA without rewriting historical V19–V29 studio sources."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v29"/"build_polish_v29.py"
ADDON=Path(__file__).with_name("unified_v30.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html")
PANEL=r"""
<section class="page" id="page-review-v30" hidden>
<div class="card">
 <h2>V30 — Объединённая проверка качества и целостности V19–V29</h2>
 <p class="muted">Единая проверка канона, персонажей, серий, сцен, боёв, визуала и анимации. Замечания не переписывают сюжет и не удаляют персонажей. Контрольный эталон создаётся только по вашей команде.</p>
 <div class="flex">
  <button class="accent" id="v30-run">Проверить весь проект</button>
  <button id="v30-snapshot">Зафиксировать контрольную точку</button>
  <button id="v30-backup">Скачать резерв JSON</button>
 </div>
 <p class="muted" id="v30-summary"></p>
 <label>Фильтр замечаний</label>
 <select id="v30-filter">
  <option value="all">Все замечания</option>
  <option value="error">Только ошибки</option>
  <option value="warning">Предупреждения</option>
  <option value="info">Информация</option>
 </select>
 <div id="v30-results" style="max-height:470px;overflow:auto"></div>
 <div class="flex">
  <button id="v30-report">Отчёт TXT</button>
  <button id="v30-manifest">Контрольный список JSON</button>
 </div>
</div>
<div class="card">
 <h2>Сезон и контроль кадров</h2>
 <pre class="report" id="v30-stage" style="white-space:pre-wrap;max-height:160px;overflow:auto"></pre>
 <canvas class="preview" id="v30-preview" width="640" height="360"></canvas>
 <label>Позиция сцены <input type="range" id="v30-position" min="0" max="100" value="42"></label>
 <p class="muted" id="v30-caption"></p>
 <button id="v30-sheet">Скачать 4 кадра PNG</button>
</div>
<div class="card">
 <h2>Что означает результат проверки</h2>
 <p>Контрольная точка сравнивает предыдущую структуру серий, текста, настроек персонажей, лора, анимации и боя. Изменённые или исчезнувшие данные отмечаются для ручной проверки; художественные изменения не блокируются.</p>
 <p class="note">Это проверка формальной целостности и эвристика согласованности. Отчёт без ошибок не означает полноценный студийный аниме-сериал или доказанное отсутствие всех смысловых противоречий. Автоудаления и автоматической перезаписи канона нет.</p>
</div>
</section>
"""

def once(text,marker,replacement):
    n=text.count(marker)
    if n!=1:raise ValueError("V30 requires one marker "+repr(marker[:95])+" found "+str(n))
    return text.replace(marker,replacement,1)

def previous():
    spec=importlib.util.spec_from_file_location("anime_v29_builder",BASE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if "function v30Audit(" in html or 'id="page-review-v30"' in html:
        raise ValueError("Already integrated V30")
    for m in ("function v29Beat(","function v28ImpactAt(","function v27Back(",
              "function v26Camera(","function v25PairPose(","function v24Dynamics(",
              "function v23HeadScale(","function v20ContinuityQA("):
        if m not in html:raise ValueError("Missing previous module "+m)
    html=once(html,'<button data-page="export">',
              '<button data-page="review-v30">Аудит V30</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
              PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V29';",
              "const storageKey='AI_ANIME_FACTORY_V30';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:29,",
              "P={format:'AIAnimeFactoryProject',version:30,")
    html=once(html,
              "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V28')",
              "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V29')||localStorage.getItem('AI_ANIME_FACTORY_V28')")
    html=once(html,"if(page==='polish-v29')v29Show();",
              "if(page==='polish-v29')v29Show();if(page==='review-v30')v30Run();")
    html=once(html,"v27Show();v28Show();v29Show();}",
              "v27Show();v28Show();v29Show();v30Run();}")
    # Do not patch QA() itself: V30 has a scoped report with severity
    # and baseline comparison, while original export QA remains unchanged.
    html=once(html,"'AI ANIME FACTORY V29  •  ANIMATION POLISH'",
              "'AI ANIME FACTORY V30  •  UNIFIED QUALITY REVIEW'")
    html=once(html,
       "const files=[{name:'AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH.html',data:selfHTML()},",
       "const files=[{name:'AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW.html',data:selfHTML()},"+
       "{name:'V30_AUDIT_REPORT_RU.txt',data:v30Report()},"+
       "{name:'V30_INTEGRITY_REPORT.json',data:JSON.stringify({baseline:P.unifiedV30?.baseline||null,current:v30ProjectView(P),issues:v30Audit()},null,2)},")
    html=once(html,"'AI_Anime_Factory_V29_ANIMATION_COMBAT_POLISH_Offline.html'",
              "'AI_Anime_Factory_V30_UNIFIED_QUALITY_REVIEW_Offline.html'")
    html=once(html,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<29)migrated.version=29;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<30)migrated.version=30;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
            "localStorage.getItem('AI_ANIME_FACTORY_V29')||"+
            "localStorage.getItem('AI_ANIME_FACTORY_V28')||")
    html=once(html,anchor,
              "\n/* V30 UNIFIED QUALITY REVIEW */\n"+addon.strip()+
              "\n/* END V30 */\n"+anchor)
    return html

def build():
    return patch(previous().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    html=build()
    for mark in ('id="page-review-v30"',"function v30Audit(","function v30Snapshot(",
                 "function v30Compare(","function v29Actor(","function v28ImpactAt(",
                 "function v20ContinuityQA(","V30_INTEGRITY_REPORT.json"):
        assert mark in html,mark
    assert V19.read_bytes()==original
    print("V30 SELFTEST PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--output",default=str(OUTPUT))
    args=parser.parse_args()
    if args.selftest:selftest();return
    out=Path(args.output).resolve()
    if out==V19.resolve():raise ValueError("Refusing overwrite of V19")
    out.parent.mkdir(parents=True,exist_ok=True)
    html=build();out.write_text(html,encoding="utf-8")
    print("V30 HTML BUILT",out,"bytes",out.stat().st_size)

if __name__=="__main__":
    main()
