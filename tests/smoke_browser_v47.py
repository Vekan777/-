#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V47 Chromium E2E: embedded real speech bytes, mouth pixels and restored audio WebM."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def wav(path):
 rate=16000
 with wave.open(str(path),"wb") as sound:
  sound.setnchannels(1);sound.setsampwidth(2);sound.setframerate(rate)
  chunks=[]
  for i in range(rate*3):
   t=i/rate
   # Conspicuous voiced/silent intervals, not a fake static envelope.
   amplitude=.56 if .15<t<.83 or 1.26<t<1.91 else .005
   chunks.append(struct.pack("<h",int(32767*amplitude*math.sin(2*math.pi*215*t))))
  sound.writeframes(b''.join(chunks))
def png(path):
 data=path.read_bytes()
 if data[:8]!=b'\x89PNG\r\n\x1a\n' or len(data)<5000:
  raise AssertionError('Not real PNG '+str(path))
 return hashlib.sha256(data).hexdigest()
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("--html",required=True)
 cli.add_argument("--out",default="dist/V47_VOICE_BROWSER")
 args=cli.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
 audio=out/"V47_REAL_TEST_SPEECH.wav";wav(audio)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1450,"height":1050},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(args.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v47-episode')?.options.length>0",timeout=45000)
   # Choose an author scene with at least one timed speaking line, keep plot unchanged.
   candidates=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V47'));
    const rows=[];
    for(let i=0;i<p.episodes.length;i++)
      for(let j=0;j<p.episodes[i].scenes.length;j++){
       const s=p.episodes[i].scenes[j];
       const line=s.lines?.find(l=>l.start<2.5&&l.duration>.2);
       if(line)rows.push({episode:i,scene:j,speaker:line.speaker,
        at:Math.max(.25,Math.min(1.5,line.start+.3))});
      }
    return rows;
   }""")
   if not candidates:raise AssertionError("No timed authored dialogue scene")
   chosen=candidates[0]
   # Use first speaker selection from original P, no changes to lines/story.
   page.locator('[data-page="art-assets-v45"]').click()
   page.locator("#v45-character").select_option("0")
   page.locator("#v45-make").click()
   page.wait_for_function("() => document.querySelector('#v45-status')?.textContent.includes('7/7')",timeout=30000)
   page.wait_for_timeout(300)
   page.locator('[data-page="voice-v47"]').click()
   page.locator("#v47-episode").select_option(str(chosen["episode"]))
   page.locator("#v47-scene").select_option(str(chosen["scene"]))
   page.locator("#v47-slot").select_option("voice")
   page.locator("#v47-timeline").fill(str(round(1000*chosen["at"]/
     max(1,float(page.evaluate("""([i,j]) => JSON.parse(
      localStorage.getItem('AI_ANIME_FACTORY_V47')).episodes[i].scenes[j].duration""",
      [chosen["episode"],chosen["scene"]]))))))
   cast=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V47'))
    .characters.map(c=>c.name)""")
   speaker=cast.index(chosen["speaker"])
   if speaker<0:raise AssertionError("Timed speaker missing from character list")
   page.locator("#v47-speaker").select_option(str(speaker))
   page.locator("#v47-save").click()
   page.locator("#v47-file").set_input_files(str(audio))
   page.wait_for_function("""() => document.querySelector('#v47-state')?.textContent.includes('сохранено')""",
    timeout=25000)
   old=page.evaluate("""([i,j]) => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V47'))
    .episodes[i].scenes[j].audioV36.voice""",[chosen["episode"],chosen["scene"]])
   if not old["embeddedV47"].startswith("data:audio/"):
    raise AssertionError("No portable audio bytes")
   if len(old["waveV47"])<100 or max(old["waveV47"])<.7 or min(old["waveV47"])>.1:
    raise AssertionError("Waveform not based on real variable-level PCM")
   if old["speakerV47"]!=chosen["speaker"]:
    raise AssertionError("Audio wrongly assigned to another speaker")
   before=out/"V47_MOUTH_DISABLED.png"
   page.locator("#v47-mouth-on").uncheck()
   page.locator("#v47-save").click()
   page.locator("#v47-preview").screenshot(path=str(before))
   base=png(before)
   page.locator("#v47-mouth-on").check()
   page.locator("#v47-save").click()
   after=out/"V47_MOUTH_AUDIO_SYNC.png"
   page.locator("#v47-preview").screenshot(path=str(after))
   if png(after)==base:
    raise AssertionError("Audio-driven lip motion did not affect real Canvas pixels")
   if 'амплитуда звука' not in page.locator("#v47-time").text_content():
    raise AssertionError("Real audio amplitude mode not active")
   # Keep music separate; V47 must preserve all three slot gain/mix settings.
   page.locator("#v47-slot").select_option("music")
   page.locator("#v47-file").set_input_files(str(audio))
   page.wait_for_function("""() => document.querySelector('#v47-state')?.textContent.includes('сохранено')""",
    timeout=25000)
   page.locator("#v47-gain").fill("42")
   page.locator("#v47-save").click()
   stored=page.evaluate("""([i,j]) => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V47'))
    .episodes[i].scenes[j].audioV36""",[chosen["episode"],chosen["scene"]])
   if not stored["music"]["embeddedV47"] or abs(stored["music"]["gain"]-.42)>.001:
    raise AssertionError("Music bytes or mixing volume not saved")
   with page.expect_download(timeout=30000) as job:
    page.locator("#v47-project").click()
   package=out/"V47_PORTABLE_FULL_PROJECT.json";job.value.save_as(str(package))
   parsed=json.loads(package.read_text(encoding='utf-8'))
   scene=parsed["episodes"][chosen["episode"]]["scenes"][chosen["scene"]]
   if scene["audioV36"]["voice"]["embeddedV47"]!=old["embeddedV47"]:
    raise AssertionError("Downloaded full JSON has lost voice bytes")
   if not parsed["characters"][0]["productionRig"]["parts"]["face"]["image"]:
    raise AssertionError("Downloaded project has lost V45 character art")
   if not parsed["episodes"][chosen["episode"]].get("storyV20"):
    raise AssertionError("Downloaded project lost V20 storyline")
   # Force actual page reload and recording with no reattached file.
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v47-episode')?.options.length>0",timeout=45000)
   survived=page.evaluate("""([i,j]) => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V47'))
    .episodes[i].scenes[j].audioV36.voice.embeddedV47""",
    [chosen["episode"],chosen["scene"]])
   if not survived.startswith("data:audio/"):
    raise AssertionError("Browser restart lost actual embedded WAV")
   # Shorten only isolated test project while keeping audio scene as first scene.
   page.evaluate("""([i,j]) => {
    const key='AI_ANIME_FACTORY_V47',p=JSON.parse(localStorage.getItem(key));
    const target=JSON.parse(JSON.stringify(p.episodes[i].scenes[j]));
    target.duration=2.7;
    p.episodes=[{...p.episodes[i],number:1,scenes:[target]}];
    localStorage.setItem(key,JSON.stringify(p));
   }""",[chosen["episode"],chosen["scene"]])
   page.reload(wait_until="load")
   page.locator('[data-page="audio-v36"]').click()
   page.locator("#v36-episode").select_option("0")
   page.locator("#v36-scene").select_option("0")
   # Absolutely do not re-attach WAV: restoring it from JSON is the tested feature.
   assert not page.locator("#v36-audiofile").evaluate("(el) => el.files.length")
   with page.expect_download(timeout=65000) as job:
    page.locator("#v36-export").click()
   movie=out/"V47_RESTORED_SPEECH_AND_MUSIC.webm"
   job.value.save_as(str(movie))
   if not job.value.suggested_filename.startswith("V47_PORTABLE_VOICE_EPISODE_"):
    raise AssertionError("Wrong final filename")
   if movie.stat().st_size<7000:raise AssertionError("No real recorded WebM")
   probe={}
   if shutil.which("ffprobe"):
    raw=subprocess.run(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,codec_name","-of","json",str(movie)],
      capture_output=True,text=True,check=True,timeout=30)
    probe=json.loads(raw.stdout)
    kinds={a["codec_type"] for a in probe.get("streams",[])}
    if not {"video","audio"}.issubset(kinds):
     raise AssertionError("WebM missing actual video and audio after JSON rehydration")
   if errors:raise AssertionError("Browser JavaScript errors: "+"; ".join(errors[:5]))
   (out/"V47_QA.json").write_text(json.dumps({
    "version":47,"embedded_real_voice_and_music":True,
    "lip_sync_pixel_change":True,"project_reloaded":True,
    "no_audio_reattachment":True,"music_gain_persisted":True,
    "story_and_art_preserved":True,"real_WebM_bytes":movie.stat().st_size,
    "ffprobe":probe},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V47 CHROMIUM PASS: real portable WAV/music, sound-driven mouth and restored audio/video WebM")
  finally:browser.close()
if __name__=="__main__":main()
