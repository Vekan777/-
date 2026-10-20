#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrate V26 camera direction without overwriting genuine V19/V20–V25."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE25=ROOT/"anime-factory"/"v25"/"build_combat_v25.py"
ADDON=Path(__file__).with_name("cinematic_v26.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V26_CINEMATIC_COMBAT.html")

PANEL=r"""
<section class="page" id="page-cinematic-v26" hidden>
<div class="card">
 <h2>V26 — Кинематографичный бой: камера и монтаж</h2>
 <p class="muted">Режиссура 2D-сцены — общий/средний/крупный планы, реакция на размеченные удары и аккуратные затемнения. Все настройки персонажей, сценария и хореографии V19–V25 сохранены.</p>
 <div class="grid">
  <div class="field"><label>Боевая сцена</label><select id="v26-scene"></select></div>
  <div class="field"><label>План камеры</label><select id="v26-style">
   <option value="dynamic">Динамическая съёмка</option>
   <option value="wide">Преимущественно общий план</option>
   <option value="close">Крупный план</option>
   <option value="subtle">Сдержанный стиль</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v26-enabled" checked> Включить режиссуру V26</label>
 <div class="grid">
  <div class="field"><label>Выразительность камеры <span id="v26-intensity-n">72</span>%</label><input type="range" id="v26-intensity" min="0" max="100"></div>
  <div class="field"><label>Слежение за действием <span id="v26-tracking-n">74</span>%</label><input type="range" id="v26-tracking" min="0" max="100"></div>
  <div class="field"><label>Акцент на ударе <span id="v26-impactFocus-n">68</span>%</label><input type="range" id="v26-impactFocus" min="0" max="100"></div>
  <div class="field"><label>Кинополосы <span id="v26-letterbox-n">62</span>%</label><input type="range" id="v26-letterbox" min="0" max="100"></div>
  <div class="field"><label>Монтажные переходы <span id="v26-transitions-n">48</span>%</label><input type="range" id="v26-transitions" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v26-preset">Пресет кинобоя</button>
 <button class="accent" id="v26-save">Сохранить режиссуру V26</button></div>
</div>
<div class="card">
 <h2>Кадр на одном времени — V25 против V26</h2>
 <div class="grid">
  <div class="field"><label>V25 — базовый ракурс</label>
   <canvas class="preview" id="v26-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V26 — операторская постановка</label>
   <canvas class="preview" id="v26-after" width="640" height="360"></canvas></div>
 </div>
 <label>Время сцены <input type="range" id="v26-position" min="0" max="100" value="45"></label>
 <p class="muted" id="v26-status"></p>
 <div class="flex"><button id="v26-sheet">Скачать 4 кадра PNG</button>
 <button id="v26-plan">Скачать список планов TXT</button></div>
</div>
<div class="card">
 <h2>Контроль качества монтажа</h2>
 <pre id="v26-qa" class="report" style="white-space:pre-wrap;max-height:260px;overflow:auto"></pre>
 <div class="note">Это управление 2D Canvas-камерой, не новая 3D-камера, motion capture или профессиональный автоматический режиссёр. Прежняя разметка попаданий не изменяется.</div>
</div>
</section>
"""

def once(txt,marker,value):
    n=txt.count(marker)
    if n!=1:raise ValueError("V26 integration anchor "+repr(marker[:90])+" count "+str(n))
    return txt.replace(marker,value,1)

