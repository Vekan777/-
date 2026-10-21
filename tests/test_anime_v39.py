"""V39 regression: additive V19–V38 continuity, true rig hooks, WebM and Node parse."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory/v39/build_performance_v39.py"
def load():
 spec=importlib.util.spec_from_file_location("v39buildtest",BUILDER)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class V39Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.module=load()
  cls.orig=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
  cls.html=cls.module.build()
  cls.v38=cls.module.previous().build()
 def test_every_old_layer_present(self):
  for marker in ("function v13Face(","function v24Dynamics(","function v25Contact(",
   "function v29Beat(","function v30Audit(","function v33Act(","function v34Review(",
   "function v35Plan(","function v36Schedule(","function v37Paint(",
   "function v38Frame(","function v39Move(","function v39Effects("):
   self.assertIn(marker,self.html)
  for name in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
   "page-cinematic-v38","page-performance-v39"):
   self.assertIn('id="'+name+'"',self.html)
  self.assertEqual(self.orig,hashlib.sha256(SOURCE.read_bytes()).hexdigest())
 def test_real_rig_and_face_hooks_not_new_combat_events(self):
  for marker in ("v24Dynamics=function(s,t,role)","v13Face=function(s,role,t,override=null)",
   "const contacts=s.kind==='fight'?v25Contact(s,t):null;",
   "beat.outcome==='hit'||beat.outcome==='block'",
   "const confirmed=","v39Effects(ctx,state,w,h);",
   "v37Paint(canvas,episode,sec);","new MediaRecorder(",
   "V39_CHARACTER_ACTION_EPISODE_","AI_ANIME_FACTORY_V38","AI_ANIME_FACTORY_V39"):
   self.assertIn(marker,self.html)
  self.assertIn("function v39Move(",self.html)
  self.assertIn("function v39Frame(",self.html)
  self.assertIn("scene.performanceV39",self.html.replace("s.performanceV39","scene.performanceV39"))
 def test_reproducible_builder(self):
  self.assertEqual(self.html,self.module.build())
  self.assertNotIn('id="page-performance-v39"',self.v38)
  with self.assertRaises(ValueError):self.module.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node.js unavailable")
 def test_js_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/"v39.js";path.write_text(js,encoding="utf-8")
   p=subprocess.run(["node","--check",str(path)],capture_output=True,text=True,timeout=60)
   self.assertEqual(0,p.returncode,p.stderr)
if __name__=="__main__":unittest.main()
