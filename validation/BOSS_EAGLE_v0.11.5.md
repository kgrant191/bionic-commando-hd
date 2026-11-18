# Generator/boss entrance eagle — v0.11.5

The two detailed native eagle-header cells now select a gold eagle plaque
across every currently mapped background palette: five palette variants,
ten rules. Radio-arrow and ordinary doorway patterns remain unchanged.
This is the documented marker to retain when adding later boss entrances.
The marker stays within the native 16×8-pixel eagle footprint; no new
neighbor lookups, gameplay edits or shared one-pixel replacements were added.

## Playback

The exact ZIP was extracted and installed for a complete, single-attempt
12,044-frame playback of `2.mmo` (178.2 seconds; exit 0). Protected screen
buffers were enabled. No crash or loader errors occurred; 202 RAM and 202 PPU
checkpoints matched the original. All 3,280 audited graphics states had
matching rules. All 4,340 existing Area 2 neighbor references remain bounded.

348 screenshots were captured. Visual checks covered ordinary doors (733,
1201, 3151), rifleman steps (2876/2882/2889/2896), green/red dialogue
(3841/4321/4561), the scrolling eagle doorway (9553/9601/9721), entry into
the generator room (10093) and Area 02 Clear (11533).

A targeted 500-frame prefix of the earlier closed-door recording was also
played, original and HD. All ten RAM and ten PPU checkpoints matched.
Frame 440 confirms the eagle stays above the intact closed panel and Spencer
remains in front. This was a doorway check, not a full earlier-area regression.

Shared-pattern validation covers the other existing palette variants. All
46 previous runtime PNGs and all 185,421 existing tile rules are unchanged.
No claim is made that unrecorded future-area palettes have been validated.

## Archive

- `Bionic_Commando_HD_v0.11.5.zip`
- 49 runtime PNG/TXT files; 45849753 bytes
- SHA256 `aa58a1314e6cce7a819a3aa588c228ab34c77d16b19a373df98782f4f5db86d9`
- Full playback: `replay-area2/eagle-door-delivery`
- Targeted check: `replay-area2/eagle-closed-door-check`
- Reports: `v0115-verification.json`, `v0115-closed-door.json`,
  `v0115-build.json`, `v0115-package.json`

ZIP only; no ROM, emulator, recordings, source art, MP4 or Git bundle.
