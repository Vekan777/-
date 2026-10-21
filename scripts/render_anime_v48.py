#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V48 resumable-per-episode real WebM+audio, SRT/VTT and optional H264/AAC MP4.

This is sequential real-time Chromium production, not fake offline video.
Uses V36's original MediaRecorder and V47-embedded audio after reload.
Never holds 1800 PNGs / full video frames in Python memory.
Resumes only at completed-episode boundaries with checksum validation.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_HTML=ROOT/"anime-factory"/"v48"/"AI_Anime_Factory_V48_EPISODE_ENGINE.html"
def sha(data):return hashlib.sha256(data).hexdigest()
def atomic_json(target,obj):
 target.parent.mkdir(parents=True,exist_ok=True)
 tmp=target.with_name(target.name+".writing")
 tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
 tmp.replace(target)
def command(cmd,timeout=150):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if p.returncode:
  raise RuntimeError("Command failed: "+" ".join(map(str,cmd))+"\n"+p.stderr[-1900:])
 return p.stdout
def probe(file):
 if not shutil.which("ffprobe"):raise RuntimeError("FFprobe is required for actual media verification")
 d=json.loads(command(["ffprobe","-v","error","-show_entries",
  "format=duration:stream=codec_type,codec_name","-of","json",str(file)],90))
 types={s.get("codec_type") for s in d.get("streams",[])}
 if not {"video","audio"}.issubset(types):raise RuntimeError("Missing video/audio tracks in "+str(file))
 # MediaRecorder WebM often omits format.duration despite valid video packets.
 # Measure actual video PTS from the demuxer instead of assuming absent=0.
 reported=float(d.get("format",{}).get("duration") or 0)
 if reported<.3:
  raw=command(["ffprobe","-v","error","-select_streams","v:0",
   "-show_entries","packet=pts_time","-of","csv=p=0",str(file)],90)
  timestamps=[]
  for line in raw.splitlines():
   try:timestamps.append(float(line.strip().split(",")[0]))
   except (ValueError,IndexError):pass
  if timestamps:reported=max(timestamps)
 d["_verified_duration"]=reported
 if reported<.3:
  raise RuntimeError("Video is too short or no timestamps: "+str(d)[:1600])
 return d
