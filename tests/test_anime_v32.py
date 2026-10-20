"""V32: original V19 preserved; keyframes alter genuine procedural anatomy."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v32"/"build_keyframes_v32.py"
spec=importlib.util.spec_from_file_location("v32_builder",GEN)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class V32Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes()
  cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.sha

 def test_retains_all_history_and_editors(self):
  for tab in ("story-v20","visual-v21","acting-v22","character-v23",
              "animation-v24","combat-v25","cinematic-v26",
              "world-v27","interaction-v28","polish-v29",
              "review-v30","visual-v31","keyframe-v32"):
   self.assertIn('id="page-'+tab+'"',self.html)
  for key in ("function v20CanonLines(","function v23HeadScale(",
              "function v24Dynamics(","function v25PairPose(",
              "function v26Camera(","function v27Back(",
              "function v28Ground(","function v29Beat(",
              "function v30Audit(","function v31Grade("):
   self.assertIn(key,self.html)

 def test_real_procedural_joint_and_face_integration(self):
  for key in ("v29=v29Actor(s,t,role),v32=v32Pose(s,t,role);",
              "v29.lean+v32.lean;",
              "-54-attack*12+v32.elbowLX",
              "v29.handX+v32.handRX",
              "v29.rootX+v32.rootX",
              "v32Foot(s,t,role,'left',v29FootPose(",
              "const f=v32Face(s,t,role,v13Face(",
              "g.rotate(v32.headTilt);const hs="):
   self.assertIn(key,self.html)
  self.assertEqual(self.html.count("g.rotate(v32.headTilt);const hs="),2)

 def test_scene_storage_and_exports(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V32';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:32,",self.html)
  self.assertIn("if(Number(migrated.version)<32)migrated.version=32;",self.html)
  for v in range(19,33):
   if v==20 or v>=21:
    self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(v)+"')",self.html)
  for elem in ("v32-scene","v32-style","v32-enabled","v32-silhouette",
               "v32-gesture","v32-expression","v32-hold","v32-anticipation",
               "v32-keyframe","v32-key-value","v32-before","v32-after",
               "v32-position","v32-save","v32-preset","v32-sheet","v32-plan","v32-qa"):
   self.assertIn('id="'+elem+'"',self.html)
  self.assertIn("V32_SCENE_POSES.json",self.html)

 def test_imported_png_are_unchanged_and_rig_optional(self):
  self.assertEqual(V19.read_bytes(),self.original)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
  code=(ROOT/"anime-factory"/"v32"/"keyframes_v32.js").read_text(encoding="utf-8")
  self.assertIn("function v32Cue(",code)
  self.assertIn("function v32Face(",code)
  self.assertIn("v29Beat(s,t)",code)
  self.assertNotIn("Math.random(",code)
  self.assertNotIn("fetch(",code)

 def test_reproducible_and_duplicate_guard(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"//duplicate")

 @unittest.skipUnless(shutil.which("node"),"Node not installed")
 def test_integrated_javascript_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v32js_") as tmp:
   file=Path(tmp)/"studio.js";file.write_text(js,encoding="utf-8")
   out=subprocess.run(["node","--check",str(file)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,out.returncode,out.stderr)

if __name__=="__main__":unittest.main()
