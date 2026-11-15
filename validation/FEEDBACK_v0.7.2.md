# v0.7.2 visual feedback and regression review

This review build addresses the seven issues reported on 15 November 2026.

| Reported issue | Change | Visual evidence |
|---|---|---|
| Area 4 boss grows and shrinks | A fixed scale and head anchor replace independent pose stretching. The shield and torso keep their proportions as the legs move. | Area 4 frames 10170, 10176 and 10200; per-pose previews |
| Debrief reads `04Area Clear` with mismatched digits | Static AREA/CLEAR labels surround the live area number. Complete font mappings cover A–Z and 0–9. The bonus symbol uses the same XP cartridge. | Area 4 frame 11280; cave recording final debrief |
| Bullet is hard to see | Broad upright white-and-green cartridge based on the original native silhouette. One sprite is shared by room and enemy drops. | Area 13 frame 2520; cave enemy-drop frame 2040 |
| Red Area 13 runner changes size | All three runner paintings use one body scale and stable head alignment. Red rifle guards receive the same correction. | Area 13 frames 3006, 3018, 3024, 3360 |
| White NPC portrait has wrong clothes/headwear | Two distinct white patrol-cap portraits match the younger and older standing NPCs, including idle/talking mouths. | Area 13 frames 1320 and 2160 |
| Health indicators differ in style | Player and enemy pips share the same metal bezel and inset lens. Original palette colors, counts and timing remain live. | Area 4 frames 600 and 10200; Area 13 frame 3360 |
| First descent reveals scenery below water | Area 1-only replacement requires native water immediately above a stale bottom-edge tile. It also handles water-pattern tiles with stale wall palettes. | New water recording frames 30–240 and later return at 1260 |

The water artifact exists in the native rendering as stale nametable scenery. The pack covers its visible bottom-edge fragments without writing game memory or changing level geometry.

## Recording coverage

Six unique supplied recordings are replayed in MesenCE 2.2.1. The duplicate opening recording is not counted twice.

| Recording | Frames | RAM/PPU checkpoints |
|---|---:|---:|
| Opening / Area 1 full recording | 40,442 | 339 |
| Closed door / enemy hit feedback | 1,081 | 11 |
| Cave / elevator / generator / debrief | 6,842 | 59 |
| Area 13 | 7,434 | 63 |
| Area 4 | 11,830 | 100 |
| Water glitch | 2,065 | 70 |
| Total | 69,694 | 642 |

Final results are in `v072-summary.json`: all 642 RAM and PPU checkpoints match the native replays, every audited tile/palette occurrence has a replacement rule, and no HD-pack loader errors were reported. Each replay report records the installed pack hashes, RAM/PPU parity, image dimensions and loader checks. Tile audits evaluate native tile/palette replacement selection over every replay frame. Pose additions retain the duplicate-layer coalescing that prevents overlapping enemies from losing sprite strips.

## Review limits and additional finding

Visual review uses sampled full-screen captures and dense captures around the reported animations and conversations. A matched tile rule does not prove every image is artistically finished. Unrecorded actions and later areas are outside this review.

An inherited top-edge scroll sliver is still visible in the original opening recording around frame 19320. Its pixels are identical to the prior build. It is separate from the reported bottom water-edge fault and remains a follow-up visual issue; this build is not claimed to eliminate every native scrolling artifact.

ROM SHA1: `D3A4BFD995D18C4A386971631759AECA3A7CFF8D`. No ROM, movie or savestate is included in the install ZIP or source bundle. Gameplay, palettes, dialogue strings and animation timing remain driven by the original game.
