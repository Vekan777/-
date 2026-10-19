"""V21 source, compatibility and JavaScript regression tests."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/"anime-factory"/"v21"/"build_visual_v21.py"
V19=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
spec=importlib.util.spec_from_file_location("anime_v21_patch", GEN)
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class VisualV21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=V19.read_bytes()
        cls.page=builder.build()

    @classmethod
    def tearDownClass(cls):
        assert V19.read_bytes()==cls.before, "Original V19 was mutated"

    def test_renderer_and_combat_retained(self):
        for marker in ("function drawScene(", "function drawModel(",
                       "function impact19Draw(", "function combat18Sim(",
                       "function combat18Continuity()", "function exportEpisode()",
                       "function v20ContinuityQA()", "function v20CanonLines()"):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.page)
        self.assertEqual(self.page.count("function drawScene("),1)

    def test_visual_hooks_reach_actual_frame(self):
        for marker in ("v21AtmosphereBack(g,w,h,s,sec);",
                       "v21CharacterBack(g,w,h,s,sec,poses);",
                       "v21CharacterDetail(g,w,h,s,sec,poses,hero,second);",
                       "v21ImpactDetails(g,w,h,s,sec,impactV19,poses);",
                       "v21AtmosphereFront(g,w,h,s,sec);",
                       "v21Grade(g,w,h,s,sec);"):
            with self.subTest(hook=marker):
                self.assertIn(marker,self.page)

    def test_ui_and_scene_persistence(self):
        self.assertIn('id="page-visual-v21"',self.page)
        self.assertIn('data-page="visual-v21"',self.page)
        for prop in ("v21-look","v21-weather","v21-save","v21-preset",
                     "v21-rim","v21-sheet","v21-intensity","v21-depth"):
            self.assertIn('id="'+prop+'"',self.page)
        self.assertIn("s.visualV21",self.page)
        self.assertIn("V21_VISUAL_SETTINGS.json",self.page)

    def test_old_projects_not_overwritten(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V21'",self.page)
        self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V19')",self.page)
        self.assertIn("function migrateV20Original(raw)",self.page)
        self.assertIn("function migrate(raw)",self.page)
        self.assertIn("version:21",self.page)
        self.assertIn("legacyOriginal",self.page)

    def test_visual_effects_only_on_hits(self):
        self.assertIn("['hit','block'].includes(st.event.outcome)",self.page)
        self.assertIn("v21Rand",self.page)
        self.assertIn("function v21ShotSheet()",self.page) if False else None
        self.assertIn("async function v21ShotSheet()",self.page)

    def test_source_unmodified(self):
        self.assertEqual(V19.read_bytes(),self.before)
        self.assertGreater(len(self.page.encode("utf-8")),len(self.before))

    @unittest.skipUnless(shutil.which("node"),"Node required for JS syntax checking")
    def test_complete_integrated_javascript_syntax(self):
        self.assertEqual(self.page.count("<script>"),1)
        body=self.page.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/"v21.js"
            file.write_text(body,encoding="utf-8")
            done=subprocess.run(["node","--check",str(file)],capture_output=True,
                                text=True,timeout=40)
            self.assertEqual(done.returncode,0,done.stderr)


if __name__=="__main__":
    unittest.main()
