"""V47 tests: true V36 encoded audio restore, waveform mouth, old V19–V46 and JS syntax."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
SOURCE=ROOT/"anime-factory/v47/build_voice_v47.py"
spec=importlib.util.spec_from_file_location("v47_qa_builder",SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class VoiceV47(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old_sha=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.prior=m.previous().build()
  cls.html=m.build()
 def test_actual_media_hook(self):
  for key in ("function v47KeepAudio(","function v47RestoreScene(",
    "function v47RestoreEpisode(","await v47RestoreEpisode(ep);",
    "function v47Wave(","mouth=function(s,c,sec)",
    "v47PaintMouthOnCutout(g,s,c,t);",
    "embeddedV47","waveV47","createMediaStreamDestination()",
    "new MediaRecorder(","V47_PORTABLE_VOICE_EPISODE_"):
   self.assertIn(key,self.html,key)
  self.assertNotIn("function v47RestoreEpisode(",self.prior)
 def test_historical_2d_never_removed(self):
  for x in ("function drawProductionPerson(","function v45DrawBackground(",
    "function v46LayerMotion(","function v44Pose(","function v43Shot(",
    "function v42Layers(","function v41Cape(","function v40FaceInk(",
    "function v39Move(","function v37Paint(","function v36Schedule(",
    "function v35Plan(","function v25Contact(","function mouth(",
    "AI_ANIME_FACTORY_V46","AI_ANIME_FACTORY_V47",
    'id="page-voice-v47"'):
   self.assertIn(x,self.html,x)
  self.assertEqual(self.old_sha,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_determinism_and_safe_double_patch(self):
  self.assertEqual(m.build(),self.html)
  with self.assertRaises(ValueError):m.patch(self.html,"/*duplicate*/")
 @unittest.skipUnless(shutil.which("node"),"Node missing")
 def test_real_browser_script_parses(self):
  self.assertEqual(1,self.html.count("<script>"))
  js=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/"v47.js";target.write_text(js,encoding="utf-8")
   r=subprocess.run(["node","--check",str(target)],capture_output=True,text=True,timeout=50)
   self.assertEqual(0,r.returncode,r.stderr)
if __name__=="__main__":unittest.main()
