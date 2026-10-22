"""Blender 3.6 native validation for two edited ART M1 fight scenes.
Run: blender -b SCENE_01_A1_EDITABLE.blend -t 2 --python native_validate_a1.py
These checks are structural, not a substitute for studio artistic acceptance.
"""
import bpy
import json
s=bpy.context.scene
skels=[x for x in bpy.data.objects if x.type=="ARMATURE"]
rows=[]
for rig in skels:
    ik=[(b.name,c.name,c.type) for b in rig.pose.bones for c in b.constraints if c.type=="IK"]
    meshes=[o for o in bpy.data.objects if o.type=="MESH" and o.parent==rig and o.data.shape_keys]
    rows.append(dict(name=rig.name,bones=len(rig.data.bones),ik=ik,shape_key_counts=[len(m.data.shape_keys.key_blocks)-1 for m in meshes]))
curves=[o for o in bpy.data.objects if o.type=="CURVE" and o.name.startswith("A1")]
lights=[o for o in bpy.data.objects if o.type=="LIGHT" and o.name.startswith("A1")]
materials=[m for m in bpy.data.materials if m.name.startswith("A1")]
result={"episode":s.get("A1_EPISODE"),"art_status":s.get("A1_ART_STATUS"),"rigs":rows,"curves":len(curves),"lights":len(lights),"materials":len(materials)}
assert len(skels)==2,result
assert all(r["bones"]==21 and 24 in r["shape_key_counts"] for r in rows),result
assert sum(len(r["ik"]) for r in rows)>=2,result
assert len(curves)>=50 and len(lights)>=4 and len(materials)>=5,result
assert s.get("A1_ART_STATUS")=="DRAFT_TESTED_VISUAL_PASS_NOT_PROFESSIONAL",result
assert s.camera is not None
print("A1_NATIVE_QA_PASS",json.dumps(result,ensure_ascii=False))
