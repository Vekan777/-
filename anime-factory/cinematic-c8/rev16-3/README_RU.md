# AI Anime Factory C8 Rev16.3 — actual Blender grip/sole/wardrobe checkpoint (2026-10-22)

**Technical prototype only. Art gate `PRODUCTION_BLOCKED`.**

Created from the **real C8 Rev16.2 .blend**, retaining immutable source and legacy C8 assets. Heavy Blender/GLB/media files and complete build scripts live in the downloadable ChatGPT ZIP, **not in GitHub**. This PR is a verified checkpoint; do not claim a GitHub binary release.

## What is implemented
- 12 additional original Blender-mesh wardrobe objects with actual armature modifiers and animation visibility starting at frame 567 (6 details per actor), including gauntlets and layered lower garments. This is low-poly procedural costume work **not** a professional adult character overhaul.
- Measured deformed toe mesh surfaces over **84 frames x 4 feet = 336** cases. The first IK adjustment still left 29 cases below -1.2cm; a second limited bisection pass corrected an additional 34 case readings. Final minimum approximately **-0.0041m**, no sampled proxy toe mesh below -0.012m. This is **not** a claim of accurate foot skating, all-body collision, or floor realism.
- Sword grip proximity checked in **84 frames x 2 actors = 168**: max wrist-to-hilt proxy gap `0.04575m`, below the 9cm gate. No finger animation or validated sword physics.
- 11 original pose sample frames have unchanged SHA-256 `3719e12dae88cef59eb8f1846d7b1c108584c1cf6fcd82554ed99536d8258246`.
- Opened the final native .blend in an independent Blender 3.6.23 process: **46/46** checks passed. Exported final GLB and *reimported it into clean Blender*: 2 x 21 joint skeletons, 122 meshes (12 wardrobe additions), four animation sets, 24 face morph channels per actor, six images.
- 5/5 local quality-gate unit tests passed. **All five stage processes** of the separate from-source rollback-capable orchestrator completed with exit_code=0, leaving original source unchanged.
- Actual **15 continuous Blender-rendered frames, 384 x 216 at 12fps, 1.25 seconds**. The entire 84-frame duel or full episode was NOT newly rendered.

## Art review
Side-by-side still frames show only modest visible art improvement. Large unconvincing white hands, oversized shoulder/torso anatomy, stiff blocking, simplistic costuming, incomplete expression/voice and camera acting remain. Render pixels and human artistic review outrank structural test scores.

## Verified downloadable archives
- Full Windows ZIP `AI_ANIME_FACTORY_C8_REV16_3_REAL_STUDIO_ENGINE_FULL_WINDOWS.zip` — 19,787,407 bytes, **36 entries**, SHA256 `ad607bb179ca772b94d147bde8b4f1614c5db6062cc9da5b7b1fb28f649cd2ea`.
- Compact native project `AI_ANIME_FACTORY_C8_REV16_3_NATIVE_BLENDER_COMPACT_WINDOWS.zip` — 6,174,963 bytes, **18 entries**, SHA256 `a06f391a6a5fd11a818c56ea2826cb8c8e32f2d886afc1e60bfc51d572367424`.
- ZIP CRC and **all per-file SHA-256 manifest entries** verified.
- Windows 10 user-device test not yet carried out. Linux Blender 3.6.23 CPU QA only.

**Never remove `PRODUCTION_BLOCKED` without new art, voice, timeline/full-episode and actual hardware validation.**
