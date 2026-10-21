"""V38 regressions: exact V19 source, preserved V35/36/37 and real Canvas JS."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SCRIPT=ROOT/"anime-factory/v38/build_cinematic_v38.py"
spec=importlib.util.spec_from_file_location("v38buildtests",SCRIPT)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class V38Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original_hash=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.previous=mod.previous().build()
  cls.html=mod.build()
 def test_preserves_legacy_visual_and_sound(self):
  for feature in ("function drawScene(","function v30Audit(",
   "function v33Act(","function v34Review(","function v35Plan(",
   "function v35Frame(","function v36Schedule(","function v37Paint(",
   "function v37SubtitleFile(","function v38Frame(","function v38Manifest("):
   self.assertIn(feature,self.html)
  for page in ("page-assembly-v35","page-audio-v36",
    "page-subtitles-v37","page-cinematic-v38"):
   self.assertIn('id="'+page+'"',self.html)
  self.assertEqual(self.original_hash,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_real_captured_camera_graded_video(self):
  self.assertIn("const state=v38Frame($('v36-preview'),ep,v36At);",self.html)
  self.assertIn("const current=v38Frame($('v37-preview'),ep,v37At);",self.html)
  self.assertIn("ctx.filter='brightness(",self.html)
  self.assertIn("ctx.drawImage(raw,",self.html)
  self.assertIn("v37Paint(canvas,episode,sec);",self.html)
  self.assertIn("captureStream(",self.html)
  self.assertIn("new MediaRecorder(",self.html)
  self.assertIn("V38_CINEMATIC_EPISODE_",self.html)
  self.assertIn("cameraV38",self.html)
  self.assertIn("AI_ANIME_FACTORY_V37",self.html)
  self.assertIn("AI_ANIME_FACTORY_V38",self.html)
 def test_builder_stable_and_additive(self):
  self.assertEqual(mod.build(),self.html)
  self.assertIn("function v37Paint(",self.previous)
  self.assertNotIn('id="page-cinematic-v38"',self.previous)
  with self.assertRaises(ValueError):mod.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node missing")
 def test_javascript_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  body=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"v38.js";src.write_text(body,encoding="utf-8")
   outcome=subprocess.run(["node","--check",str(src)],
                          capture_output=True,text=True,timeout=60)
   self.assertEqual(outcome.returncode,0,outcome.stderr)
if __name__=="__main__":unittest.main()
