# Current build — v0.11.3

`scripts/build_v0113.py` passes an Area 2 slime atlas and corrected rifleman
pose records through the existing builders. The optional inputs default to
None, retaining earlier-version generation when those builders run directly.
`capture/area2-v0113/enemy-poses.json` changes poses 18/19 from kneeling to
standing/passing steps from the existing painted rifleman atlas, at one scale.
`scripts/package_v0113.py` produces the current review ZIP.

## v0.11.2 foundation

# Doorway and crash correction — v0.11.2

`scripts/build_v0112.py` uses the existing painted assets with an opaque doorway
backing and bounds Area 2 neighbor conditions before their evaluation.
`scripts/package_v0112.py` creates the installable review ZIP.

`tools/regression_audit_guarded.cpp` and `tools/guarded_screen.h` place an
inaccessible page immediately after each native HD screen buffer. This exposes
the Mesen nearby-condition off-by-one read without patching the emulator binary.
Playback must run once and fail on a nonzero exit; do not hide failures by
retrying the movie. See `validation/AREA2_v0.11.2.md` for the reproduction.

## v0.11.1 foundation

# Area 2 visual corrections — v0.11.1

`scripts/build_v0111.py` layers the Area 2 screenshot corrections over the
v0.11.0 generator. The new structure/effect/recoil source atlases are in
`art/area2-*-v0111.png`; the recorded native assemblies are in
`capture/area2-polish/`.

Current review workflow: work on the area supplied by the user and play its
recording before delivery. Run a full regression only when explicitly requested.
Deliver only the installable ZIP unless the user asks for other formats.

Use `python3 scripts/package_v0111.py` to create the current ZIP.

## v0.11.0 foundation

Run `python3 scripts/build.py` (optionally `--output /path/to/output`).
Dependencies: Python 3, Pillow, NumPy, SciPy, DejaVu Sans Mono Bold and the
MesenCE xBRZ wrapper in `tools/scale.so`. Set `BIONIC_XBRZ_LIBRARY` and
`BIONIC_MONO_FONT` to override the scaler and font paths on another platform.

The v0.10.6 approved ZIP is preserved, hash-verified, in `baselines/v0106/`.
The intermediate v0.10.2–v0.10.6 generator changes were not available after
workspace recovery. Never rerun the v0.10.1 generator over this baseline.
The current builder adds only scoped Area 2 rules and two runtime images.

`capture/area2/` contains extracted native pattern metadata, material phase
assignments and actor pose records. `art/area2-*` holds generated source artwork.
All gameplay state, hitboxes, camera behavior and animation timing remain native.
The tracked carrier uses its stable chassis cell as the artwork anchor; the
independently turning driver cannot mirror or shift its chassis. Body fragments
use painted fallback crops when the anchor leaves the visible viewport.

`python3 scripts/package_v0110.py` creates the installable ZIP and extracts
that exact archive for replay. It does not create movies or Git bundles.
`validation/AREA2_v0.11.0.md` records the final playback and prior-area checks.

## Earlier development history

# Current build — v0.9.8

Run `python3 scripts/build.py` to reproduce all 37 approved runtime files.
Use `--output /path/to/output` to build into a separate directory.
Dependencies: Python 3, Pillow and NumPy.

Git history through v0.8.2 was recovered exactly from the earlier bundle and
its original v0.7.6 prerequisite. The intermediate v0.8.3–v0.9.6 generator
sources were not available; their approved output is preserved in the
hash-verified `baselines/v096/` snapshot. The current build applies the
versioned v0.9.7 and v0.9.8 artwork/mapping patches to that snapshot, then
checks every result against `baselines/v098.json`. It does not regenerate
those intermediate designs from the old v0.8.2 generator.

`build_v082.py` and the historical source remain available for reference.
`V097_DEVELOPMENT.md`, `V098_DEVELOPMENT.md`, and `validation/v09*` describe
the recent fixes and recorded checks. Baseline images shared with the current
pack are identical Git objects, avoiding duplicated asset bytes in the bundle.

