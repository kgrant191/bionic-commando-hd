# Development checkpoint — v0.4.1

## Inputs

- User ROM: Bionic Commando (USA).nes, 262160 bytes.
- Whole-file SHA1: D3A4BFD995D18C4A386971631759AECA3A7CFF8D.
- Whole-file SHA256: ade9a70b5cdb94ff24e2f37a0327262e5f94037580256dc36c483fae729f31f2.
- File CRC32: 5D78010D; PRG CRC32: D2574720.
- NES 2.0 header, mapper 1, 256 KiB PRG, 8 KiB CHR RAM.
- Recording: Bionic Commando (USA)(1).mmo; format 3, Mesen 2.2.1,
  starting save state, 40442 input frames (about 11 minutes 13 seconds).
- The recording reaches Area 1 Clear, then returns to the map.
- Original ROM and movie are private local inputs, excluded from this source.

## Build

Use Python 3 with Pillow, NumPy and SciPy, and MesenCE 2.2.1's xBRZ scaler wrapper:

```sh
export BIONIC_XBRZ_LIBRARY=/absolute/path/scale.so
python3 scripts/build.py
```

The optional `BIONIC_UI_FONT` points to DejaVu Sans Bold or a compatible TTF.
The default is `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`.
Build dependencies and font binaries are not included.

`tools/scale.cpp` is a small wrapper around the pinned core's bundled xBRZ:

```sh
g++ -shared -fPIC -O2 -I"$MESEN_SOURCE" tools/scale.cpp \
  "$MESEN_CORE" -Wl,-rpath,"$(dirname "$MESEN_CORE")" -o scale.so
```

MesenCE source revision used for the native helpers: nesdev-org/MesenCE
tag 2.2.1, revision 20ba206. Upstream licenses apply to upstream code.

## Capture

`tools/capture.cpp` is a native headless test harness linked against the matching
MesenCore shared library. Its arguments are HOME ROM MMO LUA RAW_PACK_OR_DASH.
A directory as the last argument records original visible tile/palette keys;
`-` uses the installed pack under HOME/HdPacks/<ROM base name>/.

Environment variables:

- `BIONIC_CAPTURE_HOME`: HOME, where the script writes its completion marker.
- `BIONIC_CAPTURE_DIR`: screenshots and RAM/PPU checkpoints.
- `BIONIC_CAPTURE_FRAMES`: defaults to 40442.
- `BIONIC_CAPTURE_STEP`: checkpoint interval, defaults to 120.
- `BIONIC_SCREENSHOT_FRAMES`: optional comma-separated screenshot frame list;
  RAM/PPU checkpoints continue at the normal interval.
- `BIONIC_METADATA_DIR`: optional per-frame rendered CHR-RAM tile positions.
- `BIONIC_METADATA_STEP`: metadata interval, defaults to 120.
- `BIONIC_SPRITES_ONLY=1`: omit background metadata during dense sprite capture.
- `SKIP_METADATA=1`: skip the rendered-tile listener for normal verification.

Delete HOME/done before reusing a capture home. Set maximum speed after movie
load. The harness allows Lua file IO and disables normal window/audio/input.
The source copy of HdNesPpu.h needs `public:` after its opening class brace to
expose read-only metadata; the emulator binary itself is unchanged.

## Mapping

This game uses CHR RAM, so keys are **16-byte pattern hex strings plus palette**,
not CHR-ROM tile numbers. The builder's visible-tile capture omits a few
resident/occluded patterns. The build also includes the rendered metadata keys
to cover those cases. See build_stats.json for counts.

- Atlas cells are 32 × 32, on 2048-pixel-wide PNG pages (scale 4).
- Tile rules remain palette-specific, with no unsafe default-palette rules.
- Exact original screenshot matches determine crop coordinates in the painted
  reference art. This avoids the video-thread offset between Lua screenshots
  and native PPU notification metadata.
- Normal-title and radio screen conditions use rendered pattern+palette keys.
- Radio text stays live; painted portrait overlays follow original sprite keys. The title background includes the
  prompt and copyright and suppresses the original title tiles/sprites.
- Sky openings are masked from original tile pixels. Water phases, including
  sparse one-pixel foam patterns, share the painted water material.
- Eight-pixel top/bottom overscan removes the observed edge garbage without
  changing the ROM or hiding the normal dialogue, map and status regions.

Reference frames: 480 title; 1200 radio; 1920 map; 3000 landing;
3480 fortress; 3960 tower; 7320 communication room; 11640 underground;
38400 final room; 39360 reactor; 39840 Area Clear; 40442 end of recording.

## v0.2.0 additions

Base GitHub commit: cc54af325fab7608d0d1ccee8019c945a8a17599.
Feature branch: feature/map-characters-v0.2.0.

- `capture/sprite-keys.json`: 784 unique sprite pattern/palette pairs from a
  15-frame sample of the complete movie; 23 extend the baseline key inventory.
- `scripts/characters.py`: original animated masks with palette-aware material
  relief, painted cloth samples and selected painted face crops. The action
  sheet is a source of detail/materials, not a promise of full-pose replacement.
- `scripts/scenes.py`: live map overlay handling and eight radio expression
  overlays for four people. Original portrait palettes are hidden only during
  radio screens; sprite triggers restore each speaker/expression at its native
  timing. Validation records the exact trigger keys.
- Map terrain uses background priority 10 (behind NES background tiles), so
  live routes and numbers are never hidden. Portrait overlays use priority 20.
- Tower source is aligned with piecewise geometry landmarks before extraction;
  previously approved environment mappings take precedence over new crops.
- Generated portrait and action artwork is kept as source; all final previews
  are actual emulator captures, not concept art.
