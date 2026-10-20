#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V35 production scene assembly preserving genuine V19–V34 HTML."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v34"/"build_storyboard_v34.py"
ADDON=Path(__file__).with_name("assembly_v35.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V35_SCENE_ASSEMBLY.html")
PANEL=r"""
<section class="page" id="page-assembly-v35" hidden>
<div class="card">
 <h2>V35 — Сборка эпизода и производственный контроль</h2>
 <p class="muted">Непрерывная шкала серии по настоящим сценам проекта. Плавное наложение между соседними кадрами без удаления сцен, изменения оригинальных длительностей, сюжета и боевых событий. Работает локально в Canvas.</p>
 <div class="grid">
  <div class="field"><label>Серия</label><select id="v35-episode"></select></div>
  <div class="field"><label>Редактировать переход после сцены</label><select id="v35-scene"></select></div>
 </div>
 <label><input type="checkbox" id="v35-enabled" checked> Использовать переход после выбранной сцены</label>
 <label>Наложение кадров соседних сцен: <span id="v35-transition-n">0.35</span> сек
 <input id="v35-transition" type="range" min="0" max="150" step="5" value="35"></label>
 <p class="muted">Максимум перехода — 1,5 секунды, но он автоматически ограничивается третью длины каждой соседней сцены. Последняя сцена завершается без наложения.</p>
 <button class="accent" id="v35-save">Сохранить монтажный переход</button>
</div>
<div class="card">
 <h2>Непрерывный предпросмотр всей серии</h2>
 <canvas class="preview" id="v35-preview" width="640" height="360"></canvas>
 <div class="flex">
  <button id="v35-play">Воспроизвести</button><button id="v35-start">В начало</button>
 </div>
 <label>Положение на общей шкале <input id="v35-progress" type="range" min="0" max="1000" value="0"></label>
 <p id="v35-time" class="muted">Время серии</p>
 <pre id="v35-sequence" class="report" style="white-space:pre-wrap;max-height:220px;overflow:auto"></pre>
 <p class="note">Предпросмотр V35 соединяет именно визуальные кадры. Звуковые дорожки не микшируются и автоматический MP4 здесь не создаётся. Для видеозаписи и звука используйте обычные функции экспорта и внешний монтаж/FFmpeg.</p>
</div>
<div class="card">
 <h2>Контроль длительности и последовательности</h2>
 <div class="flex">
  <button id="v35-audit">Проверить всю сборку</button>
  <button id="v35-report">Скачать TXT-лист монтажа</button>
  <button id="v35-json">Скачать JSON-манифест серии</button>
  <button id="v35-sheet">Скачать 6 кадров серии PNG</button>
 </div>
 <pre id="v35-audit-result" class="report" style="white-space:pre-wrap;max-height:320px;overflow:auto"></pre>
 <p class="muted">Эвристики показывают слишком короткие и длинные сцены, ограничения наложения, монтажную ось V34 и несоответствия временной шкалы. Не переписывают авторский сюжет.</p>
</div>
</section>
"""
def once(txt,old,new):
 n=txt.count(old)
 if n!=1:raise ValueError("V35 anchor "+repr(old[:100])+" occurrences="+str(n))
 return txt.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("anime_v34_builder",BASE)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def patch(html,addon):
 if "function v35Plan(" in html or 'id="page-assembly-v35"' in html:
  raise ValueError("V35 already added")
 for mark in ("function v34Camera(","function v33Act(","function v32Pose(",
              "function v30Audit(","function drawScene(","function v34Review("):
  if mark not in html:raise ValueError("Missing V19–V34 feature "+mark)
 html=once(html,'<button data-page="export">',
   '<button data-page="assembly-v35">Сборка серии V35</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
   PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V34';",
   "const storageKey='AI_ANIME_FACTORY_V35';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:34,",
   "P={format:'AIAnimeFactoryProject',version:35,")
 html=once(html,
   "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V33')",
   "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V34')||localStorage.getItem('AI_ANIME_FACTORY_V33')")
 html=once(html,"if(page==='storyboard-v34')v34Show();",
   "if(page==='storyboard-v34')v34Show();if(page==='assembly-v35')v35Show();")
 html=once(html,"v32Show();v33Show();v34Show();}",
   "v32Show();v33Show();v34Show();v35Show();}")
 html=once(html,"function show(page){currentPage=page;playing=false;",
   "function show(page){if(page!=='assembly-v35')v35Pause();currentPage=page;playing=false;")
 html=once(html,"'AI ANIME FACTORY V34  •  STORYBOARD & SHOTS'",
   "'AI ANIME FACTORY V35  •  EPISODE ASSEMBLY'")
 html=once(html,
   "const files=[{name:'AI_Anime_Factory_V34_STORYBOARD_CONTINUITY.html',data:selfHTML()},",
   "const files=[{name:'AI_Anime_Factory_V35_SCENE_ASSEMBLY.html',data:selfHTML()},"+
   "{name:'V35_EPISODE_ASSEMBLY_RU.txt',data:v35Report()},"+
   "{name:'V35_EPISODE_ASSEMBLY.json',data:JSON.stringify(v35Manifest(),null,2)},")
 html=once(html,"'AI_Anime_Factory_V34_STORYBOARD_CONTINUITY_Offline.html'",
   "'AI_Anime_Factory_V35_SCENE_ASSEMBLY_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<34)migrated.version=34;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<35)migrated.version=35;return migrated;}")
 anchor=("try{const old=localStorage.getItem(storageKey)||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V34')||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V33')||")
 html=once(html,anchor,"\n/* V35 SCENE ASSEMBLY */\n"+
   addon.strip()+"\n/* END V35 */\n"+anchor)
 return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 orig=V19.read_bytes();result=build()
 for mark in ("function v35Plan(","function v35Frame(","function v35Audit(",
              "function v34Camera(","function v33Face(","function v30Audit(",
              "V35_EPISODE_ASSEMBLY.json"):
  assert mark in result,mark
 assert V19.read_bytes()==orig
 print("V35 BUILDER PASS",len(result.encode("utf-8")),hashlib.sha256(orig).hexdigest())
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--selftest",action="store_true")
 a.add_argument("--output",default=str(OUTPUT))
 args=a.parse_args()
 if args.selftest:selftest();return
 dst=Path(args.output).resolve()
 if dst==V19.resolve():raise ValueError("Refusing to overwrite V19")
 dst.parent.mkdir(parents=True,exist_ok=True)
 body=build();dst.write_text(body,encoding="utf-8")
 print("V35 HTML BUILT",dst,dst.stat().st_size)
if __name__=="__main__":main()
