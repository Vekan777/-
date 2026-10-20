#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V27 environment from original V19 and additive V20–V26 builders."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v26"/"build_cinematic_v26.py"
ADDON=Path(__file__).with_name("world_v27.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V27_WORLD_QUALITY.html")

PANEL=r"""
<section class="page" id="page-world-v27" hidden>
<div class="card">
 <h2>V27 — Мир и окружение: глубина, земля, свет</h2>
 <p class="muted">Процедурные 2D-слои для каждой сцены. Планы камеры, сюжет, способности и персонажи V19–V26 сохраняются. Нарисованные PNG персонажей не изменяются.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v27-scene"></select></div>
  <div class="field"><label>Тип окружения</label><select id="v27-biome">
   <option value="auto">Как в сценарии</option>
   <option value="city">Город</option>
   <option value="forest">Лес</option>
   <option value="temple">Храм</option>
   <option value="battlefield">Поле боя</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v27-enabled" checked> Добавить слои мира V27</label>
 <div class="grid">
  <div class="field"><label>Многослойная глубина <span id="v27-depth-n">76</span>%</label><input type="range" id="v27-depth" min="0" max="100"></div>
  <div class="field"><label>Атмосферный свет <span id="v27-lighting-n">68</span>%</label><input type="range" id="v27-lighting" min="0" max="100"></div>
  <div class="field"><label>Контакт с землёй <span id="v27-grounding-n">74</span>%</label><input type="range" id="v27-grounding" min="0" max="100"></div>
  <div class="field"><label>Воздушная перспектива <span id="v27-atmosphere-n">61</span>%</label><input type="range" id="v27-atmosphere" min="0" max="100"></div>
  <div class="field"><label>Передний план <span id="v27-foreground-n">52</span>%</label><input type="range" id="v27-foreground" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v27-preset">Пресет мира</button>
 <button class="accent" id="v27-save">Сохранить окружение V27</button></div>
</div>
<div class="card">
 <h2>Одна сцена, одна секунда — сравнение V26 / V27</h2>
 <div class="grid">
  <div class="field"><label>V26 — исходный кадр</label>
   <canvas class="preview" id="v27-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V27 — глубина и окружение</label>
   <canvas class="preview" id="v27-after" width="640" height="360"></canvas></div>
 </div>
 <label>Время сцены <input type="range" id="v27-position" min="0" max="100" value="45"></label>
 <p class="muted" id="v27-caption"></p>
 <div class="flex"><button id="v27-sheet">Скачать 4 кадра PNG</button>
 <button id="v27-plan">Скачать паспорт мира TXT</button></div>
</div>
<div class="card">
 <h2>Контроль окружения</h2>
 <pre id="v27-qa" class="report" style="white-space:pre-wrap;max-height:260px;overflow:auto"></pre>
 <div class="note">Это стилизованный 2D Canvas-мир с перспективой, а не геометрический 3D-мир. Детали добавляются процедурно и не заменяют нарисованные вручную фоны.</div>
</div>
</section>
"""

def once(txt,old,new):
    count=txt.count(old)
    if count!=1:
        raise ValueError("V27 integration marker "+repr(old[:100])+" count="+str(count))
    return txt.replace(old,new,1)

