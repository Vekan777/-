# C8 Rev16.5 — actual Blender root-motion and connected hand repair

**2026-10-22 · Blender 3.6.23 Linux CPU · Technical test PASS, studio-art acceptance BLOCKED.**

The real Rev16.4 native .blend was the immutable input. Root-cause diagnosis at frame 617: replacement arms used a static old world transform while the actor armature object translated, so the rig-bent hand and arm-shell were visibly offset by roughly half a meter at some poses.

## What was actually built and reverified
- Four **contiguous skinned arm meshes** (120 vertices/110 faces each): shoulder, elbow, forearm, wrist and palm topology; source original arms kept for frames 1–566, new variants at 567–650.
- Four separate five-finger meshes (20 fingers in total), skinned to existing hand bones. These fingers are *procedural props without independently animated finger joints* and are **not** a studio-quality grip or weapon simulation.
- Corrected the world-motion mismatch by parenting both sleeve mesh and finger mesh to the moving armature **while retaining the armature deformation modifier**. This avoids the static world-transform problem in Rev16.4.
- Independent native Blender QA: **115/115 checks**. At 8 sampled action frames × 4 arms, maximum sampled endpoint mismatch between skinned sleeves and corresponding animated pose bone endpoints **0.03622 m** (not a full-scene collision clearance test).
- Old 11 sampled poses preserve digest `3719e12dae88cef59eb8f1846d7b1c108584c1cf6fcd82554ed99536d8258246`.
- glTF 2.0 exported and imported into fresh Blender: **2 armatures ×21 joints, 2 heads with >=24 shape keys, 4 connected arm meshes and 4 finger meshes**.
- Actual **12 sequential Eevee frames 611–622, 384x216, 12 FPS, 1.000s**; no looping held-frames animatic.
- **10/10 Python unittests** and safe rebuilding from the released full ZIP in a freshly extracted folder, four subprocess stages returning 0. Source .blend SHA256 unchanged.

## Deliverables (actual downloads in ChatGPT, not stored as heavy binaries in GitHub)
- Full Windows ZIP: `AI_ANIME_FACTORY_C8_REV16_5_REAL_HAND_CONTINUITY_FULL_WINDOWS.zip`: **26,448,396 bytes**, 27 ZIP entries; SHA256 `14c8214542a5d84a52d9fa815459f6c1e9e2cb37bdb29d45e036330183ab62c0`.
- Compact Windows ZIP: `AI_ANIME_FACTORY_C8_REV16_5_NATIVE_SCENE_COMPACT_WINDOWS.zip`: **9,687,632 bytes**, 19 ZIP entries; SHA256 `d5b82171552c1d24bbdaa18e551a402dc42ea1b33e736f4404d67e945c2a1c65`.
- Both ZIP archives verified: CRC + SHA256 of every entry (manifest does not hash itself).
- Source immutable .blend SHA256 `ae20ce1fb81bfad4b1a55eb5b02d581dfcff0e0bdcf4675a2ee894dfdf24938e`.

**Not achieved:** individually animated finger joints, believable hand-to-sword contact, full body anatomy, convincing cinematic action, Russian voice and MFA timing, full 20+ minute episode, Windows 10 real GPU test, licensing/artistic acceptance. Keep `PRODUCTION_BLOCKED`.

Start on Windows with Blender 3.6.23 x64, `START_HERE_WINDOWS.bat`. For full rebuilding additionally use Python 3.10+ and `REBUILD_SAFE_WINDOWS.bat`. A Windows hardware smoke run has **not** been executed in this environment.
