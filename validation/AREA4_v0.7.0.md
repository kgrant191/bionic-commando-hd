# v0.7.0 — Area 4 and Area 13 regression review

## Changes

- Area 4: painted gorge, cave stonework, copper pipes, shaft mesh, vents and ledges; six guard pose records; communicator and flare equipment icons; boss dialogue expressions; radio/goal doorway trim.
- Area 13: white idle NPC designs, separate armed/unarmed green characters, a dedicated red runner cycle, and red rifle guard coverage matching its native identity. White guard artwork remains white during damage palette cycling.
- Capsule pill and burning flare replace the incorrect supply-case and medical-cross pickups. Real supply cases, medical-building signs and parachutes retain their separate roles.
- Shared native sprite anchors now use a single virtual addition per palette/offset. This removes 85 duplicate layers, which otherwise consumed MesenCE's four-sprites-per-pixel capacity and clipped overlapping enemies even when the duplicate artwork was invisible.

## Replay results

All five unique supplied recordings were replayed with the final runtime pack. The original unnumbered movie and `(1)` movie are byte-identical, so the duplicate is covered by the opening replay.

| Recording | Frames | RAM/PPU checkpoints | State mismatches | Missing tile matches |
|---|---:|---:|---:|---:|
| area4 | 11,830 | 100 | 0 | 0 |
| door | 1,081 | 11 | 0 | 0 |
| cave | 6,842 | 59 | 0 | 0 |
| area13 | 7,434 | 63 | 0 | 0 |
| opening | 40,442 | 339 | 0 | 0 |

Total: 67,629 recorded frames and 572 deterministic checkpoints. No HD loader errors. Every observed tile/palette was audited across the full recordings; every virtual layer has a fallback and all atlas crops are within bounds. The validator rejects duplicate native-anchor/palette/offset additions.

The separate `v070-*-replay.json` reports contain installed-pack hashes and checkpoint results. `v070-*-tile-audit.tsv` contains all-frame tile-rule observations.

## Visual review and limits

Rendered screenshots were sampled every 120 frames, with additional consecutive Area 13 frames 5998–6009 and 6660–6672 for hit/alarm palette changes. Review includes uniform colors, distinct NPC identities, red walking phases, pickup icons, doors, overlap, cave darkness, boss dialogue and transitions. Native alarm/background palette cycling is retained.

The audit proves that a replacement rule was selected, not that every tile is custom painted or that every rendered frame was inspected. Some effects, small silhouettes and unrecorded equipment states retain a smoothed/material baseline. Partially occluded figures may use the most common pose for a recognized head until their complete pose signature is visible. Later areas and unrecorded states are not covered. Starter weapon art remains the existing pistol design; full equipment-dependent weapon art is pending.

No ROM, memory, gameplay, geometry, controls, music or audio changes. Eight native rows remain cropped at the top and bottom as in the existing pack. This is a review build for MesenCE/Mesen-compatible HD pack format 109.
