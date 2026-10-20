"""AI Anime Factory V22 source, compatibility, and integrated JS tests."""
from __future__ import annotations
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v22"/"build_acting_v22.py"
spec=importlib.util.spec_from_file_location("anime_v22_builder",BUILDER)
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class AnimeV22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=SOURCE.read_bytes()
        cls.html=b.build()

    @classmethod
    def tearDownClass(cls):
        if SOURCE.read_bytes()!=cls.original:
            raise AssertionError("Original V19 changed")

    def test_all_prior_rendering_functions_survive(self):
        for token in ("function drawScene(", "function drawRigPerson(",
                      "function combat18Sim(", "function impact19State(",
                      "function v20CanonLines(", "function v21AtmosphereBack(",
                      "function v22Mood(", "function v22CombatClarity(",
                      "function exportEpisode()"):
            with self.subTest(token=token):
                self.assertIn(token,self.html)

    def test_v22_integrated_tab(self):
        self.assertIn('id="page-acting-v22"',self.html)
        self.assertIn('data-page="acting-v22"',self.html)
        for name in ("v22-scene","v22-beat-list","v22-playhead",
                     "v22-save-beat","v22-contact","v22-hero","v22-partner"):
            self.assertIn('id="'+name+'"',self.html)

    def test_v22_saved_project_schema(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V22'",self.html)
        self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V21')",self.html)
        self.assertIn("P={format:'AIAnimeFactoryProject',version:22,",self.html)
        self.assertIn("function migrateV21Original(",self.html)
        self.assertIn("function migrate(raw)",self.html)
        self.assertIn("s.actingV22",self.html)

    def test_no_overwriting_user_art(self):
        # Face modification is inside fallback procedural rig only.
        self.assertIn("v22FaceDetails(g,c,s,role,t,design,f)",self.html)
        self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)

    def test_emotions_and_combat_features(self):
        for token in ("function v22ActingQA(", "function v22SaveBeat(",
                      "function v22NewBeat(", "function v22DeleteBeat(",
                      "function v22ActorSheet(", "function v22BodyBreath(",
                      "if(!['hit','block'].includes(st.result)", "V22_ACTING_PLAN_RU.txt"):
            with self.subTest(token=token):
                self.assertIn(token,self.html)

    def test_original_byte_for_byte(self):
        self.assertEqual(SOURCE.read_bytes(),self.original)
        self.assertGreater(len(self.html.encode("utf-8")),len(self.original))

    @unittest.skipUnless(shutil.which("node"),"Node.js not available")
    def test_integrated_js_syntax(self):
        self.assertEqual(self.html.count("<script>"),1)
        js=self.html.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory(prefix="anime_v22_test_") as td:
            p=Path(td)/"studio_v22.js"
            p.write_text(js,encoding="utf-8")
            result=subprocess.run(["node","--check",str(p)],
                                  capture_output=True,text=True,timeout=35)
            self.assertEqual(result.returncode,0,result.stderr)

if __name__=="__main__":
    unittest.main()
