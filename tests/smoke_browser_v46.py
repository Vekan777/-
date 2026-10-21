#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V46 real Chromium: seven-layer motion, keyframes, reusable clip, persistence, WebM/audio."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def tone(path):
 rate=16000
 with wave.open(str(path),"wb") as out:
  out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
  out.writeframes(b"".join(struct.pack("<h",int(9000*math.sin(2*math.pi*440*i/rate)))
   for i in range(rate*3)))
def real_png(file):
 raw=file.read_bytes()
 if raw[:8]!=b"\x89PNG\r\n\x1a\n" or len(raw)<5000:raise AssertionError("Missing genuine PNG "+str(file))
 return hashlib.sha256(raw).hexdigest()
def main():
 args=argparse.ArgumentParser()
 args.add_argument("--html",required=True)
 args.add_argument("--out",default="dist/V46_ANIMATION_BROWSER")
 opt=args.parse_args()
 folder=Path(opt.out).resolve();folder.mkdir(parents=True,exist_ok=True)
 wav=folder/"V46_TEST_VOICE.wav";tone(wav)
 errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage",
    "--disable-gpu","--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1450,"height":1090},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(opt.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v46-episode')?.options.length>0",timeout=45000)
   page.locator('[data-page="art-assets-v45"]').click()
   page.locator("#v45-character").select_option("0")
   page.locator("#v45-make").click()
   page.wait_for_function("() => document.querySelector('#v45-status')?.textContent.includes('7/7')",timeout=25000)
   page.wait_for_timeout(350)
   page.locator('[data-page="animation-v46"]').click()
   page.locator("#v46-episode").select_option("0")
   page.locator("#v46-scene").select_option("0")
   page.locator("#v46-role").select_option("hero")
   page.locator("#v46-part").select_option("arms")
   page.locator("#v46-position").fill("480")
   baseline=folder/"V46_BEFORE_KEYFRAMES.png"
   page.locator("#v46-preview").screenshot(path=str(baseline))
   h0=real_png(baseline)
   canon=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V46'))""")
   if canon["version"]!=46 or not canon["episodes"][0].get("storyV20"):
    raise AssertionError("Prior storyline or new version missing")
   page.locator("#v46-action").select_option("strike")
   page.locator("#v46-action-apply").click()
   page.locator("#v46-position").fill("480")
   after=folder/"V46_AFTER_REAL_STRIKE.png"
   page.locator("#v46-preview").screenshot(path=str(after))
   if real_png(after)==h0:raise AssertionError("Real keyframes do not change drawn actor pixels")
   project=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V46'))""")
   tr=project["episodes"][0]["scenes"][0]["animationV46"]["tracks"]["hero"]
   if len(tr)!=7 or sum(map(len,tr.values()))!=35:
    raise AssertionError("Not 35 keyframes in seven genuine body-part tracks")
   if project["episodes"][0]["storyV20"]!=canon["episodes"][0]["storyV20"]:
    raise AssertionError("Animation overwrote story canon")
   if not project["characters"][0]["productionRig"]["parts"]["arms"]["image"].startswith("data:image/png;base64,"):
    raise AssertionError("V45 art layers lost")
   # Hand-authored key on another body part: times 0.29 and 0.73.
   page.locator("#v46-part").select_option("face")
   page.locator("#v46-position").fill("290")
   page.locator("#v46-angle").fill("25")
   page.locator("#v46-x").fill("8")
   page.locator("#v46-ease").select_option("hold")
   page.locator("#v46-key-save").click()
   key=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V46'))
    .episodes[0].scenes[0].animationV46.tracks.hero.face
    .find(k=>Math.abs(k.t-.29)<.01)""")
   if not key or key["angle"]!=25 or key["ease"]!="hold":
    raise AssertionError("Manual hold-keyframe not persisted")
   page.locator("#v46-onion").check()
   ghost=folder/"V46_ONION_SKIN.png"
   page.locator("#v46-preview").screenshot(path=str(ghost))
   real_png(ghost)
   page.locator("#v46-onion").uncheck()
   page.locator("#v46-clip-name").fill("Удар героя — повторное использование")
   page.locator("#v46-clip-save").click()
   page.wait_for_function("() => document.querySelector('#v46-clip-count').textContent.includes('1 сохран')",timeout=15000)
   page.locator("#v46-scene").select_option("1")
   page.locator("#v46-role").select_option("partner")
   page.locator("#v46-clip").select_option("0")
   page.locator("#v46-clip-apply").click()
   project=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V46'))""")
   if len(project["animationClipsV46"])!=1:
    raise AssertionError("Reusable clip library not stored")
   copied=project["episodes"][0]["scenes"][1]["animationV46"]["tracks"]["partner"]
   if len(copied)!=7 or len(copied["arms"])!=5:
    raise AssertionError("Reusable 2D action not applied to second actor")
   if project["episodes"][0]["scenes"][1]["kind"]!=canon["episodes"][0]["scenes"][1]["kind"]:
    raise AssertionError("Clip changed existing story type")
   with page.expect_download(timeout=30000) as job:
    page.locator("#v46-json").click()
   package=folder/"V46_ANIMATION_LIBRARY.json";job.value.save_as(str(package))
   stored=json.loads(package.read_text(encoding="utf-8"))
   if stored["version"]!=46 or len(stored["clips"])!=1:
    raise AssertionError("Exported library JSON missing")
   with page.expect_download(timeout=30000) as job:
    page.locator("#v46-frame").click()
   sheet=folder/"V46_FOUR_REAL_KEYFRAMES.png";job.value.save_as(str(sheet));real_png(sheet)
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v46-scene')?.options.length>1",timeout=45000)
   recovered=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V46'))""")
   if len(recovered.get("animationClipsV46",[]))!=1:
    raise AssertionError("Reload lost reusable animation clip")
   if not recovered["characters"][0]["productionRig"]["parts"]["arms"]["image"]:
    raise AssertionError("Reload lost original imported V45 asset")
   if not recovered["episodes"][0]["scenes"][1]["animationV46"]["tracks"]["partner"]["arms"]:
    raise AssertionError("Reload lost partner animation")
   # Shortening episode ONLY inside isolated test browser localStorage, never source.
   page.evaluate("""() => {
    const k='AI_ANIME_FACTORY_V46',p=JSON.parse(localStorage.getItem(k));
    const source=p.episodes[0].scenes;
    p.episodes[0].scenes=[JSON.parse(JSON.stringify(source[0])),
      JSON.parse(JSON.stringify(source[1]))];
    p.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(k,JSON.stringify(p));
   }""")
   page.reload(wait_until="load")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-slot").select_option("voice")
   page.locator("#v36-audiofile").set_input_files(str(wav))
   page.wait_for_function("() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')",timeout=20000)
   with page.expect_download(timeout=60000) as job:
    page.locator("#v36-export").click()
   video=folder/"V46_ANIMATED_WITH_VOICE.webm";job.value.save_as(str(video))
   if not job.value.suggested_filename.startswith("V46_ANIMATION_ENGINE_EPISODE_"):
    raise AssertionError("V46 WebM uses wrong version")
   if video.stat().st_size<6500:raise AssertionError("No actual recorded WebM")
   probe={}
   if shutil.which("ffprobe"):
    proc=subprocess.run(["ffprobe","-v","error","-show_entries",
     "format=duration:stream=codec_type,codec_name","-of","json",str(video)],
     capture_output=True,text=True,check=True,timeout=30)
    probe=json.loads(proc.stdout)
    kinds={x["codec_type"] for x in probe.get("streams",[])}
    if not {"audio","video"}.issubset(kinds):
     raise AssertionError("V46 WebM missing real video/audio tracks")
   if errors:raise AssertionError("JS runtime errors: "+"; ".join(errors[:5]))
   (folder/"V46_QA.json").write_text(json.dumps({
    "version":46,"real_2d_layer_motion_pixels":True,
    "keyframes_7_parts":35,"edited_hold_frame":True,
    "reusable_clip_into_second_actor":True,"onion_skin":True,
    "art_and_story_preserved":True,"recovery_after_reload":True,
    "audio_video_WebM_bytes":video.stat().st_size,"ffprobe":probe
   },ensure_ascii=False,indent=2),encoding="utf-8")
   print("V46 CHROMIUM PASS: real 7-layer keyframes, clips, onion, persisted canon and audio/video")
  finally:browser.close()
if __name__=="__main__":main()
