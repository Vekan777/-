"""V49 preservation and unified studio structural tests."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILD=ROOT/"anime-factory/v49/build_unified_v49.py"
spec=importlib.util.spec_from_file_location("unified_builder_qa",BUILD)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class V49Unified(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.sha=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
  cls.prior=m.previous().build()
  cls.new=m.build()
 def test_all_working_stages_and_migration(self):
  for term in ("function v49Audit(","function v49IssuesForEpisode(",
   "function v49Backup(","function v49QuickRender(",
   "function v49Route(","function v49ChecklistExport(",
   "window.v49UnifiedBridge=Object.freeze","productionV49",
   "AI_ANIME_FACTORY_V49","AI_ANIME_FACTORY_V48",
   'id="page-unified-v49"',"V49_UNIFIED_EPISODE_",
   "function v48Manifest(","function v47RestoreEpisode(",
   "function v46SaveKey(","function v45DrawBackground(",
   "function v44Pose(","function v43Shot(","function v42Layers(",
   "function v41Cape(","function v40FaceInk(",
   "function v39Move(","function v37SubtitleFile(",
   "function v36Start(","function v35Plan(","function v25Contact("):
   self.assertIn(term,self.new,term)
  self.assertNotIn("function v49Audit(",self.prior)
 def test_history_and_determinism(self):
  self.assertEqual(m.build(),self.new)
  self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),self.sha)
  with self.assertRaises(ValueError):m.patch(self.new,"repeat")
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_real_browser_javascript_syntax(self):
  self.assertEqual(1,self.new.count("<script>"))
  js=self.new.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"v49.js";p.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(p)],capture_output=True,text=True,timeout=60)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=="__main__":unittest.main()
