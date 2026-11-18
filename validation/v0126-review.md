# Area 3 v0.12.6 readability review

The user's two remaining issues were caused by collapsed native distinctions.
The first 12 gray outdoor patterns (catalog indices 71–82) are passable snowy
cliff markings, while the remaining 58 patterns (83–140) form solid barriers.
The passable family now uses the same soft snow painting as surrounding
patches. Solid gray stone remains unchanged.

Four sprite patterns previously blended into ordinary ledges are the two
plant pre-emergence warning phases. The new art shows broken snow, torn turf,
a dark fissure and loose soil. It follows the native positions, mirroring,
clipping and eight-frame phase cadence, without an independent timer.

## Deliverable

- `Bionic_Commando_HD_v0.12.6.zip`
- SHA256 `e872499e5efe02f334074d0b6e3713f7c4de414c394769e2b6209671b77d7483`
- 47,424,649 bytes; 57 runtime files (55 PNG and two text files).
- All files match both a clean default rebuild and the completed playback.
- ZIP only; no ROM, emulator, recording, MP4, bundle or source painting.

## Playback and verification

The unchanged MesenCE 2.2.1 core completed all 11,110 input frames of `3.mmo`
in the single guarded run `v0126-pass1`, before packaging. All 187 RAM and
187 PPU checkpoints match the original-game reference. All extracted ZIP
files were compared byte-for-byte with the pack loaded by that completed run.

Every-frame auditing found 3,175 graphics states with zero unmapped states.
All 12 passable patterns choose the new snow art; all 58 solid patterns retain
the exact preceding stone selection. Both painted warning phases are used.
The four warning patterns retain identical first/last frames and audit
instance counts. Native reference metadata contains 853 warning frames
between frames 2003 and 5056, across 119 phase intervals.

All 3,159 other graphics states retain their preceding rule selections,
counts and frame spans. All 260 common non-outdoor screenshots are identical
to v0.12.5. Checks for the 16 doorway cells, five explosion patterns,
281 reused robot states and three-frame wrapped-body edge comparison pass.
The final run produced 1,006 valid screenshots and one empty startup capture.

## Visual review and scope

Viewed full-size frames 2010 and 2401. Inspected aligned warning details at
2004, 2010, 2012, 2018, 2020, 2044, 2052 and 2066 to compare the two phases.
Later contact sheets cover 3001, 3601, 4410, 4420, 4800, 4810, 5030 and 5041,
including multiple spawn locations, cliff sections and the entrance.

This is full emulator playback plus every-frame auditing and sampled visual
review, not individual visual inspection of every frame. Only the supplied
Area 3 recording was replayed; no whole-project regression was run.

All 195,148 preceding rules and 54 preceding PNGs remain unchanged. Sixteen
new Area 3 outdoor rules use eight deduplicated atlas cells. There are no new
conditions, sprite additions or invalid tile references. All 11,085 existing
Area 3 neighbor references retain their bounds guards.
