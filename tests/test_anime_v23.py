"""AI Anime Factory V23 integrity, compatibility and syntax regression checks."""
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
BUILDER=ROOT/"anime-factory"/"v23"/"build_character_v23.py"
spec=importlib.util.spec_from_file_location("anime_v23_builder",BUILDER)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class AnimeV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=V19.read_bytes()
        cls.original_sha=hashlib.sha256(cls.original).hexdigest()
        cls.html=module.build()

    @classmethod
    def tearDownClass(cls):
        if hashlib.sha256(V19.read_bytes()).hexdigest()!=cls.original_sha:
            raise AssertionError("Original V19 changed during tests")

    def test_prior_editors_and_story_preserved(self):
        for token in ('id="page-story-v20"','id="page-visual-v21"',
                      'id="page-acting-v22"','id="page-character-v23"',
                      'function combat17State(','function combat18Sim(',
                      'function impact19State(','function v20CanonLines(',
                      'function v21AtmosphereBack(','function v22Mood(',
                      'function v22FaceDetails(','function exportEpisode()'):
            with self.subTest(token=token):
                self.assertIn(token,self.html)

    def test_seven_character_parameters(self):
        for token in ('v23-profile','v23-anatomy','v23-hairDetail',
                      'v23-costumeDetail','v23-secondaryMotion',
                      'v23-enabled','v23-character','v23-save','v23-sheet',
                      'v23-preview','v23-txt'):
            self.assertIn('id="'+token+'"',self.html)

    def test_anatomical_and_motion_wiring(self):
        for token in ('function v23TorsoForm(','function v23LegForm(',
                      'function v23ArmForm(','function v23FaceForm(',
                      'function v23HairForm(','function v23HeadScale(',
                      'function v23Secondary(','v23LegForm(g,c,s,role,t,steps);',
                      'v23HairForm(g,c,s,role,t,wind);',
                      'v23CostumeForm(g,c,s,role,t,cloth);'):
            with self.subTest(token=token):
                self.assertIn(token,self.html)

    def test_v23_migration_retains_old_storage_and_data(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V23';",self.html)
        self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V22')",self.html)
        self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V21')",self.html)
        self.assertIn("P={format:'AIAnimeFactoryProject',version:23,",self.html)
        self.assertIn("function v20CarryUnknown(",self.html)
        self.assertIn('if(Number(migrated.version)<23)migrated.version=23;',self.html)
        self.assertIn('V23_CHARACTER_SETTINGS.json',self.html)

    def test_user_imported_art_not_overpainted(self):
        self.assertIn(
            'if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;',
            self.html)
        self.assertIn("if(img?.complete&&img.naturalWidth)",self.html)

    def test_build_non_destructive_and_deterministic(self):
        self.assertEqual(V19.read_bytes(),self.original)
        self.assertEqual(module.build(),self.html)
        self.assertGreater(len(self.html),len(self.original))
        with self.assertRaises(ValueError):
            module.patch(self.html, "/* extension */")

    @unittest.skipUnless(shutil.which("node"),"Node.js unavailable")
    def test_integrated_javascript_syntax(self):
        self.assertEqual(self.html.count("<script>"),1)
        js=self.html.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory(prefix="v23_js_") as tmp:
            path=Path(tmp)/"app.js"
            path.write_text(js,encoding="utf-8")
            proc=subprocess.run(["node","--check",str(path)],
                                capture_output=True,text=True,timeout=50)
            self.assertEqual(proc.returncode,0,proc.stderr)

if __name__=="__main__":
    unittest.main()
