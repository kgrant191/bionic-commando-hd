# Area 2 doorway and crash correction — v0.11.2

Scope: the supplied `2.mmo`, especially the first doorway and its transition.
No other-area recordings were replayed.

## Reproduction and cause

The v0.11.1 outpost art left the doorway interior transparent, revealing the
mountain/sky background. An opaque nearly black interior backing now fills only
that opening; the facade and outer transparency retain their existing artwork.

The available MesenCE core's `HdPackTileNearbyCondition` accepts a pixel index
equal to `ScreenPixelCount` because its bounds check uses `>` instead of `>=`.
This accesses the first element beyond the allocated HD screen array. The new
Area 2 neighbor mappings exposed this during the first doorway transition.

A test runner placed an inaccessible memory page immediately after both native
HD screen arrays. It used the existing MesenCore.so without patching its code.
v0.11.1 faulted on that exact protected boundary after the frame 1140 checkpoint;
the stack resolved to `HdPackTileNearbyCondition::InternalCheckCondition` and
`HdNesPack<4>::Process`. The older v0.11.0 pack passed the 1,900-frame control.
The corrected candidate also passed the same 1,900-frame protected-buffer test.

The pack now evaluates screen-coordinate bounds before Area 2 neighbor checks,
including sprite mirroring. This prevents the one-past-screen access and row
wrapping. 3,091 rules receive bounds, with 4,234 neighbor references verified
statically. Other-area rule behavior is outside this revision's playback scope.

## Final ZIP verification

- Installed and played the exact extracted v0.11.2 archive.
- Completed all 12,044 inputs in a single run, exit code 0, with protected screen
  buffers active. No automatic movie retries were used.
- All 202 RAM and 202 PPU checkpoints matched the original recording.
- All 3,230 audited graphics states matched rules; no loader errors, invalid tile
  references, duplicate additions or missing virtual fallbacks were found.
- Captured 885 screenshots. Reviewed doorway approach and transition frames,
  representative aqueduct/combat frames, both pipe layouts and the clear screen.
  This is sampled visual review, not a claim of reviewing every frame by eye.
- The final installed files matched the archive's extracted files byte for byte.

The test uses the available Linux MesenCE core, not the user's desktop app.
It reproduces and eliminates the relevant invalid renderer read; it does not
constitute a platform-wide emulator certification or a full-game regression.

## Delivered archive

- `Bionic_Commando_HD_v0.11.2.zip`
- 47 runtime files; 45748547 bytes
- SHA256 `a1ed570f98bde70a3bcb2b86dbd67093cf038fb49cdf20e177d17dda9ee18dac`
- Playback: `replay-area2/door-fix-delivery`
- Reports: `v0112-verification.json`, `v0112-build.json`,
  `v0112-bounds-regression.json`, `v0112-package.json`.

Only runtime PNG/TXT files are packaged. No ROM, movie, emulator, MP4 or bundle.
