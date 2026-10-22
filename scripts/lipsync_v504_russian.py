#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.4 Russian acoustic mouth-cue alignment using actual WAV and Rhubarb's
language-independent phonetic recognizer. NOT perfect human phoneme alignment.
No new art is generated: 6 mouth poses are drawn on existing character art.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,math,subprocess,tempfile,wave
from pathlib import Path

def run(args,inp=None):
    p=subprocess.run([str(x) for x in args],input=inp,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError(" ".join(map(str,args[:5]))+"\n"+p.stderr.decode(errors="replace")[-1200:])
    return p.stdout

def align_scene(scene,rhubarb,tmp):
    voice=scene["audioV36"]["voice"]
    encoded=voice["embeddedV47"]
    assert encoded.startswith("data:audio/mpeg;base64,")
    binary=base64.b64decode(encoded.split(",",1)[1])
    raw=run(["ffmpeg","-hide_banner","-loglevel","error","-i","pipe:0",
       "-ac","1","-ar","16000","-f","s16le","pipe:1"],binary)
    import array
    pcm=array.array("h");pcm.frombytes(raw)
    rate=16000
    off=float(voice.get("offset",.25))
    spans=voice["segmentsV501"]
    if len(spans)!=len(scene["lines"]):raise ValueError("Voice/line mismatch")
    cues=[]
    for i,(seg,line) in enumerate(zip(spans,scene["lines"])):
        start=max(0,round(float(seg["start"])*rate))
        end=min(len(pcm),round(float(seg["end"])*rate))
        if end-start<rate//6:raise ValueError("Too short for lip analysis")
        wav=tmp/f"dialogue_{i}.wav";outs=tmp/f"mouth_{i}.json"
        transcript=tmp/f"text_{i}.txt"
        with wave.open(str(wav),"wb") as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
            f.writeframes(pcm[start:end].tobytes())
        transcript.write_text(line["text"]+"\n",encoding="utf-8")
        run([rhubarb,"-r","phonetic","-f","json","-d",transcript,
             "-o",outs,wav])
        result=json.loads(outs.read_text(encoding="utf-8"))
        for cue in result.get("mouthCues",[]):
            if cue["value"] not in "ABCDEFGHX":raise ValueError("Invalid cue")
            st=round(off+float(seg["start"])+float(cue["start"]),3)
            en=round(off+float(seg["start"])+float(cue["end"]),3)
            if en<=st:continue
            if st>float(scene["duration"])+.01:raise ValueError("Cue beyond scene duration")
            cues.append({"start":st,"end":min(en,float(scene["duration"])),
                         "shape":cue["value"],"role":seg["role"]})
    cues.sort(key=lambda c:c["start"])
    for c in cues:
        if c["end"]<=c["start"]:raise ValueError("Invalid lip cue")
    scene["v504Lip"]={"method":"Rhubarb phonetic non-English Russian",
         "accuracy":"AUDIO_DERIVED_APPROX_NOT_GOLD_PHONEME_ALIGNMENT",
         "cues":cues,"model":"Rhubarb v1.14.0 phonetic",
         "humanReviewed":False}
    return len(cues)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--rhubarb",default="rhubarb")
    p.add_argument("--episodes",default="1,2")
    a=p.parse_args()
    src=Path(a.project);dest=Path(a.out)
    if src.resolve()==dest.resolve():raise ValueError("Never overwrite source")
    original=src.read_bytes();data=json.loads(original)
    accepted=set(int(x) for x in a.episodes.split(","))
    from collections import Counter
    d=Counter();n=0
    with tempfile.TemporaryDirectory(prefix="v504_rhb_") as t:
      work=Path(t)
      for ei,ep in enumerate(data["episodes"]):
        if ei+1 not in accepted:continue
        for si,scene in enumerate(ep["scenes"]):
            amount=align_scene(scene,a.rhubarb,work)
            d[f"ep{ei+1:02d}"]+=amount;n+=1
            print(f"Russian Rhubarb {ei+1}/{si+1}: {amount} sound-grounded cues",flush=True)
    if n!=len(accepted)*6:raise ValueError("Incomplete lip cue alignment")
    data["v504LipSync"]={"status":"TECHNICAL_PHONETIC_CUES_NOT_HUMAN_APPROVED",
      "method":"Rhubarb phonetic per utterance","episodes":sorted(accepted),
      "sceneCount":n,"cueCounts":d,"perfectPhonemeAlignment":False,
      "sourceJsonSha256":hashlib.sha256(original).hexdigest()}
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    assert src.read_bytes()==original
    print("PASS: source-protected",n,"Russian phonetic lipsync scenes",dict(d))
if __name__=="__main__":main()
