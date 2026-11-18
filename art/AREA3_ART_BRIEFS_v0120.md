# Area 3 artwork, v0.12.0

Five generated sources provide painted material, architecture and creature assets.
The source images retain their original resolution and alpha. Runtime assembly
uses versioned, reproducible crops in `scripts/build_v0120.py`.

- `area3-materials-v0120.png`: four material swatches: brown alpine rock,
  blue-gray granite, packed snow and vertical dead-pine bark.
- `area3-industry-v0120.png`: olive pipe, blue service column, chain-link wall
  grille, steel bridge, moving lift and steel spikes.
- `area3-creatures-v0120.png`: three crawling leg poses, inflated/deflated
  balloon insects, and closed/open carnivorous plant mouths.
- `area3-details-v0120.png`: flat plant mouth, two seed projectiles, snowy
  platform lip, pipe elbow and industrial doorway.
- `area3-communicator-v0120.png`: red field radio inventory icon.

All source prompts requested orthographic game assets, consistent upper-left
lighting, readable shapes and alpha gutters. No generated text enters gameplay.
The approved alpine panorama and golden eagle plaque are reused unchanged.
The approved red knife-guard sheet supplies the radio-room enemies.

Native CHR patterns, palettes, flip flags and local part signatures select the
art. No timer, ROM patch or gameplay-memory write drives animation. Native
collision boundaries and the original seed trajectories remain unchanged.
Full enemy bodies use native head anchors. Existing virtual sprite destinations
are reused where an addition with the same anchor/offset already exists.

Art replacement scope is Area 3. Shared previous PNGs and tile rules stay byte-
identical; all new replacement rules have a positive `area3` condition. Neighbor
lookups short-circuit at screen boundaries before accessing adjacent tiles.
