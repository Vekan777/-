import copy
import json
import struct
import tempfile
import unittest
from pathlib import Path
from studio import director, asset_gate, ru_alignment

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'examples/REV15_DUEL_LYRA_KAEL_NONCANON.json'

class DirectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.scene=json.loads(SRC.read_text(encoding='utf-8'))

    def test_scene_valid(self):self.assertEqual(director.validate(self.scene),[])
    def test_duplicate_character_rejected(self):
        s=copy.deepcopy(self.scene);s['characters'][1]['id']='lyra'
        self.assertTrue(director.validate(s))
    def test_no_last_beat_rejected(self):
        s=copy.deepcopy(self.scene);s['beats'].pop()
        self.assertIn('Last beat',str(director.validate(s)))
    def test_nonfinite_rejected(self):
        s=copy.deepcopy(self.scene);s['beats'][0]['actors']['lyra']['xyz'][0]=float('nan')
        self.assertIn('Non-finite',str(director.validate(s)))
    def test_authored_waypoints_exact(self):
        frames=director.sample(self.scene,director.DEFAULT_PARAMS)
        for beat in self.scene['beats']:
            for actor in self.scene['characters']:
                k=actor['id'];self.assertEqual(frames[beat['frame']-1]['actors'][k]['xyz'],
                                                beat['actors'][k]['xyz'])
    def test_no_collision_in_sample(self):
        self.assertGreater(director.evaluate(self.scene,director.DEFAULT_PARAMS)['minimum_actor_root_distance_m'], .65)
    def test_intrusion_rejected(self):
        s=copy.deepcopy(self.scene)
        s['beats'][3]['actors']['lyra']['xyz']=[.91,0.,0.]
        metrics=director.evaluate(s,director.DEFAULT_PARAMS)
        self.assertTrue(any('collision' in e or 'contact' in e for e in metrics['technical_errors']))
    def test_deterministic_and_non_destructive(self):
        old=copy.deepcopy(self.scene)
        a=director.improve(self.scene,iterations=20,seed=19)
        b=director.improve(self.scene,iterations=20,seed=19)
        self.assertEqual(a['parameters'],b['parameters'])
        self.assertEqual(a['audit'],b['audit'])
        self.assertEqual(self.scene,old)
        self.assertEqual(a['original_beats_sha256'], director.sha256(old['beats']))
    def test_accepted_improvements_not_worse(self):
        a=director.improve(self.scene,iterations=80,seed=22)
        self.assertTrue(a['improvement_accepted'])
        self.assertGreater(a['final_metrics']['score_kinematic_proxy'], a['initial_metrics']['score_kinematic_proxy'])
        self.assertFalse(a['final_metrics']['technical_errors'])
        self.assertTrue(any(not v['accepted'] for v in a['audit']))
        self.assertEqual(a['qa_gate'],'PRODUCTION_BLOCKED')
    def test_bad_params_blocked(self):
        s=copy.deepcopy(self.scene);s['params']['swing']=float('inf')
        with self.assertRaises(ValueError):director.improve(s)
    def test_original_identities_preserved(self):
        v=director.improve(self.scene,iterations=2)
        self.assertEqual(v['original_characters'],self.scene['characters'])
        self.assertFalse(v['final_metrics']['rendered_video_evaluated'])
        self.assertFalse(v['final_metrics']['professional_art_approved'])
    def test_unachievable_contacts_blocked(self):
        s=copy.deepcopy(self.scene);s['beats'][3]['actors']['kael']['xyz']=[7.0,0,0]
        metrics=director.evaluate(s,director.DEFAULT_PARAMS)
        self.assertTrue(any('contact' in e for e in metrics['technical_errors']))
        a=director.improve(s,iterations=5)
        self.assertFalse(a['improvement_accepted'])
        self.assertEqual(a['parameters'],s['params'])

class AssetTests(unittest.TestCase):
    def test_empty_glb_json_rejected_as_art(self):
        result=asset_gate.audit({'asset':{'version':'2.0'}})
        self.assertEqual(result['decision'],'PRODUCTION_BLOCKED')
        self.assertFalse(result['art_quality_verified'])
    def test_basic_glb_parsing_and_audit(self):
        data={'asset':{'version':'2.0'},'meshes':[{'primitives':[{'attributes':{'POSITION':0},'mode':4,'targets':[{} for _ in range(24)]}]}],
              'accessors':[{'count':6000}], 'skins':[{'joints':list(range(21))}]*2}
        payload=json.dumps(data).encode('utf-8');payload+=b' ' * ((4-len(payload)%4)%4)
        raw=struct.pack('<4sII',b'glTF',2,12+8+len(payload))+struct.pack('<I4s',len(payload),b'JSON')+payload
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'test.glb';file.write_bytes(raw)
            self.assertEqual(asset_gate.load_asset(file),data)
            report=asset_gate.audit(asset_gate.load_asset(file))
            self.assertIn('facial_expressivity_review_required_few_morphs',report['warnings'])
            self.assertEqual(report['numeric_checks']['max_morph_targets_on_one_primitive'],24)
    def test_invalid_glb_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'bad.glb';file.write_bytes(b'not-a-glb')
            with self.assertRaises(ValueError):asset_gate.load_asset(file)

class AudioTests(unittest.TestCase):
    def test_missing_inputs_are_not_aligned(self):
        with tempfile.TemporaryDirectory() as folder:
            r=ru_alignment.align(Path(folder)/'no.wav',Path(folder)/'no.txt',Path(folder)/'out.TextGrid')
            self.assertEqual(r['alignment_status'],'BLOCKED_NOT_ALIGNED')
            self.assertFalse(r['phoneme_timing_validated'])
            self.assertIn('valid_WAV_missing',r['errors'])

if __name__=='__main__':unittest.main()

class VisemeTests(unittest.TestCase):
    def test_phone_tier_parsing(self):
        from studio import textgrid_visemes
        data='''File type = "ooTextFile"\nObject class = "TextGrid"\nitem [1]:\n  class = "IntervalTier"\n  name = "phones"\n  intervals [1]:\n    xmin = 0.0\n    xmax = 0.1\n    text = "m"\n  intervals [2]:\n    xmin = 0.1\n    xmax = 0.2\n    text = "a"\n'''
        parsed=textgrid_visemes.parse_phone_tier(data)
        self.assertEqual(len(parsed),2)
        self.assertEqual(textgrid_visemes.PHONE_VISEMES['m'],'MBP')
    def test_missing_audio_blocks_visemes(self):
        from studio import textgrid_visemes
        with tempfile.TemporaryDirectory() as p:
            report=textgrid_visemes.audit_textgrid(Path(p)/'no.TextGrid',Path(p)/'no.wav')
            self.assertFalse(report['visemes'])
            self.assertEqual(report['status'],'BLOCKED_NOT_ALIGNED')
