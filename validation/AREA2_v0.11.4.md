# Area 2 screenshot corrections — v0.11.4

Scope: the supplied `2.mmo` and three November 18 review screenshots.
No other area recording was replayed.

## Corrections

- Replaced the alternate final-door header and standalone round wall outlets.
- Completed the longer lower pipe shaft, including its off-screen-elbow case.
- Removed the stray pipe fragment in the black platform underside.
- Replaced the tall outlet's pale native rim and separated pool chunks with a
  metal mouth and vertically connected blue slime. Masonry shows through the
  transparent edges instead of a rectangular black gap.
- Kept the v0.11.3 soldier steps, moving blobs and blue ground slime, and the
  opaque entrance and screen-boundary guards from v0.11.2.

All 45 previously installed PNGs and 180,326 non-Area-2 tile rules are
unchanged. New background replacements require Area 2, its cave condition
and palette `0F2B1C0B`.

## Playback evidence

A complete 12,044-frame candidate replay was visually checked, then an
additional fragment correction was applied. The deliverable is validated
separately from its extracted ZIP using the unmodified MesenCE core with
protected screen buffers and no retry loop.

Visual samples include the entrance and first blobs (733, 1201, 1453), tall
slime and scrolling (1717, 2281–2449), walking steps (2876/2882/2889/2896,
5270/5278, 6205/6212), green/red dialogue (3841/4321/4561), earlier pipe
layouts (6811, 6961, 7201, 7693), the reported late pipe and door (9313,
9361, 9553, 9601), and the clear screen (11533).

This is a sampled visual review of the supplied recording; unrecorded game
states and other areas are outside this revision's validation scope.

## Final result

The extracted final ZIP completed all 12,044 inputs in one 210.4-second run,
exit code 0, with no retries or memory faults. All 202 RAM and 202 PPU
checkpoints matched the native reference. All 3,280 audited graphics states
had a matching rule; there were no uncovered states or loader errors.
All 4,340 Area 2 neighbor references were bounded before evaluation.
The run captured 1,089 screenshots for sampled visual review.

- Archive: `Bionic_Commando_HD_v0.11.4.zip`
- Runtime files: 48; bytes: 45843293
- SHA256: `96a6dfcc39962e3ef9e49c06021bd546e92b33f3582d0dade6410faf0ff5160e`
- Playback: `replay-area2/layouts-final`
- Reports: `v0114-verification.json`, `v0114-build.json`,
  `v0114-scope.json`, `v0114-package.json`.

The ZIP contains runtime PNG/TXT files only. No ROM, recordings, emulator,
MP4, source atlases or Git bundle are included.
