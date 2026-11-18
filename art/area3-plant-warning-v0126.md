# Giant plant warning artwork

`area3-plant-warning-v0126.png` was generated with the built-in image tool
for the two native pre-emergence animation phases. The prompt requested two
transparent, side-by-side frames of churning snowy grass and soil: broken
white snow on torn green turf, a dark earthy split, brown clods and snow
chips, with distinct left and right heaves. No plant bud is visible yet.
The style is crisp hand-painted arcade pixel art with readable chunky shapes.

The builder crops both frames to a common alpha bounding box and scales each
to a native 8x16 sprite column at 4x resolution (32x64). The four repeated
columns, phase changes and mirroring come from the original game's sprites.
No extra sprites, collision changes or independent animation timer are added.

Passable cliff markings reuse the existing packed-snow painting in
`area3-classic-materials-v0125.png`. Solid gray stone is unchanged.
