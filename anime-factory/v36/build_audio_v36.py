#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add V36 audio & real-time WebM recording to the exact V35 generated HTML."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v35"/"build_assembly_v35.py"
ADDON=Path(__file__).with_name("audio_v36.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html")

PANEL=r"""
<section class="page" id="page-audio-v36" hidden>
<div class="card">
 <h2>V36 — Сведение звука и экспорт эпизода</h2>
 <p class="muted">Три независимых звуковых слоя для сцены: речь, музыка и эффекты. Звук синхронизируется с общей временной шкалой V35 и плавно затухает на переходах. Авторские сцены, сюжет и их длительности не изменяются.</p>
 <div class="grid">
  <div class="field"><label>Эпизод</label><select id="v36-episode"></select></div>
  <div class="field"><label>Сцена для звука</label><select id="v36-scene"></select></div>
  <div class="field"><label>Дорожка</label><select id="v36-slot"><option value="voice">Речь / диалоги</option><option value="music">Музыка (повторять)</option><option value="fx">Эффекты</option></select></div>
  <div class="field"><label>Добавить собственный звук WAV, MP3, OGG</label><input id="v36-audiofile" type="file" accept="audio/*"></div>
 </div>
 <p id="v36-asset" class="note">Звуковой файл не выбран.</p>
 <label>Громкость слоя: <span id="v36-gain-value">1.00</span>
  <input id="v36-gain" type="range" min="0" max="200" value="100" step="5"></label>
 <label>Задержка после начала сцены (сотые доли секунды):
  <input id="v36-offset" type="number" min="0" max="12000" value="0" step="5"></label>
 <p class="muted">Задержка указывается в сотых долях секунды: 50 = 0,5 сек. Музыка повторяется до конца сцены; голос и звуковые эффекты играют один раз.</p>
 <button class="accent" id="v36-save">Сохранить громкость и сдвиг</button>
 <p class="note">Звуковые файлы загружаются только в память браузера. В резервном JSON остаются названия и настройки, но не аудиобайты: после повторного открытия переподключите те же звуковые файлы. Перед редактированием сделайте резервную копию проекта в «Аудит V30».</p>
</div>
<div class="card">
 <h2>Предпросмотр всей серии со звуком</h2>
 <canvas class="preview" id="v36-preview" width="640" height="360"></canvas>
 <div class="flex">
  <button id="v36-play">Слушать + смотреть</button>
  <button id="v36-stop">Стоп / в начало</button>
 </div>
 <label>Время серии <input type="range" id="v36-position" min="0" max="1000" value="0"></label>
 <p class="muted" id="v36-clock">Общий таймкод V35</p>
</div>
<div class="card">
 <h2>Реальный видеоэкспорт V36</h2>
 <p class="muted">Chrome/Edge записывает настоящие Canvas-кадры и подключённые аудиодорожки в файл WebM с помощью MediaRecorder. Запись идёт в реальном времени: для серии длиной 1 минута потребуется воспроизвести всю минуту. Для Windows прилагается CONVERT_MP4_WINDOWS.bat на основе FFmpeg.</p>
 <label>Кадров в секунду <select id="v36-fps">
  <option value="6">6 FPS — слабый ноутбук</option><option value="12">12 FPS</option>
  <option value="24">24 FPS — выше нагрузка</option>
 </select></label>
 <div class="flex">
  <button class="accent" id="v36-export">Записать и скачать WebM эпизода</button>
  <button id="v36-audit">Аудит звука</button>
  <button id="v36-json">Экспорт JSON-плана V36</button>
 </div>
 <pre id="v36-result" class="report" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
 <p class="note">MP4 кодируется внешним FFmpeg. Программа не создаёт автоматически речь, музыку и актёрские озвучки: нужны выбранные пользователем файлы. Без дорожек WebM будет без слышимого звука. Остановка или смена вкладки прервёт запись.</p>
</div>
</section>
"""

def once(txt,old,new):
    n=txt.count(old)
    if n!=1:
        raise ValueError("V36 anchor "+repr(old[:100])+" occurrences="+str(n))
    return txt.replace(old,new,1)

def previous():
    spec=importlib.util.spec_from_file_location("anime_v35_builder",BASE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def patch(html,addon):
    if "function v36Schedule(" in html or 'id="page-audio-v36"' in html:
        raise ValueError("V36 already present")
    for feature in ("function v35Plan(","function v35Frame(","function v35Audit(",
                    "function v34Camera(","function v33Act(","function v30Audit(",
                    "function drawScene("):
        if feature not in html:
            raise ValueError("Legacy V19–V35 feature missing: "+feature)
    html=once(html,'<button data-page="export">',
              '<button data-page="audio-v36">Звук / экспорт V36</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
              PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V35';",
              "const storageKey='AI_ANIME_FACTORY_V36';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:35,",
              "P={format:'AIAnimeFactoryProject',version:36,")
    html=once(html,
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V34')",
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V35')||localStorage.getItem('AI_ANIME_FACTORY_V34')")
    html=once(html,"if(page==='assembly-v35')v35Show();",
              "if(page==='assembly-v35')v35Show();if(page==='audio-v36')v36Show();")
    html=once(html,"v34Show();v35Show();}",
              "v34Show();v35Show();v36Show();}")
    html=once(html,
      "function show(page){if(page!=='assembly-v35')v35Pause();currentPage=page;playing=false;",
      "function show(page){if(page!=='audio-v36')v36Stop();if(page!=='assembly-v35')v35Pause();currentPage=page;playing=false;")
    html=once(html,"'AI ANIME FACTORY V35  •  EPISODE ASSEMBLY'",
              "'AI ANIME FACTORY V36  •  AUDIO / EPISODE EXPORT'")
    html=once(html,
      "const files=[{name:'AI_Anime_Factory_V35_SCENE_ASSEMBLY.html',data:selfHTML()},",
      "const files=[{name:'AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html',data:selfHTML()},"+
      "{name:'V36_AUDIO_EPISODE.json',data:JSON.stringify(v36Manifest(),null,2)},")
    html=once(html,"'AI_Anime_Factory_V35_SCENE_ASSEMBLY_Offline.html'",
              "'AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT_Offline.html'")
    html=once(html,
      "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<35)migrated.version=35;return migrated;}",
      "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<36)migrated.version=36;return migrated;}")
    anchor=("try{const old=localStorage.getItem(storageKey)||"+
      "localStorage.getItem('AI_ANIME_FACTORY_V35')||")
    html=once(html,anchor,"\n/* V36 AUDIO EPISODE */\n"+
      addon.strip()+"\n/* END V36 */\n"+anchor)
    return html

def build():
    return patch(previous().build(),ADDON.read_text(encoding="utf-8"))

def selftest():
    original=V19.read_bytes()
    built=build()
    for item in ("function v36Schedule(","function v36Manifest(","function v35Plan(",
                 "function v34Review(","function v30Audit(","id=\"v36-export\"",
                 "V36_AUDIO_EPISODE.json","AI_ANIME_FACTORY_V36"):
        assert item in built,item
    assert V19.read_bytes()==original
    print("V36 BUILDER PASS",len(built.encode("utf-8")),hashlib.sha256(original).hexdigest())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--output",default=str(OUTPUT))
    a=p.parse_args()
    if a.selftest:selftest();return
    output=Path(a.output).resolve()
    if output==V19.resolve():raise ValueError("Refusing to overwrite V19")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(build(),encoding="utf-8")
    print("V36 HTML BUILT",output,output.stat().st_size)

if __name__=="__main__":
    main()
