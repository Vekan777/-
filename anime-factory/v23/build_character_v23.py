#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build V23 from genuine V19 through V20, V21 and V22 without rewriting them."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER22=ROOT/"anime-factory"/"v22"/"build_acting_v22.py"
ADDON=Path(__file__).with_name("character_v23.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V23_CHARACTER_QUALITY.html")

PANEL=r"""
<section class="page" id="page-character-v23" hidden>
<div class="card">
 <h2>V23 — Качество персонажей: силуэт, волосы, костюмы и движение</h2>
 <p class="muted">Улучшения применяются к процедурным рисованным персонажам. Загруженные PNG и авторские рисунки сохраняются нетронутыми.</p>
 <div class="grid">
  <div class="field"><label>Персонаж</label><select id="v23-character"></select></div>
  <div class="field"><label>Телосложение</label><select id="v23-profile">
   <option value="balanced">Сбалансированное</option>
   <option value="heroic">Героическое</option>
   <option value="slim">Стройное</option>
  </select></div>
 </div>
 <label><input type="checkbox" id="v23-enabled" checked> Включить улучшения V23 для выбранного персонажа</label>
 <div class="grid">
  <div class="field"><label>Анатомия и пропорции: <span id="v23-anatomy-n">72</span>%</label><input type="range" id="v23-anatomy" min="0" max="100"></div>
  <div class="field"><label>Волосы и пряди: <span id="v23-hairDetail-n">76</span>%</label><input type="range" id="v23-hairDetail" min="0" max="100"></div>
  <div class="field"><label>Материалы костюма: <span id="v23-costumeDetail-n">70</span>%</label><input type="range" id="v23-costumeDetail" min="0" max="100"></div>
  <div class="field"><label>Вторичные движения: <span id="v23-secondaryMotion-n">65</span>%</label><input type="range" id="v23-secondaryMotion" min="0" max="100"></div>
 </div>
 <div class="flex"><button id="v23-preset">Пресет персонажа</button>
 <button class="accent" id="v23-save">Сохранить персонажа V23</button></div>
</div>
<div class="grid">
 <div class="card">
  <h2>Анимация и пропорции в контексте сцены</h2>
  <canvas class="preview" id="v23-preview" width="960" height="540"></canvas>
  <label>Время сцены <input type="range" id="v23-playhead" min="0" max="100" value="45"></label>
  <div class="muted" id="v23-caption"></div>
  <div class="flex"><button id="v23-sheet">Сохранить 4 кадра PNG</button>
   <button id="v23-txt">Скачать паспорт V23 TXT</button></div>
 </div>
 <div class="card">
  <h2>Контроль качества</h2>
  <pre id="v23-report" class="report" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
  <div class="note">Для художественного уровня студийного аниме требуются нарисованные модели и ручная проверка. V23 улучшает 2D-процедурный риг, но не создаёт нейронные видео или 3D.</div>
 </div>
</div>
</section>
"""

def once(txt,needle,replacement):
    occurrences=txt.count(needle)
    if occurrences!=1:
        raise ValueError("Unique V23 integration marker missing/duplicated: "+
                         repr(needle[:95])+" count="+str(occurrences))
    return txt.replace(needle,replacement,1)

