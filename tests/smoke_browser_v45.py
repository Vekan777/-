#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chromium evidence V45: actual two actors/layers and two worlds, portable images and WebM sound."""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,struct,subprocess,wave,zlib
from pathlib import Path
from playwright.sync_api import sync_playwright
def make_png(target,color):
 width,height=64,36
 raw=b''.join(b'\x00'+bytes(color)*(width) for _ in range(height))
 def chunk(tag,payload):
  return struct.pack('>I',len(payload))+tag+payload+struct.pack('>I',zlib.crc32(tag+payload)&0xffffffff)
 target.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',
  struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
  chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
def make_audio(target):
 rate=16000
 with wave.open(str(target),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes(b''.join(struct.pack('<h',round(8500*math.sin(2*math.pi*440*i/rate)))
    for i in range(rate*3)))
def checksum(p):
 b=p.read_bytes()
 if b[:8]!=b'\x89PNG\r\n\x1a\n' or len(b)<5000:
  raise AssertionError('No genuine PNG: '+str(p))
 return hashlib.sha256(b).hexdigest()
def main():
 cli=argparse.ArgumentParser()
 cli.add_argument('--html',required=True)
 cli.add_argument('--out',default='dist/V45_ART_BROWSER')
 opts=cli.parse_args()
 out=Path(opts.out).resolve();out.mkdir(parents=True,exist_ok=True)
 red=out/'V45_BG_FOREST.png';blue=out/'V45_BG_CASTLE.png'
 make_png(red,(220,65,75));make_png(blue,(50,80,230))
 wav=out/'V45_VOICE.wav';make_audio(wav)
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=[
   '--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
   '--autoplay-policy=no-user-gesture-required'])
  page=browser.new_page(viewport={'width':1480,'height':1100},accept_downloads=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  try:
   page.goto(Path(opts.html).resolve().as_uri(),wait_until='load',timeout=60000)
   page.wait_for_function("() => document.querySelector('#v45-character')?.options.length>=2",timeout=45000)
   page.locator('[data-page="art-assets-v45"]').click()
   page.locator('#v45-character').select_option('0')
   page.locator('#v45-layer').select_option('arms')
   page.locator('#v45-save').click()
   prior=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V45'))""")
   if prior['version']!=45 or not prior['episodes'][0].get('storyV20'):
    raise AssertionError('V45 did not preserve story')
   before=out/'V45_ORIGINAL_STAGE.png'
   page.locator('#v45-preview').screenshot(path=str(before))
   original=checksum(before)
   page.locator('#v45-make').click()
   page.wait_for_function("""() => document.querySelector('#v45-status')?.textContent.includes('7/7')""",
     timeout=25000)
   # Default procedural character becomes a 7-PNG composite, not an empty menu.
   one=page.evaluate("""() => {
    const p=JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V45'));
    return p.characters[0].productionRig.parts;
   }""")
   if sum(x['image'].startswith('data:image/png;base64,') for x in one.values())!=7:
    raise AssertionError('7 generated cutout layers are absent')
   page.locator('#v45-layer').select_option('arms')
   page.locator('#v45-pivot-x').fill('22')
   page.locator('#v45-pivot-y').fill('-70')
   page.locator('#v45-pivot-angle').fill('18')
   page.locator('#v45-save').click()
   stage=out/'V45_REAL_LAYERED_ACTOR.png'
   page.locator('#v45-preview').screenshot(path=str(stage))
   if checksum(stage)==original:
    raise AssertionError('Generated real PNG rig did not change image')
   page.locator('#v45-bg-file').set_input_files(str(red))
   page.wait_for_function("""() => document.querySelector('#v45-background-status')?.textContent.includes('V45_BG_FOREST')""",timeout=15000)
   page.locator('#v45-background-rights').fill('Original studio art test')
   page.locator('#v45-bg-save').click()
   page.wait_for_timeout(250)
   forest=out/'V45_FOREST_STAGE.png'
   page.locator('#v45-preview').screenshot(path=str(forest))
   if checksum(forest)==checksum(stage):
    raise AssertionError('Imported real PNG background did not paint frame')
   page.locator('#v45-scene').select_option('0:1')
   page.locator('#v45-bg-file').set_input_files(str(blue))
   page.wait_for_function("""() => document.querySelector('#v45-background-status')?.textContent.includes('V45_BG_CASTLE')""",timeout=15000)
   page.locator('#v45-background-rights').fill('Original castle test art')
   page.locator('#v45-bg-save').click()
   page.wait_for_timeout(200)
   castle=out/'V45_CASTLE_STAGE.png'
   page.locator('#v45-preview').screenshot(path=str(castle))
   if checksum(castle)==checksum(forest):
    raise AssertionError('Two distinct imported environments rendered identical')
   page.locator('#v45-character').select_option('1')
   page.locator('#v45-layer').select_option('face')
   page.locator('#v45-file').set_input_files(str(blue))
   page.wait_for_function("""() => document.querySelector('#v45-status')?.textContent.includes('1/7')""",timeout=15000)
   page.locator('#v45-rights').fill('Original second character')
   page.locator('#v45-save').click()
   with page.expect_download(timeout=30000) as job:
    page.locator('#v45-project').click()
   project=out/'V45_PORTABLE_2D_PROJECT.json'
   job.value.save_as(str(project))
   exported=json.loads(project.read_text(encoding='utf-8'))
   if not exported['episodes'][0]['scenes'][0]['bgV45']['image'].startswith('data:image/png;base64,'):
    raise AssertionError('First scene background not portable')
   if not exported['episodes'][0]['scenes'][1]['bgV45']['image'].startswith('data:image/png;base64,'):
    raise AssertionError('Second scene background not portable')
   if not exported['characters'][1]['productionRig']['parts']['face']['image']:
    raise AssertionError('Second character layer not portable')
   if exported['characters'][0]['artV45']['pivots']['arms']['x']!=22:
    raise AssertionError('Articulated pivot not stored')
   if exported['episodes'][0]['storyV20']!=prior['episodes'][0]['storyV20']:
    raise AssertionError('Canonical story overwritten by art studio')
   with page.expect_download(timeout=30000) as job:
    page.locator('#v45-plan').click()
   engine=out/'V45_ENGINE_PRODUCTION_PLAN.json';job.value.save_as(str(engine))
   plan=json.loads(engine.read_text(encoding='utf-8'))
   if plan['version']!='45.0.0' or plan['audit']['characterCount']<2:
    raise AssertionError('Production engine snapshot invalid')
   with page.expect_download(timeout=30000) as job:
    page.locator('#v45-frame').click()
   sheet=out/'V45_FOUR_REAL_FRAMES.png'
   job.value.save_as(str(sheet));checksum(sheet)
   # Persistence after closing/reloading and no reupload: PNG data must survive.
   page.reload(wait_until='load')
   page.wait_for_function("() => document.querySelector('#v45-character')?.options.length>=2",timeout=45000)
   restored=page.evaluate("""() => JSON.parse(localStorage.getItem('AI_ANIME_FACTORY_V45'))""")
   if not restored['characters'][0]['productionRig']['parts']['arms']['image']:
    raise AssertionError('Reload dropped generated actor images')
   if not restored['episodes'][0]['scenes'][1]['bgV45']['image']:
    raise AssertionError('Reload dropped second imported scene background')
   # Browser-only short recording: never alter repository or source episode data.
   page.evaluate("""() => {
    const key='AI_ANIME_FACTORY_V45',p=JSON.parse(localStorage.getItem(key));
    const a=p.episodes[0].scenes;
    p.episodes[0].scenes=[JSON.parse(JSON.stringify(a[0])),JSON.parse(JSON.stringify(a[1]))];
    p.episodes[0].scenes.forEach(s=>s.duration=1.3);
    localStorage.setItem(key,JSON.stringify(p));
   }""")
   page.reload(wait_until='load')
   page.locator('[data-page="audio-v36"]').click()
   page.locator('#v36-slot').select_option('voice')
   page.locator('#v36-audiofile').set_input_files(str(wav))
   page.wait_for_function("""() => document.querySelector('#v36-asset').textContent.includes('аудио подключено')""",
    timeout=20000)
   with page.expect_download(timeout=60000) as job:
    page.locator('#v36-export').click()
   video=out/'V45_ART_ENGINE_WITH_AUDIO.webm';job.value.save_as(str(video))
   if not job.value.suggested_filename.startswith('V45_ART_ENGINE_EPISODE_'):
    raise AssertionError('Wrong WebM version')
   if video.stat().st_size<6000:raise AssertionError('WebM is empty')
   probe={}
   if shutil.which('ffprobe'):
    p=subprocess.run(['ffprobe','-v','error','-show_entries',
      'format=duration:stream=codec_type,codec_name','-of','json',str(video)],
      capture_output=True,text=True,check=True,timeout=30)
    probe=json.loads(p.stdout)
    kinds={stream['codec_type'] for stream in probe.get('streams',[])}
    if not {'video','audio'}.issubset(kinds):
     raise AssertionError('WebM missing audio+video '+str(kinds))
   if errors:raise AssertionError('Browser errors: '+'; '.join(errors[:5]))
   (out/'V45_BROWSER_QA.json').write_text(json.dumps({
    'version':45,'generated_character_7_png_layers':True,
    'second_character_import':True,'two_scenes_custom_backgrounds':True,
    'pivot_roundtrip':True,'story_unchanged':True,'project_persists_after_reload':True,
    'video_bytes':video.stat().st_size,'ffprobe':probe,'errors':errors
   },ensure_ascii=False,indent=2),encoding='utf-8')
   print('V45 CHROMIUM PASS: 7 cutout PNGs, 2 characters, 2 custom worlds, portable JSON and audio WebM')
  finally:browser.close()
if __name__=='__main__':main()
