# C8 Rev16.1 — real Blender facial rebuild checkpoint

**Technical prototype; artistic gate: PRODUCTION_BLOCKED.** This update is a follow-on to C8 Rev16 and does **not** replace earlier C8 Rev14/Rev16 sources.

## Actual implementation (Linux Blender 3.6.23 CPU, 2026-10-22)
- Procedurally built replacement 3D heads for Lira and Kael, each 468 vertices and 24 new morph targets. Reused the original 21-bone skeleton per character.
- The original deforming meshes and 24 original facial targets remain archived within the native .blend; Blender facial shape key drivers synchronize new heads, and a jaw/eyeblink bridge is included.
- Fixed a visually rejected trial with distracting procedural strands, corrected the gap between neck and head, and added separate back-of-head hair geometry.
- Original actor action keyframe-point snapshots: deterministic F-curve SHA-256 **2/2 unchanged**.
- Actual Blender scene QA 28/28, GLB structural QA 8/8, GLB import smoke test 5/5, and seven local Python quality-guard unittests passed.
- The glTF 2.0 GLB exports 2 skins with 21 joints each, four animation collections, 100 meshes, images, and two skinned 24-morph head meshes. glTF cannot guarantee faithful round-trip of Blender expression drivers: .blend is the editing source.
- The 14-frame 1.17s Eevee preview is **partial early staging footage** (before the final posterior hair revision). The 4.33s companion is a **storyboard animatic with held frames**, not a newly rendered 48-frame film.
- The full Windows zip was checked by CRC and per-file SHA-256 manifest; Windows execution on the user's laptop was not tested.

## Exact archives (available in the originating ChatGPT reply, not stored in GitHub)
- `AI_ANIME_FACTORY_C8_REV16_1_REAL_CHARACTER_ENGINE_FULL_WINDOWS.zip`: 26,214,548 bytes, SHA-256 `91354994d1b9734fed7aad92acbb06e4164fa080bb450b07b9b25882c8a78eee`.
- `AI_ANIME_FACTORY_C8_REV16_1_NATIVE_BLENDER_COMPACT_WINDOWS.zip`: 8,127,330 bytes, SHA-256 `4880d4c6f382fcf78a949b678c1cfc45e577137882c17432344cd6f1a7e1544b`.

GitHub checkpoint in this PR includes documentation and technical evidence; **full Blender scene, GLB and Python source for the program are in the downloadable ChatGPT archive, not committed here**.

## Outstanding blockers
The bodies and battle timing remain stylized and mechanically animated; true weight transfer and sword/foot contact need re-authoring. The new face mesh is a basic procedural sculpt, not high-end studio anatomy or paint. Human visual acceptance, verified Russian voice+phoneme alignment, a completed episode and real Windows 10 testing are missing. Do not lift `PRODUCTION_BLOCKED` solely because programmatic checks pass.
