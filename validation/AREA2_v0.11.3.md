# Area 2 blue slime and walking correction — v0.11.3

Scope: the supplied `2.mmo`. No earlier-area recordings were replayed.

## Corrections

- Replaced watery hazard sprites with dense blue slime blob poses. Native
  squashing/stretching phases, motion and collisions remain live.
- Replaced the ground strips and pipe discharge with thick blue slime pools
  and connected pipe-to-pool joins, rather than watery streaks or spray.
- The 20 background pattern/palette pairs and nine sprite patterns are still
  gated to Area 2. Future areas and other slime palettes are not recolored.
- The short rifleman was incorrectly assigned the same kneeling image for
  native poses 18 and 19. Those poses now select cells 0 and 2 from the existing
  painted enemy atlas, using one body scale and the native animation cadence.
- Retained the opaque doorway and bounded-neighbor crash correction.

## Playback and validation

A 3,100-frame protected-buffer probe confirmed the initial slime behavior and
rifleman step change. The exact final ZIP was then extracted, installed and
played through all 12,044 inputs in one run, with protected screen buffers
active and no retries. Exit code was 0; no memory fault or loader error occurred.

All 202 RAM and 202 PPU checkpoints matched the original movie. All 3,230
observed graphics states had matching rules. Structural checks found no invalid
tile references, duplicate additions or missing virtual fallbacks. All 4,232
Area 2 neighbor references were bounded before their evaluation.

The run captured 772 screenshots. Visual review included blob phases near
1186–1248, pools/outlets at 1201 and 1453, player damage at 2644, rifleman steps
at 2876/2882/2889/2896 and 5270/5278/6205/6212, the green/red radio portraits
at 3841/4321, and the clear screen at 11533. Both movement directions show
alternating steps. The review is sampled; it does not claim every frame or
unrecorded gameplay state has been visually inspected.

## Delivered archive

- `Bionic_Commando_HD_v0.11.3.zip`
- 47 runtime files; 45722284 bytes
- SHA256 `f37f8e24cecd25fcda4c421e80061a0d2f0003cfda3b520d4d9e8819fdf312e4`
- Playback: `replay-area2/slime-walk-delivery`
- Reports: `v0113-verification.json`, `v0113-build.json`,
  `v0113-enemy-poses.json`, `v0113-package.json`.

Only runtime PNG/TXT files are included. No ROM, recording, emulator, MP4,
source art atlas or Git bundle is packaged.
