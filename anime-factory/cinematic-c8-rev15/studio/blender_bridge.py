"""Safe Blender 3.6 sidecar adapter: only creates an additive NLA animation in a COPY.

Run from Blender 3.6: blender -b source.blend --python studio/blender_bridge.py -- \
  --motion output/REV15_APPROVED_MOTION.json --mapping examples/BLENDER_RIG_MAPPING_TEMPLATE.json \
  --out output/REV15_EXPERIMENTAL.blend

NOTE: Requires user-supplied mapping of actual Rev14 armature/bone names.
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    import bpy
    extra=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser=argparse.ArgumentParser()
    parser.add_argument('--motion',required=True,type=Path)
    parser.add_argument('--mapping',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args(extra)
    motion=json.loads(args.motion.read_text(encoding='utf-8'))
    mapping=json.loads(args.mapping.read_text(encoding='utf-8'))
    source=Path(bpy.data.filepath).resolve()
    destination=args.out.resolve()
    if not source.is_file():raise RuntimeError('SOURCE_BLEND_REQUIRED')
    if source==destination:raise RuntimeError('REFUSE_OVERWRITE_SOURCE_BLEND')
    if motion['format']!='c8-rev15-approved-kinematics-v1':raise RuntimeError('INVALID_MOTION_FORMAT')
    if not motion['improvement_accepted'] or motion['final_metrics']['technical_errors']:
        raise RuntimeError('REJECTED_MOTION_NOT_APPLIED')
    actors=mapping.get('actors',{})
    controls={'torso_pitch':'X','weapon_arm':'X','guard_arm':'X'}
    axis_indices={'X':0,'Y':1,'Z':2}
    resolved={}
    # Preflight everything first (never partly modify a project with missing bones).
    for character in motion['original_characters']:
        who=character['id']; meta=actors.get(who)
        if not meta or not meta.get('object') or not meta.get('bone_map'):
            raise RuntimeError(f'MISSING_RIG_MAPPING:{who}')
        obj=bpy.data.objects.get(meta['object'])
        if not obj or obj.type!='ARMATURE':raise RuntimeError(f'NOT_ARMATURE:{who}:{meta["object"]}')
        for control in controls:
            bone_name=meta['bone_map'].get(control)
            if not bone_name or bone_name not in obj.pose.bones:
                raise RuntimeError(f'MISSING_BONE:{who}:{control}')
            if obj.pose.bones[bone_name].rotation_mode!='XYZ':
                raise RuntimeError(f'ROTATION_MODE_NOT_EULER_XYZ:{who}:{bone_name}')
        resolved[who]=obj
    f0=1; f1=motion['frame_count']
    for character in motion['original_characters']:
        who=character['id'];obj=resolved[who];meta=actors[who]
        obj.animation_data_create()
        action=bpy.data.actions.new('C8_REV15_DIRECTOR_ADDITIVE_'+who)
        # Euler additive action NLA. Original action and authored pose keys are preserved.
        for control in controls:
            bone=meta['bone_map'][control]
            axis=axis_indices.get(meta.get('axes',{}).get(control,'X'))
            if axis is None:raise RuntimeError(f'INVALID_AXIS:{control}')
            path='pose.bones["'+bone.replace('\\','\\\\').replace('"','\\"')+'"].rotation_euler'
            fc=action.fcurves.new(data_path=path,index=axis,action_group='REV15_DIRECTOR')
            for frame in motion['frames']:
                v=frame['actors'][who][control]
                fc.keyframe_points.insert(frame['frame'],v,options={'FAST'})
            for key in fc.keyframe_points:key.interpolation='BEZIER';key.handle_left_type='AUTO_CLAMPED';key.handle_right_type='AUTO_CLAMPED'
            fc.update()
        track=obj.animation_data.nla_tracks.new()
        track.name='C8_REV15_EXPERIMENTAL_OVERLAY'
        strip=track.strips.new('REV15_ADDITIVE_'+who,f0,action)
        strip.blend_type='ADD';strip.influence=1.0
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=f1
    bpy.context.scene.render.fps=motion['scene_fps']
    destination.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination))
    print('REV15_BLE​NDER_BRIDGE_EXPERIMENTAL_OUTPUT:',str(destination))
    print('ART_QA_STILL_BLOCKED: real meshes, sword path, eyes, face and acting require review')

if __name__=='__main__':main()