def make_mp4(source,dst):
 if not shutil.which("ffmpeg"):raise RuntimeError("FFmpeg is required for MP4 export")
 command(["ffmpeg","-y","-hide_banner","-loglevel","error",
  "-i",str(source),"-map","0:v:0","-map","0:a:0",
  "-c:v","libx264","-preset","veryfast","-crf","23",
  "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",
  "-movflags","+faststart",str(dst)],max(180,source.stat().st_size//10000))
 return probe(dst)
def load_checkpoint(path,project_hash,html_hash,fps):
 try:d=json.loads(path.read_text(encoding="utf-8"))
 except (FileNotFoundError,ValueError):d={}
 if d.get("project_sha256")!=project_hash or d.get("html_sha256")!=html_hash or d.get("fps")!=fps:
  return {"schema":"V48/Progress/1","project_sha256":project_hash,
   "html_sha256":html_hash,"fps":fps,"episodes":{}}
 if not isinstance(d.get("episodes"),dict):d["episodes"]={}
 return d
def choose_episodes(page,arg):
 count=page.evaluate("() => window.v48BatchBridge.count()")
 if count<1:raise RuntimeError("No episodes in project")
 if arg:
  parts=[int(x) for x in arg.split(",") if x.strip()]
  if not parts or min(parts)<1 or max(parts)>count:raise ValueError("Episode numbers out of range")
  return list(dict.fromkeys(n-1 for n in parts))
 return list(range(count))
def main():
 parser=argparse.ArgumentParser(description="V48 sequential WebM, MP4 and SRT/VTT")
 parser.add_argument("--html",default=str(DEFAULT_HTML))
 parser.add_argument("--project",help="Full portable V47/V48 project JSON, incl. embedded audio")
 parser.add_argument("--out",default=str(ROOT/"dist"/"V48_EPISODE_EXPORT"))
 parser.add_argument("--episodes",help="Comma-separated episode numbers (1-based), default all")
 parser.add_argument("--fps",type=int,choices=(6,12,24),default=6)
 parser.add_argument("--mp4",action="store_true",help="Also encode H264/AAC MP4 through FFmpeg")
 parser.add_argument("--fresh",action="store_true",help="Ignore prior completed episode checkpoint")
 parser.add_argument("--qa-short",action="store_true",
  help="CI ONLY: shortens first two series to ~2.5s each, without changing source files")
 args=parser.parse_args()
 path=Path(args.html).resolve()
 if not path.is_file():raise FileNotFoundError(path)
 out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
 source=Path(args.project).resolve() if args.project else None
 data=source.read_text(encoding="utf-8") if source else ""
 if source:
  project=json.loads(data)
  if not isinstance(project.get("episodes"),list) or not project["episodes"]:
   raise ValueError("Invalid project file — no episodes")
  project["version"]=48
  # No clip normalization here: old canon must be byte-for-byte unchanged.
 digest=sha(data.encode()) if source else "BUILTIN_DEMO"
 checkpoint=out/"V48_RENDER_CHECKPOINT.json"
 ck=load_checkpoint(checkpoint,digest,sha(path.read_bytes()),args.fps)
 if args.fresh:ck["episodes"]={}
 def persist():atomic_json(checkpoint,ck)
 def resume_done(i,base):
  row=ck["episodes"].get(str(i),{})
  webm=out/(base+".webm")
  if row.get("status")!="completed" or not webm.is_file():return False
  if row.get("sha256")!=sha(webm.read_bytes()):return False
  if args.mp4 and not (out/(base+".mp4")).is_file():return False
  probe(webm)
  if args.mp4:probe(out/(base+".mp4"))
  return True
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox",
   "--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  context=browser.new_context(accept_downloads=True)
  page=context.new_page()
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(path.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v48-episode')?.options.length>0",
    timeout=45000)
   if source:
    # Import only after an ordinary page boot. Passing file JSON as a
    # Playwright argument avoids script-injection escaping/origin problems.
    # V48, V49 UNIFIED and V50 FINAL have different localStorage namespaces.
    # The previously hard-coded V48 key silently made V49/V50 batches render
    # the default demo instead of the actual supplied project. Fix in-place.
    active_key=page.evaluate("""() => (
      document.querySelector('#page-final-v50') ? 'AI_ANIME_FACTORY_V50' :
      document.querySelector('#page-unified-v49') ? 'AI_ANIME_FACTORY_V49' :
      'AI_ANIME_FACTORY_V48'
    )""")
    page.evaluate("""([key,raw]) => {
      localStorage.setItem(key,raw);
      if(localStorage.getItem(key)!==raw)
       throw Error('Imported project localStorage readback failed');
    }""",[active_key,data])
    page.reload(wait_until="load")
    try:
     page.wait_for_function("() => document.querySelector('#v48-episode')?.options.length>0",
      timeout=25000)
    except Exception as ex:
     stored=page.evaluate("""key => ({
       bytes:localStorage.getItem(key)?.length||0,
       options:document.querySelector('#v48-episode')?.options.length||0
     })""",active_key)
     raise RuntimeError("Imported V48 project failed to initialize: "+str(stored)+
      "; browser errors: "+"; ".join(errors[:6])) from ex
   if args.qa_short:
    page.evaluate("() => window.v48BatchBridge.testShorten()")
    page.reload(wait_until="load")
    page.wait_for_function("() => document.querySelector('#v48-episode')?.options.length===2",
     timeout=45000)
   indices=choose_episodes(page,args.episodes)
   report={"schema":"V48/RenderOutput/1","episodes":[],"projectSha256":digest,
    "renderHtmlSha256":sha(path.read_bytes()),"fps":args.fps,"generatedAt":time.time()}
   for i in indices:
    meta=page.evaluate("(idx) => window.v48BatchBridge.episode(idx)",i)
    base=f"episode_{i+1:02d}"
    webm=out/(base+".webm")
    mp4=out/(base+".mp4")
    subtitles={}
    for ext in ("srt","vtt"):
     contents=page.evaluate("([idx,fmt]) => window.v48BatchBridge.subtitles(idx,fmt)",[i,ext])
     target=out/(base+"."+ext);target.write_text(contents,encoding="utf-8")
     subtitles[ext]={"file":target.name,"sha256":sha(target.read_bytes())}
    if not resume_done(i,base):
     ck["episodes"][str(i)]={"status":"in_progress",**meta}
     persist()
     page.locator('[data-page="audio-v36"]').click()
     page.locator("#v36-episode").select_option(str(i))
     page.locator("#v36-scene").select_option("0")
     page.locator("#v36-fps").select_option(str(args.fps))
     before=len(errors)
     # Native browser MediaRecorder uses original v35 timeline, V47 sound,
     # V48 end card. No unverified offline re-render of a fake episode.
     with page.expect_download(timeout=int((meta["duration"]+45)*1000)) as download:
      page.locator("#v36-export").click()
     item=download.value
     item.save_as(str(webm))
     if len(errors)>before:raise RuntimeError("Browser JS error: "+"; ".join(errors[before:]))
     if webm.stat().st_size<6500:raise RuntimeError("Empty WebM")
     info=probe(webm)
     if abs(float(info["_verified_duration"])-meta["duration"])>1.9:
      raise RuntimeError("WebM duration mismatch with V35 episode")
     if args.mp4:make_mp4(webm,mp4)
     ck["episodes"][str(i)]={"status":"completed",**meta,
      "sha256":sha(webm.read_bytes()),"bytes":webm.stat().st_size}
     persist()
     print("V48 COMPLETE",i+1,meta["title"],round(meta["duration"],2),
      "s",webm.stat().st_size,"bytes",flush=True)
    else:print("V48 VERIFIED RESUME / SKIPPED",i+1,meta["title"],flush=True)
    report["episodes"].append({**meta,
     "webm":webm.name,"webmSha256":sha(webm.read_bytes()),
     "mp4":mp4.name if args.mp4 else None,
     "mp4Sha256":sha(mp4.read_bytes()) if args.mp4 else None,
     "subtitles":subtitles})
    atomic_json(out/"V48_SEASON_RENDER_MANIFEST.json",report)
   if errors:raise RuntimeError("Browser errors: "+"; ".join(errors[:5]))
   print("V48 COMPLETE VERIFIED",len(report["episodes"]),
    "episodes; WebM+audio, SRT/VTT, optional H264/AAC MP4")
  finally:browser.close()
if __name__=="__main__":
 try:main()
 except Exception as err:
  print("V48 RENDER FAILED:",str(err),file=sys.stderr)
  raise SystemExit(1)