## Historical development notes

# Development checkpoint — v0.8.0

New review inputs: intro.mmo (4,752 frames), 5.mmo (22,377), and 15.mmo (7,236).
They use embedded Mesen 2.2.1 states and the same USA ROM listed below.
`capture/new-*` contains selected original screenshots and native tile metadata,
not ROMs or private movies. `scripts/next_areas.py` owns the new scoped mappings.
Scene state $00CE selects story panels; $004D selects areas; $004C == $13
selects overhead interceptions. No conditions use capture frame numbers.

## Earlier build and capture details

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
  `python3 scripts/validate_seams.py` (compares the saved v0.4.0 and v0.4.1 Git commits).
- The source bundle is cumulative from the previously pushed v0.3.0 commit
  0c153e4f056eb2ba5c8e8872d5116ffced281534, so a separate v0.4.0 import is not required.
- Package the comparison preview with `scripts/package.py --screenshots HD_DIR
  --before V040_SCREENSHOT_DIR --output OUTPUT_DIR`. Frames 3600 and 4800 are
  identical replay inputs in both folders; the preview uses equal crops/zoom.

## v0.4.2 closed exterior door and hit palette

Base commit: 249a6380309fd85fde261948914c7b3a09680cf1.
Branch: fix/closed-door-hit-frames-v0.4.2.

- `Bionic Commando (USA)(2).mmo` is a 1,081-frame save-state recording.
  Capture its metadata every frame: a 15-frame interval can miss the brief
  enemy palette states. Selected metadata is under `capture/feedback-v042/`.
- Six enemy patterns already existed in the normal palette, but were missing
  under FF202A0F during the hit flash. Adding the captured pairs lets the
  existing pose builder create the same complete painting, tint and masks.
  Twelve virtual tiles are added for that palette. Thirteen additional
  scrolling-edge patterns use the existing structural material fallback.
- The closed exterior door is composed of five unique sprite patterns in
  palette FF30150F. Native door sprites cover HD actor additions because of
  sprite ordering. `scripts/closed_door.py` instead composites the new panel
  into sixteen background cells, then blanks those five native sprite keys.
  Per-cell `spriteNearby` guards follow the live native panel; no frame numbers,
  absolute screen positions or RAM writes are used as runtime triggers.
- The panel starts one native pixel above the background body grid. Cropping
  preserves that offset and the existing header. Local row/left-edge tests
  distinguish repeated cells and still work when the emblem is off screen.
  Open doors remain governed by the prior rules. Both crossing directions,
  scrolling entry and recorded hit frames are inspected in the short replay.
- Short-replay validation uses `scripts/validate.py --frames 1081 --report
  replay-feedback-v042.json` with original/HD/home/log arguments as usual.
  Original and HD RAM are captured every frame for this recording. The full
  movie keeps its 120-frame checkpoints and writes `validation/replay.json`.

- `validation/v042-art-regression.json` confirms that all 4,093 existing
  default tile images are pixel-identical to v0.4.1. The changes add new
  keys and conditional rules instead of repainting unrelated defaults.
- The v0.4.2 comparison preview uses this short recording: frames 440, 480
  and 154, with the same crop and zoom in v0.4.1 and v0.4.2. Pass those folders
  to `scripts/package.py --before OLD --screenshots NEW --output OUTPUT`.
- The cumulative source bundle still uses the pushed v0.3.0 commit
  0c153e4f056eb2ba5c8e8872d5116ffced281534 as its prerequisite.

## v0.5.0 cave, combat, generator and results

Base commit: 1b9e93f349fbc10326a48c8ab925824dc6976786.
Branch: feature/cave-generator-polish-v0.5.0.

- `Bionic Commando (USA)(3).mmo` contains 6,842 inputs, from the cave lift through
  Area Clear. Every-frame native tile metadata finds 86 new pattern/palette pairs.
  `capture/feedback-v050/extra-keys.json` and `new-keys-audit.json` retain their
  inventory, first/last observations and counts without including the movie.
