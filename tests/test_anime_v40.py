"""V40 regression: original V19 and V20–V39 + actual vector character art hooks."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SCRIPT=ROOT/"anime-factory/v40/build_art_v40.py"
spec=importlib.util.spec_from_file_location("v40buildertests",SCRIPT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class V40Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.orig=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.html=module.build()
  cls.before=module.previous().build()
 def test_preserves_history(self):
  for token in ("function drawScene(","function v23FaceForm(",
   "function v23HairForm(","function v23CostumeForm(","function v24Dynamics(",
   "function v25Contact(","function v29Beat(","function v30Audit(",
   "function v33Act(","function v34Review(","function v35Plan(",
   "function v36Schedule(","function v37Paint(","function v38Frame(",
   "function v39Move(","function v40FaceInk(","function v40HairInk(",
   "function v40CostumeInk("):
   self.assertIn(token,self.html)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
   "page-cinematic-v38","page-performance-v39","page-character-art-v40"):
   self.assertIn('id="'+page+'"',self.html)
  self.assertEqual(self.orig,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_true_vector_art_not_overlay(self):
  for marker in ("v23FaceForm=function(","v23HairForm=function(",
   "v23CostumeForm=function(","v40FaceBase(g,c,s,role,t);",
   "v40FaceInk(g,c,s,role,t);","v40HairInk(g,c,s,role,t,wind);",
   "v40CostumeInk(g,c,s,role,t,cloth);","AI_ANIME_FACTORY_V40",
   "AI_ANIME_FACTORY_V39","V40_CHARACTER_ART_EPISODE_",
   "new MediaRecorder("):
   self.assertIn(marker,self.html)
  self.assertNotIn('id="page-character-art-v40"',self.before)
  self.assertIn('id="v40-before"',self.html)
  self.assertIn('id="v40-after"',self.html)
 def test_stable_builder(self):
  self.assertEqual(self.html,module.build())
  with self.assertRaises(ValueError):module.patch(self.html,"// already")
 @unittest.skipUnless(shutil.which("node"),"Node not installed")
 def test_node_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  code=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/"v40.js";path.write_text(code,encoding="utf-8")
   out=subprocess.run(["node","--check",str(path)],capture_output=True,text=True,timeout=60)
   self.assertEqual(out.returncode,0,out.stderr)
if __name__=="__main__":unittest.main()
