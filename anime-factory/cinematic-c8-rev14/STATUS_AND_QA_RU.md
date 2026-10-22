# AI Anime Factory C8 Rev14 — CPU Quality Autopilot

**Technical release, artistic studio acceptance = false.** Released as a C8 iteration (not a finished professional anime factory). Binaries and complete source are in the ChatGPT ZIP downloads, not falsely claimed to live in GitHub.

## Final checked downloads
- AI_ANIME_FACTORY_C8_REV14_CPU_AUTOPILOT_WINDOWS.zip — 67,454,473 bytes, 563 source/data files, sha256 dc61d954544b9fb595039a967259d8a5b106006994fb8818c1424d8ca1734125
- C8_REV14_CPU_AUTOPILOT_COMPACT_WINDOWS.zip — 18,214,142 bytes, 41 files, sha256 20794e2744be115adf0a1456439350c4e849b23a4378f2bfecd917e4b89f5271
- C8_REV14_VERIFIED_QA_REPORTS.zip — 2,925,566 bytes, 19 files, sha256 fba8c0d93e4a47cfbdcc69b863eef626187cb65762f08e6461744cdc7279facb
All ZIP CRC and per-file SHA-256 manifest checks passed. Final GLB is **C8_REV14_CORRECTED_SKINNED.glb**, exported from the corrected Blender project (avoiding a stale model/scene mismatch).

## Actual verification
- Real Blender 3.6.23 CPU build on a fully available 518-frame source scene; two 21-bone skinned characters; 24 nonempty facial shapes; 3,072 face key insertions; procedural texture microdetail in ten materials.
- First automated pose correction was rejected for worsening the intended asymmetry measure; fixed candidate increased mean torso pitch difference at authored contacts 0.1866→0.5166 radians, passed 10 sword-contact geometry checks with no unintended nearby crossings.
- Full 518 real Workbench CPU frames at 224×126 / 12 FPS, 43.166984s H264/AAC MP4 and three separate Cycles 640×360 stills.
- Actual decoded-video motion QA, same algorithm/threshold: Rev12 472/517 near-still transitions; Rev14 271/517. Rendering details and framing also affect pixel differences; this is not a studio animation score.
- Audio contains one prior user-provided synthetic Russian speech sample and ten procedural Foley impacts, not professionally recorded Russian acting.
- Nine Python tests passed and exported final corrected glTF 2.0 GLB with skins and animations.
- Optional genuine Russian acoustic forced-alignment bridge to externally installed Montreal Forced Aligner and `russian_mfa`, but MFA was NOT installed or executed in this QA environment. Its status correctly reads BLOCKED_NOT_ALIGNED; no fake phoneme timing.
- PRODUCTION_BLOCKED release gate flags low visual motion, missing real forced alignment/voice performance, immature sculpt and battle choreography, incomplete 20+ minute episode.
- Windows BAT/PowerShell starters create Blender output and STUDIO_TOOLS/REPORT_FOR_CHATGPT.zip; the user's actual Windows machine was NOT tested.
- Full bundle retains original Rev11 sources and source Rev12 .blend, but is not a full integrated migration of V19–V50.

The result remains stylized and far short of Solo Leveling/A-1 Pictures studio quality.
