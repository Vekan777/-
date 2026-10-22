# AI Anime Factory C8 Rev16 — real Blender art rebuild

**Status: experimental real 3D assets, `PRODUCTION_BLOCKED`.** This is NOT a professional finished anime episode.

## Verified real Blender 3.6.23 work (CPU)
- Loaded user-provided real `C8_REV14_CORRECTED_ART_ACTING.blend` (not surrogate models).
- Preserved original 1–518 frames at 12 FPS and source 21-bone armature for Lira and Kael. Both retain 24 expression morphs.
- Added 2 real UV maps, 6 **packed** new 768×768 texture images, 10 remapped existing materials, 43 tapered mesh hair locks bone-attached, 26 costume armor details, original identities retained.
- Two real Cycles comparison renders (frames 84 and 241, 864×486).
- Created append-only 519–566 battle montage (48 frames, 12 FPS), encoded four-second 512×288 H.264/AAC MP4 with original synthetic foley. The montage **reuses and retimes Rev14 authored poses**; it is not new studio-grade fight animation.
- Exported a real textured animated GLB (~32 MB): 2 skins, 24 morph targets per actor, 6 embedded images, 32 materials, 4 glTF animations.
- Blender fixed 28 WeightedNormal auto-smooth compatibility warnings; re-opened and checked resulting scene.
- Real bpy audit 11/11 passed; Python QA 8/8 passed. Motion check: 48 frames, 47 transitions, none below 0.009 pixel-delta threshold in this render (not an acting-quality metric).
- Actually rendered and evaluated 3 lighting candidates; conservatively rejected the 2 alternative proposals; original kept as rollback.
- Source `.blend` and actual final `.glb`, textures, MP4, scenes, 48 PNG render frames and full Python source are inside the downloadable **ChatGPT conversation ZIP**, not checked into GitHub to avoid enormous binaries. All 6 texture images are also embedded in the native Blender file.

## Technical acceptance vs artistic acceptance
Original models are still stylized with child-like proportions. No claim of natural acting, face realism, motion capture, physical hair, studio-grade fight choreography, fully verified Russian lip-sync/dubbing, or completed 20-minute episode. The benchmark is an objective proxy, not quality proof. `PRODUCTION_BLOCKED` remains correct.

## Next
Correct face anatomy and proportions with sculpt/retopology while retaining actor identity; test on actual native Windows 10 laptop; art-direct battle clips and feet/weapon impact; genuine Russian voices and phoneme alignment; full-episode automated continuity tests, legal rights for original IP, human studio review. Avoid reproducing Solo Leveling copyrighted assets.

## Building from Rev14 source
1. Use official Blender 3.6.23; load `C8_REV14_CORRECTED_ART_ACTING.blend`.
2. Run `studio/rebuild_scene.py` from the conversation ZIP with Blender background Python (creates separate art scene and real GLB).
3. Run `studio/append_battle_and_render.py` to add frame 519–566 montage. On CPU this can take minutes; restart with `studio/resume_render.py`.
4. Run `studio/production_quality_engine.py` (Python 3.10+, numpy, Pillow), scene audit in Blender, and manually inspect real frames.
Do not overwrite the original .blend; preserve checksums and keep human artistic acceptance gate.