def base25():
    spec=importlib.util.spec_from_file_location("anime_v25_builder",BASE25)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(txt,addon):
    if "function v26Camera(" in txt or 'id="page-cinematic-v26"' in txt:
        raise ValueError("V26 already present")
    for tag in ("function v25PairPose(","function v24Dynamics(",
                "function v23HeadScale(","function v22Mood(","function v20CanonLines("):
        if tag not in txt:raise ValueError("Integrated source missing "+tag)
    txt=once(txt,'<button data-page="export">',
         '<button data-page="cinematic-v26">Камера V26</button><button data-page="export">')
    txt=once(txt,'<section class="page" id="page-export" hidden>',
         PANEL+'<section class="page" id="page-export" hidden>')
    txt=once(txt,"const storageKey='AI_ANIME_FACTORY_V25';",
         "const storageKey='AI_ANIME_FACTORY_V26';")
    txt=once(txt,"P={format:'AIAnimeFactoryProject',version:25,",
         "P={format:'AIAnimeFactoryProject',version:26,")
    txt=once(txt,
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V24')",
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V25')||localStorage.getItem('AI_ANIME_FACTORY_V24')")
    txt=once(txt,"if(page==='combat-v25')v25Show();",
         "if(page==='combat-v25')v25Show();if(page==='cinematic-v26')v26Show();")
    txt=once(txt,"v23Show();v24Show();v25Show();}",
         "v23Show();v24Show();v25Show();v26Show();}")
    txt=once(txt,
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA());",
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA());")
    # Camera move is applied to exactly the existing canvas coordinate system.
    txt=once(txt,
        "const camera14=cin14Camera(s,v);g.scale(cam.scale*camera14.zoom,cam.scale*camera14.zoom);g.translate(-w/2-(cam.x+camera14.dx)*w,-h/2-(cam.y+camera14.dy)*h);",
        "const camera14=cin14Camera(s,v),camera26=v26Camera(s,sec);"+
        "g.scale(cam.scale*camera14.zoom*camera26.zoom,cam.scale*camera14.zoom*camera26.zoom);"+
        "g.translate(-w/2-(cam.x+camera14.dx+camera26.dx)*w,-h/2-(cam.y+camera14.dy+camera26.dy)*h);")
    # Overlay is drawn at absolute frame coordinates AFTER original post.
    txt=once(txt," cin14Post(g,w,h,s,sec);\n}",
         " cin14Post(g,w,h,s,sec);v26FinishFrame(g,w,h,s,sec);\n}")
    txt=once(txt,"'AI ANIME FACTORY V25  •  COMBAT CHOREOGRAPHY'",
         "'AI ANIME FACTORY V26  •  CINEMATIC COMBAT'")
    txt=once(txt,
        "const files=[{name:'AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY.html',data:selfHTML()},",
        "const files=[{name:'AI_Anime_Factory_V26_CINEMATIC_COMBAT.html',data:selfHTML()},"+
        "{name:'V26_SHOT_LIST_RU.txt',data:v26Plan()},"+
        "{name:'V26_CAMERA_SETTINGS.json',data:JSON.stringify(P.episodes.map(e=>"+
        "({number:e.number,scenes:e.scenes.filter(s=>s.kind==='fight').map(s=>"+
        "({title:s.title,cinemaV26:v26Options(s)}))})),null,2)},")
    txt=once(txt,"'AI_Anime_Factory_V25_COMBAT_CHOREOGRAPHY_Offline.html'",
         "'AI_Anime_Factory_V26_CINEMATIC_COMBAT_Offline.html'")
    txt=once(txt,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<25)migrated.version=25;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<26)migrated.version=26;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V25')||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V24')||")
    txt=once(txt,anchor,"\n/* V26 CINEMATIC COMBAT */\n"+
         addon.strip()+"\n/* END V26 */\n"+anchor)
    return txt

def build():
    return patch(base25().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    html=build()
    for mark in ('id="page-cinematic-v26"',"function v26Camera(",
                 "function v26FinishFrame(","function v26Plan(",
                 "function v25PairPose(","function v24Dynamics(",
                 "function v23HeadScale(","function v20CanonLines(",
                 "function impact19State(","V26_CAMERA_SETTINGS.json"):
        assert mark in html,mark
    assert original==V19.read_bytes()
    print("V26 PATCH PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default=str(OUTPUT))
    parser.add_argument("--selftest",action="store_true")
    opts=parser.parse_args()
    if opts.selftest:selftest();return
    target=Path(opts.output).resolve()
    if target==V19.resolve():raise ValueError("Never overwrite V19 original")
    target.parent.mkdir(parents=True,exist_ok=True)
    payload=build()
    target.write_text(payload,encoding="utf-8")
    print("V26 HTML BUILT",target,"bytes",target.stat().st_size)

if __name__=="__main__":main()
