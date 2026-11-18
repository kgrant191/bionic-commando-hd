# Area 2 source art

- `area2-materials-v0110.png`: generated four-part material sheet: gray mossy aqueduct rock, dark teal masonry, mossy stone ledge, turquoise flowing water. Runtime assembly retains native masks and animation phases; rock crops use recorded world-pattern phase alignment.
- `area2-tracked-carrier-v0110.png`: generated transparent side-view tracked carrier, red helmeted driver, teal steel chassis and extended boom. Runtime replaces the native hanging hazard separately and attaches chassis art to its stable native body anchor. Hub alternatives alter only the hub disks.
- `area2-grenadier-v0110.png`: generated six-pose transparent 3×2 sheet matching the established crimson infantry. Three running poses, grenade wind-up, throwing follow-through and a spare standing pose. Hand grenades only, with no rifle or launcher changes between poses. The runtime uses the first five poses, aligns helmets and feet to recorded native anchors, and discards low-alpha matte pixels.

Generated source images are retained intact. Cropping, scaling, alpha cleanup,
palette handling and native tile assembly are reproducible in the build scripts.
No ROM or movie file is distributed.
