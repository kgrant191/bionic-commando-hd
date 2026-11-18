# Area 2 correction artwork

Generated with the built-in image generator, with genuine transparent alpha,
then extracted, scaled and mapped to recorded native assemblies by the builder.
No hand-redrawn NES masks substitute for the replacement object artwork.

## Structures

Source: `area2-structures-v0111.png`. Six-cell, three-column/two-row atlas.
Prompt: a detailed painted military side-scroller asset sheet, orthographic
front view, upper-left light, no text or labels, transparent gutters. Separate
weathered gray concrete outpost with olive roof railing and open doorway;
brushed steel aqueduct doorway; connected steel U-pipe with elbows and clamps;
round wall outlet with drainage plate; wood supply crate with metal straps;
paired steel ledge mount. No sky, ground, characters or shadows. Restrained
dark teal weathering and realistic material highlights, no NES pixel masks.

The builder isolates the largest connected component of each structure before
cropping. This excludes a neighboring facade edge that entered the doorway
cell's transparent gutter. Openings retain transparency. Pipes use neighboring
native tile signatures so repeated wall cells can carry one continuous image.
The later narrow shaft fixture reuses the same painted pipe sections and vent
cap, with its own neighboring-pattern mapping for the shared middle cells.

## Effects

Source: `area2-effects-v0111.png`. Six-cell, three-column/two-row atlas.
Prompt: three successive orange explosion phases, compact ignition, larger
turbulent fire burst, and dissipating smoke; three successive turquoise water
splash phases, low crown, tall plume, falling plume. Crisp detailed painted
game effects, transparent background, equal cells, consistent centers and
bottom alignment, no labels, faces, rigid outlines, scenery or shadows.

Native explosion and splash timing, OAM mirroring and footprints remain live.
Clipped water fragments have painted fallbacks when neighbor tests are absent.

## Red recoil pose

Source: `area2-recoil-v0111.png`. Three-column/one-row atlas.
Prompt: the same compact crimson-helmeted infantry soldier facing left,
crimson uniform, brown webbing and dark boots, in hit recoil with one leg
extended, falling recoil with knees tucked, and kneeling rifle-aim poses.
Detailed painted sprite art, equal anatomy and helmet scale, genuine alpha,
no blood, injury, muzzle flash, labels, shadows or environment.

The recorded recoil uses the first cell. The other cells remain source-only;
the runtime atlas includes only mapped cells. Palette flashes keep the red
uniform recognizable. Spencer's correction reuses his existing painted art.
