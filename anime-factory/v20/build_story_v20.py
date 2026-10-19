#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build AI Anime Factory V20 Story/Combat from genuine unchanged V19 HTML.

Injects an integrated tab and behaviour into the ORIGINAL IIFE so that
offline JSON import/export, canvas render and episode ZIP all still work.
No external JavaScript or network dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V19 = ROOT / "anime-factory" / "v19" / "AI_Anime_Factory_V19.html"
JS = Path(__file__).with_name("story_v20.js")
DEST = Path(__file__).with_name("AI_Anime_Factory_V20_STORY_COMBAT.html")

PANEL = r"""
<section class="page" id="page-story-v20" hidden>
 <div class="card">
  <h2>V20 — Контроль сюжета, памяти и последствий</h2>
  <p class="muted">Постоянный журнал канона по сериям. Не стирает сцены, способности, ключевые позы V16 или удары V19.</p>
  <div class="grid">
   <div class="field"><label>Серия</label><select id="v20-episode"></select></div>
   <div class="field"><label>После боя: ранение и состояние</label><input id="v20-wound" maxlength="2500" placeholder="Кто ранен, что сохраняется в следующей серии"></div>
  </div>
  <div class="grid">
   <div class="field"><label>Какое воспоминание потеряно</label><input id="v20-memoryLost" maxlength="400"></div>
   <div class="field"><label>Цена призыва душ и ограничение силы</label><input id="v20-soulCost" maxlength="2500"></div>
  </div>
  <div class="grid">
   <div class="field"><label>Доверие (0–100)</label><input type="number" min="0" max="100" id="v20-trust"></div>
   <div class="field"><label>Романтическая близость (0–100)</label><input type="number" min="0" max="100" id="v20-affection"></div>
  </div>
  <div class="grid">
   <div class="field"><label>Улика и подготовка поворота</label><textarea id="v20-clue" maxlength="2500"></textarea></div>
   <div class="field"><label>Последствия действий для следующей серии</label><textarea id="v20-payoff" maxlength="2500"></textarea></div>
  </div>
  <div class="grid">
   <div class="field"><label>Локация и переход</label><input id="v20-location" maxlength="2500"></div>
   <div class="field"><label>Дневник воспоминаний героя</label><input id="v20-memoryJournal" maxlength="2500"></div>
  </div>
  <div class="field"><label>Режиссёрские заметки (свет, мимика, монтаж, звук)</label><textarea id="v20-notes" maxlength="2500"></textarea></div>
  <div class="flex">
   <button class="accent" id="v20-save">Сохранить журнал серии</button>
   <button id="v20-check">Повторная проверка канона</button>
   <button id="v20-fight">Читаемый бой: сохранить техники и фазы</button>
  </div>
 </div>
 <div class="grid">
  <div class="card">
   <h2>Непрерывность и проверки</h2>
   <pre id="v20-audit" class="report" style="white-space:pre-wrap;max-height:370px;overflow:auto"></pre>
   <pre id="v20-summary" class="report" style="white-space:pre-wrap"></pre>
  </div>
  <div class="card">
   <h2>Экспорт постановки</h2>
   <p class="muted">Контактный лист 4 ключевых кадров берётся из действующего рендера V19 с новой хореографией, если она применена.</p>
   <div class="flex">
    <button id="v20-png">Создать четыре кадра PNG</button>
    <button id="v20-report">Скачать канон TXT</button>
    <button class="accent" id="v20-story-zip">Скачать Story ZIP + JSON</button>
   </div>
   <div class="note">Это процедурный 2D-аниматик, а не готовый профессиональный мультфильм. Проверяйте драматургию и анимацию вручную.</div>
  </div>
 </div>
</section>
"""

def replace_once(source, original, replacement):
    if source.count(original) != 1:
        raise ValueError("V19 expected marker not unique: " + original[:100])
    return source.replace(original, replacement, 1)


