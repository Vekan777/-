#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a complete V41 editor non-destructively over the real V40/V19 chain."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory/v40/build_art_v40.py"
ADDON=Path(__file__).with_name("silhouette_v41.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html")

PANEL=r"""
<section class="page" id="page-silhouette-v41" hidden>
<div class="card">
 <h2>V41 — Силуэты, плащи и костюмы персонажей</h2>
 <p class="muted">Три различимых архетипа: защитник в доспехе, подвижный разведчик и маг с длинным одеянием. Настоящие контуры тела/костюма рисуются в 2D-риге и следуют движениям сцены. Рисовка V40, мимика V39, звук V36 и история сохраняются.</p>
 <div class="grid">
  <div class="field"><label>Персонаж</label><select id="v41-character"></select></div>
  <div class="field"><label>Тип силуэта</label><select id="v41-shape">
    <option value="guardian">Защитник — широкие плечи, длинный плащ</option>
    <option value="ranger">Разведчик — асимметричный костюм, хвост волос</option>
    <option value="arcanist">Маг — длинная мантия и эмблема</option>
  </select></div>
  <div class="field"><label>Цвет акцентов</label><select id="v41-palette">
   <option value="gold">Золото</option><option value="aqua">Бирюза</option>
   <option value="violet">Аметист</option><option value="ember">Янтарь</option>
  </select></div>
 </div>
 <label><input id="v41-enabled" type="checkbox" checked> Включить силуэт и костюм V41</label>
 <div class="grid">
  <div class="field"><label>Размах и динамика плаща <span id="v41-label-cape">88</span>%</label><input id="v41-cape" type="range" min="0" max="100"></div>
  <div class="field"><label>Броня плеч <span id="v41-label-shoulders">86</span>%</label><input id="v41-shoulders" type="range" min="0" max="100"></div>
  <div class="field"><label>Воротник и пластины <span id="v41-label-collar">66</span>%</label><input id="v41-collar" type="range" min="0" max="100"></div>
  <div class="field"><label>Сапоги и швы <span id="v41-label-boots">72</span>%</label><input id="v41-boots" type="range" min="0" max="100"></div>
  <div class="field"><label>Форма волос <span id="v41-label-hair">55</span>%</label><input id="v41-hair" type="range" min="0" max="100"></div>
  <div class="field"><label>Герб / эмблема <span id="v41-label-emblem">78</span>%</label><input id="v41-emblem" type="range" min="0" max="100"></div>
 </div>
 <button class="accent" id="v41-save">Сохранить силуэт персонажа</button>
 <p class="note">Новые параметры хранятся только в silhouetteV41 выбранного персонажа. Пользовательские PNG остаются без изменений. Это дополнительная рисовка векторного 2D-рига, а не создание 3D-моделей.</p>
</div>
<div class="card">
 <h2>Реальная проверка до и после на одном кадре</h2>
 <div class="grid">
  <div class="field"><label>V40 без нового силуэта</label><canvas class="preview" id="v41-before" width="640" height="360"></canvas></div>
  <div class="field"><label>V41 c новым силуэтом</label><canvas class="preview" id="v41-after" width="640" height="360"></canvas></div>
 </div>
 <label>Таймкод сцены <input id="v41-time" type="range" min="0" max="100" value="35"></label>
 <p class="muted" id="v41-caption">Выберите героя и сравните.</p>
 <div class="flex">
  <button id="v41-sheet">Скачать 4 кадра PNG</button>
  <button id="v41-json">Скачать параметры V41 JSON</button>
  <button id="v41-audit">Аудит читаемости силуэтов</button>
 </div>
 <pre class="report" id="v41-report" style="white-space:pre-wrap;max-height:310px;overflow:auto"></pre>
 <p class="note">Процедурные персонажи участвуют в прежнем проигрывателе V35 и реальной записи WebM со звуком V36. Внешние статичные PNG, которые перекрывают модель, не преобразуются автоматически.</p>
</div>
</section>
"""

