# Continuous Area 3 tree artwork

The image tool painted `area3-tree-v0127.png` from the native silhouette guide
`area3-tree-silhouette-v0127.png`. The brief requested one weathered dead pine
with long bark fissures, cylindrical shading and grain curving naturally from
the trunk into the right branch. Preserve the native broken crown, branch
length, width and tip, with no foliage, new branches, scenery or snow.

The preceding builder rotated separately sampled 8x8 tile textures, producing
square patches. The new builder slices coherent crown, junction, trunk, branch
and tip modules from the painting before dividing them into 4x replacement
tiles. The left junction and tip mirror the corresponding painted modules.
Every tile receives its exact preceding native alpha mask, preserving all
broken contours and gameplay geometry. Only catalog indices 9–32 and 37–40
of background palette 1C271707 are trees; indices 33–36 are cliff bands.