def patch(source, extension):
    if 'id="page-story-v20"' in source or "v20CanonLines" in source:
        raise ValueError("This source was already patched to V20")
    if not source.lstrip().startswith("<!DOCTYPE html>"):
        raise ValueError("Expected standalone HTML input")
    if "combatV19" not in source or "function exportEpisode" not in source:
        raise ValueError("Expected genuine V19 combat/editor source")

    result = replace_once(source, '<button data-page="export">',
                          '<button data-page="story-v20">Сюжет и бой V20</button><button data-page="export">')
    result = replace_once(result, '<section class="page" id="page-export" hidden>',
                          PANEL + '<section class="page" id="page-export" hidden>')
    result = replace_once(result, 'function migrate(raw){',
                          'function migrateV19Original(raw){')
    result = replace_once(result, "if(page==='timeline')drawPreview();",
                          "if(page==='timeline')drawPreview();if(page==='story-v20')renderStoryV20();")
    result = replace_once(result, 'renderImpact19();renderQA();}',
                          'renderImpact19();renderQA();renderStoryV20();}')
    result = replace_once(result, 'function QA(){const issues=[];',
                          'function QA(){const issues=v20ContinuityQA().map(x=>x.message);')
    result = replace_once(result, "const files=[{name:'AI_Anime_Factory_V19.html',data:selfHTML()},{name:'PROJECT_V19.json',data:JSON.stringify(P,null,2)},",
                          "const files=[{name:'AI_Anime_Factory_V20_STORY_COMBAT.html',data:selfHTML()},"
                          "{name:'PROJECT_V20.json',data:JSON.stringify(P,null,2)},"
                          "{name:'PROJECT_V19_COMPAT.json',data:JSON.stringify(P,null,2)},"
                          "{name:'V20_CANON_REPORT_RU.txt',data:v20CanonLines()},"
                          "{name:'V20_SHOT_PLAN_RU.txt',data:v20ShotPlan()},"
                          "{name:'V20_QA_REPORT.json',data:JSON.stringify(v20ContinuityQA(),null,2)},")
    result = replace_once(result, "'_PROJECT_V19.json'", "'_PROJECT_V20.json'")
    result = replace_once(result, "'AI_Anime_Factory_V19_Offline.html'",
                          "'AI_Anime_Factory_V20_STORY_COMBAT_Offline.html'")
    result = replace_once(result, "try{const old=localStorage.getItem(storageKey);",
                          "\n/* V20 Story & Combat extension begins */\n" +
                          extension.strip() +
                          "\n/* V20 Story & Combat extension ends */\n" +
                          "try{const old=localStorage.getItem(storageKey);")
    return result


def selftest():
    old = V19.read_bytes()
    text = old.decode("utf-8")
    addon = JS.read_text(encoding="utf-8")
    result = patch(text, addon)
    assert "function migrateV19Original(raw){" in result
    assert "function migrate(raw){" in result
    assert "v20CanonLines" in result
    assert "id=\"page-story-v20\"" in result
    assert "'PROJECT_V20.json'" in result
    assert "function drawScene(" in result
    assert "function combat18Sim(" in result
    assert "function impact19State(" in result
    assert "function exportEpisode()" in result
    assert "V20_CANON_REPORT_RU.txt" in result
    assert "v20Story" not in text
    assert old == V19.read_bytes()
    assert len(result.encode("utf-8")) > len(old)
    print("V20 STATIC PATCH TEST PASS",
          "V19_SHA256=" + hashlib.sha256(old).hexdigest(),
          "V20_BYTES=" + str(len(result.encode("utf-8"))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DEST))
    ap.add_argument("--selftest", action="store_true")
    opts = ap.parse_args()
    if opts.selftest:
        selftest()
        return
    output = Path(opts.output).resolve()
    if output == V19.resolve():
        raise ValueError("Refusing to overwrite original V19")
    output.parent.mkdir(parents=True, exist_ok=True)
    combined = patch(V19.read_text(encoding="utf-8"), JS.read_text(encoding="utf-8"))
    output.write_text(combined, encoding="utf-8")
    print("V20 CREATED:", output, "bytes", output.stat().st_size)


if __name__ == "__main__":
    main()
