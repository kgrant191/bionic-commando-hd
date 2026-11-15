# Area 1 fixes — v0.7.6

## Changes

- Replace the damaged exterior doorway composite with a straight red steel frame. Cover both the tower doorway and the first communication-room header variant.
- Retain the painted closed-door panels and Spencer's foreground appearance. Review the radio-room interior entrance and the cave/generator entrance.
- Replace the four POW lettering patterns and two mirrored green recovery-flask patterns with dedicated reward artwork.
- Replace the orbiting POW star in both observed palettes. Native position, mirroring, lifetime and expiration remain controlled by the game.
- Add dedicated bazooka-soldier grenade wind-up and release poses, including the previously unmapped release head, plus a compact thrown grenade.
- Add painted lower-body fallback fragments for a red soldier clipped above the screen. Limit shared-pattern fallbacks to the normal red-enemy palette; retain existing Spencer and damage rules.

## Input

New recording: `Bionic Commando (USA)(5).mmo`, 2,407 input frames.
SHA-256: `1783bd74fda6a155005e88dbd71c3604659891c92f902cc11457dfb2e68920e3`.
The source bundle excludes the recording and ROM.

## Full replay regression

Seven unique supplied recordings passed with 72,101 input frames and 724 native-versus-HD RAM/PPU checkpoints. All checkpoints matched, every observed tile key had a matching pack rule, and no HD-pack loader errors were reported.

| Recording | Frames | Checkpoints |
|---|---:|---:|
| Opening / Area 1 clear | 40,442 | 339 |
| Closed door and enemy damage | 1,081 | 11 |
| Cave, elevator and generator | 6,842 | 59 |
| Area 13 | 7,434 | 63 |
| Area 4 | 11,830 | 100 |
| Water / flare feedback | 2,065 | 70 |
| POW / crate / grenade feedback | 2,407 | 82 |

The seven-recording snapshot has hires.txt SHA-256 `3c47d03a1a2e34dbb937e0e0015b302a95e1d5aa143c82ad5b3146b1e2fc67cb`. See `v076-summary.json`, the individual replay reports, and tile-audit TSVs.

## Final doorway-header correction

Visual review found four additional header patterns at the first communication-room entrance. These were corrected after the full replay run. A per-key semantic comparison confirms that only those four header replacements changed: every other replacement's pixels, per-key priority, conditions and sprite additions are identical. See `v076-final-header-scope.json`.

The final shipping pack then passed the 7,920-frame opening prefix and the complete 1,081-frame closed-door recording: 9,001 additional frames, 78 matching RAM/PPU checkpoints, zero unmatched tile keys and no loader errors. See `v076-final-door-summary.json` and the two final replay reports.

Final hires.txt SHA-256: `365d504fb1a4da19885f37016e07618cf9d7938299d3ed1c20ef72a660ab2fc3`.

## Visual inspection and limits

Reviewed matching before/after samples of both exterior doorframe variants, the closed door with Spencer in front, the communication-room interior, cave/generator entrance, grenade release, clipped red-soldier fragments, and POW-star animation/expiration. Tile-rule coverage alone does not prove visual quality; these samples were inspected separately.

The new movie does not show a complete green-flask pickup. Its native patterns were recovered from the supplied screenshot, matched byte-for-byte at ROM offsets 132192 and 132208, and verified as a static assembly using native horizontal mirroring. The preview explicitly labels the bottom reward row as mapped tile assemblies. See `v076-item-mapping.json`.

Visual inspection is sampled; unrecorded stages and states remain untested. A previously known thin scenery strip at the Area 1 top edge is outside this correction. ROM bytes, gameplay, collision, RNG and item timing are unchanged. The install ZIP contains only runtime pack files and its README.
