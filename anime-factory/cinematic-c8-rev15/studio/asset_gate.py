"""Conservative glTF/GLB structure audit (not a substitute for visual art review)."""
import argparse
import json
import struct
from pathlib import Path


def load_asset(path):
    path=Path(path)
    if path.suffix.lower()=='.gltf':
        return json.loads(path.read_text(encoding='utf-8'))
    if path.suffix.lower()!='.glb':
        raise ValueError('Expected .glb or .gltf')
    with path.open('rb') as f:
        header=f.read(12)
        if len(header)!=12:
            raise ValueError('Truncated GLB header')
        magic,version,length=struct.unpack('<4sII',header)
        if magic!=b'glTF' or version!=2 or length!=path.stat().st_size:
            raise ValueError('Invalid GLB header or declared length')
        chunk_hdr=f.read(8)
        if len(chunk_hdr)!=8:raise ValueError('Missing JSON chunk')
        size,ctype=struct.unpack('<I4s',chunk_hdr)
        if ctype!=b'JSON' or size>16_000_000:
            raise ValueError('Unexpected GLB JSON chunk')
        payload=f.read(size)
        if len(payload)!=size:raise ValueError('Truncated JSON chunk')
        return json.loads(payload.decode('utf-8'))


def audit(data, expected_actors=2):
    meshes=data.get('meshes',[]); skins=data.get('skins',[])
    accessors=data.get('accessors',[])
    materials=data.get('materials',[])
    num_primitives=0;triangles=0;max_morphs=0;skinned_joints=[]
    warnings=[]
    for mesh in meshes:
        for p in mesh.get('primitives',[]):
            num_primitives+=1
            mode=p.get('mode',4)
            # No triangles can be inferred from strip/fan or absent indices safely.
            if mode==4:
                idx=p.get('indices')
                pos=p.get('attributes',{}).get('POSITION')
                ref=idx if idx is not None else pos
                if isinstance(ref,int) and 0<=ref<len(accessors):
                    triangles+=accessors[ref].get('count',0)//3
            max_morphs=max(max_morphs,len(p.get('targets',[])))
    for skin in skins:skinned_joints.append(len(skin.get('joints',[])))
    normal_textured=sum('normalTexture' in m for m in materials)
    pbr_textured=sum('baseColorTexture' in m.get('pbrMetallicRoughness',{}) for m in materials)
    metallic_textured=sum('metallicRoughnessTexture' in m.get('pbrMetallicRoughness',{}) for m in materials)
    details={"meshes":len(meshes),"primitives":num_primitives,"skins":len(skins),
        "joints_per_skin":skinned_joints,"triangles_estimated":triangles,
        "max_morph_targets_on_one_primitive":max_morphs,"materials":len(materials),
        "materials_with_normal_map":normal_textured,
        "materials_with_base_color_texture":pbr_textured,
        "materials_with_metallic_roughness_texture":metallic_textured}
    if len(skins)<expected_actors:
        warnings.append('too_few_skinned_actors')
    if skinned_joints and min(skinned_joints)<35:
        warnings.append('skeletal_expressivity_review_required_few_joints')
    if max_morphs<30:
        warnings.append('facial_expressivity_review_required_few_morphs')
    if triangles<15000:
        warnings.append('geometry_detail_review_required_low_triangle_budget')
    if not normal_textured:
        warnings.append('normal_map_material_detail_missing')
    if not pbr_textured:
        warnings.append('base_color_texture_missing')
    if not metallic_textured:
        warnings.append('roughness_workflow_requires_review')
    if not data.get('animations'):
        warnings.append('no_embedded_animation')
    if not skins and meshes:
        warnings.append('unskinned_characters_or_environment_only')
    return {"format":"c8-rev15-asset-audit-v1","numeric_checks":details,
            "warnings":warnings,"art_quality_verified":False,
            "decision":"ART_REVIEW_REQUIRED" if not warnings else "PRODUCTION_BLOCKED",
            "note":"Triangle/bone/morph counts and texture presence cannot establish professional appearance."}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('file',type=Path)
    ap.add_argument('--output',type=Path,default=Path('output/REV15_ASSET_AUDIT.json'))
    args=ap.parse_args()
    report=audit(load_asset(args.file))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
