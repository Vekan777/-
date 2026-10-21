"""V42 non-destructive regression and real Canvas compositing hooks."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SCRIPT=ROOT/"anime-factory/v42/build_stage_v42.py"
spec=importlib.util.spec_from_file_location("v42testbuilder",SCRIPT)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V42Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.old=builder.previous().build()
  cls.html=builder.build()
 def test_previous_versions_preserved(self):
  for term in ("function drawScene(","function v23TorsoForm(","function v24Dynamics(",
    "function v25Contact(","function v29Beat(","function v30Audit(",
    "function v33Act(","function v34Review(","function v35Plan(",
    "function v36Schedule(","function v37Paint(","function v38Frame(",
    "function v39Move(","function v40FaceInk(","function v41Cape(",
    "function v42Layers(","function v42Manifest("):
   self.assertIn(term,self.html,term)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
    "page-cinematic-v38","page-performance-v39","page-character-art-v40",
    "page-silhouette-v41","page-stage-v42"):
   self.assertIn('id="'+page+'"',self.html,page)
  self.assertEqual(self.original,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_true_canvas_and_canonical_battle(self):
  for s in ("const v42Before=v38Frame;","v38Frame=function(canvas,episode,sec)",
    "v42Layers(canvas,result);","v37Paint(canvas,episode,sec);",
    "beat.outcome==='hit'||beat.outcome==='block'","new MediaRecorder(",
    "V42_STAGE_DEPTH_EPISODE_","AI_ANIME_FACTORY_V41","AI_ANIME_FACTORY_V42"):
   self.assertIn(s,self.html)
  self.assertIn("function v42Noise(",self.html)
  self.assertIn("createRadialGradient(",self.html)
  self.assertNotIn('id="page-stage-v42"',self.old)
 def test_build_reproducible_and_duplicate_refused(self):
  self.assertEqual(self.html,builder.build())
  with self.assertRaises(ValueError):builder.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
 def test_javascript_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"v42.js";file.write_text(js,encoding="utf-8")
   outcome=subprocess.run(["node","--check",str(file)],text=True,
    capture_output=True,timeout=60)
   self.assertEqual(0,outcome.returncode,outcome.stderr)
if __name__=="__main__":unittest.main()
