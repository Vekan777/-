"""AI Anime Factory V44: source continuity, real rig dynamics/feet and executable JS."""
from __future__ import annotations
import hashlib,importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory/v19/AI_Anime_Factory_V19.html"
FILE=ROOT/"anime-factory/v44/build_keyposes_v44.py"
spec=importlib.util.spec_from_file_location("v44test",FILE)
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class V44Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v19sha=hashlib.sha256(V19.read_bytes()).hexdigest()
  cls.old=builder.previous().build()
  cls.html=builder.build()
 def test_every_old_renderer_continues(self):
  for s in ("function drawScene(","function v23TorsoForm(",
   "function v24Dynamics(","function v24FootPose(","function v25Contact(",
   "function v29Beat(","function v30Audit(","function v33Act(",
   "function v34Review(","function v35Plan(","function v36Schedule(",
   "function v37Paint(","function v38Frame(","function v39Move(",
   "function v40FaceInk(","function v41Cape(","function v42Layers(",
   "function v43Shot(","function v44Pose("):
   self.assertIn(s,self.html,s)
  for page in ("page-assembly-v35","page-audio-v36","page-subtitles-v37",
   "page-cinematic-v38","page-performance-v39","page-character-art-v40",
   "page-silhouette-v41","page-stage-v42","page-action-v43",
   "page-keyposes-v44"):
   self.assertIn('id="'+page+'"',self.html,page)
  self.assertEqual(self.v19sha,hashlib.sha256(V19.read_bytes()).hexdigest())
 def test_true_pose_not_only_overlay(self):
  for tok in ("const v44PrevDynamics=v24Dynamics,v44PrevFoot=v24FootPose;",
   "v24Dynamics=function(s,t,role)","v24FootPose=function(s,t,role,side,baseX,baseY)",
   "const contact=v25Contact(s,seconds);",
   "defender&&contact.outcome==='hit'","defender&&contact.outcome==='dodge'",
   "new MediaRecorder(","V44_TRUE_KEYPOSES_EPISODE_",
   "AI_ANIME_FACTORY_V43","AI_ANIME_FACTORY_V44"):
   self.assertIn(tok,self.html,tok)
  self.assertNotIn('id="page-keyposes-v44"',self.old)
 def test_repeat_build_and_duplicate_protection(self):
  self.assertEqual(self.html,builder.build())
  with self.assertRaises(ValueError):builder.patch(self.html,"// duplicate")
 @unittest.skipUnless(shutil.which("node"),"Node missing")
 def test_node_syntax(self):
  self.assertEqual(self.html.count("<script>"),1)
  code=self.html.split("<script>",1)[1].split("</script>",1)[0]
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"v44.js";p.write_text(code,encoding="utf-8")
   run=subprocess.run(["node","--check",str(p)],capture_output=True,text=True,timeout=60)
   self.assertEqual(0,run.returncode,run.stderr)
if __name__=="__main__":unittest.main()
