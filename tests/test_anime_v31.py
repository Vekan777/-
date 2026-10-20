"""V31 visual production QA, non-destructive grading and V19–V30 integrity."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v31"/"build_visual_v31.py"
spec=importlib.util.spec_from_file_location("visual_v31_builder",BUILDER)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class V31Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes()
  cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert cls.sha==hashlib.sha256(V19.read_bytes()).hexdigest()

 def test_all_prior_studio_tabs_and_story(self):
  for tab in ("story-v20","visual-v21","acting-v22","character-v23",
              "animation-v24","combat-v25","cinematic-v26",
              "world-v27","interaction-v28","polish-v29","review-v30","visual-v31"):
   with self.subTest(tab=tab):self.assertIn('id="page-'+tab+'"',self.html)
  for func in ("function v20CanonLines(","function v21AtmosphereBack(",
               "function v22Mood(","function v23HeadScale(",
               "function v24Dynamics(","function v25PairPose(",
               "function v26Camera(","function v27Back(",
               "function v28Ground(","function v29Beat(",
               "function v30Audit("):
   self.assertIn(func,self.html)

 def test_pixel_data_and_final_draw_scene(self):
  js=(ROOT/"anime-factory"/"v31"/"visual_v31.js").read_text(encoding="utf-8")
  for key in ("function v31Grade(","function v31Metrics(",
              "getImageData(0,0,w,h)","putImageData(image,0,0)",
              "function v31Assess(","function v31ReviewProject(",
              "source.slice(0,24)"):
   self.assertIn(key,js)
  self.assertIn("cin14Post(g,w,h,s,sec);v26FinishFrame(g,w,h,s,sec);v31Grade(g,w,h,s);",self.html)
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)

 def test_storage_and_ui(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V31';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:31,",self.html)
  self.assertIn("if(Number(migrated.version)<31)migrated.version=31;",self.html)
  for v in (30,29,28,27,26,25,24,23,22,21,19):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(v)+"')",self.html)
  for elem in ("v31-scene","v31-position","v31-enabled","v31-exposure",
               "v31-contrast","v31-saturation","v31-vignette",
               "v31-before","v31-after","v31-analyze","v31-all",
               "v31-save","v31-preset","v31-report","v31-json","v31-sheet"):
   self.assertIn('id="'+elem+'"',self.html)
  self.assertIn("V31_VISUAL_REPORT.json",self.html)

 def test_original_and_user_imported_art_preserved(self):
  self.assertEqual(V19.read_bytes(),self.original)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)

 def test_builder_anchors_fail_loudly(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"//duplicate")

 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_node_integrated_script_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/"integrated_v31.js";f.write_text(js,encoding="utf-8")
   p=subprocess.run(["node","--check",str(f)],text=True,capture_output=True,timeout=55)
   self.assertEqual(p.returncode,0,p.stderr)

if __name__=="__main__":unittest.main()