def base22():
    spec=importlib.util.spec_from_file_location("anime_v22_builder",BUILDER22)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def patch(text,addon):
    if "function v23Style(" in text or 'id="page-character-v23"' in text:
        raise ValueError("Already V23")
    for marker in ["function v22Mood(", "function v21AtmosphereBack(",
                   "function v20CanonLines(", "function drawRigPerson("]:
        if marker not in text:
            raise ValueError("Expected genuine integrated V22 source: "+marker)
    text=once(text,'<button data-page="export">',
              '<button data-page="character-v23">Персонажи V23</button><button data-page="export">')
    text=once(text,'<section class="page" id="page-export" hidden>',
              PANEL+'<section class="page" id="page-export" hidden>')
    text=once(text,"const storageKey='AI_ANIME_FACTORY_V22';",
              "const storageKey='AI_ANIME_FACTORY_V23';")
    text=once(text,"P={format:'AIAnimeFactoryProject',version:22,",
              "P={format:'AIAnimeFactoryProject',version:23,")
    text=once(text,
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V21')||localStorage.getItem('AI_ANIME_FACTORY_V19')",
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V22')||localStorage.getItem('AI_ANIME_FACTORY_V21')||localStorage.getItem('AI_ANIME_FACTORY_V19')")
    text=once(text,"if(page==='acting-v22')v22Show();",
              "if(page==='acting-v22')v22Show();if(page==='character-v23')v23Show();")
    text=once(text,"renderStoryV20();v21RenderPanel();v22Show();}",
              "renderStoryV20();v21RenderPanel();v22Show();v23Show();}")
    text=once(text,
       "concat(v21VisualQA(),v22ActingQA());",
       "concat(v21VisualQA(),v22ActingQA(),v23CharacterQA());")
    # Improve the existing fallback rig instead of drawing over imported art.
    text=once(text,
       "const attack=d.attack*p,block=d.block*p,steps=d.steps*p,wind=(Math.sin(t*4.2-1.1)+.7*d.attack-1.5*d.block)*d.hair,cloth=(Math.sin(t*2.7-.6)+1.4*d.attack-d.recover)*d.cloth;",
       "const attack=d.attack*p,block=d.block*p,steps=d.steps*p,wind=(Math.sin(t*4.2-1.1)+.7*d.attack-1.5*d.block)*d.hair+v23Secondary(s,c,t,role).hair,cloth=(Math.sin(t*2.7-.6)+1.4*d.attack-d.recover)*d.cloth+v23Secondary(s,c,t,role).cloth;")
    text=once(text,
       "g.rotate(lean);g.translate(0,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t));",
       "g.rotate(lean);g.translate(0,Math.sin(t*2)*1.8+v22BodyBreath(s,role,t)+v23Secondary(s,c,t,role).body);")
    text=once(text,
       "g.ellipse(footR[0]+3,footR[1]+4,18,7,0,0,7);g.fill();",
       "g.ellipse(footR[0]+3,footR[1]+4,18,7,0,0,7);g.fill();v23LegForm(g,c,s,role,t,steps);")
    text=once(text,
       "g.lineTo(-35-cloth*6,-78);g.closePath();g.fill();",
       "g.lineTo(-35-cloth*6,-78);g.closePath();g.fill();v23TorsoForm(g,c,s,role,t,cloth);")
    text=once(text,
       "drawEmblem(g,c,design);drawAccessory(g,c,design,cloth);drawV12ClothDetails(g,c,design,cloth);",
       "drawEmblem(g,c,design);drawAccessory(g,c,design,cloth);drawV12ClothDetails(g,c,design,cloth);v23CostumeForm(g,c,s,role,t,cloth);")
    text=once(text,
       "rigStroke(g,rightElbow,[65,-110],rightHand,'#eccdc1',10);",
       "rigStroke(g,rightElbow,[65,-110],rightHand,'#eccdc1',10);v23ArmForm(g,c,s,role,t,leftElbow,leftHand,rightElbow,rightHand);")
    # The same head scale is shared by face and hair to prevent detachment.
    head="const hs=design.eyeStyle==='round'?1.07:1;g.scale(hs,hs);"
    if text.count(head)!=2:
        raise ValueError("Face/hair rig head-scale anchors changed")
    text=text.replace(head,
        "const hs=(design.eyeStyle==='round'?1.07:1)*v23HeadScale(c);g.scale(hs,hs);",2)
    text=once(text,
       "v22FaceDetails(g,c,s,role,t,design,f);g.restore();",
       "v22FaceDetails(g,c,s,role,t,design,f);v23FaceForm(g,c,s,role,t);g.restore();")
    text=once(text,
       "drawExtraHair(g,c,design,wind);drawV12HairDetails(g,c,design,wind);g.restore();",
       "drawExtraHair(g,c,design,wind);drawV12HairDetails(g,c,design,wind);v23HairForm(g,c,s,role,t,wind);g.restore();")
    text=once(text,
       "'AI ANIME FACTORY V22  •  ACTING & COMBAT'",
       "'AI ANIME FACTORY V23  •  CHARACTER QUALITY'")
    text=once(text,
       "const files=[{name:'AI_Anime_Factory_V22_ACTING_COMBAT.html',data:selfHTML()},",
       "const files=[{name:'AI_Anime_Factory_V23_CHARACTER_QUALITY.html',data:selfHTML()},"+
       "{name:'V23_CHARACTER_LOOKDEV_RU.txt',data:v23Report()},"+
       "{name:'V23_CHARACTER_SETTINGS.json',data:JSON.stringify(P.characters.map(c=>"+
       "({name:c.name,id:c.id,qualityV23:v23Style(c)})),null,2)},")
    text=once(text,
       "'AI_Anime_Factory_V22_ACTING_COMBAT_Offline.html'",
       "'AI_Anime_Factory_V23_CHARACTER_QUALITY_Offline.html'")
    marker=("try{const old=localStorage.getItem(storageKey)||"+
      "localStorage.getItem('AI_ANIME_FACTORY_V22')||"+
      "localStorage.getItem('AI_ANIME_FACTORY_V21')||"+
      "localStorage.getItem('AI_ANIME_FACTORY_V19');")
    # This patch runs inside the existing single script scope before project loading.
    text=once(text,marker,
       "\n/* V23 CHARACTER QUALITY / compatibility-preserving migration */\n"+
       "function migrate(raw){const migrated=migrateV21Original(raw);"+
       "if(Number(migrated.version)<23)migrated.version=23;return migrated;}\n"+
       addon.strip()+"\n/* END V23 */\n"+marker)
    return text

def build():
    return patch(base22().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    result=build()
    for marker in ('id="page-character-v23"',"function v23HeadScale(",
       "function v23TorsoForm(","function v23Secondary(","function v23CharacterQA(",
       "function v22Mood(","function v20CanonLines(","function v21AtmosphereBack(",
       "function impact19State(","function combat18Sim(", "V23_CHARACTER_SETTINGS.json"):
        assert marker in result,marker
    assert V19.read_bytes()==original
    print("V23 SOURCE PATCH PASS",len(result.encode("utf-8")),
          hashlib.sha256(original).hexdigest())

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--selftest",action="store_true")
    cli.add_argument("--output",default=str(OUTPUT))
    a=cli.parse_args()
    if a.selftest:selftest();return
    out=Path(a.output).resolve()
    if out==V19.resolve():
        raise ValueError("Refusing to overwrite V19")
    out.parent.mkdir(parents=True,exist_ok=True)
    result=build()
    out.write_text(result,encoding="utf-8")
    print("V23 HTML BUILT",out,"bytes",out.stat().st_size)

if __name__=="__main__":
    main()
