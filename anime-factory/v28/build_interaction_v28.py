#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add V28 actor-environment interaction to genuine V19→V27 studio."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v27"/"build_world_v27.py"
ADDON=Path(__file__).with_name("interaction_v28.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html")

PANEL=r"""
<section class="page" id="page-interaction-v28" hidden>
<div class="card">
 <h2>V28 — Персонажи и мир: следы, пыль, свет, последствия боя</h2>
 <p class="muted">Свет и эффект контакта подстраиваются к реальному положению персонажей. События попаданий берутся только из уже существующей разметки боя V19/V17. Сюжет, камера, мир и редакторы V19–V27 сохраняются.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v28-scene"></select></div>
  <div class="field"><label>Стиль взаимодействия</label><select id="v28-style">
   <option value="auto">Автоматический</option>
   <option value="subtle">Сдержанный</option>
   <option value="dramatic">Выразительный</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v28-enabled" checked> Включить взаимодействие V28</label>
 <div class="grid">
  <div class="field"><label>Контакт ног с землёй <span id="v28-footsteps-n">72</span>%</label><input type="range" id="v28-footsteps" min="0" max="100"></div>
  <div class="field"><label>Пыль при движении <span id="v28-dust-n">68</span>%</label><input type="range" id="v28-dust" min="0" max="100"></div>
  <div class="field"><label>Отражённый свет <span id="v28-bounce-n">73</span>%</label><input type="range" id="v28-bounce" min="0" max="100"></div>
  <div class="field"><label>Следы ударов на земле <span id="v28-scars-n">61</span>%</label><input type="range" id="v28-scars" min="0" max="100"></div>
  <div class="field"><label>Боевой световой акцент <span id="v28-impactFX-n">68</span>%</label><input type="range" id="v28-impactFX" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v28-preset">Кинематографичный профиль</button>
 <button class="accent" id="v28-save">Сохранить взаимодействие V28</button></div>
</div>
<div class="card">
 <h2>Один кадр, одна сцена — сравнение V27 / V28</h2>
 <div class="grid">
  <div class="field"><label>V27 — мир без взаимодействия V28</label>
    <canvas class="preview" id="v28-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V28 — контакт персонажей с миром</label>
    <canvas class="preview" id="v28-after" width="640" height="360"></canvas></div>
 </div>
 <label>Время сцены <input type="range" id="v28-position" min="0" max="100" value="45"></label>
 <p class="muted" id="v28-caption"></p>
 <div class="flex"><button id="v28-sheet">Скачать 4 кадра PNG</button>
 <button id="v28-plan">Скачать план взаимодействий TXT</button></div>
</div>
<div class="card">
 <h2>Контроль визуальных эффектов</h2>
 <pre id="v28-qa" class="report" style="white-space:pre-wrap;max-height:260px;overflow:auto"></pre>
 <div class="note">Эффекты являются процедурной 2D-постановкой, не физической симуляцией и не постоянно сохраняемыми повреждениями мира. Изображения PNG персонажей не перерисовываются.</div>
</div>
</section>
"""

def once(txt,old,new):
    count=txt.count(old)
    if count!=1:
        raise ValueError("V28 expected one marker: "+repr(old[:100])+" count "+str(count))
    return txt.replace(old,new,1)

