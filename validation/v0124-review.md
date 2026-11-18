# Area 3 v0.12.4 snowy cliff review

The outdoor cliff now uses a coherent packed-snow finish instead of mixed
brown rock, scattered snow and green vegetation. Softer blue snow marks the
non-grappleable recesses. Solid ledges use snow caps and shaded glacier ice.
The actual dead pine trees, deep sinking powder and mountain panorama retain
their preceding artwork. Collision and grapple behavior are unchanged.

## Deliverable

- `Bionic_Commando_HD_v0.12.4.zip`
- SHA256 `931e8fe5e2bb4fe5af8c7847773a9c91a07e9f64e364fe8e5d610441b337d18e`
- 47,109,578 bytes; 55 runtime files.
- Every runtime file matches a clean default rebuild byte for byte.

## Final playback

The final run, `v0124-resumed`, completed all 11,110 input frames of `3.mmo`
in one uninterrupted guarded playback using the unchanged MesenCE 2.2.1 core.
An earlier attempt stopped during the connection interruption and was not
used as the final validation. No crash occurred in the completed run.

Playback completed before packaging. After the ZIP was created and extracted,
all 55 extracted runtime files were verified byte-for-byte against the pack
loaded by that completed playback. All 187 RAM and 187 PPU checkpoints match
the original-game reference, with zero state mismatches.

Every-frame auditing covered 3,181 graphics
states with zero unmapped states. All 296 changed material pattern/palette
pairs select snow artwork or explicitly retained doorway art. There are no
old rock or vegetation fallbacks in these recorded states. The 16 doorway
cells, all five explosion patterns, 281 robot states and three-frame boss-edge
pixel check remain valid.

All 2,872 other graphics states
select the same rules with the same observation counts and frame spans as
v0.12.3. All 260 common non-outdoor screenshots are byte-identical to that
approved playback. The final run produced 798 valid PNG screenshots and one
empty startup capture before the first rendered image.

## Visual review and corrections

The first review exposed brown horizontal strips incorrectly classified as
bark. These are cliff indices 33–36 and now receive snow. Actual tree indices
9–32 and 37–40 retain their wood. A second review exposed bright foreground
patches over the darker ice face; those strips now sample their underlying
ledge column at the native one-pixel offset while retaining native alpha and
draw priority. Eight recorded foreground states selected those aligned rules.

Reviewed the final outdoor sheet at frames 1441, 1900, 2041, 3001, 4501 and
5041, plus full-size foreground views at 2041 and 3001. These cover the tree
and deep snow, cliff approach, ascent, grappled ledges, enemies, foreground
occlusion and entrance. This is sampled visual review plus every-frame
auditing; it does not claim every frame was individually viewed.

All 194,492 preceding tile rules and 52 preceding PNGs remain unchanged.
The 328 added rules require Area 3, including 16 unchanged doorway rules
repeated to preserve priority. There are no new sprite additions or invalid
tile references. All 11,061 Area 3 neighboring-cell references are bounded.

Only the supplied Area 3 recording was replayed. Other areas and unrecorded
routes remain outside this review. The ZIP contains only the installable
pack and notes, with no ROM, emulator, movie, MP4, source painting or bundle.
