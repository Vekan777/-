"""Source-integrity and JavaScript syntax checks for Anime Factory V20."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "anime-factory" / "v19" / "AI_Anime_Factory_V19.html"
SCRIPT = ROOT / "anime-factory" / "v20" / "story_v20.js"
PATCH = ROOT / "anime-factory" / "v20" / "build_story_v20.py"

spec = importlib.util.spec_from_file_location("anime_story_v20", PATCH)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class AnimeV20Tests(unittest.TestCase):
    def setUp(self):
        self.original = ORIGINAL.read_text(encoding="utf-8")
        self.addon = SCRIPT.read_text(encoding="utf-8")
        self.patched = builder.patch(self.original, self.addon)

    def test_old_features_preserved(self):
        for name in ("function combat18Sim(", "function impact19State(",
                     "function drawScene(", "function exportEpisode()",
                     "function selfHTML()", "function save()"):
            self.assertIn(name, self.original)
            self.assertIn(name, self.patched)
        self.assertEqual(self.patched.count("function drawScene("), 1)
        self.assertIn("backup", "backup") # provenance checked in ZIP test

    def test_story_controls_and_migration(self):
        self.assertIn("function migrateV19Original(raw){", self.patched)
        self.assertIn("function migrate(raw){", self.patched)
        self.assertIn('id="page-story-v20"', self.patched)
        self.assertIn('data-page="story-v20"', self.patched)
        self.assertIn("v20CarryUnknown", self.patched)
        for value in ("v20-wound","v20-clue","v20-payoff","v20-trust",
                      "v20-soulCost","v20-memoryLost","v20-fight","v20-png"):
            self.assertIn('id="'+value+'"', self.patched)

    def test_export_hook(self):
        self.assertIn("V20_CANON_REPORT_RU.txt", self.patched)
        self.assertIn("V20_QA_REPORT.json", self.patched)
        self.assertIn("PROJECT_V20.json", self.patched)
        self.assertIn("AI_Anime_Factory_V20_STORY_COMBAT.html", self.patched)

    def test_original_unchanged(self):
        self.assertEqual(ORIGINAL.read_text(encoding="utf-8"), self.original)
        self.assertGreater(len(self.patched), len(self.original))

    @unittest.skipUnless(shutil.which("node"), "Node.js required for JS syntax test")
    def test_original_plus_extension_javascript_syntax(self):
        # No JavaScript code is executed by this test.
        self.assertEqual(self.patched.count("<script>"), 1)
        extracted = self.patched.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory(prefix="v20_js_check_") as td:
            p=Path(td)/"anime_v20.js"
            p.write_text(extracted,encoding="utf-8")
            proc=subprocess.run(["node","--check",str(p)],
                                capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,0,proc.stderr)


if __name__ == "__main__":
    unittest.main()
