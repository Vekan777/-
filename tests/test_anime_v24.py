"""V24 animation source, migration, legacy protection and deterministic code tests."""
from __future__ import annotations
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v24"/"build_animation_v24.py"
spec=importlib.util.spec_from_file_location("anime_v24_builder",BUILDER)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class AnimeV24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig=V19.read_bytes()
        cls.hash=hashlib.sha256(cls.orig).hexdigest()
        cls.html=mod.build()

    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(V19.read_bytes()).hexdigest()==cls.hash

    def test_previous_editors_and_story_untouched(self):
        for token in ('id="page-story-v20"','id="page-visual-v21"',
                      'id="page-acting-v22"','id="page-character-v23"',
                      'id="page-animation-v24"','function v20CanonLines(',
                      'function v21AtmosphereBack(','function v22Mood(',
                      'function v23HeadScale(','function combat17State(',
                      'function combat18Sim(','function impact19State(',
                      'function exportEpisode()'):
            with self.subTest(token=token):self.assertIn(token,self.html)

    def test_new_joint_motion_pipeline(self):
        for token in ("function v24Dynamics(","function v24FootPose(",
                      "function v24MotionQA(","function v24Preview(",
                      "v24FootPose(s,t,role,'left'","const v24=v24Dynamics(s,t,role);",
                      "v24.headX","v24.rootX","v24.hair","v24.cloth",
                      "v24.strike","v24.guard","v24.step"):
            with self.subTest(token=token):self.assertIn(token,self.html)

    def test_v24_scene_controls(self):
        for name in ('v24-scene','v24-style','v24-enabled','v24-stride',
                     'v24-weight','v24-anticipation','v24-recoil',
                     'v24-followThrough','v24-before','v24-after',
                     'v24-save','v24-sheet','v24-playhead','v24-plan'):
            self.assertIn('id="'+name+'"',self.html)

    def test_v23_v22_fallback_and_json_migration(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V24';",self.html)
        for version in ("V23","V22","V21","V19"):
            self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_"+version+"')",self.html)
        self.assertIn("P={format:'AIAnimeFactoryProject',version:24,",self.html)
        self.assertIn("if(Number(migrated.version)<24)migrated.version=24;",self.html)
        self.assertIn("function v20CarryUnknown(",self.html)
        self.assertIn("V24_SCENE_MOTION.json",self.html)

    def test_user_imported_art_not_redrawn(self):
        self.assertIn(
            'if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;',
            self.html)
        self.assertIn("if(img?.complete&&img.naturalWidth)",self.html)
        self.assertEqual(V19.read_bytes(),self.orig)

    def test_idempotence_guard_and_repeatable_builder(self):
        self.assertEqual(mod.build(),self.html)
        with self.assertRaises(ValueError):
            mod.patch(self.html,"// already integrated")

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_javascript_syntax(self):
        self.assertEqual(self.html.count("<script>"),1)
        js=self.html.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory(prefix="v24_node_") as temp:
            f=Path(temp)/"integrated.js";f.write_text(js,encoding="utf-8")
            out=subprocess.run(["node","--check",str(f)],
                               capture_output=True,text=True,timeout=50)
            self.assertEqual(out.returncode,0,out.stderr)

if __name__=="__main__":unittest.main()
