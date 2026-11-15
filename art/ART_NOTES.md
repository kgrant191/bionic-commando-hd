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

## v0.4.1 sources

| Asset | Prompt and use |
| --- | --- |
| exterior-seams-v4.1.png | Built-in image edit of a 4×3 texture atlas: replace cyan strips with matching rusty steel or warm rock, preserve cell alignment and all other motifs; ladder holes remain black. Only contaminated pixels and their immediate fringe are consumed by the builder. |
| radio-door-v4.1.png | Built-in image generation from the native background-only door layout and control-room style reference: continuous brushed-steel lintel, recessed square end housings, thin straight jambs, pure black open interior, no symbols, figures or threshold. All eight background patterns use this one aligned source. |

## v0.4.2 source

`closed-door-v4.2.png` was generated with the built-in image tool from an
in-game closed-door style reference. Prompt: front-facing, edge-to-edge square
military security-door panel, worn burgundy and charcoal steel, center seam,
inset panels and bolts, small silver mechanical wing/radio badge in the middle
third; no scenery, lettering, people or political symbols. The builder scales
it to the native 32 by 24 pixel panel at 4x and maps it under the live actors.

## v0.5.0 sources

All six new sources were made with the built-in image tool. These are the final
prompt specifications; the deterministic builder slices and fits them to native
geometry. Preview comparisons are actual emulator frames.

| Asset | Final prompt specification |
| --- | --- |
| cave-lift-v5.png | Edit the cave screenshot with all geometry locked. Replace flat purple lift hydraulics with detailed brushed steel, blue-black ribs, pistons, bolts and valves. Replace the blue doorway with a dark steel gate and cyan indicator, and the red platform with rust-red metal and a silver underside. Finish coarse rock edges. Remove Spencer; retain olive wall, red rocks and black voids. |
| cave-fixtures-v5.png | Preserve the cave screenshot layout and accepted rock, pipe and wall art. Complete flat purple crate edges as riveted gunmetal, elevator strips as silver rims and coarse vertical rock strips as detailed red stone. Remove both figures, no added objects or text. |
| reactor-reference-v5.png | Edit the generator screenshot at fixed geometry. Remove characters, orb and explosions. Complete purple housing/pipe slivers and unfinished blue vent panels with adjacent painted steel materials. Retain amber core, gold platforms, navy walls and black voids. |
| effects-v5.png | Four transparent cells: compact orange-white impact, expanding radial fireball, dissipating blast ring with an open center, and symmetrical ceiling-mounted steel electric emitter with cyan coil. Crisp painted arcade style, separate complete silhouettes, no labels or background. |
| area-clear-spencer-v5.png | Recreate only the original victory-screen figure as a full-body transparent painted cutout. Orange swept-back hair, sunglasses, green fatigues, black boots, radio and shoulder bazooka; visibly robotic silver left arm with articulated metal fingers. Relaxed airborne victory pose, detailed 1990s arcade illustration, no text or scene. |
| armored-guard-fire-v5.png | Use the existing stocky armored guard as the identity reference. One full-body transparent pose: burgundy helmet and armor, feet apart, torso facing forward, head turned left, one arm extended horizontally left with a silver mechanical gauntlet and short wrist barrel, the other fist at the torso. Preserve proportions and painted arcade style; no projectile, floor, labels or other figures. |

The shallow swing addition reuses and reflects the existing v0.4 swing painting.
The results-screen frame and live typography are drawn by the pack builder.

## Area 13 assets

Generated with the built-in image tool, then integrated as 4x tile/metasprite atlas assets.
- area13-exterior.png: redraw the exact Area 13 outpost geometry in the established painted metal/stone style, bronze shutters, medical cross, rocky bank, teal water.
- area13-interior.png: exact stone-room layout, limestone borders and dark slate brick recesses, no characters.
- area13-poses-v3.png: eight white-guard poses in a 4-by-2 transparent sheet, native standing/aiming/walking/landing forms.
- area13-npcs.png: olive and burgundy sentries. Alpha cleanup in the atlas builder discards the generator's soft surrounding halo; body proportions are preserved.
- area13-portraits.png: white, burgundy and olive helmeted contacts, closed/open mouth rows; three columns by two rows.
- area13-items.png: olive supply canister, red first-aid badge and cream/burgundy parachute with cords.

Generated scene artwork is sampled into CHR-RAM tile rules; it is not a static replacement screenshot. Live sprites, collision geometry, dialogue text, item timing and palette alarms remain driven by the ROM.

- area13-informant.png: auburn-haired neutral-area informant, closed/open mouth pair based directly on the recorded portrait.
