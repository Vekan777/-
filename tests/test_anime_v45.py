"""V45 historical preservation, true V15 drawn cutout integration and JS parsing."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILD=ROOT/"anime-factory/v45/build_art_engine_v45.py"
spec=importlib.util.spec_from_file_location("v45_test_builder",BUILD)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V45Regressions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.hash=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.old=builder.previous().build();cls.new=builder.build()
 def test_true_native_cutout_and_background_injection(self):
  for snippet in ("function v45DrawBackground(","function v45GenerateLayers(",
    "const AnimeProductionEngineV45=",
    "if(!v45DrawBackground(g,w,h,s,sec))drawBG(",
    "const pv45=v45PivotFor(c,name);",
    "function drawProductionPerson(","function drawScene(",
    'id="v45-scene"','id="page-art-assets-v45"'):
   self.assertIn(snippet,self.new,snippet)
  self.assertNotIn("function v45DrawBackground(",self.old)
 def test_full_previous_modules_and_project_migration(self):
  for term in ("function v24Dynamics(","function v25Contact(",
    "function v35Plan(","function v36Schedule(",
    "function v37Paint(","function v38Frame(",
    "function v39Move(","function v40FaceInk(",
    "function v41Cape(","function v42Layers(",
    "function v43Shot(","function v44Pose(",
    "AI_ANIME_FACTORY_V44","AI_ANIME_FACTORY_V45",
    "V45_ART_ENGINE_EPISODE_"):
   self.assertIn(term,self.new,term)
  self.assertEqual(hashlib.sha256(V19.read_bytes()).hexdigest(),self.hash)
 def test_determinism_and_repatch_protection(self):
  self.assertEqual(builder.build(),self.new)
  with self.assertRaises(ValueError):
   builder.patch(self.new,"// engine","// studio")
 @unittest.skipUnless(shutil.which("node"),"Node.js not available")
 def test_browser_javascript_parser(self):
  self.assertEqual(self.new.count("<script>"),1)
  js=self.new.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as temp:
   target=Path(temp)/"v45.js";target.write_text(js,encoding="utf-8")
   run=subprocess.run(["node","--check",str(target)],
    capture_output=True,text=True,timeout=60)
   self.assertEqual(run.returncode,0,run.stderr)
if __name__=="__main__":unittest.main()