def base27():
    spec=importlib.util.spec_from_file_location("anime_v27_builder",BASE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def patch(html,addon):
    if "function v28Options(" in html or 'id="page-interaction-v28"' in html:
        raise ValueError("V28 already integrated")
    for key in ("function v27Back(","function v26Camera(","function v25Contact(",
                "function v24Dynamics(","function v23HeadScale(",
                "function v20CanonLines("):
        if key not in html:raise ValueError("Prior source missing "+key)
    html=once(html,'<button data-page="export">',
        '<button data-page="interaction-v28">Взаимодействие V28</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
        PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V27';",
        "const storageKey='AI_ANIME_FACTORY_V28';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:27,",
        "P={format:'AIAnimeFactoryProject',version:28,")
    html=once(html,
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V26')",
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V27')||localStorage.getItem('AI_ANIME_FACTORY_V26')")
    html=once(html,"if(page==='world-v27')v27Show();",
        "if(page==='world-v27')v27Show();if(page==='interaction-v28')v28Show();")
    html=once(html,"v25Show();v26Show();v27Show();}",
        "v25Show();v26Show();v27Show();v28Show();}")
    html=once(html,
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA(),v27QA());",
        "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA(),v24MotionQA(),v25QA(),v26QA(),v27QA(),v28QA());")
    # Draw ambient bounce UNDER imported characters, preserving user art layers.
    html=once(html,
        "v27Back(g,w,h,s,sec);cin14Layers(g,w,h,s,sec,'far');",
        "v27Back(g,w,h,s,sec);v28Background(g,w,h,s,sec);cin14Layers(g,w,h,s,sec,'far');")
    # Use poses that already include V17/V19 impacts + V25 choreography.
    html=once(html,
        "v27Feet(g,w,h,s,sec,poses);for(const p of [poses.hero,poses.partner])",
        "v27Feet(g,w,h,s,sec,poses);v28Ground(g,w,h,s,sec,poses);v28CombatGround(g,w,h,s,sec,poses);for(const p of [poses.hero,poses.partner])")
    # Actor light is deliberately restrained and does not change any combat result.
    html=once(html,
        "v22CombatClarity(g,w,h,s,sec,combat17,poses);",
        "v22CombatClarity(g,w,h,s,sec,combat17,poses);v28ActorLight(g,w,h,s,sec,poses);")
    html=once(html,"'AI ANIME FACTORY V27  •  WORLD QUALITY'",
        "'AI ANIME FACTORY V28  •  CHARACTER–ENVIRONMENT'")
    html=once(html,
        "const files=[{name:'AI_Anime_Factory_V27_WORLD_QUALITY.html',data:selfHTML()},",
        "const files=[{name:'AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION.html',data:selfHTML()},"+
        "{name:'V28_INTERACTION_PLAN_RU.txt',data:v28Plan()},"+
        "{name:'V28_INTERACTION_SETTINGS.json',data:JSON.stringify(P.episodes.map(e=>"+
        "({number:e.number,scenes:e.scenes.map(s=>({title:s.title,interactionV28:v28Options(s)}))})),null,2)},")
    html=once(html,"'AI_Anime_Factory_V27_WORLD_QUALITY_Offline.html'",
        "'AI_Anime_Factory_V28_CHARACTER_WORLD_INTERACTION_Offline.html'")
    html=once(html,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<27)migrated.version=27;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<28)migrated.version=28;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V27')||"+
        "localStorage.getItem('AI_ANIME_FACTORY_V26')||")
    html=once(html,anchor,"\n/* V28 CHARACTER WORLD INTERACTION */\n"+
        addon.strip()+"\n/* END V28 */\n"+anchor)
    return html

def build():
    return patch(base27().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    before=V19.read_bytes()
    content=build()
    for key in ('id="page-interaction-v28"',"function v28Ground(",
                "function v28CombatGround(","function v28ActorLight(",
                "function v28ImpactAt(","function v27Feet(",
                "function v26Camera(","function v25PairPose(",
                "function v20CanonLines(","V28_INTERACTION_SETTINGS.json"):
        assert key in content,key
    assert V19.read_bytes()==before
    print("V28 SELFTEST PASS",len(content.encode("utf-8")),hashlib.sha256(before).hexdigest())

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--selftest",action="store_true")
    cli.add_argument("--output",default=str(OUTPUT))
    args=cli.parse_args()
    if args.selftest:selftest();return
    out=Path(args.output).resolve()
    if out==V19.resolve():raise ValueError("Cannot overwrite original V19")
    out.parent.mkdir(parents=True,exist_ok=True)
    content=build()
    out.write_text(content,encoding="utf-8")
    print("V28 HTML BUILT",out,"bytes",out.stat().st_size)

if __name__=="__main__":main()
