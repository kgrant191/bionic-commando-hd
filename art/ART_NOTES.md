# Artwork sources

Six generated painted reference assets underpin this test build. They were
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

All image references are resized to 1024 × 960 during the build. The final
display crops the outer eight source rows from top and bottom. Remaining
sprites and UI use the separately documented smoothed baseline.