- Source ZIP packaging explicitly excludes `.git`, Python caches, ROMs, movies
  and binaries.

## v0.3.0 additions

Base local commit: ec4374112fbf7293b361b9c0650d356b4f7a594d.
Feature branch: feature/level1-art-v0.3.0.

- `capture/spencer-poses.json` and `capture/enemy-poses.json` describe selected
  native component groups relative to their original sprite anchor.
- `scripts/poses.py` uses local `spriteNearby` signatures and HD `<addition>`
  tiles to render complete painted figures. Virtual tiles inherit native OAM
  direction/priority; conditional blanks hide the corresponding original parts.
  Unmatched poses retain the prior material fallback. Virtual keys are checked
  for collisions with captured patterns and have explicit blank fallbacks.
- Signatures distinguish pattern sets, not one-pixel coordinate differences:
  Mesen's nearby test checks pixels rather than exact tile origins. Variants
  with the same pattern set share a painting to prevent partial-pose seams.
- `validation/*_pose_mapping.json` records anchors, signatures, bounds and
  virtual keys. These are rendering-only keys, separate from captured keys.
- `art/reactor-machine-v3.png` aligns to original frame 38880's machinery crop
  (176,24)-(256,200). Exact screenshot matches select the relevant CHR patterns.
- Captured background-color flashes reuse normal painted tiles and restore the
  original flash color over palette-index-zero regions. Sprite palettes remain
  independent of this environment handling.
- Two additional native variants share existing Spencer paintings, for 18 pose
  records from 16 source cells. This extends running/arm transition coverage.
- `art/machinery-reference-v3.png` supplies the olive-brass material for palette
  0F2A1908 and previously unmapped underground fixtures from frame 25800.
  Piecewise landmarks align the painting before exact-pattern crop extraction.
- `<options>disableSpriteLimit` uses Mesen's adaptive removal of the NES sprite
  limit. The first HD replay exposed horizontal gaps during crowded combat;
  the final replay checks this rendering option against the original RAM state.

## v0.4.0 feedback fixes

Base commit: 0c153e4f056eb2ba5c8e8872d5116ffced281534.
Branch: fix/level1-feedback-v0.4.0.

- Spencer's replacement sheet exposes his mechanical grappling arm. Two rotated
  head anchors get dedicated swing paintings and complete native component masks,
  including black-only boots and the overlaid hand/weapon tile.
- Enemy source cells use one uniform scaling factor (152 / cell width); their
  native feet and helmet anchors determine placement without stretching anatomy.
- Only the eight foam keys found at frame 2640 can receive water. The lamp's 14
  pattern/palette pairs are mapped separately from native frame 7680, including
  its repeated post. Matching beam/wall patterns share paintings across the
  native sky-edge palette change; remaining edges get material swatches.
- `scripts/equipment.py` detects the native equipment frame. Its background
  follows the native grid and cursor bounds. Only captured frame/END tiles are
  suppressed; newly introduced text remains live. Icons use exact native
  pattern+palette keys, under menu or world-map guards.
- `capture/ui/` contains full menu and map-equipment metadata. A private controlled
  replay retains the first 2380 inputs of the original movie, then 620 neutral
  frames, to hold the item-selection screen for testing. It changes no RAM.
- Mesen 2.2.1 supports `<condition>name,memoryCheckConstant,ADDR,==,VALUE` with
  hexadecimal address/value, so equipment can select a separate painted pose
  family even when original head/body keys are shared. Do not invent that address:
  verify the selected-weapon state with additional loadouts first. This version
  tests the starter weapon only and does not claim all weapon variants.

## v0.4.1 doorway and seams

Base commit: c8bf62f8f962cccf2ce09fae875749f995bb975e.
Branch: fix/door-platform-seams-v0.4.1.

- Doorway patterns are collected directly from the native background metadata
  at frame 7320, rectangle (32,160)-(64,192). Eight nonempty patterns map the
  complete header/jamb painting, including patterns occluded in the screenshot.
  The repeated middle-jamb pattern keeps one consistent crop. Black interior
  tiles remain unchanged. The same pattern set occurs at 14 sampled room states.
- `capture/exterior-seams.json` identifies the eleven affected structural cells
  and their layout in `art/exterior-seams-v4.1.png`. During building, only opaque
  blue/cyan contamination plus a one-pixel fringe is replaced from the repaired
  source atlas. Native alpha and all unrelated colors are retained. The water
  palette is excluded. This fixes shared texture rules throughout the recording,
  rather than adding patches at individual screen coordinates.
- `validation/door-seams-v0.4.1.json` compares all 12,775 rules to v0.4.0; only
  those 19 patterns change. `validation/seam_mapping.json` records pixel counts. Re-run the tile comparison with
  `python3 scripts/validate_seams.py` (requires the saved v0.4.0 Git commit).
- The source bundle is cumulative from the previously pushed v0.3.0 commit
  0c153e4f056eb2ba5c8e8872d5116ffced281534, so a separate v0.4.0 import is not required.
- Package the comparison preview with `scripts/package.py --screenshots HD_DIR
  --before V040_SCREENSHOT_DIR --output OUTPUT_DIR`. Frames 3600 and 4800 are
  identical replay inputs in both folders; the preview uses equal crops/zoom.

## Next art passes

1. Expand painted pose coverage and inspect transitions, flips and damage states.
2. Remaining enemies, projectiles and effects.
3. Remaining equipment icons, Area Clear figure and more detailed map vehicles.
4. Remaining architectural variants; inspect shared tile patterns.
5. Gather later-area and unrecorded-move recordings before expanding coverage.

This is a review build. No GitHub release is implied by its local version.
