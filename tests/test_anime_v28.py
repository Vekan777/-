"""V28 regressions: original V19 immutable, old modules retained, deterministic event FX."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v28"/"build_interaction_v28.py"
spec=importlib.util.spec_from_file_location("v28_builder",BUILDER)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class V28Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=ORIGINAL.read_bytes()
  cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=mod.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==cls.sha
 def test_old_editors_and_combat_story_remain(self):
  for text in ('id="page-story-v20"','id="page-visual-v21"','id="page-acting-v22"',
               'id="page-character-v23"','id="page-animation-v24"',
               'id="page-combat-v25"','id="page-cinematic-v26"',
               'id="page-world-v27"','id="page-interaction-v28"',
               'function impact19State(','function combat17State(',
               'function v20CanonLines(','function v22Mood(',
               'function v23HeadScale(','function v24Dynamics(',
               'function v25PairPose(','function v26Camera(',
               'function v27Feet(','function exportEpisode()'):
   with self.subTest(text=text):self.assertIn(text,self.html)
 def test_actor_environment_in_live_renderer(self):
  for text in ('function v28Background(','function v28Ground(',
               'function v28CombatGround(','function v28ActorLight(',
               'v27Back(g,w,h,s,sec);v28Background(g,w,h,s,sec);',
               'v27Feet(g,w,h,s,sec,poses);v28Ground(g,w,h,s,sec,poses);',
               'v28CombatGround(g,w,h,s,sec,poses);',
               'v22CombatClarity(g,w,h,s,sec,combat17,poses);v28ActorLight(g,w,h,s,sec,poses);'):
   self.assertIn(text,self.html)
 def test_no_unverified_hits(self):
  js=(ROOT/"anime-factory"/"v28"/"interaction_v28.js").read_text(encoding="utf-8")
  for text in ("if(s.kind!=='fight')return null;","v25Contact(s,t)",
               "['hit','block'].includes(v.outcome)","if(!v.active", "if(!effect||!poses"):
   self.assertIn(text,js)
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)
 def test_preservation_and_json(self):
  self.assertEqual(ORIGINAL.read_bytes(),self.original)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V28';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:28,",self.html)
  self.assertIn("if(Number(migrated.version)<28)migrated.version=28;",self.html)
  for i in [27,26,25,24,23,22,21,19]:
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(i)+"')",self.html)
  for key in ("v28-scene","v28-style","v28-enabled","v28-footsteps",
              "v28-dust","v28-bounce","v28-scars","v28-impactFX",
              "v28-before","v28-after","v28-save","v28-sheet","v28-plan"):
   self.assertIn('id="'+key+'"',self.html)
  self.assertIn("V28_INTERACTION_SETTINGS.json",self.html)
 def test_repeat_build(self):
  self.assertEqual(mod.build(),self.html)
  with self.assertRaises(ValueError):mod.patch(self.html,"//duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v28_js_") as td:
   f=Path(td)/"full.js";f.write_text(js,encoding="utf-8")
   res=subprocess.run(["node","--check",str(f)],capture_output=True,text=True,timeout=50)
   self.assertEqual(res.returncode,0,res.stderr)
if __name__=="__main__":unittest.main()
