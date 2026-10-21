#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 sound post-production, no third-party media: procedural ambience
and action Foley. Optional Russian actor WAV clips (24 clips, one per line).
Every modified object is a copy; V50.1 input is never overwritten.
Audio cue sync is derived from actual decoded WAV frame counts.
"""
from __future__ import annotations
import argparse,base64,copy,hashlib,json,math,random,shutil,struct,subprocess,tempfile,wave
from pathlib import Path

RATE=16000
ROLES={"hero","miyu","ren","saira","archon"}
def check(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                     timeout=120,check=False)
    if p.returncode:raise RuntimeError(" ".join(map(str,cmd[:5]))+
                                        " "+p.stderr.decode(errors="replace")[-900:])
def export_mp3(samples,root,basename):
    wav=root/(basename+".wav")
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes(struct.pack("<"+"h"*len(samples),*samples))
    mp3=root/(basename+".mp3")
    check(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(wav),
           "-ac","1","-ar",str(RATE),"-b:a","40k",str(mp3)])
    b=mp3.read_bytes()
    if len(b)>180000:raise ValueError("Audio too large for portable JSON")
    return "data:audio/mpeg;base64,"+base64.b64encode(b).decode("ascii")
def synth(sec,si,episode,kind):
    # Source-generated soundtrack, independent of copyrighted media.
    rng=random.Random(episode*100+si+12)
    total=round(RATE*sec)
    duration=max(.1,sec)
    roots=[164.81,146.83,130.81,174.61,116.54,196][si]
    phase=[0,0,0,0]
    atmos=[];foley=[]
    for j in range(total):
        t=j/RATE
        swell=(.25+.30*math.sin(math.pi*t/duration)**2)
        chord=0.0
        for k,harmonic in enumerate((1,1.189,1.498,.50)):
            phase[k]+=2*math.pi*roots*harmonic/RATE
            chord+=math.sin(phase[k])*(1/(k+1))
        shimmer=.10*math.sin(t*9+.8*math.sin(t*.5))
        value=(chord*.40+shimmer)*swell
        atmos.append(max(-32760,min(32760,round(value*11000))))
        hit=0.
        centers=([1.4,3.3,5.5,7.4] if kind=="fight" else
                 [1.6,4.1] if kind in ("opening","ending") else
                 [2.1,5.6] if kind=="betrayal" else [3.4])
        for n,point in enumerate(centers):
            dx=t-point
            if 0<=dx<.32:
                envelope=math.exp(-dx*14)
                if kind=="fight":
                    hit+=envelope*(rng.uniform(-1,1)*.34+
                            .47*math.sin(2*math.pi*(150-70*dx)*dx))
                elif kind=="betrayal":
                    hit+=envelope*(.32*math.sin(dx*300)+.08*rng.uniform(-1,1))
                else:hit+=envelope*.13*math.sin(2*math.pi*(140+si*12)*dx)
        foley.append(max(-32760,min(32760,round(hit*29000))))
    return atmos,foley

def read_recording(path):
    # Only WAV mono/stereo, 16-bit PCM; reject ambiguous input.
    with wave.open(str(path),"rb") as w:
        n=w.getnframes();sr=w.getframerate();ch=w.getnchannels()
        if w.getsampwidth()!=2 or ch not in (1,2):
            raise ValueError(str(path)+": expected WAV 16-bit PCM, mono/stereo")
        frames=w.readframes(n)
    # Resample consistently using FFmpeg rather than naive wave interpolation.
    return sr,ch,frames,n/sr
def merge_actor_lines(scene,episode_index,scene_index,folder,tmp):
    original=scene.get("lines") or []
    segments=[];voice_parts=[]
    for idx,line in enumerate(original,1):
        name=f"e{episode_index+1:02d}_s{scene_index+1:02d}_l{idx:02d}.wav"
        p=folder/name
        if not p.is_file():raise FileNotFoundError("Missing Russian actor recording "+str(p))
        _,_,_,length=read_recording(p)
        if not .4<=length<=9:raise ValueError(name+": length 0.4..9 sec required")
        target=tmp/(name+".16k.wav")
        check(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(p),
               "-ac","1","-ar",str(RATE),"-sample_fmt","s16",str(target)])
        with wave.open(str(target),"rb") as w:
            if w.getframerate()!=RATE or w.getnchannels()!=1:
                raise ValueError("voice resampling failed")
            audio=w.readframes(w.getnframes())
        voice_parts.append((audio,len(audio)/(2*RATE),line))
    # Audio offset and subtitles begin at exactly 0.25 sec.
    cursor=0.
    with wave.open(str(tmp/"actor_voice.wav"),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
        for i,(audio,duration,line) in enumerate(voice_parts):
            w.writeframes(audio)
            role=line["speaker"]
            cast={"Акира":"hero","Мию":"miyu","Рэн":"ren",
                  "Сайра":"saira","Архонт":"archon"}
            if role not in cast:raise ValueError("Unknown canon actor "+role)
            segments.append({"role":cast[role],"start":round(cursor,3),
                             "end":round(cursor+duration,3)})
            cursor+=duration
            if i+1<len(voice_parts):
                w.writeframes(b"\0\0"*int(RATE*.35));cursor+=.35
    if cursor+1.4>12.:
        raise ValueError("Voice too long for V50.1's 12-second scene: "
                         "record shorter lines or split the scene")
    audio=tmp/"actor_voice.wav"
    # extract 50Hz amplitude for lips with correct time and speaker
    with wave.open(str(audio),"rb") as w:
        buf=w.readframes(w.getnframes())
    n=len(buf)//2
    pcm=struct.unpack("<"+"h"*n,buf)
    hop=RATE//50
    values=[math.sqrt(sum((v/32768)**2 for v in pcm[i:i+hop])/
                      max(1,len(pcm[i:i+hop])))
            for i in range(0,n,hop)]
    norm=max(.012,sorted(values)[round(.95*(len(values)-1))]) if values else .012
    waveform=[round(min(1.0,v/norm),3) for v in values]
    mp3=tmp/"actor_voice.mp3"
    check(["ffmpeg","-hide_banner","-loglevel","error","-y",
           "-i",str(audio),"-b:a","64k","-ac","1",str(mp3)])
    encoded="data:audio/mpeg;base64,"+base64.b64encode(mp3.read_bytes()).decode()
    voice=scene.setdefault("audioV36",{}).setdefault("voice",{})
    voice.update({"name":f"licensed_ru_e{episode_index+1:02d}_s{scene_index+1:02d}.mp3",
                  "embeddedV47":encoded,"durationV47":round(cursor,3),
                  "waveV47":waveform,"sampleRateV47":50,"offset":.25,"gain":1,
                  "mouthEnabledV47":True,"segmentsV501":segments,
                  "languageV501":"ru-RU","actingStatusV501":"ACTOR_RECORDINGS_RIGHTS_PENDING"})
    scene["lines"]=[
      {**line,"start":round(seg["start"]+.25,3),
       "duration":round(seg["end"]-seg["start"],3)}
      for line,seg in zip(original,segments)]
    scene["subtitlesV37"]={"cues":[
      {"start":round(seg["start"]+.25,3),"end":round(seg["end"]+.25,3),
       "speaker":line["speaker"],"text":line["text"]}
      for line,seg in zip(original,segments)]}
    scene["pilotV50"]["speech_source"]="User-supplied Russian WAV, rights not verified"
    scene["pilotV50"]["speech_rights"]="REQUIRES SIGNED TALENT AGREEMENTS"
    return len(voice_parts)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--actor-voices",help="Folder with all 24 WAV files e01_s01_l01.wav etc")
    ap.add_argument("--no-foley",action="store_true")
    args=ap.parse_args()
    if not shutil.which("ffmpeg"):raise RuntimeError("Install FFmpeg")
    src=Path(args.project).resolve()
    original=json.loads(src.read_text(encoding="utf-8"))
    if len(original.get("episodes",[]))<2 or not original.get("v501Visual",{}).get("enabled"):
        raise ValueError("Expected completed V50.1 pilot JSON")
    data=copy.deepcopy(original)
    data["v502Director"]={"enabled":True,"approval":False,
                           "voiceMode":"recorded" if args.actor_voices else "espeak_preview",
                           "rightsVerified":False}
    imported=0
    with tempfile.TemporaryDirectory(prefix="anime_v502_sound_") as td:
        root=Path(td)
        for ei,ep in enumerate(data["episodes"][:2]):
            for si,scene in enumerate(ep["scenes"]):
                if args.actor_voices:
                    with tempfile.TemporaryDirectory(prefix="scene_voice_") as v:
                        imported+=merge_actor_lines(scene,ei,si,Path(args.actor_voices),Path(v))
                if not args.no_foley:
                    length=float(scene["duration"])
                    music,fx=synth(length,si,ei+1,scene["kind"])
                    for label,audio,gain in (("music",music,.14),("fx",fx,.22)):
                        slot=scene.setdefault("audioV36",{}).setdefault(label,{})
                        slot.update({"embeddedV47":export_mp3(audio,root,f"e{ei+1}_s{si+1}_{label}"),
                                     "name":f"original_v502_{label}_e{ei+1}_s{si+1}.mp3",
                                     "durationV47":round(length,3),"gain":gain,"offset":0,
                                     "sourceV502":"GENERATED_ORIGINAL_PROCEDURAL",
                                     "rightsV502":"No third-party recordings."})
    data["v502Director"]["originalProjectSha256"]=hashlib.sha256(src.read_bytes()).hexdigest()
    assert data.get("pilotProductionV50",{}).get("originalV50ProjectSha256")
    dest=Path(args.output).resolve()
    if dest==src:raise ValueError("Never overwrite original project")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V50.2 POSTPROCESS",dest,"bytes",dest.stat().st_size,
          "originalPRESERVED",True,"actorWAVImported",imported,
          "russianVoice",data["v502Director"]["voiceMode"],
          "commercialRightsVerified",False)
if __name__=="__main__":main()
