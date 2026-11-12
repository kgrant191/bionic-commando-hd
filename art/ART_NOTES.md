# Artwork sources

Generated painted reference assets underpin this test build. They were
made with the built-in image-generation tool, then consumed by the deterministic
pack builder. Runtime screenshots in the preview are emulator output, not
concept mockups.

The shared art brief was: crisp hand-painted 1990s arcade-remaster style;
orthographic side view; preserve the supplied screen's platform, wall, pipe,
window and floor geometry; remove characters and projectiles from background
references; no added structures, blur, perspective shifts or lettering.

Final prompt specifications:

| Asset | Prompt specification |
| --- | --- |
| level1-reference.png | Redraw the fortress screenshot in aligned olive-gray masonry, rusty red steel girders, copper-red barrels, grass-topped warm rock, blue foamy water and clear blue sky. Remove both soldiers and the grappling rope. |
| interior-reference.png | Preserve the underground screenshot's exact shaft, platform and pipe geometry. Redraw orange rock as rusty-red natural rock, green diagonal walls as dark olive plating, blue tubes as blue steel, purple ledges as gunmetal with fine violet edges. Remove the player, rope and projectiles. |
| control-reference.png | Preserve the communication room layout. Redraw corrugated gunmetal floor/ceiling, green military machinery, cyan grid screens, pipes and burgundy console controls. Remove Spencer and radio-wave pixels. |
| reactor-reference.png | Preserve the final room layout. Redraw flat blue walls as navy metal panels, gold platform ledges, cyan computer grids and gunmetal corrugation. Remove every soldier and projectile; keep black openings. |
| radio.png | Preserve the two empty black top panels and exact lower radio silhouette/control layout. Add brushed gunmetal panel frames and detailed olive-drab field-radio hardware, muted cyan glass and green indicators. Remove text and portrait for live runtime layers. |
| title.png | BIONIC in angular brushed steel with red insets, COMMANDO in golden industrial type. Dark blue fortress and radio towers at dusk. Orange-haired Spencer in sunglasses and green uniform at lower right, metallic forearm visible. Reserve dark center/bottom areas for runtime prompt and copyright composition. |

## v0.2.0 sources

| Asset | Use in the pack |
| --- | --- |
| map-terrain.png | Painted desert, jungle and coast placed behind the game's live route/number tiles and units. |
| portraits.png | Six aligned portrait cells: operator and commander (closed/open mouth), enemy soldier and bearded officer. |
| enemy-talking.png | Talking-mouth variants of the enemy soldier and bearded officer; the officer is reused in the final-room dialogue box. |
| action-poses.png | Painted Spencer/soldier material and face reference. The current pack samples cloth, relief and selected heads, retaining the original animated tile masks. Full pictured poses are not yet runtime replacements. |
| tower-reference.png | Tower stucco, damaged corners, coping, doorway and sky. Build-time piecewise coordinate alignment matches native geometry before extracting new tiles; existing approved tile art takes precedence. |

Scene backgrounds use 1024 × 960. The final display crops the outer eight
source rows from top and bottom. Portrait overlays keep a fixed canvas and
crop rectangle across talking states. Sprite/detail limitations are documented
in README.md. Actual-emulator preview screenshots are separate from these
source paintings.

## v0.3.0 sources

| Asset | Use in the pack |
| --- | --- |
| spencer-poses-v3.png | Transparent 4×4 sheet based on native pose references. Red hair, sunglasses, olive fatigues, dark boots and steel bionic arm. Each selected pose is fitted to its original opaque bounds and rendered using HD-only additions anchored to the native head. |
| enemy-poses-v3.png | Transparent 4×3 sheet with eleven occupied cells. Burgundy helmets and uniforms, dark boots and steel weapons. Native standing, crouching, running, throwing, bazooka and armored-guard poses determine bounds and facing. |
| reactor-machine-v3.png | Aligned close-up painting of blue-steel reactor tubing, gunmetal housings and an amber core, with enemies and projectiles removed. |
| machinery-reference-v3.png | The later underground room, preserving its original geometry while replacing lime-green machinery with olive-brass cylinders and tubular rails. Native layout landmarks align the source before tile extraction. |

The v0.3 pose sheets provide full runtime figures for selected signatures;
the earlier action sheet remains the material fallback for other patterns.


## v0.4.0 sources

| Asset | Use in the pack |
| --- | --- |
| spencer-poses-v4.png | Edit of the 4×4 Spencer sheet: exposed brushed-steel shoulder, elbow, forearm and articulated fingers on the left grappling arm; human right weapon hand. |
| spencer-swing-v4.png | Two transparent painted cells aligned to previously uncovered rotated head/body groups. Red hair and skin remain visible while the mechanical arm reaches toward the grapple. |
| equipment-lamp-v4.png | Three-column transparent atlas: starter handgun, military radio and warm ivory searchlight on a rusty red steel post. Exact native icon and lamp patterns select the corresponding crops. |

Enemy poses now share one uniform source-to-output scale; each native pose's
feet and helmet position determine placement. Background/cursor geometry for
the equipment screen is drawn programmatically from the native menu layout.
