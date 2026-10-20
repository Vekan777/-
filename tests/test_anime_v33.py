"""V33 source preservation, rig acting integration, migration and JS syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
GEN=ROOT/"anime-factory"/"v33"/"build_acting_v33.py"
spec=importlib.util.spec_from_file_location("v33_builder",GEN)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V33Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes();cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.sha
 def test_historical_pages(self):
  for k in ("story-v20","visual-v21","acting-v22","character-v23","animation-v24",
            "combat-v25","cinematic-v26","world-v27","interaction-v28",
            "polish-v29","review-v30","visual-v31","keyframe-v32","acting-v33"):
   self.assertIn('id="page-'+k+'"',self.html)
  for k in ("function v20CanonLines(","function v23HeadScale(","function v24Dynamics(",
            "function v29Beat(","function v30Audit(","function v31Grade(",
            "function v32Pose(","function v32Face("):
   self.assertIn(k,self.html)
 def test_true_face_gaze_and_hand_joint_integration(self):
  for k in ("v32=v32Pose(s,t,role),v33=v33Act(s,t,role);",
            "v32.elbowLX+v33.elbowLX","v32.handRX+v33.handRX",
            "v32.rootY+v33.rootY","const f=v33Face(s,t,role,v32Face(",
            "v32.headX+v33.headX","g.rotate(v32.headTilt+v33.headTilt);const hs="):
   self.assertIn(k,self.html)
  self.assertEqual(self.html.count("g.rotate(v32.headTilt+v33.headTilt);const hs="),2)
 def test_migration_original_and_art(self):
  self.assertEqual(self.original,V19.read_bytes())
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V33';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:33,",self.html)
  self.assertIn("if(Number(migrated.version)<33)migrated.version=33;",self.html)
  for n in [19]+list(range(21,33)):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(n)+"')",self.html)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
  self.assertIn("V33_SCENE_ACTING.json",self.html)
 def test_controls_and_determinism(self):
  for k in ("v33-scene","v33-style","v33-enabled","v33-gaze",
            "v33-emotion","v33-gesture","v33-breathing",
            "v33-transitions","v33-before","v33-after","v33-position",
            "v33-save","v33-preset","v33-qa","v33-plan","v33-sheet"):
   self.assertIn('id="'+k+'"',self.html)
  addon=(ROOT/"anime-factory"/"v33"/"acting_v33.js").read_text(encoding="utf-8")
  for k in ("function v33Face(","function v33Signal(","function v33Act(",
            "const m=v22Mood(","v32Cue(s,t)","function v33Plan("):
   self.assertIn(k,addon)
  self.assertNotIn("Math.random(",addon)
  self.assertNotIn("fetch(",addon)
 def test_idempotent_and_guarded(self):
  self.assertEqual(self.html,builder.build())
  with self.assertRaises(ValueError):builder.patch(self.html,"//already")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_valid_js(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"app.js";f.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(f)],text=True,capture_output=True,timeout=60)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=="__main__":unittest.main()
