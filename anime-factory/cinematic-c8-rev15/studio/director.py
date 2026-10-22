"""Deterministic, non-destructive choreography candidate search for C8 Rev15.

Produces sampled motion and an auditable decision log. Does not pretend to render or
inspect final pictures. The original scene, story and character assets are untouched.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
from pathlib import Path

KEYS = ("swing", "guard", "recoil", "anticipation", "follow", "breath", "weight")
TARGETS = {"swing": 1.12, "guard": .48, "recoil": .38,
           "anticipation": .45, "follow": .82, "breath": .023, "weight": .29}
LIMITS = {"swing": (.05, 1.6), "guard": (.03, .8), "recoil": (.01, .7),
          "anticipation": (.05, .8), "follow": (.1, 1.3),
          "breath": (0.0, .08), "weight": (.01, .7)}
DEFAULT_PARAMS = {"swing": .12, "guard": .11, "recoil": .03,
                  "anticipation": .07, "follow": .2, "breath": .004, "weight": .05}


def sha256(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def clamp(x, a, b):
    return max(a, min(b, x))


def smoothstep(x):
    x = clamp(x, 0.0, 1.0)
    return x*x*(3-2*x)


def bell(x, centre, width):
    x = (x-centre)/max(width, 1e-6)
    return math.exp(-.5*x*x)


def validate(scene):
    errors = []
    fps = scene.get('fps')
    total = scene.get('frames')
    if not isinstance(fps, int) or fps < 6 or fps > 120:
        errors.append('fps must be integer 6..120')
    if not isinstance(total, int) or total < 12 or total > 100000:
        errors.append('frames must be integer 12..100000')
    chars = scene.get('characters', [])
    if len(chars) != 2:
        errors.append('Exactly two character tracks are required for the Rev15 duel plugin')
    ids = [c.get('id') for c in chars if isinstance(c, dict)]
    if len(set(ids)) != len(ids) or any(not isinstance(v, str) or not v for v in ids):
        errors.append('Character IDs must be unique nonempty strings')
    if len(chars) == 2 and (chars[0].get('style') == chars[1].get('style')):
        errors.append('Distinct actor style IDs required; identity cannot be randomized')
    beats = scene.get('beats', [])
    if len(beats) < 3:
        errors.append('At least three authored beats required')
    last = 0
    for beat in beats:
        f = beat.get('frame')
        if not isinstance(f, int) or f <= last or not isinstance(total,int) or f > total:
            errors.append('Beat frames must be strictly increasing and inside shot')
            continue
        last = f
        actors = beat.get('actors')
        if not isinstance(actors, dict) or set(actors) != set(ids):
            errors.append(f'Missing actor poses at frame {f}')
            continue
        for name in ids:
            pos = actors[name].get('xyz')
            if (not isinstance(pos, list) or len(pos) != 3 or
               any(type(v) not in (int, float) or not math.isfinite(v) for v in pos)):
                errors.append(f'Non-finite or missing xyz for {name} at {f}')
        event = beat.get('event', 'movement')
        if event not in ('movement','hold','strike','block','reaction','recover'):
            errors.append(f'Unknown beat event {event}')
        if event in ('strike','block') and beat.get('attacker') not in ids:
            errors.append(f'Attacker identity missing at {f}')
    if beats and isinstance(total,int) and beats[-1].get('frame') != total:
        errors.append('Last beat must match frame count (prevents extrapolated endings)')
    if beats and beats[0].get('frame') != 1:
        errors.append('First beat must be frame 1')
    return errors


def root_sample(beats, actor_id, frame):
    """Root follows authored waypoints exactly (no story/scene-position mutation)."""
    if frame <= beats[0]['frame']:
        return beats[0]['actors'][actor_id]['xyz'][:]
    for a, b in zip(beats, beats[1:]):
        if frame <= b['frame']:
            t = smoothstep((frame-a['frame'])/(b['frame']-a['frame']))
            av = a['actors'][actor_id]['xyz']; bv = b['actors'][actor_id]['xyz']
            return [round(av[i]*(1-t)+bv[i]*t, 6) for i in range(3)]
    return beats[-1]['actors'][actor_id]['xyz'][:]


def sample(scene, params):
    beats = scene['beats']
    fps = scene['fps']
    ids = [c['id'] for c in scene['characters']]
    actors = {c['id']: c for c in scene['characters']}
    out = []
    for frame in range(1, scene['frames']+1):
        frame_data = {'frame': frame, 'actors': {}}
        for who in ids:
            style = actors[who]['style']
            # Style-specific rhythm; no random alterations to face, proportions or IDs.
            rhythm = {'counter': 1.0, 'agile': 1.17, 'heavy': .74}.get(style, 1.0)
            sign = 1 if who == ids[0] else -1
            attack = sum(bell(frame,b['frame']-3,5) for b in beats
                         if b.get('attacker') == who and b['event']=='strike')
            defend = sum(bell(frame,b['frame'],8) for b in beats
                         if b.get('attacker') != who and b['event'] in ('strike','block'))
            recovery = sum(bell(frame,b['frame']+6,9) for b in beats
                           if b.get('attacker') != who and b['event']=='strike')
            windup = sum(bell(frame,b['frame']-13,6) for b in beats
                         if b.get('attacker') == who and b['event']=='strike')
            follow = sum(bell(frame,b['frame']+8,8) for b in beats
                         if b.get('attacker') == who and b['event']=='strike')
            breathing = params['breath']*math.sin(frame*2*math.pi/(fps*2.65)*rhythm)
            # Angles are bone-intent controls in radians, not fabricated rendered metrics.
            frame_data['actors'][who] = {
                'xyz': root_sample(beats, who, frame),
                'yaw': 0.0 if sign > 0 else math.pi,
                'torso_pitch': round(sign*(params['anticipation']*windup-
                       params['recoil']*recovery+params['weight']*follow/2)+breathing,6),
                'weapon_arm': round(sign*(params['swing']*attack-
                                      params['follow']*follow+params['guard']*defend),6),
                'guard_arm': round(sign*(-params['guard']*defend*.8+
                                    params['weight']*windup/2),6),
                'pelvis_shift': round(params['weight']*(attack+recovery)*.1,6),
                'breath': round(breathing,6)
            }
        out.append(frame_data)
    return out


def evaluate(scene, params, frames=None):
    """Evaluates kinematics only; independent rendered-video and human reviews remain required."""
    if frames is None: frames = sample(scene, params)
    ids = [c['id'] for c in scene['characters']]
    fps = scene['fps']
    min_dist = float('inf'); max_speed = 0; near_still_active = 0; active_count = 0
    contact_distances = []; invalid = []
    for idx, state in enumerate(frames):
        p, q = [state['actors'][who]['xyz'] for who in ids]
        dist = math.sqrt(sum((p[k]-q[k])**2 for k in range(3)))
        min_dist = min(min_dist, dist)
        if idx:
            prev = frames[idx-1]
            distance_travelled = []
            joint_change = []
            for who in ids:
                old, curr = prev['actors'][who],state['actors'][who]
                distance_travelled.append(math.dist(old['xyz'],curr['xyz']))
                max_speed = max(max_speed, math.dist(old['xyz'],curr['xyz'])*fps)
                joint_change.append(sum(abs(curr[j]-old[j]) for j in ('torso_pitch','weapon_arm','guard_arm')))
            active = any(abs(idx+1-b['frame'])<12 and b['event'] in ('strike','block','reaction') for b in scene['beats'])
            if active:
                active_count += 1
                if sum(distance_travelled)+sum(joint_change) < .025:
                    near_still_active += 1
    if min_dist < .65:
        invalid.append(f'actor_collision:min_root_distance={min_dist:.3f}m')
    if max_speed > 7:
        invalid.append(f'unrealistic_root_speed:{max_speed:.2f}m/s')
    for beat in scene['beats']:
        if beat['event'] in ('strike','block'):
            poses = frames[beat['frame']-1]['actors']
            d = math.dist(poses[ids[0]]['xyz'],poses[ids[1]]['xyz'])
            contact_distances.append(round(d,3))
            if not .9 <= d <= 2.2:
                invalid.append(f'weapon_contact_staging_miss:frame={beat["frame"]},distance={d:.3f}')
    # Quality proxy deliberately rewards *meaningful articulation*, never mere pixel flicker.
    rewards = sum(1-((params[k]-TARGETS[k])/(LIMITS[k][1]-LIMITS[k][0]))**2 for k in KEYS)/len(KEYS)
    near_ratio = near_still_active/max(1,active_count)
    score = round(100*(rewards-.15*near_ratio),5)
    metrics = {'score_kinematic_proxy':score,'minimum_actor_root_distance_m':round(min_dist,3),
        'maximum_root_speed_m_s':round(max_speed,3),'active_near_still_ratio':round(near_ratio,4),
        'contact_distances_m':contact_distances,'technical_errors':invalid,
        'rendered_video_evaluated':False,'professional_art_approved':False}
    return metrics


def improve(scene, iterations=100, seed=20261022, patience=25):
    errors=validate(scene)
    if errors:
        raise ValueError('INVALID_SCENE: '+'; '.join(errors))
    baseline=scene.get('params',DEFAULT_PARAMS)
    if any(k not in baseline or not isinstance(baseline[k],(float,int)) or
            not LIMITS[k][0] <= baseline[k] <= LIMITS[k][1] for k in KEYS):
        raise ValueError('INVALID_PARAMS: all parameters must be finite and within bounded limits')
    rng=random.Random(seed)
    best={k:float(baseline[k]) for k in KEYS}
    initial_metrics=evaluate(scene,best)
    best_metrics=initial_metrics
    events=[]; stagnation=0
    for i in range(1, iterations+1):
        proposed=dict(best)
        keys=rng.sample(list(KEYS), k=1+rng.randrange(3))
        for key in keys:
            amount=rng.uniform(.10,.48)
            trial=best[key]+(TARGETS[key]-best[key])*amount+rng.uniform(-.028,.028)
            proposed[key]=round(clamp(trial,*LIMITS[key]),6)
        current=evaluate(scene,proposed)
        accept=(not current['technical_errors'] and current['score_kinematic_proxy']>
                best_metrics['score_kinematic_proxy']+1e-6)
        if accept:
            best=proposed;best_metrics=current;stagnation=0
        else: stagnation+=1
        events.append({'iteration':i,'accepted':accept,'score':current['score_kinematic_proxy'],
                 'technical_errors':current['technical_errors'],'changed_parameters':keys})
        if stagnation>=patience: break
    approved_frames=sample(scene,best)
    preserve_keys = copy.deepcopy(scene)
    # New motion is a *sidecar*; authored beats and character geometry never overwritten.
    return {
        'format':'c8-rev15-approved-kinematics-v1',
        'input_sha256':sha256(scene),
        'source_scene':preserve_keys.get('scene_id','unknown'),
        'original_characters':copy.deepcopy(scene['characters']),
        'original_beats_sha256':sha256(scene['beats']),
        'scene_fps':scene['fps'],'frame_count':scene['frames'],
        'initial_metrics':initial_metrics,'final_metrics':best_metrics,
        'improvement_accepted':best_metrics['score_kinematic_proxy']>initial_metrics['score_kinematic_proxy'] and not best_metrics['technical_errors'],
        'parameters':best,'iterations_executed':len(events),
        'audit':events,'frames':approved_frames,
        'qa_gate':'PRODUCTION_BLOCKED',
        'remaining_human_gates':['character_model_sculpt','scene_lighting_and_rendered_frames',
            'storyboard_readability','acting_and_fight_direction','voice_performance',
            'MFA_verified_audio_alignment','final_episode_acceptance','licensing']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene',type=Path)
    parser.add_argument('--output',type=Path,default=Path('output/REV15_APPROVED_MOTION.json'))
    parser.add_argument('--report',type=Path,default=Path('output/REV15_QA_REPORT_RU.json'))
    parser.add_argument('--iterations',type=int,default=100)
    parser.add_argument('--seed',type=int,default=20261022)
    args=parser.parse_args()
    if args.iterations not in range(1,1001):
        parser.error('--iterations should be 1..1000 (bounded search, no infinite loops)')
    scene=json.loads(args.scene.read_text(encoding='utf-8'))
    result=improve(scene,iterations=args.iterations,seed=args.seed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    report={k:v for k,v in result.items() if k not in ('frames','audit','original_characters')}
    report['accepted_candidates']=sum(e['accepted'] for e in result['audit'])
    report['rejected_candidates']=sum(not e['accepted'] for e in result['audit'])
    report['notes_ru']='Оценивается только кинематика; качество моделей, рендера, речи и драматургии НЕ подтверждено.'
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"REV15: {result['initial_metrics']['score_kinematic_proxy']} -> {result['final_metrics']['score_kinematic_proxy']}; accepted {report['accepted_candidates']}, rejected {report['rejected_candidates']}")
    print(f"Motion: {args.output}\nReport: {args.report}\nSTATUS: {result['qa_gate']}")

if __name__=='__main__':main()
