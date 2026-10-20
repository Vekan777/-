#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate V22 Acting & Combat from unchanged original V19, V20 and V21."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER21=ROOT/"anime-factory"/"v21"/"build_visual_v21.py"
ADDON=Path(__file__).with_name("acting_v22.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V22_ACTING_COMBAT.html")

PANEL=r"""
<section class="page" id="page-acting-v22" hidden>
<div class="card">
 <h2>V22 — Актёрская постановка и ясный бой</h2>
 <p class="muted">Ключи эмоций для обоих героев, детальная мимика векторного рига и визуальный акцент подтверждённых попаданий. Старые сюжетные сцены сохраняются.</p>
 <div class="grid">
  <div class="field"><label>Сцена</label><select id="v22-scene"></select></div>
  <div class="field"><label><input type="checkbox" id="v22-enabled" checked> Актёрские настройки включены</label></div>
 </div>
 <div class="grid">
  <div class="field"><label>Мимика: <span id="v22-faceStrength-n">70</span>%</label><input id="v22-faceStrength" type="range" min="0" max="100"></div>
  <div class="field"><label>Акцент ударов: <span id="v22-combatFocus-n">72</span>%</label><input id="v22-combatFocus" type="range" min="0" max="100"></div>
  <div class="field"><label>Дыхание и микродвижения: <span id="v22-breathing-n">56</span>%</label><input id="v22-breathing" type="range" min="0" max="100"></div>
 </div>
 <div class="flex">
  <button id="v22-preset">Поставить эмоции по жанру сцены</button>
  <button class="accent" id="v22-save">Сохранить параметры V22</button>
 </div>
</div>
<div class="grid">
 <div class="card">
  <h2>Эмоции героев по времени</h2>
  <div class="field"><label>Текущие актёрские ключи</label><select id="v22-beat-list" size="4" style="min-height:115px"></select></div>
  <div class="grid">
   <div class="field"><label>Момент в сцене, %</label><input type="number" min="0" max="100" id="v22-t" value="50"></div>
   <div class="field"><label>Главный герой</label><select id="v22-hero">
    <option value="neutral">Спокойствие</option><option value="gentle">Нежность</option>
    <option value="determined">Решимость</option><option value="angry">Гнев</option>
    <option value="sad">Печаль</option><option value="shocked">Шок</option>
   </select></div>
   <div class="field"><label>Второй герой</label><select id="v22-partner">
    <option value="neutral">Спокойствие</option><option value="gentle">Нежность</option>
    <option value="determined">Решимость</option><option value="angry">Гнев</option>
    <option value="sad">Печаль</option><option value="shocked">Шок</option>
   </select></div>
  </div>
  <div class="flex">
   <button id="v22-new">+ Ключ в текущем времени</button>
   <button class="accent" id="v22-save-beat">Сохранить ключ</button>
   <button id="v22-delete">Удалить ключ</button>
  </div>
 </div>
 <div class="card">
  <h2>Предварительный просмотр</h2>
  <canvas id="v22-preview" class="preview" width="960" height="540"></canvas>
  <label>Время сцены <input type="range" min="0" max="100" value="50" id="v22-playhead"></label>
  <div id="v22-time" class="muted"></div>
  <div class="flex">
   <button id="v22-contact">Сохранить 4 актёрских кадра PNG</button>
   <button id="v22-report">Скачать постановку TXT</button>
  </div>
 </div>
</div>
<div class="card">
 <h2>Проверка актёрской непрерывности</h2>
 <pre id="v22-qa" class="report" style="white-space:pre-wrap;max-height:270px;overflow:auto"></pre>
 <div class="note">Мимика V22 улучшает только процедурный векторный риг. Импортированные PNG персонажей сохраняются без поверхностной дорисовки лиц. Это не генератор новых фотореалистичных персонажей.</div>
</div>
</section>
"""

def replace_once(text,a,b):
    if text.count(a)!=1:
        raise ValueError("Unique marker not found: "+repr(a[:90])+" (count "+str(text.count(a))+")")
    return text.replace(a,b,1)

