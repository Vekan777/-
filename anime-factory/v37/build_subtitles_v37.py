#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V37 non-destructive subtitles & episode delivery, layered on V36."""
from __future__ import annotations
import argparse, hashlib, importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BASE=ROOT/"anime-factory"/"v36"/"build_audio_v36.py"
ADDON=Path(__file__).with_name("subtitles_v37.js")
OUTPUT=Path(__file__).with_name("AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html")
PANEL=r"""
<section class="page" id="page-subtitles-v37" hidden>
<div class="card">
 <h2>V37 — Субтитры, диалоги и контроль выпуска</h2>
 <p class="muted">Новые субтитры накладываются поверх настоящего кадра V35, в том числе при записи WebM во вкладке V36. Все исходные длительности, анимация, сцены, герои и звук сохраняются без изменений.</p>
 <div class="grid">
  <div class="field"><label>Серия</label><select id="v37-episode"></select></div>
  <div class="field"><label>Сцена</label><select id="v37-scene"></select></div>
  <div class="field"><label>Изменить реплику или создать новую</label><select id="v37-cue"></select></div>
 </div>
 <div class="grid">
  <div class="field"><label>Начало относительно сцены (сек)</label><input id="v37-start" type="number" min="0" max="3600" step="0.05" value="0"></div>
  <div class="field"><label>Конец относительно сцены (сек)</label><input id="v37-end" type="number" min="0" max="3600" step="0.05" value="2"></div>
  <div class="field"><label>Имя говорящего (необязательно)</label><input id="v37-speaker" maxlength="64" placeholder="Персонаж"></div>
 </div>
 <label>Текст реплики <textarea id="v37-text" rows="3" maxlength="240" placeholder="Точный текст реплики, без переписывания сюжета"></textarea></label>
 <div class="flex"><button class="accent" id="v37-save">Сохранить реплику</button><button id="v37-remove">Удалить выбранную реплику</button></div>
 <p class="note">Текст субтитров вводится вручную и сохраняется только в subtitlesV37. V37 не придумывает новые реплики персонажей автоматически.</p>
</div>
<div class="card">
 <h2>Реальный предпросмотр субтитров</h2>
 <canvas class="preview" id="v37-preview" width="640" height="360"></canvas>
 <div class="flex"><button id="v37-play">Воспроизвести</button><button id="v37-first">В начало</button></div>
 <label>Время серии <input id="v37-seek" type="range" min="0" max="1000" value="0"></label>
 <p id="v37-clock" class="muted">Выберите серию</p>
 <p class="note">Предпросмотр V37 показывает видео и субтитры. Для звука и записи WebM откройте «Звук / экспорт V36» — в V37 кадры этой вкладки также будут содержать введённые субтитры.</p>
</div>
<div class="card">
 <h2>Субтитры SRT / WebVTT и углублённый аудит</h2>
 <div class="flex">
  <button id="v37-srt">Скачать SRT выбранной серии</button>
  <button id="v37-vtt">Скачать WebVTT выбранной серии</button>
  <button id="v37-json">Скачать JSON-план V37</button>
  <button id="v37-audit">Проверить все субтитры</button>
 </div>
 <pre id="v37-report" class="report" style="white-space:pre-wrap;max-height:320px;overflow:auto"></pre>
 <p class="muted">Экспорт учитывает реальное начало каждой сцены из V35, включая переходы. Проверяются текст, конец сцены, слишком быстрое чтение и пересечения реплик. Это не доказательство художественного качества и отсутствия сценарных ошибок.</p>
</div>
</section>
"""
def once(body,old,new):
    count=body.count(old)
    if count!=1:raise ValueError("V37 anchor: "+repr(old[:95])+" count="+str(count))
    return body.replace(old,new,1)
