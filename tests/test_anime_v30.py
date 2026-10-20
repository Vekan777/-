"""V30 non-destructive QA regression and original V19–V29 preservation tests."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILD=ROOT/"anime-factory"/"v30"/"build_unified_v30.py"
spec=importlib.util.spec_from_file_location("v30_unified",BUILD)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class V30ReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=V19.read_bytes()
  cls.sha=hashlib.sha256(cls.old).hexdigest()
  cls.html=builder.build()
 @classmethod
 def tearDownClass(cls):
  assert cls.sha==hashlib.sha256(V19.read_bytes()).hexdigest()

 def test_every_prior_editor_is_available(self):
  for k in ("story-v20","visual-v21","acting-v22","character-v23",
            "animation-v24","combat-v25","cinematic-v26","world-v27",
            "interaction-v28","polish-v29","review-v30"):
   self.assertIn('id="page-'+k+'"',self.html)

 def test_all_historical_pipeline_and_user_art_intact(self):
  for m in ("function v20CanonLines(","function v20ContinuityQA(",
            "function v23HeadScale(","function v24Dynamics(","function v25PairPose(",
            "function v26Camera(","function v27Back(","function v28Ground(",
            "function v29Beat(","function exportEpisode()",
            "if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;"):
   self.assertIn(m,self.html)
  self.assertEqual(self.old,V19.read_bytes())

 def test_explicit_protected_snapshot_and_non_destructive_integrity(self):
  js=(ROOT/"anime-factory"/"v30"/"unified_v30.js").read_text(encoding="utf-8")
  for m in ("function v30Stable(","function v30Hash(","function v30Snapshot(",
            "function v30Compare(","function v30Audit(","function v30Report(",
            "function v30Backup(","function v30Sheet(","delete extra.unifiedV30;",
            "v20ContinuityQA()","[\'ритм V29\',v29QA]"):
   self.assertIn(m,js)
  self.assertNotIn("Math.random(",js)
  self.assertNotIn("fetch(",js)
  self.assertNotIn("P.episodes.splice(",js)
  self.assertNotIn("P.characters.splice(",js)

 def test_upgrade_and_exports(self):
  self.assertIn("const storageKey='AI_ANIME_FACTORY_V30';",self.html)
  self.assertIn("P={format:'AIAnimeFactoryProject',version:30,",self.html)
  self.assertIn("if(Number(migrated.version)<30)migrated.version=30;",self.html)
  for v in (29,28,27,26,25,24,23,22,21,19):
   self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(v)+"')",self.html)
  for k in ("v30-run","v30-snapshot","v30-backup","v30-report","v30-manifest",
            "v30-filter","v30-results","v30-summary","v30-stage",
            "v30-preview","v30-position","v30-sheet"):
   self.assertIn('id="'+k+'"',self.html)
  self.assertIn("V30_INTEGRITY_REPORT.json",self.html)

 def test_reproducible_and_duplicate_guard(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"//duplicate")

 @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
 def test_js_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory(prefix="v30_node_") as tmp:
   f=Path(tmp)/"studio.js";f.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(f)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,r.returncode,r.stderr)

if __name__=="__main__":unittest.main()
