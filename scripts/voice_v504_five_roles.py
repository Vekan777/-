#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.4 5 distinct Russian voice lanes: two existing Piper + MIT Silero CIS Base.
The latter is generated in CI or a sufficiently modern machine (AVX2);
Windows i7-3630QM plays baked WAV/MP3 in the exported 2D episodes instead.
Neither voices nor visual art are automatically human-approved.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,subprocess,tempfile,wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"scripts/voice_v503_dual.py"
SILERO_ROLE={
    "silero_miyu":"ru_albina",
    "silero_saira":"ru_zhadyra",
    "silero_archon":"ru_eduard",
}
PIPER_ROLE={"denis","dmitri"}
CACHE={}
def audio_converter(audio,root,name):
    # Original Silero v5 CIS Base emits 24k mono float32.
    f=Path(root)/(name+".24k.wav")
    target=Path(root)/(name+".22k.wav")
    a=np.asarray(audio,dtype=np.float32).ravel()
    if len(a)<6000 or float(np.max(np.abs(a)))<.005:
        raise RuntimeError("Silero voice was silent or too short: "+name)
    a=np.asarray(np.clip(a,-1,1)*32767,dtype=np.int16)
    with wave.open(str(f),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(a.tobytes())
    proc=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-i",str(f),"-ar","22050","-ac","1","-sample_fmt","s16",str(target)],
        capture_output=True,timeout=60)
    if proc.returncode:raise RuntimeError("Silero resampling failed: "+proc.stderr.decode()[-700:])
    with wave.open(str(target),"rb") as w:
        if w.getframerate()!=22050 or w.getnchannels()!=1:raise RuntimeError("Resampling format invalid")
        raw=w.readframes(w.getnframes())
    return np.frombuffer(raw,dtype='<i2').copy()
def load_silero():
    if "model" not in CACHE:
        import torch
        torch.set_num_threads(min(4,os.cpu_count() or 2))
        repo=os.environ.get("SILERO_HUB_REPO","snakers4/silero-models")
        model,_=torch.hub.load(repo_or_dir=repo,model="silero_tts",
                               language="ru",speaker="v5_cis_base",trust_repo=True)
        model.to(torch.device("cpu"))
        CACHE["model"]=model
    return CACHE["model"]
