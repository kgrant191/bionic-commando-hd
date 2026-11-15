# v0.7.3 — Area 13 conversation and scenery review

## Reported screens

| Reference | Correction | Replay evidence |
|---|---|---|
| 13-1 | Keep this in-person portrait style and the young white NPC identity. Replace only the surrounding dialogue frame and scenery. | Area 13 frame 1320 |
| 13-2 | Side-facing red soldier with the same burgundy helmet, sleeveless outfit and dark glasses as the standing rifle guard. Both mouth states have transparent backgrounds. | Area 13 frames 1740–1860 |
| 13-3 | Render one older white-cap portrait. The original top head tile occurred twice, once mirrored; a unique cheek tile now anchors the HD portrait. | Area 13 frames 2090–2300 |
| 13-4 | Complete supply-room doorway header and jambs; consistent spike-base materials. Alternating tall/short spikes also exist in the original and retain those heights. | Area 13 frames 2400–2820 |
| 13-5 | Side-facing green soldier with the helmet, green uniform and black straps of the standing armed contact. Both mouth states have transparent backgrounds. | Area 13 frames 4140–4320 |
| Scenery and borders | Painted sky, clouds, snow mountains and trees; consistent metal dialogue frames; replace native-looking barred façades. | Area 13 frames 1320, 2040, 4200 and alarm sequence |

## Implementation boundaries

Town replacements require Area 13 and exclude communication rooms, title,
world map, equipment and debrief. Dialogue strings and mouth timing remain
live. The background alarm follows the original PPU palette byte at 3F0E,
including dark, red and violet phases. Indoor black apertures remain opaque.
No ROM changes, game-memory writes, input edits or collision changes are used.

The older white portrait's unique anchor was checked against every dense
native capture containing that speaker (33 captures): exactly one matching
cheek tile at the expected offset in every case. The native mirrored head
previously caused a second HD portrait and consumed an extra sprite layer.

## Validation

Six full replays passed: 69,694 input frames, 642 matching RAM/PPU checkpoints,
zero unmatched native tile/palette keys and no HD-pack loader errors.
Replay results and installed-pack hashes are recorded in `v073-summary.json`
and the six `v073-*-replay.json` reports. A final Area 13-only façade guard
correction is followed by another complete 7,434-frame town replay; its
results are in `v073-final-area13-replay.json`. The correction requires the
barred opening near a façade tile, preventing its roof treatment from leaking
onto larger buildings. All 24 other pack files, every non-Area-13 rule
(with priority compared per tile/palette key), and its referenced conditions
are identical to the six-replay build; see `v073-final-scope-check.json`. Every-frame native tile/palette rule
selection is retained in the matching tile-audit TSV files.

The final aggregate result is `v073-final-validation.json`.

The five recordings outside Area 13 are compared with v0.7.2 captures in
`v073-outside-area13-pixel-comparison.json`. One dense Area 4 capture (10217)
returns the preceding decoded video frame; it is pixel-identical to baseline
frame 10216. This is capture timing, not a new drawing or game-state change.

## Review limits

Visual inspection uses full-screen checkpoints and dense samples around the
four town conversations, the supply room and overlapping enemies. Rule
coverage does not guarantee every drawing is finished. Unrecorded actions and
later areas remain outside this review.

The previously documented Area 1 top-edge scroll sliver around opening
frame 19320 remains a separate follow-up issue; this Area 13 pass does not
claim to fix it. The v0.7.2 first-descent bottom water-edge fix is retained.

No ROM, recording or savestate is distributed. The source bundle is incremental
from the user-pushed v0.7.2 commit `9799b049f55c0c2d9116c212964dca73debc200e`.
