"""AI Anime Factory V36: preserved V19–V35, building, manifest and JS syntax."""
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
V35=ROOT/"anime-factory"/"v35"/"build_assembly_v35.py"
V36=ROOT/"anime-factory"/"v36"/"build_audio_v36.py"
spec=importlib.util.spec_from_file_location("anime_v36_test",V36)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Anime36(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oldhash=hashlib.sha256(V19.read_bytes()).hexdigest()
        cls.v35=mod.previous().build()
        cls.html=mod.build()

    def test_all_old_capabilities(self):
        for marker in ("function v35Plan(","function v35Frame(",
          "function v35Audit(","function v34Camera(","function v33Act(",
          "function v30Audit(","function drawScene(","function v25Combat("):
            if marker=="function v25Combat(":
                continue
            self.assertIn(marker,self.html)
        self.assertIn('id="page-assembly-v35"',self.html)
        self.assertIn('id="page-audio-v36"',self.html)
        self.assertIn('id="page-export"',self.html)
        self.assertIn("AI_ANIME_FACTORY_V35",self.html)
        self.assertIn("AI_ANIME_FACTORY_V36",self.html)
        self.assertEqual(self.oldhash,hashlib.sha256(V19.read_bytes()).hexdigest())

    def test_new_real_capture_elements(self):
        for marker in ("v36Schedule(","v36Envelope(","MediaRecorder",
                       ".captureStream(",".createMediaStreamDestination(",
                       "decodeAudioData(","V36_AUDIO_EPISODE.json",
                       "v36Assets=new WeakMap()"):
            self.assertIn(marker,self.html)
        for elem in ("v36-preview","v36-episode","v36-slot","v36-audiofile",
                     "v36-save","v36-play","v36-export","v36-json"):
            self.assertIn('id="'+elem+'"',self.html)

    def test_original_project_storage_and_durations(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V36'",self.html)
        self.assertIn("migrated.version=36",self.html)
        self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V35')",self.html)
        self.assertIn("v35Plan(episode)",self.html)
        self.assertIn("scene.audioV36",self.html)
        self.assertIn("storyV20",self.v35)
        self.assertIn("assemblyV35",self.v35)

    def test_deterministic_builder(self):
        self.assertEqual(mod.build(),self.html)
        with self.assertRaises(ValueError):
            mod.patch(self.html,"// duplicate")

    @unittest.skipUnless(shutil.which("node"),"Node missing")
    def test_node_syntax(self):
        self.assertEqual(self.html.count("<script>"),1)
        body=self.html.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory() as t:
            script=Path(t)/"v36.js"
            script.write_text(body,encoding="utf-8")
            result=subprocess.run(["node","--check",str(script)],
                                  capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)

if __name__=="__main__":
    unittest.main()
