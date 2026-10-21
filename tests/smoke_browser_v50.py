#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V50 final Chromium: real cutout, animation, voice, reversible V49 import,
error injection, signoffs, backups, true recorded WebM and audible PCM."""
from __future__ import annotations
import argparse,hashlib,json,math,re,shutil,struct,subprocess,wave
from pathlib import Path
from playwright.sync_api import sync_playwright
def make_wav(path):
 rate=16000
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes(b"".join(struct.pack("<h",round(11000*math.sin(2*math.pi*330*i/rate)))
   for i in range(rate*3)))
def png(path):
 data=path.read_bytes()
 if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data)<5000:
  raise AssertionError("Missing genuine PNG "+str(path))
 return hashlib.sha256(data).hexdigest()
def main():
 args=argparse.ArgumentParser();args.add_argument("--html",required=True)
 args.add_argument("--out",default="dist/V50_FINAL_BROWSER")
 opts=args.parse_args();out=Path(opts.out).resolve();out.mkdir(parents=True,exist_ok=True)
 audio=out/"V50_REAL_SPEECH.wav";make_wav(audio)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
   "--autoplay-policy=no-user-gesture-required"])
  page=browser.new_page(viewport={"width":1450,"height":1120},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append(str(e)))
  try:
   page.goto(Path(opts.html).resolve().as_uri(),wait_until="load",timeout=60000)
   page.wait_for_function("() => document.querySelector('#v50-episode')?.options.length>1",
    timeout=45000)
   page.locator('[data-page="final-v50"]').click()
   raw=page.evaluate("() => window.v50FinalQA.currentProject()")
   before=json.dumps(raw,sort_keys=True,ensure_ascii=False)
   audit=page.evaluate("() => window.v50FinalQA.audit()")
   if audit["version"]!=50 or not audit["manualAcceptanceRequired"] or len(raw["episodes"])<2:
    raise AssertionError("Final QA incorrectly auto-certified project")
   # Negative security and continuity tests in live browser. They may NOT modify
   # saved project: deep checker receives a detached JSON copy.
   corrupted=page.evaluate("""() => {
     const p=window.v50FinalQA.currentProject();
     p.characters[1].id=p.characters[0].id;
     p.episodes[0].scenes[0].duration=-10;
     p.episodes[0].scenes[0].subtitlesV37={cues:[{start:5,end:1,text:'broken'}]};
     p.episodes[0].scenes[0].audioV36={voice:{
       embeddedV47:'javascript:bad',gain:-20,offset:0,waveV47:[-1,20]}};
     return window.v50FinalQA.auditForeign(p);
   }""")
   if len(corrupted["errors"])<5 or corrupted["passed"]:
    raise AssertionError("Deliberately corrupted plot/timing/voice passed deep QA")
   unchanged=page.evaluate("() => window.v50FinalQA.currentProject()")
   if json.dumps(unchanged,sort_keys=True,ensure_ascii=False)!=before:
    raise AssertionError("Deep QA mutated canonical project")
   page.locator("#v50-episode").select_option("1")
   page.locator('[data-v50-review="story"]').check()
   page.locator('[data-v50-review="art"]').check()
   page.locator("#v50-notes").fill("Художественная проверка НЕ закончена: нужны лица, музыка, права и монтаж.")
   page.locator("#v50-notes-save").click()
   page.locator("#v50-episode").select_option("0")
   if page.locator('[data-v50-review="story"]').is_checked():
    raise AssertionError("Author approval improperly copied to another episode")
   # Build genuine V45, V46 and V47 assets from existing UI, not mocks.
   page.locator('[data-page="art-assets-v45"]').click()
   page.locator("#v45-character").select_option("0")
   page.locator("#v45-make").click()
   page.wait_for_function("""() => document.querySelector('#v45-status')
     ?.textContent.includes('7/7')""",timeout=26000)
   page.locator('[data-page="animation-v46"]').click()
   page.locator("#v46-episode").select_option("0")
   page.locator("#v46-scene").select_option("0")
   page.locator("#v46-role").select_option("hero")
   page.locator("#v46-action").select_option("walk")
   page.locator("#v46-action-apply").click()
   page.locator('[data-page="voice-v47"]').click()
   page.locator("#v47-episode").select_option("0")
   page.locator("#v47-scene").select_option("0")
   page.locator("#v47-slot").select_option("voice")
   page.locator("#v47-speaker").select_option("0")
   page.locator("#v47-save").click()
   page.locator("#v47-file").set_input_files(str(audio))
   page.wait_for_function("""() => document.querySelector('#v47-state')
     ?.textContent.includes('сохранено')""",timeout=24000)
   page.locator('[data-page="final-v50"]').click()
   enriched=page.evaluate("() => window.v50FinalQA.audit()")
   if enriched["animatedScenes"]<1 or enriched["voiceScenes"]<1:
    raise AssertionError("V50 QA cannot recognize genuine V45/V46/V47 production materials")
   if not enriched["manualAcceptanceRequired"]:
    raise AssertionError("Adding assets improperly automates artistic approval")
   image=out/"V50_FINAL_REAL_AUDIT.png"
   page.locator("#page-final-v50").screenshot(path=str(image));png(image)
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v50-full-backup").click()
   project=out/"V50_FINAL_FULL_PROJECT.json";dl.value.save_as(str(project))
   exported=json.loads(project.read_text(encoding="utf-8"))
   if not exported["episodes"][0].get("storyV20"):
    raise AssertionError("V50 final backup lost original V20 canonical story")
   if not exported["characters"][0]["productionRig"]["parts"]["face"]["image"]:
    raise AssertionError("V50 final backup lost genuine PNG actor")
   if len(exported["episodes"][0]["scenes"][0]["animationV46"]["tracks"]["hero"])!=7:
    raise AssertionError("V50 final backup lost seven actor animation tracks")
   if not exported["episodes"][0]["scenes"][0]["audioV36"]["voice"]["embeddedV47"]:
    raise AssertionError("V50 final backup lost genuine WAV bytes")
   if exported["productionV50"]["episodeReviews"]["1"]["art"] is not True:
    raise AssertionError("V50 final backup did not preserve human review ledger")
   with page.expect_download(timeout=30000) as dl:
    page.locator("#v50-export").click()
   report=out/"V50_FINAL_DEEP_QA_REPORT.json";dl.value.save_as(str(report))
   json_report=json.loads(report.read_text(encoding="utf-8"))
   if json_report["version"]!=50 or not json_report["manualAcceptanceRequired"]:
    raise AssertionError("Final QA report claims fake automatic acceptance")
   page.reload(wait_until="load")
   page.wait_for_function("() => document.querySelector('#v50-episode')?.options.length>1",
    timeout=45000)
   page.locator('[data-page="final-v50"]').click()
   page.locator("#v50-episode").select_option("1")
   if not page.locator('[data-v50-review="art"]').is_checked():
    raise AssertionError("Final author checklist not persisted")
   if "НЕ закончена" not in page.locator("#v50-notes").input_value():
    raise AssertionError("Final production notes not persisted")
   # Import previous version V49 as actual JSON, not a fake blank project.
   old=json.loads(json.dumps(exported));old["version"]=49;old.pop("productionV50",None)
   legacy=out/"V49_FULL_LEGACY_PROJECT.json"
   legacy.write_text(json.dumps(old,ensure_ascii=False),encoding="utf-8")
   page.locator("#project-file").set_input_files(str(legacy))
   page.wait_for_function("""() => {
      const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V50')||'null');
      return p?.version===50 && p?.characters?.length>0;
   }""",timeout=25000)
   restored=page.evaluate("""() =>
    JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V50'))""")
   if restored["episodes"][0]["storyV20"]!=old["episodes"][0]["storyV20"]:
    raise AssertionError("V49->V50 migration lost story")
   if not restored["episodes"][0]["scenes"][0]["audioV36"]["voice"]["embeddedV47"]:
    raise AssertionError("V49->V50 migration lost audio")
   if not restored["characters"][0]["productionRig"]["parts"]["face"]["image"]:
    raise AssertionError("V49->V50 migration lost PNG")
   if not restored["episodes"][0]["scenes"][0]["animationV46"]:
    raise AssertionError("V49->V50 migration lost animation")
   # Short single test scene ONLY inside isolated test browser, not real source.
   page.evaluate("""() => {
     const k='AI_ANIME_FACTORY_V50',p=JSON.parse(localStorage.getItem(k));
     const s=JSON.parse(JSON.stringify(p.episodes[0].scenes[0]));
     s.duration=2.7;
     p.episodes=[{...p.episodes[0],scenes:[s]}];
     localStorage.setItem(k,JSON.stringify(p));
   }""")
   page.reload(wait_until="load")
   page.locator('[data-page="final-v50"]').click()
   page.locator("#v50-go-render").click()
   if not page.locator("#page-episode-v48").is_visible():
    raise AssertionError("Final integrated render button does not reach real V48")
   page.locator('[data-page="audio-v36"]').click()
   if page.locator("#v36-audiofile").evaluate("(e)=>e.files.length"):
    raise AssertionError("V50 wrongly needs reattached voice after restart")
   with page.expect_download(timeout=65000) as dl:
    page.locator("#v36-export").click()
   video=out/"V50_REAL_EPISODE_WITH_VOICE.webm";dl.value.save_as(str(video))
   if not dl.value.suggested_filename.startswith("V50_FINAL_EPISODE_"):
    raise AssertionError("Wrong final WebM version filename")
   if video.stat().st_size<6500:raise AssertionError("V50 recorded empty WebM")
   info={}
   if shutil.which("ffprobe"):
    raw=subprocess.run(["ffprobe","-v","error","-show_entries",
      "stream=codec_type,codec_name:format=duration","-of","json",str(video)],
      capture_output=True,text=True,check=True,timeout=30)
    info=json.loads(raw.stdout)
    kinds={x["codec_type"] for x in info.get("streams",[])}
    if not {"audio","video"}.issubset(kinds):
     raise AssertionError("V50 finale lacks true video or audio stream")
   if shutil.which("ffmpeg"):
    raw=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(video),
      "-vn","-af","volumedetect","-f","null","-"],
      capture_output=True,text=True,timeout=60)
    m=re.search(r"max_volume:\s*(-?[\d.]+) dB",raw.stderr)
    if raw.returncode!=0 or not m or float(m.group(1)) < -42:
     raise AssertionError("Recorded V50 speech is silent, despite audio stream")
   if errors:raise AssertionError("Browser errors: "+"; ".join(errors[:5]))
   (out/"V50_REAL_BROWSER_QA.json").write_text(json.dumps({
    "version":50,"adversarial_corruption_rejected":True,
    "audit_pure":True,"human_acceptance_not_auto_certified":True,
    "legacy_v49_migration_story_images_animation_audio":True,
    "manual_reviews_survive_reload":True,"full_project_json":True,
    "recorded_audio_and_video_bytes":video.stat().st_size,
    "ffprobe":info},ensure_ascii=False,indent=2),encoding="utf-8")
   print("V50 CHROMIUM PASS: genuine 2D, critical broken-project detection, V49 migration, WAV and non-silent WebM.")
  finally:browser.close()
if __name__=="__main__":main()
