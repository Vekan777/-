#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch genuine V19 -> V20 -> V21 2D visual studio without overwriting originals."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
V20_BUILD=ROOT/"anime-factory"/"v20"/"build_story_v20.py"
V20_ADDON=ROOT/"anime-factory"/"v20"/"story_v20.js"
V21_ADDON=Path(__file__).with_name("visual_v21.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V21_VISUAL_QUALITY.html")

PANEL=r"""
<section class="page" id="page-visual-v21" hidden>
<div class="card">
<h2>V21 — Визуальный режиссёр: освещение, мир, персонажи и удары</h2>
<p class="muted">Параметры каждой сцены хранятся в JSON. Новые слои работают при предварительном просмотре и штатном экспорте кадров.</p>
<div class="grid">
<div class="field"><label>Выбрать сцену</label><select id="v21-scene"></select></div>
<div class="field"><label>Визуальный стиль</label><select id="v21-look">
<option value="azure">Ледяная лазурь</option><option value="sunset">Золотой закат</option>
<option value="moon">Синяя луна</option><option value="emerald">Изумрудный лес</option>
<option value="crimson">Алая битва</option>
</select></div></div>
<div class="grid">
<div class="field"><label>Атмосфера</label><select id="v21-weather">
<option value="clear">Чистый воздух</option><option value="mist">Туман</option>
<option value="rain">Дождь</option><option value="snow">Снег</option>
<option value="embers">Искры и угли</option>
</select></div>
<div class="field"><label><input type="checkbox" id="v21-enabled" checked> Включить слои V21 для сцены</label></div>
</div>
<div class="grid">
<div class="field"><label>Сила цветового стиля: <span id="v21-intensity-value">72</span>%</label><input id="v21-intensity" type="range" min="0" max="100"></div>
<div class="field"><label>Глубина окружения: <span id="v21-depth-value">67</span>%</label><input id="v21-depth" type="range" min="0" max="100"></div>
<div class="field"><label>Объёмные лучи: <span id="v21-rays-value">50</span>%</label><input id="v21-rays" type="range" min="0" max="100"></div>
<div class="field"><label>Контровой свет героев: <span id="v21-rim-value">60</span>%</label><input id="v21-rim" type="range" min="0" max="100"></div>
<div class="field"><label>Искры и эффект удара: <span id="v21-sparks-value">65</span>%</label><input id="v21-sparks" type="range" min="0" max="100"></div>
<div class="field"><label>Кинозерно: <span id="v21-grain-value">10</span>%</label><input id="v21-grain" type="range" min="0" max="100"></div>
</div>
<div class="flex">
<button class="accent" id="v21-save">Применить и сохранить</button>
<button id="v21-preset">Режиссёрский пресет сцены</button>
<button id="v21-report">Скачать план освещения TXT</button>
</div></div>
<div class="grid">
<div class="card">
<h2>Предпросмотр из общего рендера</h2>
<canvas id="v21-preview" class="preview" width="960" height="540"></canvas>
<label>Время сцены: <input id="v21-position" type="range" min="0" max="100" value="50"></label>
<div id="v21-caption" class="muted"></div>
<button id="v21-sheet">Скачать четыре кадра PNG</button>
</div>
<div class="card">
<h2>Контроль композиции V21</h2>
<pre class="report" id="v21-qa" style="white-space:pre-wrap;max-height:330px;overflow:auto"></pre>
<div class="note">V21 добавляет световые и атмосферные слои в процедурный 2D-аниматик. Персонажи остаются рисованными векторными/слойными черновиками, если вы не загрузили качественный авторский арт.</div>
</div></div>
</section>
"""


def replace_once(text, old, new):
    if text.count(old)!=1:
        raise ValueError("V20 structure changed: expected unique marker "+repr(old[:90]))
    return text.replace(old,new,1)


