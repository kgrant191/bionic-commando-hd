# Area 2 v0.11.0 validation

The delivered pack was played through the supplied `2.mmo` in the native
MesenCE core. This report covers recorded behavior, not the entire game or
unrecorded weapon and enemy states.

## Area 2

- All 12,044 input frames completed, including the area-clear screen.
- 202 RAM and 202 PPU checkpoints matched the original-game replay; no
  checkpoint mismatches.
- The per-frame graphics-binding audit observed 2,901 distinct states and
  found no uncovered graphics states.
- 1,004 screenshots captured at 12-frame intervals supported visual review
  of motion sequences, scenery, carrier destruction, dialogue and end text.
- Green and red radio portraits retain their respective uniform colors.
- Compared the spike pit with the original: tips lie at the bottom of the
  view and can scroll out of sight. New artwork clarifies visible tips;
  camera, collision, geometry and damage remain unchanged.
- All 46 installed runtime files match the extracted delivery archive.

## Previous recordings

Replayed all 19 distinct earlier recordings in both the approved v0.10.6
baseline and the candidate: 133,317 input frames per build. Compared all
captured RAM/PPU checkpoints and 1,188 screenshot pairs. RAM and PPU matched.

The initial screenshot comparison had 22 differences. The asynchronous
capture can observe adjacent decoded frames. Visual review found movement,
projectile, transition or native blinking differences rather than changed
artwork. Synchronized follow-up comparisons resolved the highest-risk cases:

| Recording | Synchronized rendered frames | Pixel-hash differences |
| --- | ---: | ---: |
| Area 16 | 7,792, complete recording | 0 |
| Area 4 | 11,830, complete recording | 0 |
| Area 13 dialogue follow-up | First 4,480 | 0 |

Area 16 includes every recorded NPC conversation, the red wheeled cannon,
and scrolling buildings. No artwork regression was observed in the previous
recordings. Most earlier-area visual checks were sampled; this does not
assert exhaustive frame-by-frame visual review of every prior recording.

## Build and archive

All 42 approved baseline PNGs remain byte-identical and original rules retain
their relative order. Area 2 additions are scoped by level and scene state.
An independent rebuild reproduced all 46 runtime files byte-for-byte.
Structural validation found no duplicate sprite additions or invalid tile
references. See the adjacent JSON reports for counts and per-file hashes.

The final README correction changed only README.txt after graphics playback;
runtime PNGs and hires.txt did not change. Synchronized comparison reports
retain the earlier archive hash for provenance and also record the final
archive hash. Final archive: `Bionic_Commando_HD_v0.11.0.zip`, 43,691,389 bytes,
SHA-256 `c12ba30e3c57d42774640674f25d41c825e0a6488e172ee989075b02aa7e068a`.

Delivery contains the runtime pack only. No ROM, recording, emulator,
development files, MP4 or Git bundle is included.