def run(base_project,target,piper,voices,episodes):
    # Reuse the original V50.3 sample-accurate track reconstructor.
    spec=importlib.util.spec_from_file_location("v503_audio",BASE)
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    old_fn=core.audio.piper_speak
    core.MAP.update({"Мию":"silero_miyu","Сайра":"silero_saira",
                     "Архонт":"silero_archon"})
    for role in SILERO_ROLE:voices[role]=role
    voices["denis"]=str(Path(voices["denis"]).resolve())
    voices["dmitri"]=str(Path(voices["dmitri"]).resolve())
    counts={k:0 for k in list(SILERO_ROLE)+["denis","dmitri"]}
    sample_dir=Path(target).resolve().parent/"V504_FIVE_ACTOR_SAMPLES"
    sample_dir.mkdir(parents=True,exist_ok=True)
    def synth(piperbin,model,text,tmp):
        ident=str(model)
        if ident not in SILERO_ROLE:
            stem="denis" if "denis" in ident.lower() else "dmitri"
            counts[stem]+=1
            result=old_fn(piperbin,model,text,tmp)
            if counts[stem]==1:
                with wave.open(str(sample_dir/(stem+".wav")),"wb") as w:
                    w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050)
                    w.writeframes(np.asarray(result,dtype="<i2").tobytes())
            return result
        counts[ident]+=1
        model_obj=load_silero()
        sound=model_obj.apply_tts(text=text,speaker=SILERO_ROLE[ident],sample_rate=24000)
        if hasattr(sound,"detach"):sound=sound.detach().cpu().numpy()
        result=audio_converter(sound,tmp,ident)
        if counts[ident]==1:
            with wave.open(str(sample_dir/(ident+".wav")),"wb") as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050)
                w.writeframes(result.tobytes())
        return result
    core.audio.piper_speak=synth
    rows=[]
    src=Path(base_project).read_bytes()
    project=json.loads(src)
    baseline=[[ (l["speaker"],l["text"]) for scene in episode["scenes"] for l in scene["lines"]]
              for episode in project["episodes"]]
    canon=project["pilotProductionV50"]["originalV50ProjectSha256"]
    previous=project["seasonScriptV502"]["originalFirstTwoEpisodesSha256"]
    for ei,e in enumerate(project["episodes"]):
        if ei+1 not in episodes:continue
        for si,scene in enumerate(e["scenes"]):
            lane,seconds=core.handle(scene,voices,piper,f"ep{ei+1:02d}_s{si+1:02d}")
            for seg in scene["audioV36"]["voice"]["segmentsV501"]:
                src_name=seg["sourceV503"]
                if src_name=="PIPER_SILERO_MIYU":seg["sourceV503"]="SILERO_MIT_RU_ALBINA"
                if src_name=="PIPER_SILERO_SAIRA":seg["sourceV503"]="SILERO_MIT_RU_ZHADYRA"
                if src_name=="PIPER_SILERO_ARCHON":seg["sourceV503"]="SILERO_MIT_RU_EDUARD"
            scene["neuralV503"]["sources"]=[
                seg["sourceV503"] for seg in scene["audioV36"]["voice"]["segmentsV501"]]
            scene["audioV36"]["voice"]["actingStatusV501"]="ALL_FIVE_ROLES_SYNTHETIC_NEURAL_HUMAN_ART_REVIEW_PENDING"
            rows.append({"episode":ei+1,"scene":si+1,"seconds":seconds,
                         "voices":scene["neuralV503"]["sources"]})
            print("V50.4 voices",ei+1,si+1,round(seconds,2),flush=True)
    after=[[ (l["speaker"],l["text"]) for scene in episode["scenes"] for l in scene["lines"]]
              for episode in project["episodes"]]
    assert after==baseline and project["pilotProductionV50"]["originalV50ProjectSha256"]==canon
    assert project["seasonScriptV502"]["originalFirstTwoEpisodesSha256"]==previous
    if set(episodes)=={1,2}:
        assert counts["silero_miyu"]>=1 and counts["silero_saira"]>=1
        assert counts["denis"]>=1 and counts["dmitri"]>=1
    project["v504NeuralFiveActors"]={
        "status":"FIVE_ROLE_SYNTHETIC_DUB_HUMAN_REVIEW_REQUIRED",
        "models":{"Акира":"Piper Denis","Рэн":"Piper Dmitri",
                  "Мию":"Silero CIS Base ru_albina (MIT)",
                  "Сайра":"Silero CIS Base ru_zhadyra (MIT)",
                  "Архонт":"Silero CIS Base ru_eduard (MIT)"},
        "voicesSynthesized":counts,"episodeNumbers":sorted(episodes),
        "phonemeAlignmentApproved":False,"professionalArtApproved":False,
        "commercialRightsOfAllMediaApproved":False,
        "sourceProjectSha256":hashlib.sha256(src).hexdigest()}
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding="utf-8")
    (target.parent/"V504_VOICE_QA.json").write_text(json.dumps({
       "models":project["v504NeuralFiveActors"]["models"],"scenes":rows,
       "status":"TECHNICAL_NEURAL_DUB_NOT_HUMAN_APPROVED"},
       ensure_ascii=False,indent=2),encoding="utf-8")
    assert Path(base_project).read_bytes()==src
    print("V504 completed",len(rows),"two-speaker scenes; voice samples",counts)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--piper-bin",required=True)
    p.add_argument("--voices-dir",required=True)
    p.add_argument("--episodes",default="1,2")
    a=p.parse_args()
    voices={v:str(Path(a.voices_dir)/("ru_RU-"+v+"-medium.onnx")) for v in PIPER_ROLE}
    run(a.project,a.out,a.piper_bin,voices,{int(x) for x in a.episodes.split(",")})
if __name__=="__main__":main()