- `scripts/level_polish.py` extracts fixture tiles from exact native screenshot
  matches. The cave gate uses its full metadata grid to include cells hidden by
  Spencer. The moving lift and effects remain ordinary flipped OAM components.
- Generator palette fades alias to painted normal materials, with decreasing
  brightness at each native palette step. All-black actor palettes stay black.
- A recognized actor head can outlive its visible body-signature tiles during
  crowded OAM overlap. Virtual additions use the most frequent head-matched pose
  as a last-resort painting; local head/offset tests suppress surviving native
  fragments. Full signatures retain priority. This does not alter collision or
  animation state, but may temporarily approximate a partly obscured pose.
  When the head itself is completely hidden, surviving enemy-only body patterns
  use masked crops from the painting; shared Spencer/projectile keys retain their
  existing rules. This avoids native-colored limb fragments behind other actors.
- Spencer pose 102 covers the additional shallow swing head from 26 metadata
  observations, using a reflected source cell from `spencer-swing-v4.png`.
- Enemy pose 11 supplies the armored guard's extended-gauntlet attack. Its
  complete 13-component signature was observed 300 times in the new recording;
  the additional painting uses the same source-cell body scale as the old sheet.
- The Area Clear blank-tile/palette condition is active before the header types
  in. This pair occurs only in Area Clear in the captured inputs. Header-letter
  conditions are too late and expose the old victory figure during the pause.
  Text is rendered per native glyph, and unknown glyphs retain transparent ink.
- The new replay uses 30-frame RAM checkpoints plus first/last frames. Validate
  with `--frames 6842 --checkpoint-step 30 --report replay-feedback-v050.json`.
  The door/hit replay retains every-frame checks; the full movie retains 120-frame
  checks. Targeted screenshots include single-frame hits, overlap cases, swing,
  the shutdown fade and the first Area Clear frames.
- The v0.5.0 comparison preview uses frames 60, 960, 3276, 6180 and 6842
  from the cave-to-generator recording, at matching crops in v0.4.2 and v0.5.0.
- The source bundle remains cumulative from the last confirmed pushed v0.3.0
  commit, 0c153e4f056eb2ba5c8e8872d5116ffced281534.

## Next art passes

1. Expand painted pose coverage and inspect transitions, flips and damage states.
2. Remaining enemies, projectiles and effects.
3. Remaining equipment icons and more detailed map vehicles.
4. Remaining architectural variants; inspect shared tile patterns.
5. Gather later-area and unrecorded-move recordings before expanding coverage.

This is a review build. No GitHub release is implied by its local version.

## Area 13 checkpoint — v0.6.0

Base: feature/cave-generator-polish-v0.5.0, commit 484f70b6bb6fe8d362c96380d5fb2cc4ce8b7755.
New input: Bionic Commando (USA)(4).mmo, 7,434 frames, matching the existing ROM SHA1.
New module: scripts/area13.py; all area-specific environment replacements use a read-only area-state condition at RAM $004D == $0D and exclude map/equipment/title/radio screens.
Metadata was sampled every 6 frames, with original visible-tile recording over the entire movie. Additional keys are retained under capture/area13.
Guard metasprites reuse the native anchor, flip, priority and local pose conditions. NPC artwork retains its aspect ratio. Portrait additions attach to the moving native helmet anchor; mouth changes follow the original nearby mouth pattern.
The original and HD replay checkpoints are compared every 120 frames plus start/end. Only the graphics pack is modified; no ROM or gameplay memory writes are used.

Build: BIONIC_XBRZ_LIBRARY=/path/to/scale.so python3 scripts/build.py
Validate with scripts/validate.py using --frames 7434 --checkpoint-step 120 and the original/HD replay directories.
Package with scripts/package.py using the v0.5.0 replay as --before and the new replay as --screenshots.
Coverage is the supplied Area 13 recording; this pass does not claim a fresh full-game regression.

## v0.7.0 Area 4

`area4.py` adds area-scoped cave materials and six guard pose records. Native
RAM byte $004D == $04 selects the area; map, equipment, title, radio and results
screens are excluded. Inventory icons are independently scoped to the map and
equipment screens. No memory is written.

