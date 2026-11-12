# Development checkpoint — v0.2.0

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

## Next art passes

1. Complete individual animation-frame redraws beyond the current material
   and selected-head pass; retain every move, flip and damage state.
2. Remaining soldier heads, projectiles, reactor and effects.
3. Equipment UI, Area Clear figure and more detailed map vehicles.
4. Remaining architectural variants; inspect shared tile patterns.
5. Gather later-area and unrecorded-move recordings before expanding coverage.

This is a review build. No GitHub release is implied by its local version.
