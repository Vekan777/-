#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V34 shot continuity adds real camera framing to preserved V19–V33."""
from __future__ import annotations
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v33"/"build_acting_v33.py"
ADDON=Path(__file__).with_name("storyboard_v34.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V34_STORYBOARD_CONTINUITY.html")
PANEL=r"""
<section class="page" id="page-storyboard-v34" hidden>
<div class="card">
<h2>V34 — Раскадровка и непрерывность планов</h2>
<p class="muted">Три ключевых плана для каждой сцены: общий, средний, крупный. Плавный переход, выбор объекта камеры и контроль монтажной оси между соседними сценами. Сюжет и исходная анимация V19–V33 не переписываются.</p>
<div class="grid">
 <div class="field"><label>Сцена</label><select id="v34-scene"></select></div>
 <div class="field"><label>Объект внимания</label><select id="v34-focus">
  <option value="center">Центр сцены</option>
  <option value="hero">Главный герой</option>
  <option value="partner">Второй персонаж</option>
 </select></div>
 <div class="field"><label>Монтажная ось</label><select id="v34-axis">
  <option value="neutral">Нейтрально / без разметки</option>
  <option value="left">Слева направо</option>
  <option value="right">Справа налево</option>
 </select></div>
</div>
<label><input type="checkbox" id="v34-enabled" checked> Включить новую композицию V34</label>
<div class="grid">
 <div class="field"><label>Сила крупности <span id="v34-strength-n">76</span>%</label>
  <input id="v34-strength" type="range" min="0" max="100"></div>
 <div class="field"><label>Слежение за персонажем <span id="v34-tracking-n">52</span>%</label>
  <input id="v34-tracking" type="range" min="0" max="100"></div>
 <div class="field"><label>Плавность смены планов <span id="v34-smoothness-n">82</span>%</label>
  <input id="v34-smoothness" type="range" min="0" max="100"></div>
</div>
<div class="grid">
 <div class="field"><label>Ключевой момент</label><select id="v34-beat">
  <option value="0">Начало — 12%</option><option value="1">Середина — 50%</option>
  <option value="2">Конец — 88%</option>
 </select></div>
 <div class="field"><label>Крупность выбранного момента</label><select id="v34-shot">
  <option value="wide">Общий план</option><option value="medium">Средний план</option>
  <option value="close">Крупный план</option>
 </select></div>
</div>
<div class="flex"><button id="v34-preset">Профиль общий → крупный</button>
 <button class="accent" id="v34-save">Сохранить раскадровку</button></div>
</div>
<div class="card">
<h2>Сравнение одного момента V33 / V34</h2>
<div class="grid">
 <div class="field"><label>V33 — прежняя камера</label>
  <canvas class="preview" id="v34-before" width="640" height="360"></canvas></div>
 <div class="field"><label>V34 — планы и композиция</label>
  <canvas class="preview" id="v34-after" width="640" height="360"></canvas></div>
</div>
<label>Момент сцены <input id="v34-position" type="range" min="0" max="100" value="50"></label>
<p class="muted" id="v34-caption"></p>
<div class="flex"><button id="v34-audit">Проверить стыки сцен</button>
 <button id="v34-sheet">Скачать PNG раскадровки</button>
 <button id="v34-plan">План монтажа TXT</button></div>
<pre class="report" id="v34-report" style="white-space:pre-wrap;max-height:310px;overflow:auto"></pre>
</div>
<div class="card">
<h2>Контроль предыдущих сцен</h2>
<p class="note">Экспорт PNG включает последние кадры предыдущей сцены, три ключевых момента текущей и начало следующей в пределах серии. Проверка монтажной оси только предупреждает о возможной ошибке: она не переворачивает персонажей и не гарантирует кинематографически правильный монтаж.</p>
<p class="muted">Это процедурный 2D-аниматик; цвет, пользовательские PNG, сюжет V20, боевые результаты V19/V17, анимация и эмоции V19–V33 сохраняются. Видеомонтаж соседних кадров нужно проверять отдельно.</p>
</div>
</section>
"""
def once(s,old,new):
 n=s.count(old)
 if n!=1:raise ValueError("V34 integration anchor "+repr(old[:100])+" occurrences="+str(n))
 return s.replace(old,new,1)
