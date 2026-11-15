# v0.7.4 — Enemy shots and Spencer's damage-flash projectiles

## Findings and correction

The Area 13 white guard's projectile still used a smoothed NES tile. Spencer's
shots shared his character palette: normal shots received green character
material shading, while the invulnerability palette fell back to a flat white
NES silhouette. These are variants of the same native projectile pattern,
`000010383810000000106CC6C66C1000`.

All six captured sprite palettes now select one dedicated silver/ivory shot
with an amber rim. The replacement precedes the material and baseline
fallback rules during gameplay. Menu, dialogue-room and results conditions
remain excluded.

| Palette | Recorded use |
|---|---|
| `FF202A0F` | Spencer, normal |
| `FF202015` | Spencer, damage/invulnerability flash |
| `FF36300F` | White guards in Area 13 |
| `FF36150F` | Red guards |
| `FF30150F`, `FF30160F` | Additional existing palette aliases; not exercised by visible shots in the six replays |

The native nontransparent bounds are x=0–6 and y=1–6 within the 8×8 tile.
The replacement occupies the corresponding 28×24 region at (0,4) in a 4×
tile. OAM positions, flip flags, flight paths, speed, hit detection and
Spencer's own damage flash are unchanged. The collectible XP bullet and
flare-bomb items are separate patterns and retain their approved artwork.

## Visual evidence

The preview uses matching frames from actual v0.7.3 and v0.7.4 emulator replays:

| Recording/frame | Review |
|---|---|
| Area 13 / 6528 | White enemy shot no longer uses the white/pink NES diamond |
| Area 4 / 3924 | Spencer firing normally uses the dedicated projectile |
| Area 4 / 3912 | Spencer retains his damage tint; his shots keep the same artwork |

Dense screenshots cover Area 13 frames 6240–6672 and Area 4 frames 3780–4320
at three-frame intervals. The full recordings also include the approved town
portraits, alarm backgrounds, supply room, boss, debrief and water-edge fixes.

## Validation

The six full supplied recordings are replayed against the final installed
pack. Results are recorded in `v074-summary.json`, `v074-*-replay.json` and
the matching tile-audit TSVs. These compare native and HD RAM/PPU checkpoints,
check loader errors and check selected replacement rules.

All six replays passed: 69,694 input frames, 642 matching RAM/PPU checkpoints,
no loader errors and no unmatched tile/palette rules. The final audit reaches
the last frame of every recording. `v074-projectile-audit.json` confirms that
every visible occurrence of the projectile selects the dedicated gameplay
rule, including the normal, damage-flash, red-guard and white-guard palettes.
The two additional palette aliases are covered by the atlas comparison below;
they were not independently exercised by visible shots in these replays.

`v074-projectile-scope.json` independently compares the old and new packs.
After resolving atlas coordinates to actual RGBA pixels, all existing rules,
their priority within each tile/palette key, conditions and image content are
identical. The only drawing changes are six new rules sharing one projectile.
All 22 other pack PNGs are byte-identical to approved v0.7.3.

## Limits and delivery

Visual review samples rendered frames; it is not a manual inspection of
every frame. Unrecorded actions and later stages remain untested. The already
documented Area 1 top-edge scroll sliver near opening frame 19320 remains a
separate follow-up; the initial bottom water-edge fix is retained.

No ROM, movie or savestate is distributed. The source bundle includes the
approved v0.7.3 changes plus this fix, starting at the last user-confirmed
pushed commit `9799b049f55c0c2d9116c212964dca73debc200e`.
