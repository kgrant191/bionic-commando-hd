# Area 3 v0.12.3 winter vegetation review

The decorative outdoor mesh is replaced with dark alpine moss, creeping
juniper and small evergreen leaves with light frost. The painting stays
visually separate from solid brown rock and snowy ledges. Its four quadrants
follow native pattern adjacency, keeping the foliage aligned while scrolling.
Native contour alpha is preserved; collision and grapple behavior are unchanged.

## Deliverable

- `Bionic_Commando_HD_v0.12.3.zip`
- SHA256 `cf69d598f9b476088c75d6350391b4c75e3b9f750975875c7b580225b697d4c8`
- 47,051,570 bytes; 54 runtime files.
- All runtime files match the clean default rebuild byte for byte.

## Playback and verification

The first full `3.mmo` replay completed before packaging. The exact extracted
ZIP then completed all 11,110 input frames in one uninterrupted guarded run
using the unchanged MesenCE 2.2.1 core. No crash occurred. The loaded pack
matches the extracted ZIP byte for byte. All 187 RAM and 187 PPU checkpoints
match the original-game reference.

The every-frame audit covered 3,175 graphics
states with zero unmapped states. All 70 decorative backing patterns select
the vegetation atlas. All 3,105
other graphics states select exactly the same rules, with the same observation
counts and frame spans, as the approved v0.12.2 replay. The door, five explosion
patterns, 281 robot states and three-frame screen-edge check remain valid.

The final replay produced 718 valid PNG screenshots and one empty startup
capture before the first rendered image. All 287 common non-outdoor captures
are byte-identical to v0.12.2. All 21 inspected outdoor captures are identical
between the first playback and the exact-ZIP replay. Visual review included
full-size frame 2401, a four-view sheet (2041, 3001, 4501, 5041), and a 16-view
sheet spanning the outdoor ascent from 1840 through 5050. This combines
sampled visual inspection with every-frame auditing; it does not claim that
every frame was individually viewed.

The native outdoor layout was checked across 3,210 recorded frames. All 331
unique adjacent-pattern relationships fit one connected two-by-two texture
layout. No screen-position conditions or sprite additions were introduced.
All 194,422 preceding tile rules and 51 preceding PNGs remain unchanged;
70 new rules require Area 3's outdoor state. There are no invalid tile
references, duplicate additions or unsafe neighboring-cell references.

Earlier-area recordings and unrecorded routes were outside this review.
Only the install ZIP is delivered, with no ROM, emulator, movie, MP4, source
painting or Git bundle inside it.
