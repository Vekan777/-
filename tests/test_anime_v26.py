"""AI Anime Factory V26 cinematography, preservation and syntax regressions."""
from __future__ import annotations
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
SRC=ROOT/"anime-factory"/"v26"/"build_cinematic_v26.py"
spec=importlib.util.spec_from_file_location("v26_builder",SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class AnimeV26Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes()
  cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=mod.build()

 @classmethod
 def tearDownClass(cls):
  assert cls.sha==hashlib.sha256(V19.read_bytes()).hexdigest()

 def test_story_and_every_prior_editor(self):
  for key in ('id="page-story-v20"','id="page-visual-v21"',
              'id="page-acting-v22"','id="page-character-v23"',
              'id="page-animation-v24"','id="page-combat-v25"',
              'id="page-cinematic-v26"','function impact19State(',
              'function combat17State(','function combat18Sim(',
              'function v20CanonLines(','function v21AtmosphereBack(',
              'function v22Mood(','function v23HeadScale(',
              'function v24Dynamics(','function v25PairPose(',
              'function exportEpisode()'):
   with self.subTest(key=key):self.assertIn(key,self.html)

 def test_camera_transform_in_real_canvas(self):
  for key in ('function v26Camera(','function v26FinishFrame(',
              'camera26=v26Camera(s,sec)','camera14.zoom*camera26.zoom',
              'cam.x+camera14.dx+camera26.dx',
              'cam.y+camera14.dy+camera26.dy',
              'cin14Post(g,w,h,s,sec);v26FinishFrame(g,w,h,s,sec);'):
   with self.subTest(key=key):self.assertIn(key,self.html)

 def test_no_new_hit_or_replaced_art(self):
  self.assertIn('const contact=v25Contact(s,t);',self.html)
  self.assertIn('if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;',self.html)
  self.assertIn("if(img?.complete&&img.naturalWidth)",self.html)
  self.assertEqual(V19.read_bytes(),self.original)

 def test_v26_controls_and_export(self):
  for key in ("v26-scene","v26-enabled","v26-style","v26-intensity",
              "v26-tracking","v26-impactFocus","v26-letterbox","v26-transitions",
              "v26-before","v26-after","v26-position","v26-save","v26-sheet",
              "v26-preset","v26-plan"):
   self.assertIn('id="'+key+'"',self.html)
  self.assertIn("V26_SHOT_LIST_RU.txt",self.html)
  self.assertIn("V26_CAMERA_SETTINGS.json",self.html)

 def test_legacy_project_fallback(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V26';",self.html)
  for version in [25,24,23,22,21,19]:
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(version)+"')",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:26,",self.html)
  self.assertIn("if(Number(migrated.version)<26)migrated.version=26;",self.html)

 def test_idempotence(self):
  self.assertEqual(self.html,mod.build())
  with self.assertRaises(ValueError):mod.patch(self.html,"//duplicate")

 @unittest.skipUnless(shutil.which("node"),"Node is not available")
 def test_node_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v26_js_") as tmp:
   f=Path(tmp)/"integrated.js";f.write_text(js,encoding="utf-8")
   check=subprocess.run(["node","--check",str(f)],
                       capture_output=True,text=True,timeout=50)
   self.assertEqual(check.returncode,0,check.stderr)

if __name__=="__main__":unittest.main()
