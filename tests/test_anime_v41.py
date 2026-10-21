"""V41: strict source-preserving builder, actual rig draw hooks and JavaScript syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SCRIPT=ROOT/"anime-factory/v41/build_silhouette_v41.py"
spec=importlib.util.spec_from_file_location("v41testbuilder",SCRIPT)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V41Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original_sha=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.before=builder.previous().build()
  cls.html=builder.build()
 def test_preserved_every_previous_stage(self):
  for token in ("function drawScene(","function v23TorsoForm(",
    "function v23LegForm(","function v23FaceForm(","function v24Dynamics(",
    "function v25Contact(","function v29Beat(","function v30Audit(",
    "function v33Act(","function v34Review(","function v35Plan(",
    "function v36Schedule(","function v37Paint(","function v38Frame(",
    "function v39Move(","function v40FaceInk(","function v41Cape(",
    "function v41Armor(","function v41HairShape(","function v41Boots("):
   self.assertIn(token,self.html,token)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
    "page-cinematic-v38","page-performance-v39","page-character-art-v40",
    "page-silhouette-v41"):
   self.assertIn('id="'+page+'"',self.html,page)
  self.assertEqual(self.original_sha,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_true_2d_model_integration(self):
  for term in ("v23TorsoForm=function(","v23HairForm=function(",
    "v23LegForm=function(","v41Cape(g,c,s,role,t,cloth)",
    "v41Armor(g,c,s,role,t,cloth)","v41HairShape(g,c,s,role,t,wind)",
    "v41Boots(g,c,s,role,t,steps)","V41_SILHOUETTE_EPISODE_",
    "new MediaRecorder(","AI_ANIME_FACTORY_V41","AI_ANIME_FACTORY_V40"):
   self.assertIn(term,self.html,term)
  self.assertIn('id="v41-before"',self.html)
  self.assertIn('id="v41-after"',self.html)
  self.assertNotIn('id="page-silhouette-v41"',self.before)
 def test_deterministic_builder(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node missing")
 def test_node_js_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/"v41.js";f.write_text(js,encoding="utf-8")
   out=subprocess.run(["node","--check",str(f)],capture_output=True,text=True,timeout=60)
   self.assertEqual(out.returncode,0,out.stderr)
if __name__=="__main__":unittest.main()
