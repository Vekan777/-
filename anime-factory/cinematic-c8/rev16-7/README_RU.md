# C8 Rev16.7 — real Blender phalanx-bone implementation (2026-10-22)

**Actual source:** user's original C8 Rev16.6 complete package. Blender **3.6.23** Linux CPU, original full Rev16.6 .blend kept byte-identical. Studio gate remains `PRODUCTION_BLOCKED`.

## Source changes and verification
- Original 2 × 21-bone actor armatures preserved and extended to 2 × 51 bones: **60 new articulated phalanx bones** (proximal, middle, distal for five fingers on two hands of two actors).
- Four new meshes with individual per-phalanx skin weights and proper armature root parenting; original finger props remain in the native .blend for frames 1–566. The new poses are keyed only in additive NLA tracks on frames 567–650.
- SHA-256 digests of two original actor body actions unchanged. Original F-curves are not overwritten.
- Independent QA on the saved .blend: **73/73**. Controlled **same-frame 617** NLA-on vs NLA-off actual evaluated finger-tip mesh movements: 0.0538–0.0640 m across four hands. The first QA design comparing across different frames was rejected for incorrectly mixing root motion into the result.
- New export-only visibility override fixed an important defect: initial GLB export omitted all four articulated hand meshes because historical visibility keyframes hid them at the scene start. Corrected GLB re-import into an empty Blender scene confirms **two 51-joint armatures and four articulated finger meshes** with finger weights.
- Eight genuinely rendered consecutive Blender frames (611–618) at 384×216/12 fps = 0.667s. Also isolated technical hand renders with/without the phalanx NLA on the same frame 617. The actual model is still coarse, with visible segmented finger tubes.
- Full package rebuilt from an independently extracted ZIP: **four subprocess stages succeeded**, 73/73 checks re-passed, GLB reimport succeeded, Rev16.6 source stayed unchanged. Intentionally failing the rebuild preserved the previous outputs byte-for-byte.

## Full user-download archive
`AI_ANIME_FACTORY_C8_REV16_7_FINGER_PHALANX_FULL_WINDOWS.zip` — **27,886,021 bytes**, SHA-256 `4fe4f634b1dd4f33a4d8ba17ae4fe61d97e232d06280784f28d464e5d2478c8a`, **35 regular files + manifest**. ZIP CRC and per-file SHA-256 verified.

## Compact Windows archive
`AI_ANIME_FACTORY_C8_REV16_7_NATIVE_BLENDER_COMPACT_WINDOWS.zip` — **9,935,832 bytes**, SHA-256 `8728a9de3b0ec3ed6a0095b03e47f56fbb511f64e1c2128945de11da21beecd3`, **16 regular files + manifest**. CRC and per-file SHA-256 verified.

**Large .blend, GLB, complete build code, actual renders and videos are in the ChatGPT downloadable ZIP, NOT uploaded to GitHub.** Windows BAT launch scripts provided but the user's Windows hardware has not been tested.

**Open blockers:** coarse tubes instead of professional hand anatomy; no exact physical fingertip-to-sword contact; no advanced mesh skinning/hand sculpture; stylized childlike body proportions, mechanical choreography, no confirmed Russian acting/lip sync, no full episode and no artistic acceptance. Do not remove PRODUCTION_BLOCKED.
