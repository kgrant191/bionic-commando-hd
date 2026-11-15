# v0.7.5 — Knife guard and active flare

## Findings and corrections

The fast charging burgundy soldier is a knife attacker. His original exposed
arms and broad torso differ from the slim gun-carrying replacement. A new
three-pose sheet gives him a heavier build, helmet, sleeveless burgundy outfit
and a visible silver knife. All three poses use one body scale and head anchor.
The same native head pattern in Area 13 receives the same correction. The
separate bareheaded runner, other uniform colors and shield boss retain their
own artwork.

Reference: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Area_4
The guide distinguishes the knife attacker from the shield boss's gun/bayonet.

The active flare and ordinary bullets share native pattern
`000010383810000000106CC6C66C1000` and Spencer's palette. The generic projectile
replacement in v0.7.4 therefore also replaced the rising flare. The pickup and
equipment icon were already separate red canisters; this correction addresses
the active object, which now uses a lit red canister with a small flame.

Reference: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Items

## Flare selection

The game marks projectile slot 1 active at CPU RAM `0537`, with type `07` at
`054A`. Its screen center is stored at `0570` / `05AA`. The HD renderer's RAM
snapshot already contains the next camera step, so the visible sprite origin
is derived by subtracting signed camera deltas `00C8` / `00CA`, then the native
center offsets of 4 / 2 pixels. Rules cover camera deltas from -8 through +8.

The replacement is restricted to Area 4 gameplay, the active type-7 object,
its row and its eight-pixel screen-column span. Screen-column bounds avoid
Mesen's mirrored horizontal-origin behavior. Ordinary-shot bypass rules keep
the usual tile cache outside the flare sequence. Both normal Spencer and
his damage-flash palettes are covered. Other bullets, including shots fired
while the flare rises, retain the v0.7.4 silver artwork.

Controls, motion, collisions, damage, flare duration and lighting remain
native. No ROM or game-state changes are made.

## Visual evidence

The preview compares matching frames from actual v0.7.4 and v0.7.5 replays:

| Recording / frame | Review |
|---|---|
| Area 4 / 3840 | Broad charging soldier, forward knife and stable body scale |
| Area 13 / 1680 | Same native knife guard retains the same identity |
| Area 4 / 960 | Active flare uses a lit red canister rather than a silver shot |

All three guard poses were inspected together. Dense Area 4 screenshots cover
flare launch/rise/scrolling and the combat/damage sequence. A separate diagnostic
copy of the Area 4 input holds fire at frames 919–970 while the flare is active.
Matching v0.7.4/v0.7.5 diagnostic runs include 1,100 input frames and 185 matching
RAM/PPU checkpoints. At frames 924, 936, 948, 960, 984 and 1008, pixel differences
are confined to the flare; Spencer, ordinary gunshots and the rest of the screen
are identical. See `v075-mixed-flare-gunfire.json`.

## Regression coverage

The six supplied recordings are replayed in full using the final installed
pack. `v075-summary.json`, `v075-*-replay.json` and the matching tile-audit TSVs
record native/HD RAM and PPU comparisons, loader checks and replacement-rule
coverage. All six passed: 69,694 input frames, 642 matching RAM/PPU checkpoints,
no loader errors and no unmatched tile/palette keys. The final tile audit reaches
the end of every recording.

`v075-projectile-audit.json` resolves every selected projectile rule back to
its RGBA image. Only dedicated gunshot or flare artwork is accepted; flare
artwork is selected only in Area 4. The normal, damage-flash, red-guard and
white-guard palettes are exercised by the recordings. Two additional v0.7.4
palette aliases remain configured but are not independently exercised here.

`v075-art-scope.json` verifies that the source pose changes are confined to the
three knife-guard records in each area. All 22 other pack PNGs are byte-identical
to v0.7.4; the atlas changes to incorporate the new guard and flare.

## Limits and delivery

Visual review samples rendered frames; it is not a manual inspection of every
frame. Later stages and unrecorded equipment/actions still require review. The
already documented Area 1 top-edge scroll sliver near opening frame 19320 remains
a separate follow-up. The initial bottom water-edge correction is retained.

No ROM, recording or savestate is distributed. The source bundle starts at the
last user-confirmed pushed commit `9799b049f55c0c2d9116c212964dca73debc200e`, so
it includes the v0.7.3 and v0.7.4 work as well as these fixes.