def previous():
    spec=importlib.util.spec_from_file_location("anime_v36_builder",BASE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def patch(html,addon):
    if 'id="page-subtitles-v37"' in html or "function v37Timeline(" in html:
        raise ValueError("V37 already applied")
    for mark in ("function v36Schedule(","function v36Manifest(",
                 "function v35Plan(","function v35Frame(",
                 "function v34Review(","function v33Act(",
                 "function v30Audit(","function drawScene("):
        if mark not in html:raise ValueError("Missing preserved V19–V36: "+mark)
    html=once(html,'<button data-page="export">',
       '<button data-page="subtitles-v37">Субтитры V37</button><button data-page="export">')
    html=once(html,'<section class="page" id="page-export" hidden>',
       PANEL+'<section class="page" id="page-export" hidden>')
    html=once(html,"const storageKey='AI_ANIME_FACTORY_V36';",
       "const storageKey='AI_ANIME_FACTORY_V37';")
    html=once(html,"P={format:'AIAnimeFactoryProject',version:36,",
       "P={format:'AIAnimeFactoryProject',version:37,")
    html=once(html,
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V35')",
       "localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V36')||localStorage.getItem('AI_ANIME_FACTORY_V35')")
    html=once(html,
       "if(page==='audio-v36')v36Show();",
       "if(page==='audio-v36')v36Show();if(page==='subtitles-v37')v37Show();")
    html=once(html,"v35Show();v36Show();}",
       "v35Show();v36Show();v37Show();}")
    html=once(html,
       "function show(page){if(page!=='audio-v36')v36Stop();",
       "function show(page){if(page!=='subtitles-v37')v37Pause();if(page!=='audio-v36')v36Stop();")
    html=once(html,"'AI ANIME FACTORY V36  •  AUDIO / EPISODE EXPORT'",
       "'AI ANIME FACTORY V37  •  SUBTITLES / DELIVERY'")
    html=once(html,
       "const files=[{name:'AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT.html',data:selfHTML()},",
       "const files=[{name:'AI_Anime_Factory_V37_SUBTITLES_DELIVERY.html',data:selfHTML()},"+
       "{name:'V37_SUBTITLE_DELIVERY.json',data:JSON.stringify(v37Manifest(),null,2)},")
    html=once(html,"'AI_Anime_Factory_V36_AUDIO_EPISODE_EXPORT_Offline.html'",
       "'AI_Anime_Factory_V37_SUBTITLES_DELIVERY_Offline.html'")
    html=once(html,
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<36)migrated.version=36;return migrated;}",
       "function migrate(raw){const migrated=migrateV21Original(raw);if(Number(migrated.version)<37)migrated.version=37;return migrated;}")
    # Reuse the EXACT tested V36 media capture and mix; the frame renderer
    # is enhanced to burn real subtitles into the recorded Canvas.
    html=once(html,
       "const state=v35Frame($('v36-preview'),ep,v36At);",
       "const state=v37DrawFrame($('v36-preview'),ep,v36At);")
    html=once(html,
       "download('V36_EPISODE_'+slug(ep.title)+'.webm',blob);",
       "download('V37_EPISODE_SUBTITLES_'+slug(ep.title)+'.webm',blob);")
    html=once(html,
       "V36: реальная серия WebM готова (",
       "V37: серия WebM с субтитрами записана (")
    html=once(html,
       '<button class="accent" id="v36-export">Записать и скачать WebM эпизода</button>',
       '<button class="accent" id="v36-export">Записать WebM с субтитрами V37</button>')
    anchor="try{const old=localStorage.getItem(storageKey)||localStorage.getItem('AI_ANIME_FACTORY_V36')||"
    html=once(html,anchor,"\n/* V37 SUBTITLE TRACK / DELIVERY */\n"+addon.strip()+
       "\n/* END V37 */\n"+anchor)
    return html
def build():return patch(previous().build(),ADDON.read_text(encoding="utf-8"))
def selftest():
    orig=V19.read_bytes();v36=previous().build();output=build()
    for mark in ("function v37DrawFrame(","function v37SubtitleFile(","function v37Audit(",
                 "function v36Schedule(","function v35Frame(","function v34Review(",
                 "function v30Audit(","id=\"v37-preview\"","AI_ANIME_FACTORY_V37"):
        assert mark in output,mark
    assert V19.read_bytes()==orig
    assert "function v36Schedule(" in v36 and "function v35Frame(" in v36
    print("V37 BUILDER PASS",len(output.encode("utf-8")),hashlib.sha256(orig).hexdigest())
def main():
    args=argparse.ArgumentParser()
    args.add_argument("--selftest",action="store_true")
    args.add_argument("--output",default=str(OUTPUT))
    opts=args.parse_args()
    if opts.selftest:selftest();return
    dst=Path(opts.output).resolve()
    if dst==V19.resolve():raise ValueError("Cannot overwrite V19")
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(build(),encoding="utf-8")
    print("V37 HTML",dst,dst.stat().st_size)
if __name__=="__main__":main()
