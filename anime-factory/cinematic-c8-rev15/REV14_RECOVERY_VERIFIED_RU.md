# C8 Rev14 → Rev15.1: verified original recovery (2026-10-22)

**Do not overwrite the original Rev14 Blender project. Studio gate: PRODUCTION_BLOCKED.**

The user supplied all five original Rev14 files again. This recovery was verified *against the actual uploaded bytes*, not reconstructed from approximate filenames.

## Source identity
- Full Rev14 original ZIP: `dc61d954544b9fb595039a967259d8a5b106006994fb8818c1424d8ca1734125`, 67,454,473 bytes. ZIP CRC and all **563 file manifest SHA256 entries** passed.
- Compact Rev14 ZIP: `20794e2744be115adf0a1456439350c4e849b23a4378f2bfecd917e4b89f5271`.
- Original QA reports ZIP: `fba8c0d93e4a47cfbdcc69b863eef626187cb65762f08e6461744cdc7279facb`.
- Corrected .blend: `6ff5ef6b6550192106ec976fe74f555b644916dd16dbc771e3adb0d6ff888bbf`, 16,906,228 bytes.
- Corrected .glb: `2c67168ca111b9f5f4ee1f318f1f11011d3a4e6e1902ea305a134a308f0db0de`, 19,559,856 bytes.
- The separate corrected .blend and .glb are byte-for-byte identical to those in the full Rev14 ZIP.

## Real geometry scan
- Skinned character objects: `LIRA | ARMATURE 22 BONES` and `KAEL | ARMATURE 22 BONES`; **21 skin joints each**.
- Two organic character meshes + two swords, four meshes, 28 primitives, **about 58,784 triangles total**, **24 morph targets per organic mesh**, eight glTF animations.
- No image/texture payload is embedded in corrected GLB; its 20 materials have zero `baseColorTexture`, `normalTexture`, and `metallicRoughnessTexture` entries.
- Original Rev14 choreography: 518 authored frames at 12 fps, ten claimed authored contact times.
- Rev15 sandbox scene: 192 frames at 24 fps, *NOT the same timeline*; applying directly to 1–518 may overwrite original choreography.
- Proposed **append-only, not automatically applied** experiment begins at Blender frame 519, keeps source 12 fps and preserves frames 1–518.
- `bpy` Blender runtime was unavailable in the recovery environment; actual .blend rig rotation modes/append safety must be verified on Blender 3.6.

## Actual release artifact
`AI_ANIME_FACTORY_C8_REV15_1_RECOVERED_REAL_ASSETS_WINDOWS.zip` (65,494,296 bytes, SHA256 `34c9d0d1706eb0c9416fe2e98d053c47f533387f5369217a95feaf3168064560`) is a ChatGPT conversation download, not stored in GitHub. Includes full unchanged Rev14 ZIP + existing Rev15 source + read-only verification/staging scripts + Blender inspection script + Russian setup instructions. Freshly extracted ZIP: **14/14 new tests passed**, **18/18 original Rev15 tests passed**, source CRC/SHA pass.

## Remaining artistic blockers
Faces, costumes, PBR/UV textures, choreography, camera direction, staged voice acting, actual Russian phoneme alignment, and full-episode acceptance remain unfinished. Do not mistake this source-recovery fix for new studio-grade 3D characters.
