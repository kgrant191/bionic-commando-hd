# v0.8.1 art source briefs

Created with the built-in image-generation tool, then cropped/resized into the pack by the checked-in build scripts. Native sprite/screen references in `capture/review-v081` control geometry; the generated images do not determine gameplay boundaries.

| Source asset | Final art brief |
|---|---|
| `area5-boss-v081.png` | Preserve the native floating mechanical boss silhouette: white/cobalt armored body, upper prongs, sensor head, left gun and lower U-shaped hose. Transparent side-view sprite. |
| `ceiling-machine-v081.png` | Compact symmetrical silver/cobalt mechanical object, flat top crossbar, dark sensor slit, tapering brackets and lower skid. No human anatomy. |
| `helicopter-infantry-v081.png` | Two same-scale blue infantry poses: leaning flight and frontal hover. White helmets, visible overhead rotors, forward guns and black boots; no shields or parachutes. |
| `area5-materials-v081.png` | Six orthographic material/fixture cells: solid brown earth, olive wall, burgundy wall, rust-red barrel, paired silver coil springs and open steel/copper doorway. |
| `overhead-commandos-v081.png` | Four facing directions for red-haired Spencer with steel left arm and burgundy enemy soldiers. Steep overhead camera and compact foreshortened bodies. |
| `spencer-life-v081.png` | Symmetrical front-facing head/shoulders icon with vivid copper-red hair, sunglasses and green uniform, readable at 64×64. |
| `interception-terrain-v081.png` | Preserve shoreline/path/ridge/cover geometry; replace noisy orange soil with quieter natural brown dirt, muted rocks and calmer teal water. |
| `interception-bunker-v081.png` | Match the native roof, black opening, gray threshold and steel ramp; remove the reference soldier and use continuous material underneath. |
| `heavy-weapon-icon-v081.png` | Match the native diagonal olive heavy weapon, silver bands/muzzles and wooden lower-left grip/stock. Complete connected inventory icon. |

Radio case variants are renderer palette grades of the approved radio artwork. Existing approved knife-guard, story, door and portrait artwork is reused. Transparent generated sprites retain their alpha in the source files.

The moving room barrier, cave shutter and Area 15 shield plaques are code-native geometric fixtures in `scripts/review_fixes.py`, sliced to the original tile grid.
