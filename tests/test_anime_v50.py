"""V50 final project historical continuity and production-tool regression."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory/v50/build_final_v50.py"
sp=importlib.util.spec_from_file_location("v50_deep_qa_builder",BUILDER)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class V50Final(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original_sha=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
  cls.parent=m.previous().build()
  cls.html=m.build()
 def test_full_historical_working_render_chain(self):
  for key in ("function v50AuditProject(","function v50ReviewData(",
   "window.v50FinalQA=Object.freeze","function v50Backup(",
   "function v49Audit(","function v48Manifest(",
   "function v47RestoreEpisode(","function v46LayerMotion(",
   "function v45DrawBackground(","function v44Pose(",
   "function v43Shot(","function v42Layers(","function v41Cape(",
   "function v40FaceInk(","function v39Move(","function v37SubtitleFile(",
   "function v36Start(","function v35Plan(","function v25Contact(",
   "function drawProductionPerson(","AI_ANIME_FACTORY_V50",
   "AI_ANIME_FACTORY_V49",'id="page-final-v50"',
   "V50_FINAL_EPISODE_"):
   self.assertIn(key,self.html,key)
  self.assertNotIn("function v50AuditProject(",self.parent)
 def test_preserve_original_and_rebuild_exactly(self):
  self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),self.original_sha)
  self.assertEqual(self.html,m.build())
  with self.assertRaises(ValueError):m.patch(self.html,"duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node not available")
 def test_generated_browser_js_parses(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/"v50.js";out.write_text(js,encoding="utf-8")
   p=subprocess.run(["node","--check",str(out)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,p.returncode,p.stderr)
 def test_final_qa_is_explicitly_not_artistic_certification(self):
  for text in ("manualAcceptanceRequired:true","technical-review",
   "function v50SafeImage(","function v50SafeAudio(",
   "Скачать ВЕСЬ проект JSON"):
   self.assertIn(text,self.html,text)
if __name__=="__main__":unittest.main()
