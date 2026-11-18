# Area 3 v0.12.5 original-style terrain review

Area 3 again follows the original material arrangement: warm rounded rock,
dark soil below platforms, a green grass fringe with a thin snow cap, and
white snow patches along the cliff. Muted gray stone marks recessed backing.
The trees, deep sinking powder, pendant, doorway, industrial section, enemies,
robot boss and corrected explosions retain their preceding artwork.

## Deliverable

- `Bionic_Commando_HD_v0.12.5.zip`
- SHA256 `4035c7016b7c4ea1afd8f6ad10e6f0a30974069ee1fe814566892d2173f9aef7`
- 47,404,102 bytes; 56 runtime files (54 PNG and two text files).
- Every runtime file matches a clean default rebuild byte for byte.
- Install ZIP only; no ROM, emulator, recording, MP4, bundle or source paintings.

## Completed final playback

`v0125-final-terrain` completed all 11,110 input frames of `3.mmo` in one
uninterrupted guarded run using the unchanged MesenCE 2.2.1 core. Playback
finished before packaging. All 56 files extracted from the resulting ZIP
match the files loaded by that completed playback.

All 187 RAM and 187 PPU checkpoints match the original recording reference.
Every-frame auditing covered 3,181 graphics states with zero unmapped states.
All 296 changed material pairs select the new atlas or the preserved doorway.
The 16 door cells, five explosion patterns, 281 robot states and three-frame
wrapped-edge pixel comparison passed. No original explosion fallback was used.

All 2,872 other graphics states retain the same rules, observation counts and
frame spans as v0.12.4. All 260 common non-outdoor screenshots are identical.
The final run produced 798 valid screenshots and one empty startup capture.

## Visual review

The early review exposed overly fine rock/grass grain, an enlarged rock sample
with a visible repeat, and square soil transitions under ledges. The final
material uses a dedicated broad-stone tile, readable grass and a continuous
soil fade; the extra dirt bands across the rocky face were removed.

Reviewed full-size frames 1441, 1900 and 3001 plus contact sheets covering
2041, 2401, 3601, 4021, 4501, 4981, 5041, 5401, 6301, 7801, 9301, 9794,
9853, 9860, 9867 and 10801. These include the trees and powder, cliff approach,
vertical ascent, foreground grappling, enemies, opaque entrance, industrial
section, boss, all destruction phases and Area 03 clear screen.

This is full emulator playback with every-frame auditing and sampled visual
review, not a claim that every frame was individually inspected. Only the
supplied Area 3 recording was replayed; no whole-project regression was run.

## Scope and structure

All 194,820 preceding tile rules and 53 preceding PNGs remain unchanged.
The 328 added rules require Area 3: 312 material rules and 16 unchanged doorway
priority copies. The new atlas contains 176 cells; there are no new sprite
additions or invalid tile references. All 11,085 Area 3 neighbor references
are bounded. World-locked cliff material placement uses 872 consistent
adjacency constraints from 4,014 native frames, and the recessed material
retains its previously checked two-by-two layout.
