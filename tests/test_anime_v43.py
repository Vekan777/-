"""V43 additive scene-director regression and true V25-constrained camera transforms."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory/v43/build_director_v43.py"
spec=importlib.util.spec_from_file_location("v43testbuilder",BUILDER)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class V43Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.digest=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.old=module.previous().build()
  cls.html=module.build()
 def test_historical_functions_and_pages_unchanged(self):
  for term in ("function drawScene(","function v23TorsoForm(","function v24Dynamics(",
   "function v25Contact(","function v29Beat(","function v30Audit(",
   "function v33Act(","function v34Review(","function v35Plan(",
   "function v36Schedule(","function v37Paint(","function v38Frame(",
   "function v39Move(","function v40FaceInk(","function v41Cape(",
   "function v42Layers(","function v43DirectorState(","function v43Shot("):
   self.assertIn(term,self.html)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
   "page-cinematic-v38","page-performance-v39","page-character-art-v40",
   "page-silhouette-v41","page-stage-v42","page-action-v43"):
   self.assertIn('id="'+page+'"',self.html)
  self.assertEqual(self.digest,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_real_v25_camera_renderer_and_audio(self):
  for tok in ("const v43BaseFrame=v38Frame;","const e=v25Contact(s,local);",
    "e.outcome==='hit'","e.outcome==='block'","e.outcome==='dodge'",
    "v38Frame=function(canvas,episode,second)","ctx.rotate(options.angle);",
    "v37Paint(canvas,episode,second);","new MediaRecorder(",
    "V43_ACTION_DIRECTOR_EPISODE_","AI_ANIME_FACTORY_V42","AI_ANIME_FACTORY_V43"):
   self.assertIn(tok,self.html)
  self.assertIn("reducedMotion",self.html)
  self.assertNotIn('id="page-action-v43"',self.old)
 def test_idempotency_protection(self):
  self.assertEqual(self.html,module.build())
  with self.assertRaises(ValueError):module.patch(self.html,"/* duplicate */")
 @unittest.skipUnless(shutil.which("node"),"Node not available")
 def test_browser_js_syntax_node(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/"v43.js";p.write_text(js,encoding="utf-8")
   s=subprocess.run(["node","--check",str(p)],capture_output=True,text=True,timeout=60)
   self.assertEqual(0,s.returncode,s.stderr)
if __name__=="__main__":unittest.main()
