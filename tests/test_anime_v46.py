"""Regression for V46 actual cutout keyframe hooks, lineage and runnable browser JS."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory/v46/build_animation_v46.py"
sp=importlib.util.spec_from_file_location("anime_v46_test",BUILDER)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class V46Regression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
  cls.old=m.previous().build()
  cls.html=m.build()
 def test_real_v16_sample_extension(self):
  for fragment in ("const v46OriginalPose16=pose16Sample;",
    "pose16Sample=function(s,role,part,sec)",
    "const extra=v46LayerMotion(s,role,part,sec);",
    "function v46SaveKey(","function v46ApplyAction(",
    "function v46SaveClip(","function v46ApplyClip(",
    "function v46Render(","v46Actions={",
    "v46Parts=['legs','cape','torso','arms','face','hair','weapon']"):
   self.assertIn(fragment,self.html,fragment)
  self.assertNotIn("const v46OriginalPose16=pose16Sample;",self.old)
 def test_old_versions_untouched(self):
  for x in ("function drawProductionPerson(","function v45DrawBackground(",
    "function v44Pose(","function v43Shot(","function v42Layers(",
    "function v41Cape(","function v40FaceInk(","function v39Move(",
    "function v37Paint(","function v36Schedule(","function v35Plan(",
    "function v25Contact(","function pose16Sample(",
    "AI_ANIME_FACTORY_V46","AI_ANIME_FACTORY_V45",
    'id="page-animation-v46"',"V46_ANIMATION_ENGINE_EPISODE_"):
   self.assertIn(x,self.html,x)
  self.assertEqual(self.original,hashlib.sha256(SOURCE.read_bytes()).hexdigest())
 def test_deterministic_and_safe(self):
  self.assertEqual(self.html,m.build())
  with self.assertRaises(ValueError):m.patch(self.html,"/* duplicate */")
 @unittest.skipUnless(shutil.which("node"),"node not installed")
 def test_node_browser_js_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"v46.js";p.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(p)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,r.returncode,r.stderr)
if __name__=="__main__":unittest.main()
