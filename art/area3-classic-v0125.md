# Area 3 original-style terrain source art

User direction: return closer to the original Area 3 arrangement of rock,
dirt, grass and snow, with enhanced detail. The two supplied original-game
screenshots establish the material placement and palette.

Source PNGs were generated with the built-in image generation tool:

- `area3-classic-materials-v0125.png`: four equal panels, warm ochre/chestnut
  irregular cliff rocks, muted gray weathered recess rock, dark chocolate
  soil and pale packed snow. Orthographic HD arcade pixel art, no scenery,
  labels, borders or characters.
- `area3-snow-grass-ledge-v0125.png`: horizontal front-facing terrain strip,
  a thin white snow cap, hanging green alpine grass and a broad dark brown
  earth face with roots and fine pebbles. No icicles, large stones, sky or
  floating-island outline.
- `area3-rock-tile-v0125.png`: a dedicated square repeating warm chestnut
  and ochre cliff tile, four or five broad irregular rounded rock faces,
  shallow dark cracks and restrained speckles. Flat orthographic arcade
  pixel art, uniform illumination and no rows, stripes, scenery or snow.
  This replaces the atlas rock sample after playback exposed its repetition.

The builder crops readable material samples and slices them into native tile
positions. Native masks determine the snow patches, soil transitions and
contours. A recorded adjacency graph fixes the two-by-two texture phase in
world space; uniform fill and doorway patterns are excluded from that graph.
The two complete source images remain in `art/`; runtime uses the packed atlas.
