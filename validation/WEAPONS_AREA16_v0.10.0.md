# v0.10.0 — Weapons, damage states and Area 16

Based on approved v0.9.8 commit d4efb47954ebe73e297767ee906996061deea010.
Review branch: feature/weapons-area16-v0.10.0. No merge or public release.

## Artwork

- Dedicated red rocket launcher and green three-barrel wide cannon for the menu
  and Spencer's side-view and overhead weapon poses.
- Native equipment selector $04CA: 0 starter, 1 rocket, 2 wide cannon. Selection
  remains live through room transitions; the runtime only reads this address.
- Rocket shots keep their native sizes: 16×16 source pixels in side-view and
  8×8 in overhead play (64×64 and 32×32 at 4×). The side-view four-quarter
  layout remains a circle. The overhead shadow remains a separate sprite.
- Cover both overhead scene IDs ($004C values $13 and $14), damage palettes,
  hair overlays, dropped grenade and short hit-effect variants.
- Extend town scenery, interior, portrait, guard and pickup artwork to Area 16;
  add its narrow wheeled turret, the room contact's complete standing pose,
  and the observed door-transition palettes.
- Preserve original gameplay, animation cadence, object positions and collision.

## Replay evidence

| Replay | Movie frames | Matching RAM/PPU checkpoints | HD screenshots captured |
| --- | ---: | ---: | ---: |
| issue1-enemy.mmo | 2,010 | 68 | 334 |
| 16.mmo | 7,792 | 261 | 259 |
| Area 16 with wide-cannon test selection | 2,800 | 95 | 93 |
| Previous Area 5 boss recording | 1,940 | 66 | 64 |

All 490 checkpoints matched RAM and PPU memory, sampled every 30 frames plus
endpoints. There were no HD-loader or capture-script errors. All 64 Area 5
screenshots exactly match v0.9.8, including its corrected boss/thruster art.

The wide-cannon test sets the equipment byte in a separate diagnostic capture
script for both native and HD runs. This override is not in the pack or builder.
The supplied user recordings run without a state override.

Structural checks covered all atlas bounds, definition order, addition anchors,
virtual transparency fallbacks and 1,756 observed tile/palette pairs. Every
observed pair has a mapping; this alone does not prove each conditional mapping
was selected. Visual review used sampled screenshots and targeted damage,
projectile, grenade, weapon and town states, not every rendered frame.
Unrecorded states and later areas remain untested.

## Rebuild and verification

Run `python3 scripts/build.py --output <empty-directory>` with Pillow and NumPy.
The canonical builder uses the exact v0.9.8 runtime retained in baselines/v098,
validated against baselines/v098.json. This bypasses the older patch chain's
v0.9.7 hash mismatch in this environment. All 38 rebuilt runtime files matched.

The runtime ZIP contains only the installed pack's 38 files. Original art and
build inputs are retained in the source branch. No ROM, movies, emulator binaries
or diagnostic equipment override are included in the delivery.

Machine-readable evidence: v0100-build.json, v0100-replay.json,
v0100-reproducibility.json. `scripts/verify_v0100.py` consumes local replay
captures when those private recordings and emulator setup are available.
