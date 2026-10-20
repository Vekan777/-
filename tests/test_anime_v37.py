"""V37 subtitle editor regression: real V36 preservation and Node syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SCRIPT=ROOT/"anime-factory/v37/build_subtitles_v37.py"
def module(path):
 spec=importlib.util.spec_from_file_location("v37sub",path)
 result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
v37=module(SCRIPT)
class V37Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.hash=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
  cls.html=v37.build()
  cls.previous=v37.previous().build()
 def test_preserves_all_generations(self):
  for marker in ("function drawScene(","function v30Audit(","function v33Act(",
     "function v34Review(","function v35Plan(","function v35Frame(",
     "function v36Schedule(","function v36Manifest(","function v37Timeline(",
     "function v37DrawFrame("):
   self.assertIn(marker,self.html)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37"):
   self.assertIn('id="'+page+'"',self.html)
  self.assertEqual(self.hash,hashlib.sha256(ORIGINAL.read_bytes()).hexdigest())
 def test_real_video_recording_subtitles(self):
  self.assertIn("v37DrawFrame($('v36-preview'),ep,v36At)",self.html)
  self.assertIn("captureStream(",self.html)
  self.assertIn("new MediaRecorder(",self.html)
  self.assertIn("V37_EPISODE_SUBTITLES_",self.html)
  self.assertIn("V37_SUBTITLE_DELIVERY.json",self.html)
  self.assertIn("WEBVTT",self.html)
  self.assertIn("subtitlesV37",self.html)
  self.assertIn("AI_ANIME_FACTORY_V36",self.html)
  self.assertIn("AI_ANIME_FACTORY_V37",self.html)
 def test_builder_reproducible_and_protected(self):
  self.assertEqual(v37.build(),self.html)
  with self.assertRaises(ValueError):v37.patch(self.html,"// duplicate")
  self.assertNotIn('id="page-subtitles-v37"',self.previous)
  self.assertIn('id="page-audio-v36"',self.previous)
 @unittest.skipUnless(shutil.which("node"),"Node not installed")
 def test_javascript_node_syntax(self):
  self.assertEqual(1,self.html.count("<script>"))
  body=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as temp:
   file=Path(temp)/"v37.js";file.write_text(body,encoding="utf-8")
   r=subprocess.run(["node","--check",str(file)],capture_output=True,text=True,timeout=60)
   self.assertEqual(0,r.returncode,r.stderr)
if __name__=="__main__":unittest.main()