def once(s,needle,value):
    count=s.count(needle)
    if count!=1:
        raise ValueError(f"V41 anchor occurrences {count}: {needle[:100]}")
    return s.replace(needle,value,1)

def previous():
    spec=importlib.util.spec_from_file_location("v40_art_builder",BASE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if 'id="page-silhouette-v41"' in html or "function v41Cape(" in html:
        raise ValueError("V41 already installed")
    for mark in ("function v23TorsoForm(","function v23LegForm(",
                 "function v40FaceInk(","function v39Move(",
                 "function v38Frame(","function v37Paint(",
                 "function v35Plan(","function v36Schedule("):
        if mark not in html:
            raise ValueError("Historical V19-V40 module missing: "+mark)
    html=once(html,'<button data-page="export">',
        '<button data-page="silhouette-v41">Силуэты V41</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
        PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V40';",
        "const storageKey='AI_ANIME_FACTORY_V41';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:40,",
        "P={format:'AIAnimeFactoryProject',version:41,")
    html=once(html,
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V39')",
        "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V40')||localStorage.getItem('AI_ANIME_FACTORY_V39')")
    html=once(html,"if(page==='character-art-v40')v40Show();",
        "if(page==='character-art-v40')v40Show();if(page==='silhouette-v41')v41Show();")
    html=once(html,"v39Show();v40Show();}",
        "v39Show();v40Show();v41Show();}")
    html=once(html,
        "'AI ANIME FACTORY V40  •  CHARACTER ART / DRAWING'",
        "'AI ANIME FACTORY V41  •  CHARACTER SILHOUETTES / COSTUMES'")
    html=once(html,
        "const files=[{name:'AI_Anime_Factory_V40_CHARACTER_ART.html',data:selfHTML()},",
        "const files=[{name:'AI_Anime_Factory_V41_SILHOUETTE_STUDIO.html',data:selfHTML()},"+
        "{name:'V41_SILHOUETTES.json',data:JSON.stringify(v41Manifest(),null,2)},")
    html=once(html,"'AI_Anime_Factory_V40_CHARACTER_ART_Offline.html'",
        "'AI_Anime_Factory_V41_SILHOUETTE_STUDIO_Offline.html'")
    html=once(html,
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<40)migrated.version=40;return migrated;}",
        "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<41)migrated.version=41;return migrated;}")
    html=once(html,
        "download('V40_CHARACTER_ART_EPISODE_'+slug(ep.title)+'.webm',blob);",
        "download('V41_SILHOUETTE_EPISODE_'+slug(ep.title)+'.webm',blob);")
    html=once(html,
        "V40: улучшенная рисовка персонажей записана в WebM (",
        "V41: новый силуэт персонажей записан в WebM (")
    html=once(html,
        '<button class="accent" id="v36-export">Записать V40 с улучшенной рисовкой</button>',
        '<button class="accent" id="v36-export">Записать V41 с силуэтами и костюмами</button>')
    anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V40')||"
    html=once(html,anchor,"\n/* V41 SILHOUETTES / COSTUME RIG */\n"+addon.strip()+
        "\n/* END V41 */\n"+anchor)
    return html

def build():
    return patch(previous().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes();html=build()
    for feature in ("function v41Cape(","function v41Armor(","function v41HairShape(",
                    "function v41Boots(","v23TorsoForm=function(",
                    "function v40FaceInk(","function v39Move(",
                    "AI_ANIME_FACTORY_V41",'id="v41-after"'):
        assert feature in html,feature
    assert V19.read_bytes()==original
    print("V41 SOURCE PRESERVED",len(html.encode("utf-8")),
          hashlib.sha256(original).hexdigest())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--output",default=str(OUTPUT))
    args=ap.parse_args()
    if args.selftest:
        selftest();return
    output=Path(args.output).resolve()
    if output==V19.resolve():
        raise ValueError("Refusing to overwrite original V19")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(build(),encoding="utf-8")
    print("V41 HTML",output,output.stat().st_size)
if __name__=="__main__":
    main()