def previous():
 spec=importlib.util.spec_from_file_location("anime_v33_builder",BASE)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def patch(html,addon):
 if "function v34Camera(" in html or 'id="page-storyboard-v34"' in html:
  raise ValueError("V34 already applied")
 for x in ("function v33Face(","function v32Pose(","function v31Metrics(",
           "function v30Audit(","function v26Camera(","function drawScene("):
  if x not in html:raise ValueError("Missing V19–V33 integration "+x)
 html=once(html,'<button data-page="export">',
  '<button data-page="storyboard-v34">Раскадровка V34</button><button data-page="export">')
 html=once(html,'<section class="page" id="page-export" hidden>',
  PANEL+'<section class="page" id="page-export" hidden>')
 html=once(html,"const storageKey='AI_ANIME_FACTORY_V33';",
  "const storageKey='AI_ANIME_FACTORY_V34';")
 html=once(html,"P={format:'AIAnimeFactoryProject',version:33,",
  "P={format:'AIAnimeFactoryProject',version:34,")
 html=once(html,
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V32')",
  "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V33')||localStorage.getItem('AI_ANIME_FACTORY_V32')")
 html=once(html,"if(page==='acting-v33')v33Show();",
  "if(page==='acting-v33')v33Show();if(page==='storyboard-v34')v34Show();")
 html=once(html,"v31UpdateUI();v32Show();v33Show();}",
  "v31UpdateUI();v32Show();v33Show();v34Show();}")
 # This updates the genuine drawScene transformation used for PNG/video
 # export and for every scene, without modifying earlier V26 combat direction.
 html=once(html,
  "const camera14=cin14Camera(s,v),camera26=v26Camera(s,sec);"+
  "g.scale(cam.scale*camera14.zoom*camera26.zoom,cam.scale*camera14.zoom*camera26.zoom);"+
  "g.translate(-w/2-(cam.x+camera14.dx+camera26.dx)*w,-h/2-(cam.y+camera14.dy+camera26.dy)*h);",
  "const camera14=cin14Camera(s,v),camera26=v26Camera(s,sec),camera34=v34Camera(s,sec);"+
  "g.scale(cam.scale*camera14.zoom*camera26.zoom*camera34.zoom,cam.scale*camera14.zoom*camera26.zoom*camera34.zoom);"+
  "g.translate(-w/2-(cam.x+camera14.dx+camera26.dx+camera34.dx)*w,-h/2-(cam.y+camera14.dy+camera26.dy+camera34.dy)*h);")
 html=once(html,"'AI ANIME FACTORY V33  •  ACTING & EXPRESSION'",
  "'AI ANIME FACTORY V34  •  STORYBOARD & SHOTS'")
 html=once(html,
  "const files=[{name:'AI_Anime_Factory_V33_ACTING_EXPRESSION.html',data:selfHTML()},",
  "const files=[{name:'AI_Anime_Factory_V34_STORYBOARD_CONTINUITY.html',data:selfHTML()},"+
  "{name:'V34_SHOT_CONTINUITY_RU.txt',data:v34StoryboardText()},"+
  "{name:'V34_SCENE_SHOTS.json',data:JSON.stringify(P.episodes.map(e=>"+
  "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,storyboardV34:v34Of(s)}))})),null,2)},")
 html=once(html,"'AI_Anime_Factory_V33_ACTING_EXPRESSION_Offline.html'",
  "'AI_Anime_Factory_V34_STORYBOARD_CONTINUITY_Offline.html'")
 html=once(html,
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<33)migrated.version=33;return migrated;}",
  "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<34)migrated.version=34;return migrated;}")
 anchor=("try{const old=localStorage.getItem(storageKey)||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V33')||"+
   "localStorage.getItem('AI_ANIME_FACTORY_V32')||")
 html=once(html,anchor,"\n/* V34 STORYBOARD AND SHOT CONTINUITY */\n"+
  addon.strip()+"\n/* END V34 */\n"+anchor)
 return html
def build():
 return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
 original=V19.read_bytes();txt=build()
 for x in ("function v34Camera(","function v34Review(","function v34Sheet(",
           "function v33Act(","function v32Pose(","function v31Grade(",
           "V34_SCENE_SHOTS.json"):
  assert x in txt,x
 assert V19.read_bytes()==original
 print("V34 BUILDER PASS",len(txt.encode("utf-8")),hashlib.sha256(original).hexdigest())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--output",default=str(OUTPUT))
 p.add_argument("--selftest",action="store_true")
 a=p.parse_args()
 if a.selftest:selftest();return
 dst=Path(a.output).resolve()
 if dst==V19.resolve():raise ValueError("Cannot overwrite original V19")
 dst.parent.mkdir(parents=True,exist_ok=True)
 result=build();dst.write_text(result,encoding="utf-8")
 print("V34 HTML BUILT",dst,dst.stat().st_size)
if __name__=="__main__":main()
