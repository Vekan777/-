#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Non-destructive V50 2D pilot producer. NOT an artistic-release certificate.

Builds a real V50 project JSON from the V50 Chromium studio, retaining ALL
original episodes and the source V19-V50 canon. Episodes 1 and 2 become
production working COPIES with scripted dialogue and optionally offline TTS.
Any change to the original source project must be explicitly exported by owner.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import wave

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"anime-factory/production_v50/PILOT_EP01_EP02_RU.json"
HTML=ROOT/"dist/AI_Anime_Factory_V50_FINAL_2D.html"
OUT=ROOT/"dist/V50_PILOT_2D"
VOICE={"hero":"ru+m3","miyu":"ru+f3","ren":"ru+m2","saira":"ru+f2","archon":"ru+m1"}

def run(args):
    cp=subprocess.run(args,text=True,capture_output=True,timeout=120)
    if cp.returncode:
        raise RuntimeError(" ".join(map(str,args[:5]))+": "+cp.stderr[-1200:])
    return cp

def make_tts(lines, here):
    """One combined audio clip per scene; exact per-line duration follows WAV."""
    if not shutil.which("espeak-ng") or not shutil.which("ffmpeg"):
        raise RuntimeError("For spoken pilot install espeak-ng and FFmpeg.")
    chunks=[]
    rate=None
    for n,(role,phrase) in enumerate(lines):
        target=here/f"line_{n}.wav"
        run(["espeak-ng","-v",VOICE[role],"-s","170","-w",str(target),phrase])
        with wave.open(str(target),"rb") as sound:
            if sound.getnchannels()!=1 or sound.getsampwidth()!=2:
                raise RuntimeError("Expected mono 16-bit espeak WAV")
            if rate is None:rate=sound.getframerate()
            if rate!=sound.getframerate():raise RuntimeError("Voice sample rate mismatch")
            frames=sound.readframes(sound.getnframes())
            seconds=sound.getnframes()/rate
        chunks.append((frames,seconds))
    joined=here/"voice.wav"
    silence=struct.pack("<h",0)*int(rate*.35)
    with wave.open(str(joined),"wb") as file:
        file.setnchannels(1);file.setsampwidth(2);file.setframerate(rate)
        for i,(data,_) in enumerate(chunks):
            file.writeframes(data)
            if i+1<len(chunks):file.writeframes(silence)
    mp3=here/"voice.mp3"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(joined),
         "-ac","1","-ar","16000","-b:a","48k",str(mp3)])
    with wave.open(str(joined),"rb") as file:
        signal=file.readframes(file.getnframes())
        count=file.getnframes();sr=file.getframerate()
    # 50 Hz waveform: accurate amplitude indication but NOT phonemic lip-sync.
    hop=max(1,sr//50)
    points=[]
    for i in range(0,count,hop):
        span=signal[i*2:min(i+hop,count)*2]
        if not span:break
        samples=struct.unpack("<"+"h"*(len(span)//2),span)
        points.append(math.sqrt(sum((x/32768)**2 for x in samples)/len(samples)))
    ordered=sorted(points)
    p95=ordered[int(.95*(len(ordered)-1))] if points else 0.01
    waveform=[round(min(1,x/max(0.01,p95*.87)),3) for x in points]
    encoded=base64.b64encode(mp3.read_bytes()).decode("ascii")
    first=chunks[0][1]
    total=sum(sec for _,sec in chunks)+.35*(len(chunks)-1)
    if len(encoded)>1500000*1.4:
        raise RuntimeError("Scene voice exceeds portable V47 audio quota")
    return {"url":"data:audio/mpeg;base64,"+encoded,"wave":waveform,
            "total":round(total,2),"first":round(first,2),"bytes":mp3.stat().st_size}

def get_initial_project(html):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,
            args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page=browser.new_page()
        failures=[]
        page.on("pageerror",lambda err:failures.append(str(err)))
        try:
            page.goto(html.resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function(
                "() => window.v50FinalQA && window.v50FinalQA.currentProject()?.episodes?.length>=2",
                timeout=45000)
            project=page.evaluate("() => window.v50FinalQA.currentProject()")
            if failures:raise RuntimeError("V50 JS: "+"; ".join(failures[:3]))
            return project
        finally:browser.close()

def check_pack(pack):
    if pack.get("schema")!="AIAnimeFactory/PilotProduction/V50/1":
        raise ValueError("Unknown pilot format")
    if len(pack.get("episodes",[]))!=2:raise ValueError("Expected precisely two draft episodes")
    kinds=["opening","friendship","fight","romance","betrayal","ending"]
    for ei,ep in enumerate(pack["episodes"]):
        if ep["number"]!=ei+1:raise ValueError("Out-of-order episodes")
        if [s["kind"] for s in ep["scenes"]]!=kinds:
            raise ValueError("Canon scene sequence changed")
        for s in ep["scenes"]:
            if not (8<=s["duration"]<=12) or len(s["dialogue"])!=2:
                raise ValueError("Unusable scene length or dialogue")
            for role,line in s["dialogue"]:
                if role not in VOICE or not (10<=len(line)<=230):
                    raise ValueError("Unknown speaker or bad dialogue")
    return True

def build(project,pack,with_tts=False):
    if project.get("format")!="AIAnimeFactoryProject" or len(project.get("episodes",[]))<2:
        raise ValueError("V50 full canonical project required")
    if not project.get("episodes",[])[0].get("storyV20"):
        raise ValueError("Canonical V20 story absent")
    canonical_fingerprint=hashlib.sha256(json.dumps(project,ensure_ascii=False,
       sort_keys=True).encode("utf-8")).hexdigest()
    cast={c["id"]:c["name"] for c in project["characters"]}
    if not {"hero","lover","friend","rival","enemy"}.issubset(cast):
        raise ValueError("This pilot must use original V19 cast: hero/lover/friend/rival/enemy")
    mapping={"hero":cast["hero"],"miyu":cast["lover"],
             "ren":cast["friend"],"saira":cast["rival"],"archon":cast["enemy"]}
    # The original V19-V50 scene data (combat, camera/pose/animation, metadata)
    # remains structurally intact. Only a COPIED output JSON gains pilot fields.
    report=[]
    for ep_plan in pack["episodes"]:
        ei=ep_plan["number"]-1
        episode=project["episodes"][ei]
        if len(episode.get("scenes",[]))!=6:
            raise ValueError("Unexpected V19 episode scene count")
        if [sc["kind"] for sc in episode["scenes"]] != \
                [sc["kind"] for sc in ep_plan["scenes"]]:
            raise ValueError("V19 canon ordering changed: manual script merge required")
        if not episode.get("storyV20"):raise ValueError("V20 episode canon lost")
        episode.setdefault("pilotV50",{})
        episode["pilotV50"].update({
            "status":"DRAFT_REQUIRES_HUMAN_ART_REVIEW","logline":ep_plan["logline"],
            "arc":ep_plan["arc"],"license_status":"UNVERIFIED",
            "note":"Original V19/V20 season remains in upstream V50; this is a production copy."})
        episode["storyV20"]["wound"]=ep_plan["wound"]
        episode["storyV20"]["clue"]=ep_plan["clue"]
        episode["storyV20"]["payoff"]=ep_plan["payoff"]
        episode["storyV20"]["memoryJournal"]="Утрата воспоминания: "+ep_plan["memoryLost"]
        episode["memoryLost"]=ep_plan["memoryLost"]
        seconds=0
        for si,shot in enumerate(ep_plan["scenes"]):
            scene=episode["scenes"][si]
            voice=None
            if with_tts:
                with tempfile.TemporaryDirectory(prefix="anime_v50_voice_") as tmp:
                    voice=make_tts(shot["dialogue"],Path(tmp))
            duration=max(float(shot["duration"]),
                         round(voice["total"]+1.4,2) if voice else 0)
            if duration>12:
                raise ValueError("V50 migration clamps scenes over 12 seconds; split long dialogue first")
            scene["title"]=shot["title"]
            scene["duration"]=duration
            scene["narration"]=shot["acting"]
            scene["camera"]=shot["shot"]
            scene["pilotV50"]={"acting":shot["acting"],"camera":shot["shot"],
                "speech_source":"eSpeak NG temporary preview" if voice else "not_recorded",
                "speech_rights":"CHECK ESPEAK-NG VOICE LICENSE BEFORE COMMERCIAL RELEASE"}
            lines=[]
            for role,line in shot["dialogue"]:
                lines.append((mapping[role],line))
            first=voice["first"] if voice else (duration-1)/2
            second_start=min(duration-1.1,first+.6)
            cues=[
                {"start":.25,"end":round(min(duration-.5,first+.55),2),
                 "speaker":lines[0][0],"text":lines[0][1]},
                {"start":round(second_start,2),"end":round(duration-.45,2),
                 "speaker":lines[1][0],"text":lines[1][1]},
            ]
            if cues[1]["start"]<=cues[0]["start"]:
                raise ValueError("Unusable pilot cue")
            scene["subtitlesV37"]={"cues":cues}
            scene["dialogue"]="\n".join(f"{n}: {line}" for n,line in lines)
            scene["lines"]=[
                {"speaker":lines[0][0],"text":lines[0][1],"start":.25,
                 "duration":round(first,2),"emotion":"determined"},
                {"speaker":lines[1][0],"text":lines[1][1],
                 "start":round(second_start,2),
                 "duration":round(max(.4,duration-second_start-.5),2),
                 "emotion":"concerned"}]
            if voice:
                audio=scene.setdefault("audioV36",{})
                config=audio.setdefault("voice",{})
                config.update({"name":f"pilot_{ei+1:02d}_{si+1:02d}.mp3",
                  "embeddedV47":voice["url"],"waveV47":voice["wave"],
                  "durationV47":voice["total"],"sampleRateV47":50,
                  "gain":.95,"offset":.25,"mouthEnabledV47":True,
                  "speakerV47":lines[0][0]})
            seconds+=duration
        report.append({"episode":ep_plan["number"],"title":episode["title"],
            "scriptedScenes":6,"subtitleCues":12,"durationSeconds":round(seconds,2),
            "embeddedVoiceClips":6 if with_tts else 0,
            "artisticApproval":False,"licenseApproval":False})
    # Do not mark ANY existing productionV50 human checkbox as checked.
    project["productionV50"]={"episodeReviews":{},"notes":
       "Пилотный аниматик: ручная проверка кадров, речи, прав, монтажа НЕ завершена.",
       "qaAccepted":False}
    project["pilotProductionV50"]={"schema":pack["schema"],
        "originalV50ProjectSha256":canonical_fingerprint,
        "source":"AI Anime Factory V50 built-in story and original cast",
        "status":"DRAFT_NOT_RELEASE_READY"}
    return project,report

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--html",default=str(HTML))
    cli.add_argument("--out",default=str(OUT))
    cli.add_argument("--tts",action="store_true",help="Install espeak-ng + ffmpeg first")
    cli.add_argument("--validate-only",action="store_true")
    opt=cli.parse_args()
    pack=json.loads(PACK.read_text(encoding="utf-8"))
    check_pack(pack)
    if opt.validate_only:
        print("V50 PILOT SCRIPT FORMAT PASS: 2 episodes, 12 scenes, 24 lines")
        return
    out=Path(opt.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    project,report=build(get_initial_project(Path(opt.html)),pack,opt.tts)
    payload=json.dumps(project,ensure_ascii=False,indent=2)
    filename=out/"PROJECT_PILOT_V50.json"
    filename.write_text(payload,encoding="utf-8")
    qa={"schema":"AIAnimeFactory/PilotTechnicalQA/1",
        "status":"DRAFT_TECHNICAL_ART_REVIEW_PENDING",
        "episodes":report,"voiceIsTemporaryTTS":opt.tts,
        "humanReviewed":False,"rightsVerified":False,
        "limitations":["eSpeak TTS is an understandable robotic preview, not actor performance.",
          "Visuals remain existing 2D cutout; requires manual visual screening.",
          "Second speaker of each scene has no phoneme-correct lip animation.",
          "Music, sound effects and commercial media rights still need production.",
          "Do not publish as professional final series before artistic approval."]}
    (out/"PILOT_PRODUCTION_QA.json").write_text(
        json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V50 PILOT PROJECT",filename,"bytes",len(payload.encode()))
    print("V50 PILOT QA",json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
    main()
