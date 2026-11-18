# Area 2 background layout corrections

Reuses the approved `area2-structures-v0111.png` and
`area2-blue-slime-v0113.png` source art. No newly generated artwork or actor
changes are included.

- The standalone wall outlet uses native patterns 96/92/97/93, which differ
  from the tall backed drain mapped in v0.11.1.
- The last doorway header uses patterns 136–141 plus the existing jamb
  shoulders. Its native open space remains opaque and dark.
- The extended left pipe below the platform needs two shaft sections.
  Nearby elbow anchors select the complete assembly; painted shaft fallbacks
  handle clipping without relying on a distant off-screen elbow.
- The tall slime nozzle uses patterns 98–105. A connected metal mouth and
  vertical blue ribbon replace the old pale rim and isolated pool pieces.
  Neighbor-selected slices cover its full height. Repeated sections below
  platforms use vertical ribbon material with masonry behind transparent edges.
- Two native anchors distinguish the longer pipe layout when clearing a stray
  fragment that the older wide-pipe rules painted into the platform underside.

Source layouts are retained in `capture/area2-v0114/` at movie frames 2401,
9361 and 9601. Every new rule requires Area 2, the cave scene, and background
palette `0F2B1C0B`. All nearby checks receive screen bounds before evaluation.
