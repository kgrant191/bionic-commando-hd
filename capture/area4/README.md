# Area 4 capture evidence

Source: user-supplied `4.mmo`, 11,830 input frames, Mesen 2.2.1 format 3.
ROM SHA1: D3A4BFD995D18C4A386971631759AECA3A7CFF8D.

Native reference PNGs retain the 256×240 frame, including overscan. The adjacent
`.tiles` files record background/sprite layer, native x/y, CHR-RAM pattern,
packed palette, and OAM flips. Metadata was sampled every six frames; the
all-frame rendering audit supplies additional visible key/palette pairs.
`extra-keys.json` is their union. `original-rules.txt` is the native capture
inventory, retained as evidence rather than a shipped pack.

The builder matches exact native 8×8 pixels to the reference before sampling
paintings. The cave's palette-zero voids stay opaque black. Stone crops are
confined to valid texture cells, and structural paintings assert opaque alpha.
The far scenery uses only the recorded distant-scene patterns. Other areas are
excluded by the native area byte, and the menu/radio/results states are excluded.

Actor pose records are in `../area4-poses.json`; they retain the source CHR keys,
relative offsets, flip flags, and sample frame numbers. Three walking states
for each of the two new guard types select six paintings.
