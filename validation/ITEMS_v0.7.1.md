# v0.7.1 — Item identity correction

Reference supplied by the user: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Items
The reference identifies the collectible as a single XP bullet and the Area 13 equipment as Flare Bombs, used to illuminate Area 4. Energy Recovery is a separate item.

The room drop and enemy drops use the same native pattern (`6482FEFAFAFAFEFA5CFEFE868686FE86`). One shared cartridge image now covers all captured gameplay palettes. The flare bomb uses a compact unlit illumination canister in its room pickup and equipment icon. The former pill and burning-stick artwork is superseded.

## Targeted replay results

| Recording | Frames | RAM/PPU checkpoints | Mismatches / missing tile matches |
|---|---:|---:|---:|
| area4 | 11,830 | 100 | 0 |
| cave | 6,842 | 59 | 0 |
| area13 | 7,434 | 63 | 0 |

Total: 26,106 frames and 222 matching checkpoints, no missing tile matches or HD-loader errors. These replays cover the room drops, enemy drops (including the alternate palette), equipment icon and Area 4 gameplay. Rendered screenshots are sampled every 120 frames, with the prior targeted Area 13 hit sequences retained.

## Scope verification

Exactly five native sprite patterns changed: one bullet and four flare-bomb tiles. All 2,310 unrelated tile patterns, all conditions, sprite additions and background images match v0.7.0. See `v071-item-rule-diff.json`. No character art or gameplay changes.

The full five-recording regression remains documented in `AREA4_v0.7.0.md`. This item-only update replays the three affected recordings; it does not claim a fresh full-game or every-rendered-frame visual review. Unrecorded items and later areas remain outside coverage.