def load_v21():
    spec=importlib.util.spec_from_file_location("visual_v21_builder",BUILDER21)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(v21,extension):
    if "v22ActingQA" in v21 or 'id="page-acting-v22"' in v21:
        raise ValueError("Already V22")
    if "function v21AtmosphereBack(" not in v21 or "function v20CanonLines(" not in v21:
        raise ValueError("Expected integrated V21")
    text=replace_once(v21,'<button data-page="export">',
       '<button data-page="acting-v22">Персонажи и бой V22</button><button data-page="export">')
    text=replace_once(text,'<section class="page" id="page-export" hidden>',PANEL+'<section class="page" id="page-export" hidden>')
    text=replace_once(text,"const storageKey='AI_ANIME_FACTORY_V21';","const storageKey='AI_ANIME_FACTORY_V22';")
    text=replace_once(text,"P={format:'AIAnimeFactoryProject',version:21,","P={format:'AIAnimeFactoryProject',version:22,")
    text=replace_once(text,"localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V19')",
                          "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V21')||localStorage.getItem('AI_ANIME_FACTORY_V19')")
    text=replace_once(text,"function migrate(raw){const migrated=migrateV20Original(raw);migrated.version=21;return migrated;}",
                          "function migrateV21Original(raw){const migrated=migrateV20Original(raw);migrated.version=21;return migrated;}")
    # Never downgrade a loaded V22 project in V20 or V21 migration.
    text=replace_once(text,"migrated.version=21;return migrated;}",
                          "if(Number(migrated.version)<21)migrated.version=21;return migrated;}")
    text=replace_once(text,"if(page==='visual-v21')v21RenderPanel();",
                          "if(page==='visual-v21')v21RenderPanel();if(page==='acting-v22')v22Show();")
    text=replace_once(text,"renderImpact19();renderQA();renderStoryV20();v21RenderPanel();}",
                          "renderImpact19();renderQA();renderStoryV20();v21RenderPanel();v22Show();}")
    text=replace_once(text,"function QA(){const issues=v20ContinuityQA().map(x=>x.message).concat(v21VisualQA());",
                          "function QA(){const issues=v20ContinuityQA().map(x=>x.message).concat(v21VisualQA(),v22ActingQA());")
    text=replace_once(text,
      "const d=rigDynamics(s,t,role),mood=moodOverride||qualityMood(s,role),p=d.p",
      "const d=rigDynamics(s,t,role),mood=moodOverride||v22Mood(s,role,t,qualityMood(s,role)),p=d.p")
    text=replace_once(text,
      "g.rotate(lean);g.translate(0,Math.sin(t*2)*1.8);",
      "g.rotate(lean);g.translate(0,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t));")
    text=replace_once(text,
      "const f=v13Face(s,role,t,moodOverride);",
      "const f=v13Face(s,role,t,moodOverride||v22Mood(s,role,t,qualityMood(s,role)));")
    text=replace_once(text,
      "drawFaceMarks(g,design);drawV12FaceDetails(g,c,design,mood,blink);g.restore();",
      "drawFaceMarks(g,design);drawV12FaceDetails(g,c,design,mood,blink);v22FaceDetails(g,c,s,role,t,design,f);g.restore();")
    text=replace_once(text,
      "impact19Draw(g,w,h,s,sec,impactV19,poses);v21ImpactDetails(g,w,h,s,sec,impactV19,poses);",
      "impact19Draw(g,w,h,s,sec,impactV19,poses);v21ImpactDetails(g,w,h,s,sec,impactV19,poses);v22CombatClarity(g,w,h,s,sec,combat17,poses);")
    text=replace_once(text,
      "'AI ANIME FACTORY V21  •  VISUAL QUALITY'",
      "'AI ANIME FACTORY V22  •  ACTING & COMBAT'")
    text=replace_once(text,
      "const files=[{name:'AI_Anime_Factory_V21_VISUAL_QUALITY.html',data:selfHTML()},",
      "const files=[{name:'AI_Anime_Factory_V22_ACTING_COMBAT.html',data:selfHTML()},"
      "{name:'V22_ACTING_PLAN_RU.txt',data:v22Plan()},"
      "{name:'V22_ACTING_TRACKS.json',data:JSON.stringify(P.episodes.map(e=>({number:e.number,scenes:e.scenes.map(s=>({title:s.title,actingV22:v22Settings(s)}))})),null,2)},")
    text=replace_once(text,"'AI_Anime_Factory_V21_VISUAL_QUALITY_Offline.html'",
                       "'AI_Anime_Factory_V22_ACTING_COMBAT_Offline.html'")
    old="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V21')||localStorage.getItem('AI_ANIME_FACTORY_V19');"
    # Inside the same closure, registration occurs before project loading.
    text=replace_once(text,old,
         "\n/* V22 ACTING AND COMBAT */\n"
         +"function migrate(raw){const m=migrateV21Original(raw);m.version=22;return m;}\n"
         +extension.strip()+"\n/* END V22 */\n"+old)
    return text

def build():
    base=load_v21()
    return patch(base.build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    page=build()
    for marker in ('id="page-acting-v22"',"function v22Mood(","function v22FaceDetails(",
      "function v22CombatClarity(","function v22ActingQA(","function impact19State(",
      "function combat18Sim(","function v21AtmosphereBack(","function v20CanonLines(",
      "function migrateV21Original(raw)","V22_ACTING_PLAN_RU.txt"):
        assert marker in page,marker
    assert original==V19.read_bytes()
    assert len(page.encode('utf-8'))>len(original)
    print("V22 PATCH SELFTEST PASS",len(page.encode('utf-8')),hashlib.sha256(original).hexdigest())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--output",default=str(OUTPUT))
    args=p.parse_args()
    if args.selftest:selftest();return
    dest=Path(args.output).resolve()
    if dest==V19.resolve():raise ValueError("Refusing to overwrite V19")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(build(),encoding="utf-8")
    print("V22 HTML CREATED:",dest,"bytes",dest.stat().st_size)

if __name__=="__main__":
    main()
