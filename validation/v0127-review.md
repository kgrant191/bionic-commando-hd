# Area 3 v0.12.7 tree review

The old bark sampled and rotated individual tiles, leaving square patches
and an abrupt branch joint. The new painting supplies continuous weathered
grain through coherent trunk, branch, junction and broken-tip modules.
Both branch directions retain the original contours and grapple geometry.

## Deliverable

- `Bionic_Commando_HD_v0.12.7.zip`
- SHA256 `d799bb0a151c2fbd669009677383ffaa8525fdae9947c5ad39da20050df6092a`
- 47,487,636 bytes; 58 runtime files (56 PNG and two text files).
- All extracted files match the pack loaded by the completed playback and
  the output of a clean default rebuild.
- ZIP only; no ROM, emulator, recording, MP4, bundle or source painting.

## Playback and verification

The unchanged MesenCE 2.2.1 core completed all 11,110 input frames of `3.mmo`
in the single guarded run `v0127-pass1` (185.2 seconds), before packaging.
All 187 RAM and 187 PPU checkpoints match the original reference. Every-frame
rule auditing covers 3,175 graphics states with zero unmapped states.

All 28 tree patterns select the new artwork and retain their exact preceding
alpha contours. All 3,147 other graphics states retain their preceding rule
selections, counts and frame spans. All 884 common screenshots outside the
tree sequence are byte-identical to v0.12.6. The twelve passable snow patterns,
58 solid stone patterns, and both native plant warning phases are unchanged.
Door, robot, all destruction phases and wrapped-body edge checks pass.

The run produced 1,096 valid screenshots and one empty startup capture.
Full-size frames 1201 and 1441 were viewed. Tree contact sheets cover 1081,
1120, 1201, 1300, 1400, 1441, 1560, 1660, 1780, 1900, 1950 and 1960.
Later contact sheets cover 2010, 2401, 5041, 6301, 8371, 9793, 9855 and 10801.
This is complete emulator playback and every-frame auditing with sampled
visual review, not individual visual inspection of every frame.

## Scope

Only the supplied Area 3 recording was replayed. The 195,164 preceding tile
rules and 55 preceding PNGs remain unchanged. Twenty-eight outdoor-scoped
rules use one new atlas, with no new conditions or sprite additions.
No wider area regression, remote push, merge or release was performed.