def base26():
    spec=importlib.util.spec_from_file_location("anime_v26_builder",BASE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if "function v27World(" in html or 'id="page-world-v27"' in html:
        raise ValueError("V27 already integrated")
    for tag in ("function v26Camera(","function v25PairPose(","function v24Dynamics(",
                "function v23HeadScale(","function v22Mood(","function v20CanonLines("):
        if tag not in html:raise ValueError("Missing integrated prior module "+tag)
    html=once(html,'<button data-page="export">',
        '<button data-page="world-v27">Мир V27</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
        PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V26';",
        "const storageKey='AI_ANIME_FACTORY_V27';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:26,",
        "P={format:'AIAnimeFactoryProject',version:27,")
    html=once(html,
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V25')",
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V26')||localStorage.getItem('AI_ANIME_FACTORY_V25')")
    html=once(html,"if(page==='cinematic-v26')v26Show();",
        "if(page==='cinematic-v26')v26Show();if(page==='world-v27')v27Show();")
    html=once(html,"v24Show();v25Show();v26Show();}",
        "v24Show();v25Show();v26Show();v27Show();}")
    html=once(html,
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA());",
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA(),v27QA());")
    # The new depth pass is behind authored character drawings.
    html=once(html,
        "drawBG(g,w,h,s.background,sec,q.lighting,q.effects);v21AtmosphereBack(g,w,h,s,sec);cin14Layers(g,w,h,s,sec,'far');",
        "drawBG(g,w,h,s.background,sec,q.lighting,q.effects);v21AtmosphereBack(g,w,h,s,sec);v27Back(g,w,h,s,sec);cin14Layers(g,w,h,s,sec,'far');")
    # Contact shadows follow the already calculated character poses.
    html=once(html,
        "for(const p of [poses.hero,poses.partner]){g.fillStyle='rgba(3,9,17,.55)';",
        "v27Feet(g,w,h,s,sec,poses);for(const p of [poses.hero,poses.partner]){g.fillStyle='rgba(3,9,17,.55)';")
    # Foreground is screen-space and under later vignette/caption passes.
    html=once(html,
        "g.restore();cin14Layers(g,w,h,s,sec,'near');v21AtmosphereFront(g,w,h,s,sec);",
        "g.restore();cin14Layers(g,w,h,s,sec,'near');v21AtmosphereFront(g,w,h,s,sec);v27Front(g,w,h,s,sec);")
    html=once(html,"'AI ANIME FACTORY V26  •  CINEMATIC COMBAT'",
        "'AI ANIME FACTORY V27  •  WORLD QUALITY'")
    html=once(html,
        "const files=[{name:'AI_Anime_Factory_V26_CINEMATIC_COMBAT.html',data:selfHTML()},",
        "const files=[{name:'AI_Anime_Factory_V27_WORLD_QUALITY.html',data:selfHTML()},"+
        "{name:'V27_WORLD_PLAN_RU.txt',data:v27Plan()},"+
        "{name:'V27_WORLD_SETTINGS.json',data:JSON.stringify(P.episodes.map(e=>"+
        "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,worldV27:v27World(s)}))})),null,2)},")
    html=once(html,"'AI_Anime_Factory_V26_CINEMATIC_COMBAT_Offline.html'",
        "'AI_Anime_Factory_V27_WORLD_QUALITY_Offline.html'")
    html=once(html,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<26)migrated.version=26;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<27)migrated.version=27;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V26')||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V25')||")
    html=once(html,anchor,"\n/* V27 WORLD ENVIRONMENT */\n"+
        addon.strip()+"\n/* END V27 */\n"+anchor)
    return html

def build():
    return patch(base26().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=ORIGINAL.read_bytes()
    html=build()
    for mark in ('id="page-world-v27"',"function v27Back(",
                 "function v27Feet(","function v27Front(",
                 "function v26Camera(","function v25PairPose(",
                 "function v24Dynamics(","function v23HeadScale(",
                 "function v20CanonLines(","V27_WORLD_SETTINGS.json"):
        assert mark in html,mark
    assert ORIGINAL.read_bytes()==original
    print("V27 PATCH PASS",len(html.encode("utf-8")),hashlib.sha256(original).hexdigest())

def main():
    args=argparse.ArgumentParser()
    args.add_argument("--output",default=str(OUTPUT))
    args.add_argument("--selftest",action="store_true")
    opt=args.parse_args()
    if opt.selftest:selftest();return
    target=Path(opt.output).resolve()
    if target==ORIGINAL.resolve():raise ValueError("Refusing V19 overwrite")
    target.parent.mkdir(parents=True,exist_ok=True)
    html=build()
    target.write_text(html,encoding="utf-8")
    print("V27 HTML BUILT",target,"bytes",target.stat().st_size)

if __name__=="__main__":main()
