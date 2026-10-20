"""V35 episode assembly: timeline, source preservation and Node syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v35"/"build_assembly_v35.py"
spec=importlib.util.spec_from_file_location("v35builder",BUILDER)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V35Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=V19.read_bytes();cls.sha=hashlib.sha256(cls.source).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.sha
 def test_history_and_ui(self):
  for page in ("story-v20","visual-v21","acting-v22","character-v23",
    "animation-v24","combat-v25","cinematic-v26","world-v27",
    "interaction-v28","polish-v29","review-v30",
    "visual-v31","keyframe-v32","acting-v33","storyboard-v34",
    "assembly-v35"):
   self.assertIn('id="page-'+page+'"',self.html)
  for s in ("function v30Audit(","function v33Act(","function v34Camera(",
   "function v25PairPose(","function drawScene("):
   self.assertIn(s,self.html)
 def test_scene_assembly_canvas_and_timeline(self):
  js=(ROOT/"anime-factory"/"v35"/"assembly_v35.js").read_text(encoding="utf-8")
  for s in ("function v35Plan(","function v35Find(","function v35Frame(",
    "function v35Audit(","function v35Manifest(","function v35Sheet(",
    "v35Duration(s)/3","g.globalAlpha=clamp(inTime/overlap,0,1)",
    "requestAnimationFrame(v35Clock)","drawScene(v35Scratch(w,h),prior.scene",
    "drawScene(v35Scratch(w,h),row.scene"):
   self.assertIn(s,js)
  for illegal in ("Math.random(","fetch(","P.episodes.splice(","s.duration="):
   self.assertNotIn(illegal,js)
 def test_storage_migration_and_exports(self):
  for s in ("const storageKey='AI_ANIME_FACTORY_V35';",
    "P={format:'AIAnimeFactoryProject',version:35,",
    "if(Number(migrated.version)<35)migrated.version=35;",
    "V35_EPISODE_ASSEMBLY.json","V35_EPISODE_ASSEMBLY_RU.txt"):
   self.assertIn(s,self.html)
  for v in [19]+list(range(21,35)):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(v)+"')",self.html)
  for elem in ("v35-episode","v35-scene","v35-enabled","v35-transition",
     "v35-preview","v35-progress","v35-play","v35-start",
     "v35-save","v35-audit","v35-report","v35-json","v35-sheet"):
   self.assertIn('id="'+elem+'"',self.html)
  self.assertEqual(self.source,V19.read_bytes())
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
 def test_builder_reproducible(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_js_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/"v35.js";f.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(f)],text=True,capture_output=True,timeout=60)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=="__main__":unittest.main()
