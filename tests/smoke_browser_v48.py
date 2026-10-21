#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V48 Chromium + real 2-episode production CLI test, MP4 sound, resume and subtitles."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,sys,wave
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
def test_wav(path):
 rate=16000
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes(b"".join(struct.pack("<h",int(8500*math.sin(2*math.pi*330*i/rate)))
    for i in range(rate*3)))
def png(path):
 data=path.read_bytes()
 if data[:8]!=b"\x89PNG\r\n\x1a\n" or len(data)<5000:
  raise RuntimeError("Not true PNG "+str(path))
 return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--html",required=True)
 p.add_argument("--out",default="dist/V48_PRODUCTION_BROWSER")
 a=p.parse_args()
 html=Path(a.html).resolve()
 out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 sound=out/"V48_LICENSABLE_TEST_TONE.wav";test_wav(sound)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox",
   "--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1440,"height":1000},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(html.as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v48-episode')?.options.length>=2",timeout=45000)
   page.locator('[data-page="episode-v48"]').click()
   page.locator("#v48-episode").select_option("0")
   beginning=out/"V48_REAL_SCENE.png"
   page.locator("#v48-preview").screenshot(path=str(beginning))
   h0=png(beginning)
   page.locator("#v48-position").fill("985")
   ending=out/"V48_END_CREDITS.png"
   page.locator("#v48-preview").screenshot(path=str(ending))
   if png(ending)==h0:raise AssertionError("Real end-card did not change original episode pixels")
   page.locator("#v48-studio").fill("Тестовая студия аниме")
   page.locator("#v48-save").click()
   first=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V48'))""")
   if first["version"]!=48 or not first["episodes"][0].get("storyV20"):
    raise AssertionError("Original plot missing after V48 settings")
   # Attach a real WAV through V47 (not simulated/stub sound).
   page.locator('[data-page="voice-v47"]').click()
   page.locator("#v47-episode").select_option("0")
   page.locator("#v47-scene").select_option("0")
   page.locator("#v47-slot").select_option("voice")
   page.locator("#v47-speaker").select_option("0")
   page.locator("#v47-save").click()
   page.locator("#v47-file").set_input_files(str(sound))
   page.wait_for_function("""() => document.querySelector('#v47-state')?.textContent.includes('сохранено')""",timeout=25000)
   # Copy the SAME original/licensed audio to episode 2 within the isolated QA project.
   # All canonical plot facts and combat outcomes stay untouched.
   page.evaluate("""() => {
      const key='AI_ANIME_FACTORY_V48',p=JSON.parse(localStorage.getItem(key));
      const first=p.episodes[0].scenes[0],second=p.episodes[1].scenes[0];
      second.audioV36={...second.audioV36,
       voice:JSON.parse(JSON.stringify(first.audioV36.voice))};
      for(const ep of p.episodes.slice(0,2)){
       const s=ep.scenes[0];
       s.subtitlesV37={cues:[{start:.15,end:1.8,
        text:'Сцена с настоящим звуком и анимацией',
        speaker:p.characters[0].name}]};
      }
      localStorage.setItem(key,JSON.stringify(p));
    }""")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v48-episode')?.options.length>=2",timeout=30000)
   page.locator('[data-page="episode-v48"]').click()
   page.locator("#v48-episode").select_option("0")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v48-srt").click()
   subtitle=out/"V48_MANUAL_EPISODE.srt";dl.value.save_as(str(subtitle))
   if "-->" not in subtitle.read_text(encoding="utf-8"):
    raise AssertionError("No actual SRT cues")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v48-vtt").click()
   vtt=out/"V48_MANUAL_EPISODE.vtt";dl.value.save_as(str(vtt))
   if not vtt.read_text(encoding="utf-8").startswith("WEBVTT"):
    raise AssertionError("VTT export broken")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v48-manifest").click()
   manifest=out/"V48_SEASON_EDIT_PLAN.json";dl.value.save_as(str(manifest))
   plan=json.loads(manifest.read_text(encoding="utf-8"))
   if plan["version"]!=48 or len(plan["episodes"])<2:
    raise AssertionError("Season shot/sound plan missing")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v48-frames").click()
   sheet=out/"V48_REAL_EPISODE_FRAMES.png";dl.value.save_as(str(sheet));png(sheet)
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v48-project").click()
   portable=out/"V48_PORTABLE_TEST_PROJECT.json";dl.value.save_as(str(portable))
   project=json.loads(portable.read_text(encoding="utf-8"))
   if not project["episodes"][0]["scenes"][0]["audioV36"]["voice"]["embeddedV47"]:
    raise AssertionError("Full exported season lost original WAV bytes")
   if project["episodes"][0]["storyV20"]!=first["episodes"][0]["storyV20"]:
    raise AssertionError("V48 corrupted canonical storyline")
   if errors:raise AssertionError("Browser errors: "+"; ".join(errors[:5]))
  finally:browser.close()
 # Run TWO sequential actual Chromium MediaRecorder episodes and H264/AAC MP4.
 if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
  raise AssertionError("FFmpeg and FFprobe required for deep real V48 QA")
 batch=out/"SEASON_OUTPUT"
 cmd=[sys.executable,str(ROOT/"scripts/render_anime_v48.py"),
   "--html",str(html),"--project",str(portable),"--out",str(batch),
   "--episodes","1,2","--fps","6","--mp4","--qa-short"]
 run=subprocess.run(cmd,capture_output=True,text=True,timeout=230)
 if run.returncode:raise AssertionError("Real batch failed: "+run.stdout+"\n"+run.stderr)
 outputs=json.loads((batch/"V48_SEASON_RENDER_MANIFEST.json").read_text(encoding="utf-8"))
 if len(outputs["episodes"])!=2:raise AssertionError("Did not produce TWO real episodes")
 checkpoint=json.loads((batch/"V48_RENDER_CHECKPOINT.json").read_text(encoding="utf-8"))
 if len(checkpoint["episodes"])!=2 or any(x["status"]!="completed" for x in checkpoint["episodes"].values()):
  raise AssertionError("Completed episode checkpoint missing")
 for i in (1,2):
  base=batch/f"episode_{i:02d}"
  for ext in ("webm","mp4","srt","vtt"):
   file=base.with_suffix("."+ext)
   if not file.is_file() or file.stat().st_size<20:
    raise AssertionError("Real per-episode deliverable missing "+str(file))
  media=json.loads(subprocess.run(["ffprobe","-v","error",
   "-show_entries","stream=codec_type,codec_name:format=duration","-of","json",
   str(base.with_suffix(".mp4"))],capture_output=True,text=True,check=True,timeout=30).stdout)
  codecs={s.get("codec_name") for s in media["streams"]}
  if not {"h264","aac"}.issubset(codecs):
   raise AssertionError("MP4 must be H264/AAC, got "+str(codecs))
  if not base.with_suffix(".vtt").read_text(encoding="utf-8").startswith("WEBVTT"):
   raise AssertionError("Missing VTT in episode "+str(i))
 # Resumability proof: run identical job and require 2 checksum-confirmed skips.
 again=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 if again.returncode or again.stdout.count("V48 VERIFIED RESUME / SKIPPED")!=2:
  raise AssertionError("Checkpoint cannot resume without rerendering: "+
   again.stdout+"\n"+again.stderr)
 (out/"V48_QA.json").write_text(json.dumps({
  "version":48,"true_real_episodes":2,
  "both_mp4_h264_aac":True,"two_srt_and_vtt":True,
  "credit_pixels":True,"preserved_story_and_audio":True,
  "resumed_two_checksum_verified_episodes":True,
  "render_output":str(batch),"browser_errors":errors
 },ensure_ascii=False,indent=2),encoding="utf-8")
 print("V48 REAL CHROMIUM+FFMPEG PASSED: two separate episodes with sound, MP4 H264/AAC, VTT/SRT, checksum resume")
if __name__=="__main__":main()
