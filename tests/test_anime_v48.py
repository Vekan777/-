"""V48 continuity and production engine structure + runnable JS."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
BUILD=ROOT/"anime-factory/v48/build_episode_v48.py"
spec=importlib.util.spec_from_file_location("v48builder",BUILD)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class EpisodeV48(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.original=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.before=builder.previous().build()
  cls.html=builder.build()
 def test_episode_series_export_real_engine(self):
  for fragment in ("function v48Manifest(","function v48DrawCredits(",
   "v35Frame=function(canvas,episode,sec)",
   "function v48Subs(","v37SubtitleFile(ep,format)",
   "function v48FourFrames(","function v48RecordOne(",
   "await v36Start(true)","AI_ANIME_FACTORY_V48",
   "V48_EPISODE_", 'id="page-episode-v48"'):
   self.assertIn(fragment,self.html,fragment)
  self.assertNotIn("function v48Manifest(",self.before)
 def test_all_older_functionality_and_canon(self):
  for token in ("function v47RestoreEpisode(","function v47Wave(",
   "function v46LayerMotion(","function v45DrawBackground(",
   "function v44Pose(","function v43Shot(","function v42Layers(",
   "function v41Cape(","function v40FaceInk(","function v39Move(",
   "function v37SubtitleFile(","function v36Start(","function v35Plan(",
   "function v25Contact(","function drawProductionPerson(",
   "AI_ANIME_FACTORY_V47","AI_ANIME_FACTORY_V48"):
   self.assertIn(token,self.html,token)
  self.assertEqual(hashlib.sha256(V19.read_bytes()).hexdigest(),self.original)
 def test_builder_deterministic_and_duplicate_prevention(self):
  self.assertEqual(builder.build(),self.html)
  with self.assertRaises(ValueError):builder.patch(self.html,"already")
 @unittest.skipUnless(shutil.which("node"),"Node not installed")
 def test_browser_javascript_parses(self):
  self.assertEqual(self.html.count("<script>"),1)
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"v48.js";p.write_text(js,encoding="utf-8")
   z=subprocess.run(["node","--check",str(p)],capture_output=True,text=True,timeout=50)
   self.assertEqual(z.returncode,0,z.stderr)
 def test_batch_has_checksum_and_media_contract(self):
  py=(ROOT/"scripts/render_anime_v48.py").read_text()
  for tok in ("V48_RENDER_CHECKPOINT.json","FFprobe","--qa-short",
   "resume_done(","--mp4","libx264","-c:a","aac",
   "v37SubtitleFile","v36-export","project_sha256","html_sha256"):
   self.assertIn(tok,py,tok)
if __name__=="__main__":unittest.main()