Distant mountains and forest are a background beneath only their native tile
families. The all-zero pattern in the same palette is also used between spikes
and must remain opaque black. Rock material cells use snapped 0/32 texture
coordinates; arbitrary scrolling offsets would crop beyond the 64-pixel swatch
and introduce transparent strips. All mapped structural tile crops assert full
opacity. Spikes, ledges and stone share a palette and are classified by their
recorded scene regions, not palette alone.

See `validation/AREA4_v0.7.0.md` for the final replay coverage and limitations.

Area 13 corrections in this build separate the red runner, armed green contact,
unarmed green contact and white idle NPC artwork. Standard enemy rules are
excluded from Area 13, while white-guard additions cover all four observed hit
palettes. Their flash uses brightness rather than recoloring the uniform.
The capsule sprite and flare pickup have dedicated artwork; the equipment flare
uses the same source. Supply cases and parachutes retain their own mappings.

MesenCE caps additional sprites at four per pixel, even when their selected
replacement is transparent. `additions.py` coalesces matching native anchor,
palette and offset additions into one virtual layer, merges their area-specific
conditional artwork and emits one transparent fallback after those conditions.
This prevents inactive Area 13 layers from consuming slots needed by overlapping
Area 1 enemies. The validator rejects duplicate anchor/offset addition records.

The white recoil pose uses the same primary head anchor as the corresponding
native recoil pose outside Area 13. Its former anchor was the other half of
the head and would create a second virtual body over regular enemies. White
hit-palette additions are limited to pairs actually observed in the Area 13
all-frame audit, rather than every palette seen elsewhere in the game.

## v0.7.1 item identity correction

Reference: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Items
The room's 8x8 sprite is the same XP-bullet pattern used by defeated enemies.
`items.py` supplies a shared cartridge painting for every observed gameplay
palette, while the room and equipment screen share one flare-bomb icon.
The original flare-bomb pickup is round; the replacement uses a compact unlit
illumination canister rather than a medical badge or burning handheld stick.
Energy Recovery is a separate item. No native projectile keys are replaced.

## v0.12.0 Area 3

`build_v0120.py` wraps the approved v0.11.5 builder. All new runtime tile rules
require `area3` (`$004D == $03`); the 47 earlier PNGs and 185,431 earlier tile
rules remain unchanged. World-map, equipment and debrief additions use separate
Area 3 guards. Declare conditions before backgrounds as well as tile rules:
the loader resolves background guards while reading the file.

The recorded outdoor palette has backdrop `$1C`; the pipe-works foreground
palette begins `$39`. Native zero patterns remain transparent to the scoped
alpine panorama or opaque dark factory background. The eight occluded pipe
cells in the control room are taken from the original generated
`control-reference.png`, aligned to their native positions.

Creature CHR assemblies select distinct crawling legs, inflated/flattened
flying insects, plant-mouth phases and seeds. Seven observed knife-guard
assemblies map to three walking poses. Coalesce their virtual cells with the
existing addition destinations, including hit palettes, before emitting rules.
Never prepend a transparent unconditional fallback for a virtual key already
used by another area; retain its existing fallback below the older rules.

New neighboring-cell conditions are bounded before evaluation. The unchanged
MesenCE core is replayed using the guarded-screen harness. The complete supplied
`3.mmo` contains 11,110 input frames. Final checks require one uninterrupted
playback, a zero-unmapped-state every-frame audit, identical original-game RAM
and PPU snapshots at 187 checkpoints, and byte equality between the extracted
ZIP and the pack loaded during that playback. A separate clean rebuild must
produce the same 51 runtime files byte for byte.

Run structural/replay verification with `scripts/verify_v0120.py`; run
`scripts/package_v0120.py` to produce the installable ZIP only. Art sources and
capture catalogs live under `art/area3-*` and `capture/area3/`. Review details
and measured results are in `validation/v0120-*`. No earlier-area movie
regression was requested or performed for this revision.
