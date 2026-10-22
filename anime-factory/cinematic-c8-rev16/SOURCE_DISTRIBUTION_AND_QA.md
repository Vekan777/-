## Source distribution and provenance

This repository contains a **tested runnable GLB audit** and evidence summaries for Rev16. The complete new Blender generator source, original reuploaded Rev14 `.blend`, packaged `.blend` artifacts and GLB, 4-second H.264/AAC proof, 48 original Cycles render frames and updated AI planner are delivered in **the C8 Rev16 Windows FULL ZIP generated in ChatGPT**. GitHub does **not** host the user-provided binary assets or the complete generator source in this PR; do not assume the README is an installable package.

### Fixed on Rev16
- Real Blender 3.6.23 local runtime used, not mocked.
- Legacy original armature choreography verified across all 518 frames and 40,404 checked numeric animation values: maximum absolute difference **0.0**.
- New rendered art scene 2 actual frames (84 & 241) and 48 appended rendered frames 519–566 (4 sec @12fps, synthetic Foley).
- GLB includes 2 rigged actors, 24 morph targets, 6 embedded texture images, four animations.
- UVs and packed textures integrated; original .blend not overwritten.
- 28 WeightedNormal autosmooth compatibility issues fixed and verified.
- 11 Blender checks, 8 Python QA tests, 4 internal AI planner tests passed.
- Three lighting candidates actually rendered, two alternatives rejected.

### NOT COMPLETE
Chibi/anime stylization still falls well short of adult high-end character anatomy, dynamic hair/cloth, believable studio fight staging, natural Russian acting/lip-sync, completed original IP pilot. CI and actual Windows user machine validation unconfirmed. Keep `PRODUCTION_BLOCKED`.

Example standalone audit:
`python studio/glb_audit.py C8_REV16_CHARACTERS_REAL_SKINNED.glb`
