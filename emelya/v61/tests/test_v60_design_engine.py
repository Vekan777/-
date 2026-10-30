from pathlib import Path
import sys,hashlib,json,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engine'))
from design_autopilot import source_contract,compose_brief,MODES
from asset_manager_v60 import http
from release_guard_v60 import verify_release
ROOT=Path(__file__).resolve().parents[1]


def test_source_contract_has_6_accepted_references_and_3_art_assets():
 r=source_contract(ROOT);assert r['pass'],r['errors'];assert r['approved']==6 and r['creative_assets']==3


def test_modes_have_meaningfully_different_layouts():
 plans=[compose_brief(m) for m in MODES]
 assert len({p['layout'] for p in plans})==3
 assert len({p['hero'] for p in plans})==3
 assert len({p['cards'] for p in plans})==3
 assert all(p['owner_review_required'] and p['default_product_price'] is None for p in plans)


def test_unverified_license_blocked():
 with pytest.raises(ValueError):compose_brief('author',image_rights='unknown')
 with pytest.raises(ValueError):compose_brief('fake')


def test_network_fetch_rejects_arbitrary_urls_without_network():
 for u in ['http://upload.wikimedia.org/a.png','https://example.com/p.jpg','file:///etc/passwd','https://upload.wikimedia.org.evil.net/a','https://user@upload.wikimedia.org/a']:
  with pytest.raises(ValueError):http(u)


def test_screens_from_new_engine_are_not_old_when_available():
 screens=Path('/mnt/data/EMELYA_RELEASE_V61')
 sites=Path('/mnt/data/EMELYA_V61_SITE_BUILD')
 if not screens.exists() or not sites.exists():pytest.skip('Release screenshots not generated yet')
 r=verify_release(ROOT,screens,sites,'/mnt/data/EMELYA_RELEASE_V60_1')
 assert r['success'],r['failures']


def test_main_page_runtime_uses_art_and_owner_override(tmp_path):
 from build_emelya_premium import build
 p=build(tmp_path/'faithful','faithful')
 seed=json.loads((p/'premium_seed.json').read_text('utf8'))
 assert 'faithful' in seed['creative_banners']
 runtime=(p/'server.py').read_text('utf8')
 assert "banner==seed['banner']" in runtime
 assert "mode in ('faithful','refined','author')" in runtime
 assert (p/'DESIGN_AUTOPILOT_PLAN.json').exists()