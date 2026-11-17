# v0.10.1 — Overhead movement and Area 16 corrections

Review branch: `feature/movement-town-fixes-v0.10.1`.
Builds on v0.10.0 and includes its changes since the user's last pushed v0.9.8.
No merge or public release.

## Corrections

- Overhead Spencer previously assembled independently selected native-sized
  pieces. Overlapping walking cells, palette changes and duplicated directional
  anchors could select inconsistent parts. The new rules attach one complete
  image to a unique native anchor, verify Spencer's nearby hair overlay, and
  hide only his corresponding original components. Enemy bodies that share CHR
  patterns are distinguished by the local hair check.
- Cover the observed normal, red-flash and bright-flash palettes. Native
  invulnerability visibility/blinking is retained. Replacement art keeps a
  fixed size within each direction instead of refitting every stride's bounds.
- An input-controlled test identified the native downward and front-diagonal
  states. Down now faces forward; front diagonals use their own painted art.
  The rocket launcher has a long shoulder tube, circular muzzle and rear vent.
  All eight directions were reviewed for rocket, wide cannon and starter gun.
- Area 16 shield signs no longer depend on a neighboring tile staying on
  screen. All 26 sign patterns retain their painted crop while scrolling.
- The room contact uses a matching black-haired, bareheaded red-clothed portrait
  for both closed-mouth and talking states. Exterior white-uniformed contacts
  retain their separate artwork.
- The previous side-view weapons, large circular rocket projectile, menu,
  grenade, Area 16 terrain/rooms and Area 5 boss artwork remain intact.

## Verification

| Replay | Frames | Matching RAM/PPU checkpoints | Valid HD screenshots |
| --- | ---: | ---: | ---: |
| issue1-enemy.mmo | 2,010 | 68 | 2,009 |
| 16.mmo | 7,792 | 261 | 2,597 |
| Eight-direction diagnostic | 420 | 420 | 419 |
| Previous Area 5 boss | 1,940 | 66 | 64 |

The first emulator screenshot is empty and is excluded from valid-image counts.
The overhead replay was captured every frame, town every three frames, and
the boss every thirty frames. All 64 boss images are pixel-identical to v0.9.8.
The starter/wide diagnostic runs use a test-only equipment override, excluded
from the runtime and source delivery. They were inspected across all eight
directions; the original recordings run without input or memory overrides.

After the full town/boss capture, a final overhead-only edit narrowed native
piece suppression to avoid touching nearby enemies. The overhead and direction
tests were rerun with the final runtime. For town and boss, validation proves
that all image bytes, additions and non-overhead rules are identical, and their
sampled states never enter overhead mode. This equivalence is recorded rather
than claiming those two captures used the final hires.txt byte-for-byte.

Structural checks cover atlas bounds, condition definitions, unique addition
anchors and transparent virtual fallbacks. All 39 runtime files rebuild
byte-for-byte. The ZIP contains only runtime PNG/TXT files, with no ROM,
recordings, emulator or diagnostic overrides. The source bundle includes both
v0.10.0 and v0.10.1 changes from v0.9.8.

Visual review used dense movement strips, direction comparisons, recorded hit
states, scrolling edges and both portrait expressions. Capturing every frame
does not mean every rendered pixel was manually inspected. Unrecorded states
and later areas remain untested.

## Rebuild

`python3 scripts/build.py --output <empty-directory>`

`python3 scripts/verify_v0101.py --replay-root <private-replay-directory>`

The 52.6-second motion preview contains actual emulator captures at original
playback speed. Overhead footage is 60 fps; town captures at 20 fps are repeated
to the video's 60 fps. The static preview compares v0.10.0 and v0.10.1 captures.
