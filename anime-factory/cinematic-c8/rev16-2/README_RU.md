# AI Anime Factory C8 Rev16.2 — foot IK, original duel direction, Blender QA

**Actual local Blender 3.6.23 technical prototype; status remains PRODUCTION_BLOCKED.**

The complete real Blender scenes, GLB, Python files, preview render and Windows launcher scripts are in the ChatGPT-downloadable ZIP packages, **not in this GitHub documentation checkpoint**. Prior Rev14/Rev16/Rev16.1 data were not overwritten.

## Verified on the real Rev16.1 scene

- The original 1–566 frame animation is preserved by **11 sampled deterministic pose checks**: SHA-256 `3719e12dae88cef59eb8f1846d7b1c108584c1cf6fcd82554ed99536d8258246`. This is not an exhaustive check of all 566 frames.
- Directed appended action **567–650** at **12 FPS**: weight-shift, staggered planted-foot targets, torso anticipation, two hand-guided swords, cinematic cuts, light flash, and original revealed sigil.
- 4 append-only leg IK constraints (disabled at/before frame 566); 60 foot pitch keyframe calibration cases and 32 toe-point-height control samples. Those numerical checks **do not imply visually perfect foot contacts**.
- On frame 617, the blade-tip proxy distance is **0.1081 m** (close but not physical collision). Five added directing cameras, eight prototype rigged boot/greave pieces and revised metal materials.
- Blender scene audit: **29/29** checks. Pure Python orchestrator tests: **10/10**. No creative or visual studio acceptance.
- glTF GLB exported and re-imported into clean Blender 3.6: **2 skeletons x21 joints**, 110 meshes, 4 animations, 24 morph targets on each of two new face meshes and 4 embedded images. Blender IK and expression drivers do not automatically guarantee identical downstream glTF playback: native .blend remains authoritative.
- An **actual continuous Eevee render of 24 frames** (frames 605–628) at **320x180, 12fps, 2.000 s**, not an animatic. Four separate proof frames at 640x360; the complete appended 84-frame sequence was **not** fully rendered.

## Release packages; ChatGPT conversation downloads, not committed binary assets

- `AI_ANIME_FACTORY_C8_REV16_2_REAL_COMBAT_ENGINE_FULL_WINDOWS.zip`: **22,700,248** bytes, **59** members; sha256 `a2e47ce14e1a7663d4eaefd62a66a369be162b0ac585ffdd4b1784ae24004428`.
- `AI_ANIME_FACTORY_C8_REV16_2_NATIVE_BLENDER_COMPACT_WINDOWS.zip`: **7,382,814** bytes, **20** members; sha256 `c684eb79bb7261e2c92eab1d18b5adc5c490f27985593feda690611f9ae031dd`.
- Both archives passed ZIP CRC and each archived file's SHA-256 manifest.

## Windows launch

Run `START_HERE_WINDOWS.bat` (Blender 3.6.23 x64 for Windows). `RUN_QA_WINDOWS.bat` rechecks model/bone/timeline proxies. With the full archive and Python 3.10+, `REBUILD_FROM_REV16_1_WINDOWS.bat` reconstructs from an immutable source and backs up the previous working .blend before any replacement; on failure it restores. Windows on the user's actual device is **not yet verified**.

## Current blocking art defects

Original low-detail/chunky adult body armor, incomplete clean leg/boot weight painting, separately keyed sword hand targets, expressive body acting and damage reactions, high-end hair/cloth, professional Russian voice + actual phoneme alignment, full episode acceptance, actual Windows performance and human art review remain unresolved.

**Only technical experimental approval. Do not merge a Studio-Final tag or lift PRODUCTION_BLOCKED.**
