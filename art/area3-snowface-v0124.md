# Unified snowy cliff art

The user requested a consistent snowy wall face instead of the patchwork of
rock, snow and green vegetation. Both sources were created with the built-in
image generator and compiled into `pack/area3-snowface-v0124.png`.

`area3-snowface-v0124.png` contains two equal side-by-side texture panels.
The generation prompt requested a continuous tightly packed alpine snow face
in off-white and pale blue on the left, and matching smoother, shaded snow
in a shallow recess on the right. Both use low-contrast, wind-smoothed grain,
front-facing orthographic lighting and edge-to-edge repeating coverage, with
no rock, brown colors, vegetation, objects or text.

`area3-ice-ledge-v0124.png` edits the existing isolated snow-topped ledge.
The edit prompt requested changing all brown rock on the underside to packed
white snow and pale glacier ice, retaining the wide silhouette, thickness,
walkable upper edge, small icicles and painted game style on genuine alpha.
The runtime integration retains the preceding platform alpha contour.

The former bark classification accidentally included cliff-band indices
33–36 in palette 1C271707. These are now snow. Actual tree indices 9–32 and
37–40 retain their wood artwork.

Foreground snow strips sample the same ledge artwork at the native one-pixel
vertical offset. Their original alpha masks and draw priority remain intact.
