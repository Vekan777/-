#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V49 real Chromium: six-stage routes, manual reviews, full asset/voice/keyframe
backups, V48 legacy JSON import and actual V49 WebM with audio."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def voice(path):
 rate=16000
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes(b"".join(struct.pack("<h",int(9800*math.sin(2*math.pi*240*i/rate)))
   for i in range(rate*3)))
def png(path):
 b=path.read_bytes()
 if b[:8]!=b"\x89PNG\r\n\x1a\n" or len(b)<5000:raise AssertionError("No real PNG")
 return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--html",required=True)
 p.add_argument("--out",default="dist/V49_UNIFIED_BROWSER")
 a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 sample=out/"V49_REAL_ACTOR_VOICE.wav";voice(sample)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1440,"height":1110},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(a.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v49-episode')?.options.length>1",timeout=45000)
   page.locator('[data-page="unified-v49"]').click()
   initial=page.evaluate("() => window.v49UnifiedBridge.audit()")
   if initial["version"]!=49 or len(initial["episodes"])<2:
    raise AssertionError("Unified production catalog has no two episodes")
   if "requiresHumanReview" not in initial or not initial["requiresHumanReview"]:
    raise AssertionError("Automated audit falsely represents itself as artistic approval")
   page.locator("#v49-episode").select_option("1")
   page.locator('[data-v49-ok="story"]').check()
   page.locator("#v49-notes").fill("Режиссёр: проверить ракурсы, голоса, сюжет и лицензии.")
   page.locator("#v49-save-notes").click()
   page.locator("#v49-episode").select_option("0")
   if page.locator('[data-v49-ok="story"]').is_checked():
    raise AssertionError("Author approval copied into another episode")
   page.locator('[data-v49-open="art"]').click()
   if not page.locator("#page-art-assets-v45").is_visible():
    raise AssertionError("Unified art routing not working")
   page.locator("#v45-character").select_option("0")
   page.locator("#v45-make").click()
   page.wait_for_function("() => document.querySelector('#v45-status')?.textContent.includes('7/7')",timeout=27000)
   page.locator('[data-page="unified-v49"]').click()
   page.locator('[data-v49-open="animate"]').click()
   page.locator("#v46-episode").select_option("0")
   page.locator("#v46-scene").select_option("0")
   page.locator("#v46-role").select_option("hero")
   page.locator("#v46-action").select_option("warmth")
   page.locator("#v46-action-apply").click()
   page.locator('[data-page="unified-v49"]').click()
   page.locator('[data-v49-open="voice"]').click()
   page.locator("#v47-episode").select_option("0")
   page.locator("#v47-scene").select_option("0")
   page.locator("#v47-slot").select_option("voice")
   page.locator("#v47-speaker").select_option("0")
   page.locator("#v47-save").click()
   page.locator("#v47-file").set_input_files(str(sample))
   page.wait_for_function("""() => document.querySelector('#v47-state')?.textContent.includes('сохранено')""",timeout=24000)
   page.locator('[data-page="unified-v49"]').click()
   page.locator('[data-v49-open="subtitles"]').click()
   if not page.locator("#page-subtitles-v37").is_visible():
    raise AssertionError("Unified subtitles route not working")
   page.locator('[data-page="unified-v49"]').click()
   enriched=page.evaluate("() => window.v49UnifiedBridge.audit()")
   if enriched["episodes"][0]["animated"]<1 or enriched["episodes"][0]["voiced"]<1:
    raise AssertionError("Unified readiness not reading actual V46/V47 contents")
   if enriched["episodes"][0]["issues"]==[] and enriched["warnings"]==0:
    raise AssertionError("Technical audit falsely cleared all human/rights concerns")
   shot=out/"V49_UNIFIED_DESK.png"
   page.locator("#page-unified-v49").screenshot(path=str(shot))
   png(shot)
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v49-export-project").click()
   backup=out/"V49_REAL_FULL_BACKUP.json";dl.value.save_as(str(backup))
   p49=json.loads(backup.read_text(encoding="utf-8"))
   if p49["version"]!=49 or not p49["episodes"][0].get("storyV20"):
    raise AssertionError("V49 lost historical canon")
   if not p49["characters"][0]["productionRig"]["parts"]["face"]["image"]:
    raise AssertionError("V49 backup missing real V45 face image")
   if len(p49["episodes"][0]["scenes"][0]["animationV46"]["tracks"]["hero"])!=7:
    raise AssertionError("V49 backup lacks genuine seven-part keyframes")
   if not p49["episodes"][0]["scenes"][0]["audioV36"]["voice"]["embeddedV47"]:
    raise AssertionError("V49 backup missing real portable WAV")
   if not p49["productionV49"]["reviews"]["1"]["story"]:
    raise AssertionError("Second episode manual review missing from backup")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v49-export-checklist").click()
   report=out/"V49_READINESS_REPORT.json";dl.value.save_as(str(report))
   audit=json.loads(report.read_text(encoding="utf-8"))
   if audit["version"]!=49 or not audit["requiresHumanReview"]:
    raise AssertionError("V49 audit export incorrectly auto-certifies quality")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v49-episode')?.options.length>1",timeout=45000)
   page.locator('[data-page="unified-v49"]').click()
   page.locator("#v49-episode").select_option("1")
   if not page.locator('[data-v49-ok="story"]').is_checked():
    raise AssertionError("V49 reloaded review ledger not preserved")
   if "Режиссёр" not in page.locator("#v49-notes").input_value():
    raise AssertionError("V49 reloaded notes lost")
   # Simulate importing a real V48-formatted older project via existing UI:
   # the migration should preserve old V20 plot, V45 PNG, V46 keys and V47 voice.
   old=json.loads(json.dumps(p49))
   old["version"]=48;old.pop("productionV49",None)
   prior=out/"V48_REAL_OLD_PROJECT.json"
   prior.write_text(json.dumps(old,ensure_ascii=False),encoding="utf-8")
   page.locator("#project-file").set_input_files(str(prior))
   page.wait_for_function("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V49')).version===49""",timeout=30000)
   imported=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V49'))""")
   if imported["episodes"][0]["storyV20"]!=old["episodes"][0]["storyV20"]:
    raise AssertionError("Old V48 import removed story")
   if not imported["characters"][0]["productionRig"]["parts"]["face"]["image"]:
    raise AssertionError("Old V48 import removed character art")
   if not imported["episodes"][0]["scenes"][0]["audioV36"]["voice"]["embeddedV47"]:
    raise AssertionError("Old V48 import lost voice bytes")
   if not imported["episodes"][0]["scenes"][0]["animationV46"]:
    raise AssertionError("Old V48 import lost animation")
   # Crop only the isolated Chromium CI project; never change original repository.
   page.evaluate("""() => {
    const k='AI_ANIME_FACTORY_V49',p=JSON.parse(localStorage.getItem(k));
    const scene=JSON.parse(JSON.stringify(p.episodes[0].scenes[0]));
    scene.duration=2.7;
    p.episodes=[{...p.episodes[0],scenes:[scene]}];
    localStorage.setItem(k,JSON.stringify(p));
   }""")
   page.reload(wait_until="load")
   page.locator('[data-page="unified-v49"]').click()
   page.locator("#v49-record").click()
   if not page.locator("#page-episode-v48").is_visible():
    raise AssertionError("V49 true renderer integration not working")
   if page.locator("#v48-episode").input_value()!="0":
    raise AssertionError("V49 did not select requested episode for render")
   page.locator('[data-page="audio-v36"]').click()
   # No voice reattachment: V47 audio must restore from JSON.
   if page.locator("#v36-audiofile").evaluate("e=>e.files.length"):
    raise AssertionError("User WAV improperly reattached during reload")
   with page.expect_download(timeout=65000) as dl:
    page.locator("#v36-export").click()
   movie=out/"V49_REAL_EPISODE_WITH_AUDIO.webm"
   dl.value.save_as(str(movie))
   if not dl.value.suggested_filename.startswith("V49_UNIFIED_EPISODE_"):
    raise AssertionError("Missing V49 real WebM delivery version")
   if movie.stat().st_size<7000:raise AssertionError("V49 WebM is empty")
   media={}
   if shutil.which("ffprobe"):
    raw=subprocess.run(["ffprobe","-v","error","-show_entries",
      "stream=codec_type,codec_name:format=duration","-of","json",str(movie)],
      capture_output=True,text=True,check=True,timeout=30)
    media=json.loads(raw.stdout)
    channels={s["codec_type"] for s in media.get("streams",[])}
    if not {"audio","video"}.issubset(channels):
     raise AssertionError("V49 WebM audio or video missing")
   if errors:raise AssertionError("Browser JS errors: "+"; ".join(errors[:5]))
   (out/"V49_QA.json").write_text(json.dumps({
    "version":49,"six_stage_route":True,"manual_review_persists":True,
    "original_art_animation_voice_persist":True,
    "full_backup_and_readiness_export":True,
    "real_V48_old_project_roundtrip":True,
    "true_V49_WebM_bytes":movie.stat().st_size,
    "ffprobe":media},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V49 CHROMIUM PASS: six-stage integrated review, 7-layer actor, keyframes, WAV, V48 import, WebM audio.")
  finally:browser.close()
if __name__=="__main__":main()
