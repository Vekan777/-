#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50.2 SIX-EPISODE source-only offline compositor: real 960x540/12 FPS Canvas frames,
the THREE embedded Russian voice/music/FX tracks, no previous MP4 dependency.
Technical preview ONLY, not approved professional anime or natural actor dub.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,math,os,shutil,subprocess,tempfile
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright

SAMPLE_RATE=24000
def command(a,raw=None,timeout=180):
    p=subprocess.run(a,input=raw,capture_output=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError(str(a[:8])+" "+p.stderr.decode(errors="replace")[-1400:])
    return p.stdout
def duration(ep):
    scenes=ep["scenes"]
    return round(sum(float(s["duration"]) for s in scenes)-
        sum(min(1.5,max(0,float(s.get("assemblyV35",{}).get("transition",.35))))
            for s in scenes[:-1]),4)
def decode_embedded(value):
    if not value.startswith("data:audio/mpeg;base64,"):
        raise RuntimeError("Missing portable audio, refused silent replacement")
    src=base64.b64decode(value.split(",",1)[1],validate=True)
    raw=command(["ffmpeg","-hide_banner","-loglevel","error","-i","pipe:0",
        "-f","f32le","-ar",str(SAMPLE_RATE),"-ac","1","pipe:1"],raw=src)
    return np.frombuffer(raw,dtype="<f4").astype(np.float64)
def audio_mix(ep,length):
    count=math.ceil(length*SAMPLE_RATE)
    channels={k:np.zeros(count,dtype=np.float64) for k in ("voice","music","fx")}
    start=0.0
    for n,scene in enumerate(ep["scenes"]):
        for kind in channels:
            conf=scene["audioV36"][kind]
            pcm=decode_embedded(conf["embeddedV47"])
            gain=float(conf.get("gain",1))
            if gain<0 or gain>1:raise ValueError("Unsafe gain")
            off=float(conf.get("offset",0))
            if off<0:raise ValueError("Negative offset")
            begin=round((start+off)*SAMPLE_RATE)
            size=min(len(pcm),max(0,count-begin))
            if size>0:
                channels[kind][begin:begin+size]+=pcm[:size]*gain
        if n<len(ep["scenes"])-1:
            transition=scene.get("assemblyV35",{}).get("transition",.35)
            start+=float(scene["duration"])-float(transition)
    # Short smoothing in both directions, score ducks under Russian voices.
    live=(np.abs(channels["voice"])>.002).astype(np.float64)
    env=np.zeros(count,dtype=np.float64)
    k=1.0/max(1,round(.13*SAMPLE_RATE))
    for i in range(1,count):
        env[i]=max(live[i],env[i-1]*(1-k))
    for i in range(count-2,-1,-1):
        env[i]=max(env[i],env[i+1]*(1-k))
    a=channels["voice"]+channels["music"]*(1-.64*env)+channels["fx"]*(1-.24*env)
    level=float(np.max(np.abs(a)))
    if level>0.95:a*=.95/level
    rms=float(np.sqrt(np.mean(a*a)))
    if rms<.002:raise RuntimeError("Silent Russian preview")
    report={"duration":length,"rms":round(rms,5),"peakBeforeLimiting":round(level,4),
            "voiceActiveSamples":int(np.count_nonzero(live)),
            "threeIndependentTracks":True,"automaticMusicDucking":True,
            "naturalActorDubApproved":False}
    return a.astype("<f4").tobytes(),report
def validate(project):
    if project.get("format")!="AIAnimeFactoryProject" or len(project.get("episodes",[]))<6:
        raise ValueError("V50 source season missing")
    hash=project.get("pilotProductionV50",{}).get("originalV50ProjectSha256")
    if not hash or len(hash)!=64:raise ValueError("V19/V50 source canon absent")
    for ep in project["episodes"][:6]:
        if len(ep["scenes"])!=6:raise ValueError("Incomplete pilot story")
        for sc in ep["scenes"]:
            if not sc.get("pilotV50") or len(sc.get("lines",[]))!=2:
                raise ValueError("Scene script missing")
            for kind in ("voice","music","fx"):
                if not sc.get("audioV36",{}).get(kind,{}).get("embeddedV47"):
                    raise ValueError("Portable audio missing")
    return hash
def render(html,project,out,ei,width,fps,preview):
    ep=project["episodes"][ei]
    length=duration(ep)
    count=math.ceil(length*fps)
    if preview:count=min(count,36)
    out.mkdir(parents=True,exist_ok=True)
    errors=[];sample=[];digests=set()
    with sync_playwright() as pw:
        chrome=os.environ.get("V502_CHROMIUM_EXECUTABLE")
        opts={"executable_path":chrome} if chrome else {}
        browser=pw.chromium.launch(headless=True,
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],**opts)
        page=browser.new_page()
        page.on("pageerror",lambda x:errors.append(str(x)))
        try:
            page.goto(html.resolve().as_uri(),wait_until="load",timeout=60000)
            page.wait_for_function("() => window.v502Motion && window.v502CleanCutsQA",timeout=35000)
            # Six-episode portable JSON with audio exceeds localStorage quota.
            # The standalone HTML MUST embed the same complete project already;
            # rendering never writes browser storage or modifies source JSON.
            page.wait_for_function("() => window.v502Motion && window.v502CleanCutsQA && window.v502SeasonStageQA",timeout=35000)
            embedded=page.evaluate("""() => ({
              source:window.v50FinalQA.currentProject().seasonScriptV502?.originalFirstTwoEpisodesSha256,
              stage:window.v502SeasonStageQA.active()})""")
            if not embedded["stage"] or embedded["source"]!=project["seasonScriptV502"]["originalFirstTwoEpisodesSha256"]:
                raise RuntimeError("HTML project does not match the six-episode staged input")
            page.wait_for_function("() => window.v502CleanCutsQA.loaded()===13",timeout=35000)
            audit=page.evaluate("""()=>({
               errors:window.v50FinalQA.audit().errors,
               n:window.v50FinalQA.currentProject().episodes.length,
               art:window.v50FinalQA.currentProject().v502Art?.enabled,
               rig:window.v50FinalQA.currentProject().v502MotionRig?.enabled,
               cuts:window.v50FinalQA.currentProject().v502CleanCuts?.enabled
            })""")
            if audit["errors"] or audit["n"]<6 or not (audit["art"] and audit["rig"] and audit["cuts"]):
                raise RuntimeError("Pilot/browser QA failed "+str(audit)[:500])
            captions=page.evaluate("ei=>window.v48BatchBridge.subtitles(ei,'srt')",ei)
            (out/f"episode_{ei+1:02d}.srt").write_text(captions,encoding="utf-8")
            silent=out/f"episode_{ei+1:02d}_silent.mp4"
            cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
                 "-f","image2pipe","-framerate",str(fps),"-c:v","png","-i","pipe:0",
                 "-c:v","libx264","-preset","veryfast","-crf","19",
                 "-pix_fmt","yuv420p","-r",str(fps),str(silent)]
            process=subprocess.Popen(cmd,stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            try:
                for i in range(count):
                    t=min(length-.0001,i/fps)
                    data=page.evaluate("([ei,t,w])=>window.v502Motion.sceneFrame(ei,t,w)",
                        [ei,t,width])
                    binary=base64.b64decode(data.split(",",1)[1])
                    if not binary.startswith(b"\x89PNG\r\n\x1a\n"):
                        raise RuntimeError("Invalid frame "+str(i))
                    if i%max(1,count//10)==0:
                        name=f"ep{ei+1:02d}_frame{i:04d}.png"
                        (out/name).write_bytes(binary);sample.append(name)
                    digests.add(hashlib.sha256(binary).digest())
                    process.stdin.write(binary)
                process.stdin.close()
                stderr=process.stderr.read()
                if process.wait(timeout=120):
                    raise RuntimeError("FFmpeg "+stderr.decode(errors="replace")[-1200:])
            except BaseException:
                if process.stdin and not process.stdin.closed:process.stdin.close()
                process.kill();process.wait(timeout=5);raise
            if errors:raise RuntimeError("Chromium "+str(errors[:5]))
        finally:browser.close()
    if len(digests)<min(count,30):raise RuntimeError("Repeated/frozen frames")
    voice,aq=audio_mix(ep,count/fps)
    final=out/f"episode_{ei+1:02d}.mp4"
    with tempfile.TemporaryDirectory(prefix="v502_mix_") as td:
        pcm=Path(td)/"sound.f32";pcm.write_bytes(voice)
        command(["ffmpeg","-y","-hide_banner","-loglevel","error",
          "-i",str(silent),"-f","f32le","-ar",str(SAMPLE_RATE),"-ac","1","-i",str(pcm),
          "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k",
          "-shortest","-movflags","+faststart",str(final)])
    info=json.loads(command(["ffprobe","-v","error","-show_entries",
        "stream=codec_name,codec_type,width,height,nb_frames:format=duration",
        "-of","json",str(final)]))
    codes={s.get("codec_name") for s in info["streams"]}
    if not {"h264","aac"}.issubset(codes):raise RuntimeError("Missing H264/AAC")
    video=next(s for s in info["streams"] if s.get("codec_type")=="video")
    if int(video["width"])!=width or int(video["height"])!=round(width*9/16):
        raise RuntimeError("Resolution mismatch")
    if int(video.get("nb_frames") or count)!=count:raise RuntimeError("Frame loss")
    if abs(float(info["format"]["duration"])-count/fps)>.22:
        raise RuntimeError("Incorrect MP4 duration")
    silent.unlink()
    return {"episode":ei+1,"fps":fps,"width":width,"height":round(width*9/16),
            "frames":count,"distinctFrameDigests":len(digests),
            "seconds":float(info["format"]["duration"]),"audio":aq,
            "samples":sample,"humanArtApproved":False,"rightsApproved":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--fps",type=int,choices=(6,12,24),default=12)
    p.add_argument("--width",type=int,choices=(640,960,1280),default=960)
    p.add_argument("--episodes",default="3,4,5,6")
    p.add_argument("--preview-only",action="store_true")
    a=p.parse_args()
    for bin in ("ffmpeg","ffprobe"):
        if not shutil.which(bin):raise RuntimeError(bin+" not installed")
    project=json.loads(a.project.read_text(encoding="utf-8"))
    canon=validate(project)
    indices=[int(k)-1 for k in a.episodes.split(",")]
    if not indices or any(i<0 or i>=6 for i in indices):
        raise ValueError("Only staged pilot episodes 1 through 6 supported")
    reports=[]
    for i in indices:
        print("V50.2 OFFLINE RENDER",i+1,a.width,a.fps,flush=True)
        reports.append(render(a.html,project,a.out,i,a.width,a.fps,a.preview_only))
        print("COMPLETE",i+1,reports[-1]["frames"],flush=True)
    report={"schema":"AIAnimeFactory/V502/OfflineHighQuality/1",
            "sourceCanonSha256":canon,"episodes":reports,
            "status":"TECHNICAL_PREVIEW_ART_AND_ACTOR_DUB_PENDING",
            "commercialRightsVerified":False,"fullSeasonCompleted":False}
    (a.out/"V502_OFFLINE_RENDER_QA.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