def import_v20_builder():
    spec=importlib.util.spec_from_file_location("anime_v20_builder",V20_BUILD)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch(v20,addon):
    if "v21AtmosphereBack" in v20 or 'id="page-visual-v21"' in v20:
        raise ValueError("Already V21 or incompatible source")
    if "function v20CanonLines()" not in v20 or "function impact19State(" not in v20:
        raise ValueError("Expected integrated V20 from genuine V19")

    result=replace_once(v20,'<button data-page="export">',
                        '<button data-page="visual-v21">Визуал V21</button><button data-page="export">')
    result=replace_once(result,'<section class="page" id="page-export" hidden>',
                        PANEL+'<section class="page" id="page-export" hidden>')
    result=replace_once(result,"const storageKey='AI_ANIME_FACTORY_V19';",
                        "const storageKey='AI_ANIME_FACTORY_V21';")
    result=replace_once(result,"P={format:'AIAnimeFactoryProject',version:19,",
                        "P={format:'AIAnimeFactoryProject',version:21,")
    result=replace_once(result,"try{const old=localStorage.getItem(storageKey);",
                        "try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V19');")
    result=replace_once(result,"function migrate(raw){",
                        "function migrateV20Original(raw){")
    result=replace_once(result,"if(page==='story-v20')renderStoryV20();",
                        "if(page==='story-v20')renderStoryV20();if(page==='visual-v21')v21RenderPanel();")
    result=replace_once(result,"renderImpact19();renderQA();renderStoryV20();}",
                        "renderImpact19();renderQA();renderStoryV20();v21RenderPanel();}")
    result=replace_once(result,"function QA(){const issues=v20ContinuityQA().map(x=>x.message);",
                        "function QA(){const issues=v20ContinuityQA().map(x=>x.message).concat(v21VisualQA());")
    result=replace_once(result,
      "drawBG(g,w,h,s.background,sec,q.lighting,q.effects);cin14Layers(g,w,h,s,sec,'far');",
      "drawBG(g,w,h,s.background,sec,q.lighting,q.effects);v21AtmosphereBack(g,w,h,s,sec);cin14Layers(g,w,h,s,sec,'far');")
    result=replace_once(result,
      " drawModel(g,hero,poses.hero.x*w",
      " v21CharacterBack(g,w,h,s,sec,poses);\n drawModel(g,hero,poses.hero.x*w")
    result=replace_once(result,
      " combat17FX(g,w,h,s,sec,combat17,poses);",
      " v21CharacterDetail(g,w,h,s,sec,poses,hero,second);\n combat17FX(g,w,h,s,sec,combat17,poses);")
    result=replace_once(result,
      "impact19Draw(g,w,h,s,sec,impactV19,poses);",
      "impact19Draw(g,w,h,s,sec,impactV19,poses);v21ImpactDetails(g,w,h,s,sec,impactV19,poses);")
    result=replace_once(result,
      "g.restore();cin14Layers(g,w,h,s,sec,'near');",
      "g.restore();cin14Layers(g,w,h,s,sec,'near');v21AtmosphereFront(g,w,h,s,sec);")
    result=replace_once(result,
      " if(title){const l=activeLine(s,sec);",
      " v21Grade(g,w,h,s,sec);\n if(title){const l=activeLine(s,sec);")
    result=replace_once(result,
      "'AI ANIME FACTORY V19  •  IMPACT QUALITY'",
      "'AI ANIME FACTORY V21  •  VISUAL QUALITY'")
    result=replace_once(result,
      "const files=[{name:'AI_Anime_Factory_V20_STORY_COMBAT.html',data:selfHTML()},",
      "const files=[{name:'AI_Anime_Factory_V21_VISUAL_QUALITY.html',data:selfHTML()},"
      "{name:'V21_VISUAL_LOOKDEV_RU.txt',data:v21VisualPlan()},"
      "{name:'V21_VISUAL_SETTINGS.json',data:JSON.stringify(P.episodes.map(e=>({number:e.number,scenes:e.scenes.map(s=>({title:s.title,visualV21:v21Look(s)}))})),null,2)},")
    result=replace_once(result,
      "'AI_Anime_Factory_V20_STORY_COMBAT_Offline.html'",
      "'AI_Anime_Factory_V21_VISUAL_QUALITY_Offline.html'")
    # The functions and listeners run before loading saved projects.
    marker="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V19');"
    result=replace_once(result,marker,
        "\n/* V21 Visual Quality extension */\n"
        "function migrate(raw){const migrated=migrateV20Original(raw);migrated.version=21;return migrated;}\n"
        +addon.strip()+"\n/* End V21 */\n"+marker)
    return result


def build():
    base=import_v20_builder()
    original=ORIGINAL.read_text(encoding="utf-8")
    v20=base.patch(original,V20_ADDON.read_text(encoding="utf-8"))
    return patch(v20,V21_ADDON.read_text(encoding="utf-8"))


def selftest():
    original=ORIGINAL.read_bytes()
    result=build()
    assert result.startswith("<!DOCTYPE html>")
    for marker in ("id=\"page-visual-v21\"","function v21AtmosphereBack(",
                   "function v21CharacterDetail(", "function v21ImpactDetails(",
                   "function v21VisualQA(", "function v20CanonLines()",
                   "function combat18Sim(", "function impact19Draw(", "function exportEpisode()",
                   "'V21_VISUAL_LOOKDEV_RU.txt'","function migrateV20Original(raw){"):
        assert marker in result,marker
    assert original==ORIGINAL.read_bytes()
    assert len(result.encode("utf-8"))>len(original)
    print("V21 STATIC SOURCE CHECK PASS",
          "V19_SHA256="+hashlib.sha256(original).hexdigest(),
          "V21_BYTES="+str(len(result.encode("utf-8"))))


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--selftest",action="store_true")
    cli.add_argument("--output",default=str(OUTPUT))
    args=cli.parse_args()
    if args.selftest:
        selftest();return
    out=Path(args.output).resolve()
    if out==ORIGINAL.resolve():
        raise ValueError("Refusing to overwrite V19")
    out.parent.mkdir(parents=True,exist_ok=True)
    result=build()
    out.write_text(result,encoding="utf-8")
    print("V21 BUILT",out,len(result.encode("utf-8")),"bytes")


if __name__=="__main__":
    main()
