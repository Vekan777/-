"""V27 regression: source preservation, render wiring, JSON migration, Node syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v27"/"build_world_v27.py"
spec=importlib.util.spec_from_file_location("anime_v27_builder",BUILDER)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class AnimeV27Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes();cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.sha

 def test_every_editor_still_present(self):
  for key in ('id="page-story-v20"','id="page-visual-v21"',
              'id="page-acting-v22"','id="page-character-v23"',
              'id="page-animation-v24"','id="page-combat-v25"',
              'id="page-cinematic-v26"','id="page-world-v27"',
              'function impact19State(','function combat18Sim(',
              'function v20CanonLines(','function v21AtmosphereBack(',
              'function v22Mood(','function v23HeadScale(',
              'function v24Dynamics(','function v25PairPose(',
              'function v26Camera(','function exportEpisode()'):
   with self.subTest(key=key):self.assertIn(key,self.html)

 def test_environment_passes_in_live_canvas(self):
  for key in ('function v27Back(','function v27Feet(','function v27Front(',
              'v27Back(g,w,h,s,sec);cin14Layers(',
              'v27Feet(g,w,h,s,sec,poses);for(const p',
              "cin14Layers(g,w,h,s,sec,'near');v27Front(g,w,h,s,sec);"):
   self.assertIn(key,self.html)

 def test_no_imported_art_is_overwritten(self):
  self.assertIn('if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;',self.html)
  self.assertIn("if(img?.complete&&img.naturalWidth)",self.html)
  self.assertEqual(V19.read_bytes(),self.original)

 def test_persistence_and_controls(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V27';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:27,",self.html)
  self.assertIn("if(Number(migrated.version)<27)migrated.version=27;",self.html)
  for v in (26,25,24,23,22,21,19):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(v)+"')",self.html)
  for key in ('v27-scene','v27-biome','v27-enabled','v27-depth','v27-lighting',
              'v27-grounding','v27-atmosphere','v27-foreground',
              'v27-before','v27-after','v27-position','v27-save',
              'v27-preset','v27-sheet','v27-plan'):
   self.assertIn('id="'+key+'"',self.html)
  self.assertIn('V27_WORLD_SETTINGS.json',self.html)

 def test_deterministic_and_repeatable(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"//duplicate")
  js=(ROOT/"anime-factory"/"v27"/"world_v27.js").read_text(encoding="utf-8")
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)

 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_javascript_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v27_js_") as td:
   f=Path(td)/"studio.js";f.write_text(js,encoding="utf-8")
   res=subprocess.run(["node","--check",str(f)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,res.returncode,res.stderr)

if __name__=="__main__":unittest.main()
