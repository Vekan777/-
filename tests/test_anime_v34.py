"""V34 storyboard shot camera and continuity regression; preserve V19–V33."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIG=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v34"/"build_storyboard_v34.py"
spec=importlib.util.spec_from_file_location("v34_builder",BUILDER)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V34Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=ORIG.read_bytes()
  cls.hash=hashlib.sha256(cls.old).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(ORIG.read_bytes()).hexdigest()==cls.hash
 def test_prior_history_and_ui(self):
  for page in ("story-v20","visual-v21","acting-v22","character-v23",
     "animation-v24","combat-v25","cinematic-v26","world-v27",
     "interaction-v28","polish-v29","review-v30","visual-v31",
     "keyframe-v32","acting-v33","storyboard-v34"):
   self.assertIn('id="page-'+page+'"',self.html)
  for module in ("function v20CanonLines(","function v25PairPose(",
    "function v26Camera(","function v30Audit(","function v31Metrics(",
    "function v32Pose(","function v33Face("):
   self.assertIn(module,self.html)
 def test_real_camera_in_actual_draw_scene(self):
  self.assertIn("camera26=v26Camera(s,sec),camera34=v34Camera(s,sec)",self.html)
  self.assertIn("camera14.zoom*camera26.zoom*camera34.zoom",self.html)
  self.assertIn("camera26.dx+camera34.dx",self.html)
  self.assertIn("camera26.dy+camera34.dy",self.html)
  js=(ROOT/"anime-factory"/"v34"/"storyboard_v34.js").read_text(encoding="utf-8")
  for key in ("function v34Camera(","function v34Review(",
              "function v34ShotBlend(","function v34StoryboardText(",
              "function v34Sheet(","V34_TIMES=[.12,.5,.88]"):
   self.assertIn(key,js)
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)
 def test_persistence_and_backup(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V34';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:34,",self.html)
  self.assertIn("if(Number(migrated.version)<34)migrated.version=34;",self.html)
  for ver in [19]+list(range(21,34)):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(ver)+"')",self.html)
  for elem in ("v34-scene","v34-focus","v34-axis","v34-enabled",
    "v34-strength","v34-tracking","v34-smoothness","v34-beat",
    "v34-shot","v34-before","v34-after","v34-position",
    "v34-preset","v34-save","v34-audit","v34-sheet","v34-plan"):
   self.assertIn('id="'+elem+'"',self.html)
  self.assertIn("V34_SCENE_SHOTS.json",self.html)
  self.assertEqual(ORIG.read_bytes(),self.old)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
 def test_duplicate_and_reproducible(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_integrated_js_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v34_js_") as t:
   f=Path(t)/"integrated.js";f.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(f)],text=True,capture_output=True,timeout=60)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=="__main__":unittest.main()
