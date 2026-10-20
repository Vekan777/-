"""V25 regressions for dual-actor combat and non-destructive V19–V24 integration."""
from __future__ import annotations
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"anime-factory"/"v19"/"AI_Anime_Factory_V19.html"
BUILDER=ROOT/"anime-factory"/"v25"/"build_combat_v25.py"
spec=importlib.util.spec_from_file_location("anime_v25_builder",BUILDER)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class V25IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=ORIGINAL.read_bytes()
        cls.sha=hashlib.sha256(cls.original).hexdigest()
        cls.html=module.build()

    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==cls.sha

    def test_previous_editors_remain(self):
        for token in ('id="page-story-v20"','id="page-visual-v21"',
                      'id="page-acting-v22"','id="page-character-v23"',
                      'id="page-animation-v24"','id="page-combat-v25"',
                      'function combat17State(','function combat18Sim(',
                      'function impact19State(','function v20CanonLines(',
                      'function v21AtmosphereBack(','function v22Mood(',
                      'function v23HeadScale(','function v24Dynamics(',
                      'function exportEpisode()'):
            with self.subTest(token=token):self.assertIn(token,self.html)

    def test_choreography_changes_real_positions_and_procedural_limbs(self):
        for token in ('function v25Contact(','function v25PairPose(',
                      'function v25Actor(','function v25ContactText(',
                      'v25PairPose(s,sec,poses,combat17,impactV19);',
                      'const v24=v24Dynamics(s,t,role),v25=v25Actor(s,t,role);',
                      'v25.guard*33','v25.attack*25','v25.step'):
            with self.subTest(token=token):self.assertIn(token,self.html)

    def test_miss_does_not_create_new_hit(self):
        for token in ("outcome==='hit'||outcome==='block'",
                      "e.outcome==='hit'","e.outcome==='dodge'",
                      "contact:0","return empty;"):
            self.assertIn(token,self.html)
        self.assertIn("Только существующие события решают",self.html)

    def test_v25_ui_settings_and_exports(self):
        for key in ('v25-scene','v25-enabled','v25-style','v25-distance',
                    'v25-footwork','v25-guard','v25-response','v25-rhythm',
                    'v25-before','v25-after','v25-position','v25-status',
                    'v25-save','v25-preset','v25-sheet','v25-plan'):
            self.assertIn('id="'+key+'"',self.html)
        self.assertIn('V25_CHOREOGRAPHY.json',self.html)
        self.assertIn('V25_COMBAT_PLAN_RU.txt',self.html)

    def test_v24_legacy_storage_and_project_fields(self):
        self.assertIn("const storageKey='AI_ANIME_FACTORY_V25';",self.html)
        for version in (24,23,22,21,19):
            self.assertIn("localStorage.getItem('AI_ANIME_FACTORY_V"+str(version)+"')",self.html)
        self.assertIn("P={format:'AIAnimeFactoryProject',version:25,",self.html)
        self.assertIn("if(Number(migrated.version)<25)migrated.version=25;",self.html)
        self.assertIn("function v20CarryUnknown(",self.html)

    def test_user_illustrations_are_not_overpainted(self):
        self.assertIn("if(drawProductionPerson(g,c,x,y,scale,flipped,opened,fx,t,s,role))return;",self.html)
        self.assertIn("if(img?.complete&&img.naturalWidth)",self.html)
        self.assertEqual(ORIGINAL.read_bytes(),self.original)

    def test_builder_repeatable_and_duplicate_guard(self):
        self.assertEqual(self.html,module.build())
        with self.assertRaises(ValueError):module.patch(self.html,"//duplicate")

    @unittest.skipUnless(shutil.which("node"),"Node.js unavailable")
    def test_integrated_js_syntax(self):
        self.assertEqual(self.html.count("<script>"),1)
        js=self.html.split("<script>",1)[1].split("</script>",1)[0]
        with tempfile.TemporaryDirectory(prefix="v25_node_") as temp:
            file=Path(temp)/"studio.js";file.write_text(js,encoding="utf-8")
            res=subprocess.run(["node","--check",str(file)],
                               capture_output=True,text=True,timeout=50)
            self.assertEqual(res.returncode,0,res.stderr)

if __name__=="__main__":unittest.main()
