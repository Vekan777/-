#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 conservative story-continuity gate. Never mutates the canon.
Flags incomplete episodes and duplicate paid memories for human review.
A six-episode JSON list != a finished six-episode anime screenplay.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path

def audit(data):
    eps=data.get("episodes",[])
    issues=[]
    original=data.get("pilotProductionV50",{}).get("originalV50ProjectSha256","")
    if len(original)!=64:
        issues.append({"severity":"blocker","episode":0,
                       "code":"CANON_FINGERPRINT_MISSING",
                       "finding":"Нет контрольного отпечатка исходной V50"})
    if len(eps)<6:
        issues.append({"severity":"blocker","episode":0,
                       "code":"SEASON_INCOMPLETE","finding":"Меньше шести сюжетных эпизодов"})
    costs=collections.defaultdict(list)
    for index,episode in enumerate(eps,1):
        story=episode.get("storyV20",{})
        lost=str(episode.get("memoryLost") or story.get("soulCost") or "").strip()
        if lost:costs[lost.casefold()].append(index)
        if lost and str(story.get("soulCost","")).casefold()!=lost.casefold():
            issues.append({"severity":"blocker","episode":index,
                           "code":"MEMORY_COST_MISMATCH",
                           "finding":"Цена магии и потерянное воспоминание не совпадают"})
        if len(episode.get("scenes",[]))!=6:
            issues.append({"severity":"blocker","episode":index,
                           "code":"SCENE_SEQUENCE_INCOMPLETE",
                           "finding":"Нужны шесть сюжетных сцен"})
        for field,reason in (("clue","связующая улика"),("payoff","сюжетная развязка/последствие"),
                             ("memoryJournal","запись об утрате воспоминания")):
            if not str(story.get(field,"")).strip():
                issues.append({"severity":"blocker","episode":index,
                  "code":"STORY_"+field.upper()+"_MISSING",
                  "finding":"Отсутствует "+reason})
        scenes=episode.get("scenes",[])
        scripted=sum(1 for s in scenes if s.get("pilotV50") and
                     len(s.get("lines",[]))==2 and
                     s.get("audioV36",{}).get("voice",{}).get("embeddedV47"))
        if scripted<len(scenes):
            issues.append({"severity":"blocker","episode":index,
              "code":"NOT_FULLY_SCRIPTED_RUSSIAN",
              "finding":f"Подготовлены диалоги и черновая речь для {scripted}/{len(scenes)} сцен"})
        if index>1 and index<=2:
            previous=eps[index-2].get("storyV20",{})
            if "плеч" in str(previous.get("wound","")).casefold() and \
               "плеч" not in str(story.get("wound","")).casefold():
                issues.append({"severity":"warning","episode":index,
                  "code":"WOUND_CONTINUITY_REVIEW","finding":"Не подтверждено последствие травмы плеча"})
    for memory,numbers in costs.items():
        if len(numbers)>1:
            issues.append({"severity":"review","episode":numbers[-1],
              "code":"DUPLICATE_MEMORY_COST",
              "finding":f"Память «{memory}» указана потерянной в эпизодах {numbers}; требуется сцена объяснения или новая цена"})
    severity=collections.Counter(i["severity"] for i in issues)
    return {"schema":"AIAnimeFactory/V502/StoryContinuity/1",
       "status":"RELEASE_BLOCKED_HUMAN_STORY_REVIEW_REQUIRED" if issues else "NO_STATIC_STORY_WARNINGS",
       "seasonEpisodeCount":len(eps),
       "firstTwoPilotScriptsOnly":True,
       "originalCanonFingerprint":original,
       "issueCounts":dict(severity),"issues":issues,
       "autoRewrites":False,"artReviewApproved":False,
       "licensedNaturalRussianVoiceApproved":False,
       "professionalSeasonCompleted":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--fail-on-unapproved-season",action="store_true")
    a=p.parse_args()
    source=a.project.read_bytes()
    data=json.loads(source.decode("utf-8"))
    report=audit(data)
    if source!=a.project.read_bytes():
        raise RuntimeError("Source canon unexpectedly mutated")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V50.2 STORY QA",report["status"],report["issueCounts"],
          "origSha",hashlib.sha256(source).hexdigest()[:14])
    if a.fail_on_unapproved_season and report["status"].startswith("RELEASE_BLOCKED"):
        raise SystemExit(2)

if __name__=="__main__":main()
