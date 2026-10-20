"""V29 source, event-based animation, preservation and JS syntax regressions."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v29"/"build_polish_v29.py"
spec=importlib.util.spec_from_file_location("v29_builder",BUILDER)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class V29Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=V19.read_bytes();cls.sha=hashlib.sha256(cls.original).hexdigest()
  cls.html=mod.build()
 @classmethod
 def tearDownClass(cls):
  assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.sha
 def test_all_previous_tabs_and_story(self):
  for x in ("story-v20","visual-v21","acting-v22","character-v23",
            "animation-v24","combat-v25","cinematic-v26","world-v27",
            "interaction-v28","polish-v29"):
   with self.subTest(x=x):self.assertIn('id="page-'+x+'"',self.html)
  for x in ("function impact19State(","function v20CanonLines(",
            "function v23HeadScale(","function v24FootPose(",
            "function v25Contact(","function v27Back(",
            "function v28Ground(","function exportEpisode()"):
   self.assertIn(x,self.html)
 def test_real_procedural_joints_and_environment_ground_sync(self):
  for x in ("const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role),v29=v29Actor(s,t,role);",
            "v24.lean+v25.lean+v29.lean;",
            "v25.attack*32+v29.handX",
            "v25.step+v29.rootX",
            "v29FootPose(s,t,role,'left',v24FootPose(",
            "const foot=v29GroundPulse(s,t,role);",
            "v24.headX+v29.headX"):
   self.assertIn(x,self.html)
 def test_no_new_combat_results_or_modified_author_art(self):
  js=(ROOT/"anime-factory"/"v29"/"polish_v29.js").read_text(encoding="utf-8")
  for x in ("const c=v25Contact(s,t)","['hit','block'].includes(c.outcome)",
            "c.outcome==='dodge'","v28Footfall(s,t,role)"):
   self.assertIn(x,js)
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)
  self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
  self.assertEqual(self.original,V19.read_bytes())
 def test_ui_and_migration(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V29';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:29,",self.html)
  self.assertIn("if(Number(migrated.version)<29)migrated.version=29;",self.html)
  for ver in [28,27,26,25,24,23,22,21,19]:
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(ver)+"')",self.html)
  for key in ("v29-scene","v29-style","v29-enabled","v29-timing","v29-stance",
              "v29-follow","v29-impact","v29-smoothness","v29-before","v29-after",
              "v29-position","v29-save","v29-preset","v29-sheet","v29-plan"):
   self.assertIn('id="'+key+'"',self.html)
  self.assertIn("V29_MOTION_SETTINGS.json",self.html)
 def test_builder_reproducibility(self):
  self.assertEqual(self.html,mod.build())
  with self.assertRaises(ValueError):mod.patch(self.html,"//duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_node_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v29_js_") as td:
   file=Path(td)/"integrated.js";file.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(file)],capture_output=True,text=True,timeout=50)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=="__main__":unittest.main()
