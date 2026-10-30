"""Offline visual-art direction engine for approved store site layouts.

Honest capabilities: deterministic layout selection + artwork provenance + asset gates,
not a generative neural model. The screenshots are made by Chromium, not this module.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, math, sys

ROOT=Path(__file__).resolve().parent.parent
MODES=('faithful','refined','author')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_contract(root=ROOT):
 root=Path(root)
 rules=json.loads((root/'ART_DIRECTION_RULES_V59.json').read_text('utf8'))
 assets=json.loads((root/'APPROVED_ART_ASSETS_V60.json').read_text('utf8'))
 errors=[]
 for name,meta in rules['accepted_reference_assets'].items():
  p=root/meta['file']
  if not p.is_file() or sha(p)!=meta['sha256']:errors.append('reference corrupted: '+name)
 for mode,meta in assets.items():
  p=root/'assets_source'/meta['output']
  original=root/meta['source']
  if not p.is_file() or sha(p)!=meta['sha256']:errors.append('creative asset corrupted: '+mode)
  if not original.is_file() or sha(original)!=meta['source_sha256']:errors.append('art original corrupted: '+mode)
 for mode in MODES:
  if mode not in assets:errors.append('missing visual mode: '+mode)
 if len({rules['modes'][m]['layout'] for m in MODES})!=3:errors.append('modes are not structurally unique')
 return {'pass':not errors,'errors':errors,'approved':len(rules['accepted_reference_assets']),'creative_assets':len(assets),'distinct_layouts':len({rules['modes'][m]['layout'] for m in MODES})}


def compose_brief(kind,*,brand='Магазин ЕМЕЛЯ',category='grocery',mood='warm',image_rights='user_approved',hero_strategy=None):
 """Creates a deterministic design plan, separate from the real site content.
    No network, no secret keys, no invented product prices or claims.
 """
 if kind not in MODES:raise ValueError('Unsupported mode')
 if image_rights not in ('user_approved','CC0_verified','original'):raise ValueError('Unverified image rights')
 profiles={
  'faithful':{'layout':'approved_header_hero_feature_categories','hero':'panoramic_approved_art','hero_alignment':'text_left_image_right','cards':'compact_two_rows','footer':'light_approved','botanical':1,'text_priority':'high','photo_priority':'high','mobile':'photo_then_centered_content'},
  'refined':{'layout':'editorial_split_hero_curated_photography','hero':'warm_editorial_approved_art','hero_alignment':'photo_left_text_right','cards':'large_editorial_photography','footer':'green_premium','botanical':1,'text_priority':'high','photo_priority':'very_high','mobile':'photo_then_centered_content'},
  'author':{'layout':'full_bleed_photographic_cover_parchment_sidebar','hero':'rustic_creative_approved_art','hero_alignment':'text_panel_left_photo_right','cards':'side_catalog_with_gallery','footer':'dark_independent','botanical':2,'text_priority':'high','photo_priority':'very_high','mobile':'photo_then_centered_paper_card'}
 }
 plan=profiles[kind].copy()
 plan.update({'schema':1,'mode':kind,'brand':brand,'sector':category,'mood':mood,'image_rights':image_rights,'default_product_price':None,'claim_true_discount':False,'owner_review_required':True})
 if hero_strategy and hero_strategy not in ('original','approved_art'):raise ValueError('Hero strategy must be approved_art or original')
 if hero_strategy:plan['hero_strategy']=hero_strategy
 return plan


def install(folder,mode,root=ROOT):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 audit=source_contract(root)
 if not audit['pass']:raise RuntimeError('Rejected: '+str(audit['errors']))
 (folder/'DESIGN_AUTOPILOT_PLAN.json').write_text(json.dumps(compose_brief(mode),ensure_ascii=False,indent=2),'utf8')
 (folder/'APPROVED_ASSET_PROVENANCE.json').write_text((Path(root)/'APPROVED_ART_ASSETS_V60.json').read_text('utf8'),'utf8')
 return audit

if __name__=='__main__':
 audit=source_contract();print(json.dumps(audit,ensure_ascii=False,indent=2));sys.exit(0 if audit['pass'] else 1)