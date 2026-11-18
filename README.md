# Bionic Commando HD

**v0.12.1 — Area 3 pendant, snow and robot corrections**

Repository: https://github.com/kgrant191/bionic-commando-hd

A 4× Mesen/MesenCE graphics pack for the USA NES version of Bionic Commando.
This is a work-in-progress graphics remake covering the supplied opening story, Area 1, Area 2, Area 3, Area 13, Area 4, Area 5, Area 15 and Area 16 recordings.

## Install

1. Load your `Bionic Commando (USA).nes` ROM in Mesen or MesenCE.
2. Choose **Tools > HD Packs (NES) > Install HD Pack** and select
   `Bionic_Commando_HD_v0.12.1.zip`.
3. Confirm installation, enable HD packs in the NES video settings, and reload
   or reset the game when prompted.

For manual installation, place the contents of `pack/` together in
`HdPacks/Bionic Commando (USA)/`. If your ROM has another filename, the pack
directory must match its base name exactly.

## New in v0.12.1

- Cross pendant replaces the incorrect red radio in the equipment/map inventory.
- The stray distant-background tile by the tree limb is removed.
- Deep sinking snow uses soft, low-contrast powder texture.
- Area 3 reuses the approved Area 5 robot, damage palettes, fixed nozzle and native exhaust phases.
- Full `3.mmo` replay and exact-ZIP verification; no earlier-area movie regression.

## New in v0.12.0

- Painted alpine rock, snow, tree branches and distant mountains.
- Painted factory pipes, service columns, wall grilles, bridges, moving lifts and visible spikes.
- Crawlers, balloon insects, plant jaws and seed projectiles follow their original animation phases.
- Complete radio-room knife guards with native walking poses and damage states.
- Generator entrance eagle and AREA 03 CLEAR text. The inventory item is a cross pendant (corrected in v0.12.1).
- Validation is limited to the full supplied `3.mmo`; no wider level regression was requested.

## Included v0.11.5 fixes

- Generator/final-boss entrances display a gold eagle, selected by their original eagle-header patterns.
- The marker covers all five currently mapped palette variants; radio and ordinary doorway headers retain their own designs.
- Use the eagle consistently when adding later boss-room entrances.

## Included v0.11.4 fixes

- Complete the alternate doorway header, standalone round outlets and extended pipe beneath the platform.
- Replace stacked horizontal pool strips in the tall outlet with a connected vertical blue slime flow.
- Keep the visible pipe painted when its elbow scrolls off-screen.
- Retain the doorway crash fix, blue slime blobs and native-timed rifleman walking frames.

## Included v0.11.3 fixes

- Thick blue slime blobs, ground pools and pipe discharge replace the watery material in Area 2.
- The short red rifleman alternates two walking poses at the original animation cadence instead of sliding in a kneeling pose.
- Blue slime replacements are scoped to Area 2; future areas retain their own palette handling.

## Included v0.11.2 fixes

- The outpost entrance now has an opaque dark interior.
- Area 2 neighbor lookups stop at the screen boundaries, preventing the invalid read exposed while entering the first doorway.
- Validated using the full supplied recording with protected screen buffers.

## Included v0.11.1 corrections

- Repainted outpost facade and railing, open doorframes, crates, steel outlets, connected pipes, wall grilles and ledge mounts.
- New grenade blast and water-splash artwork follows the native animation phases.
- Complete red soldier recoil artwork replaces the pale native hurt pose.
- Spencer's additional damage palettes use his complete painted weapon/pose assembly.
- Checked with the supplied Area 2 recording only. No earlier-area regression was run for this revision.

## New in v0.11.0

- Area 2 mountain outpost, aqueduct rock, masonry, mossy platforms, flowing water and visible steel spikes.
- Painted tracked carrier, independently moving hanging hazard, red grenadier and crouching rifleman.
- Carrier chassis stays aligned through its native movement and wheel phases; recorded clipping and destruction fragments remain painted.
- Consistent Area 02 clear-screen numerals and the 2nd Platoon dialogue numeral.
- Approved v0.10.6 runtime retained as the baseline for every earlier area.

The spike tips are also at the lower viewport edge in the original game and can
scroll out of view. This artwork update preserves the original level geometry,
camera, movement, collision and damage timing. Only recorded states are covered;
this is a review build, not a finished-game release. See
`validation/AREA2_v0.11.0.md` for playback coverage and limits.

## New in v0.10.1

- Assemble overhead Spencer as one complete pose through walking and hit flashes.
- Correct downward and diagonal facing; use a substantial shoulder-fired rocket launcher.
- Keep the large circular rocket projectile and distinct three-barrel wide cannon.
- Preserve Area 16 building signs when their identifying tiles scroll off screen.
- Give the red-clothed room contact matching bareheaded red dialogue portraits.

Includes a frame-by-frame overhead replay, an eight-direction diagnostic, Area 16
scrolling/dialogue review, and the prior Area 5 boss regression. See
`validation/MOVEMENT_TOWN_v0.10.1.md` for validation scope.

## New in v0.10.0

- New rocket launcher and three-barrel wide-cannon equipment icons.
- Spencer holds the selected weapon in side-view and overhead gameplay.
- Rocket shots retain their original large circular footprint and movement.
- HD overhead damage palettes, dropped grenade and brief impact effects.
- Area 16 town scenery, interiors, portraits, guards, turret and transition palettes.

Replayed both supplied recordings, a controlled wide-cannon test, and the previous
Area 5 boss recording. See `validation/WEAPONS_AREA16_v0.10.0.md` for coverage
and limits. This is a feature-branch review build, not a public release.

## New in v0.9.8

- Keep the gray building facade stable while moving and after leaving rooms.
- Repair the doorway facade, rooftop railing and emblem, and clipped upper enemy.
- Restore the metallic blue ball and maintain HD damage/swinging graphics.
- Preserve the Area 5 boss's crimson and white armor; use a fixed rear nozzle
  and a complete animated flame with correct edge clipping.
- Retain generator hit-flash timing and its intended black side recesses.

The final Area 5 recording was checked across all 1,940 game-state frames and
646 screenshots, plus 116 consecutive thruster-animation frames.
This remains a review build; later areas and unrecorded states still need review.

## New in v0.8.2

Complete Super Joe's rear leg and boot during the intro. The existing artwork, scale and position are preserved; three missing sprite cells now render throughout the recorded scene and its palette transitions. Other scenes and gameplay artwork are unchanged from v0.8.1.

## New in v0.8.1

- Show the HD title from the initial boot and power-cycle title state. Cover story scenery and native sprite fragments through palette transitions while keeping the original text live.
- Replace Area 5's mistaken lava with solid earth; repair barrel scale, the distant wall behind lamps, open doorframes and the visible coil springs.
- Use mechanical ceiling objects, rotor-equipped blue infantry, the established knife guard and a dedicated floating robot boss.
- Rebuild overhead combat with a quieter dirt/water palette, proper overhead figures, painted barricades and an updated exit bunker.
- Cover both Area 15 supply interiors, talking portrait fragments, the red-haired 1UP, moving barrier and colored radio pickups/menu icons.
- Rejoin Area 1 cave doorway headers and jambs and replace the boss-room shutter.

Review build. Original gameplay, collision, dialogue and timing remain unchanged.
See `validation/REVIEW_FIXES_v0.8.1.md` for recorded coverage and limits.

## Area 1 corrections in v0.7.6

Rebuild the open exterior doorframe from an unobstructed steel frame. The
communication-room and boss entrances are included in the replay review.
Crate rewards now have an illustrated POW emblem and green recovery flask.
The orbiting POW star keeps its native movement and expiration timing while
using the new artwork through recorded palette changes.

The bazooka soldier now has dedicated grenade wind-up and release poses,
including the previously unmapped release head. Thrown grenades have their
own compact sprite. Clipped red soldiers retain painted lower-body pieces.

See `validation/AREA1_FIXES_v0.7.6.md` for verification and limits.

## Knife guard and active flare in v0.7.5

The fast charging burgundy guard has a broader, muscular build and carries a
visible knife. His three movement poses share one scale and head anchor. The
same native enemy in Area 13 receives the correction too; other character
identities retain their own artwork.

An active flare now appears as a lit red illumination canister. It no longer
shares the silver gunshot artwork, even when Spencer fires while the flare
is rising or the camera scrolls. The existing unlit flare pickup/equipment
icon and XP bullet collectible retain their separate designs.

Includes the v0.7.3 town improvements and v0.7.4 gunshot palette fixes.
See `validation/KNIFE_FLARE_v0.7.5.md` for evidence and review limits.

## Projectile fixes in v0.7.4

Enemy gunshots in Area 13 now use dedicated HD projectile artwork. The same
shot stays visually consistent when Spencer's invulnerability palette flashes
in Area 4. All six recorded palette variants use the same projectile instead
of alternating between character-material shading and enlarged NES graphics.
Native flight paths, timing, sprite flips and hit detection remain live.

Includes the approved v0.7.3 town portraits, scenery, frames and doorway fixes.
See `validation/PROJECTILES_v0.7.4.md` for the evidence and regression coverage.

## Area 13 polish in v0.7.3

Town conversations use illustrated three-quarter portraits against the live
black dialogue panel. Red and green contacts match their standing characters;
the two white-cap portraits retain their distinct identities. The older white
NPC now renders once, using a unique face tile instead of a mirrored head tile.
Communication-room portraits keep their existing presentation.

The dialogue and portrait frames share a restrained metal border. A painted
sky, clouds, layered snow mountains and distant trees replace the repeated
native scenery. The backdrop follows the game's alarm palette changes.
The supply-room doorway has a complete header and continuous side posts;
spikes retain the original alternating heights with clean, matching bases.
Small barred building façades also receive painted materials.

See `validation/AREA13_v0.7.3.md` for the six-recording regression results and
visual review limits.

## Visual fixes in v0.7.2

Movement frames for the Area 4 shield boss, red rifle guards and Area 13 red
runner share one body scale and a stable head anchor. White NPC portraits
match each standing character's face, white uniform and patrol cap.

The XP bullet keeps the original broad white-and-green silhouette for better
visibility. Player and enemy health use the same metal-rimmed indicator style
with their original colors, counts and timing. The mission debrief displays
`AREA 04 CLEAR` (or the live area number) in one consistent font.

The initial Area 1 descent no longer reveals stale wall and ground fragments
under the bottom water row. The replacement requires actual water directly
above the affected edge tile and is restricted to Area 1 gameplay.

See `validation/FEEDBACK_v0.7.2.md` for the replay coverage and review limits.

## Item corrections in v0.7.1

The Area 13 room drop is the same XP bullet dropped by enemies. Both use the
same cartridge artwork. Flare bombs use a compact unlit illumination canister
for their pickup and equipment icon. Energy Recovery remains a separate item.
Reference: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Items

## Area 4 in v0.7.0

Painted gorge, limestone caves, copper pipes, mesh panels, vents and ledges. Adds sleeveless guard walking states, shield guards, and flare/communicator icons. The boss dialogue portrait has idle/talking expressions, and the open doorway has painted trim. Cave darkness and native palette changes remain live.

## Area 13 corrections in v0.7.0

White, green and red uniforms retain their original colors. White idle NPCs,
armed and unarmed green contacts, and the red runner have distinct artwork.
The red runner uses a consistent three-pose cycle; the red rifle guard is also
covered. White guard hit flashes retain their white artwork. The room pickup and enemy drops share one XP-bullet cartridge. The flare bomb
is a compact illumination canister in both the room and equipment icon.
Shared sprite layers are combined to avoid clipping overlapping enemies.

See `validation/AREA4_v0.7.0.md` for replay results and review limits.

## Regression fixes in v0.6.1

- Correct Game Over detection; title art no longer covers its text.
- Suppress the painted sky during native display-off transitions.
- Add Spencer’s final lying-down death pose.
- Replace the distinct player, enemy and supply-drop parachute patterns.
- Cover the missing electrical-hazard palette variant.
- Complete the Area 13 green contact’s walking poses.

See `validation/REGRESSION_v0.6.1.md` for recording coverage and limits.

## Included artwork

- Painted cave lift machinery, moving platform, gate, crates, rock edges and elevator rims.
- Additional recorded enemy hit palettes, including the bazooka soldier, retain HD figures.
- A new firing pose for the final-room armored guard covers its extended gauntlet attack.
- A painted fallback for partially occluded actors prevents overlap/clipping from exposing NES body fragments when a complete pose signature is unavailable.
- An additional shallow swing angle reuses the painted mechanical-arm pose.
- Completed generator housings and pipe edges, painted explosion phases and electric-hazard emitters.
- Painted scenery, effects and actors fade with the native generator shutdown sequence.
- A new Area Clear illustration and results panel, active before the header types in; bonus values and reward text remain live.
- Painted closed exterior radio-room doors, with Spencer visible in front as he passes in either direction.
- The recorded enemy hit-palette variants now retain their painted poses and damage tint.
- A complete painted steel doorway in the communication room, including the previously occluded header and right jamb.
- Corrected blue contamination in the repeated barrel, platform and ladder texture crops. Real sky openings and water retain their existing artwork.
- New title artwork and readable start prompt.
- Painted radio portraits for the operator, commander, and two intercepted
  enemy speakers. All four speakers retain their talking expressions; the final-room
  officer portrait is covered too.
- Painted world-map terrain with live routes, area numbers, selection and units.
- Eighteen Spencer paintings mapped to twenty-one selected pose records covering standing, running, crouching,
  firing, hanging, swinging and the parachute entry, with full painted bodies.
- A clearly exposed steel grappling arm across the painted Spencer poses, with two additional rotated swing poses.
- Consistent enemy artwork scale across crouching and firing; pose bounds no longer stretch bodies according to weapon length.
- Twelve selected enemy poses covering rifle troops, crouching soldiers,
  bazooka troops, a grenade thrower and the large armored guard.
- Palette-specific material fallbacks and metal grapple links for other states.
- Painted fortress masonry, girders, barrels, cliffs, water, tower stucco
  and coping; an atmospheric sky replaces the flat exterior blue.
- A painted exterior searchlight; water now matches only the eight recorded foam patterns.
- Painted edge variants between walls and girders instead of the old patterned patches.
- An HD equipment menu, moving selection highlight and painted starter handgun/radio icons on both equipment and map screens.
- Painted underground rock, metal panels, pipes and platforms.
- Olive-brass cylindrical machinery and rails in the later underground section.
- Painted communication-room machinery, final-room scenery and the reactor's
  blue-steel tubing and amber core. Scenery paintings persist through captured
  background-palette flashes.
- 4× replacements covering the supplied recording's captured tile/palette keys.
- Eight NES pixels trimmed from the top and bottom to hide the observed
  scrolling garbage in the overscan area. The output is 1024 × 896 before
  aspect-ratio correction.
- Mesen's sprite-limit removal enabled to reduce missing sprite strips during
  crowded combat.

The ROM is not modified. Controls, level geometry, collisions, bionic-arm
behavior, enemies, music, dialogue content and game logic remain driven by the
original game.

## Still in progress

Painted poses follow the game's native positions, flips and animation triggers.
This is a selected-pose pass, not a complete redraw of every animation frame.
Unrecognized head patterns keep the previous material treatment; transitions and
unrecorded moves still need review. If overlap hides a recognized pose's distinguishing
body tiles, the most common painting for that head is used until the signature returns.
Some effects and unrecorded equipment icons retain a smoothed baseline. Remaining architectural variants
and map vehicle shapes need further art passes.
The new title appears as a static composition; the original sliding logo and
small title character animation are not reproduced.

The handgun is the starter-weapon design, not the final design for every weapon.
Weapon-specific artwork can use Mesen equipment-memory conditions or distinct
native weapon patterns. Machine-gun and bazooka player variants still need
recordings, verified selection state and dedicated art before they are supported.

The supplied opening/Area 1 recording, closed-door/enemy-hit recording, cave-to-generator recording and a controlled equipment-menu replay have been tested. Later areas,
unrecorded moves and alternate equipment or palette states need recordings
and validation. Shared tile patterns may affect later areas.

## Validation and source

Rebuild the runtime with `python3 scripts/build.py` (Python 3, Pillow,
NumPy, SciPy and the included xBRZ scaling library). The current builder
reconstructs the preserved v0.10.6 baseline, applies the approved Area 2
patches, then adds the Area 3 rules and generated artwork.

`validation/v0121-verification.json` records the exact-ZIP Area 3 replay,
every-frame mapping audit, original-game RAM/PPU parity and screen-bound
checks. `validation/v0121-reproducibility.json` records the clean rebuild
comparison. See `validation/v0121-review.md` for visual review scope.

The install ZIP contains only the pack and its install notes. ROMs, emulator
binaries, gameplay recordings and developer files are not included.

Tested core: MesenCE 2.2.1; HD-pack format 109.
Whole-file ROM SHA1: `D3A4BFD995D18C4A386971631759AECA3A7CFF8D`.


## Area 13 review pass

Adds Area 13 scenery, stone interiors, white guards and parachutes, neutral-area contacts, animated dialogue portraits and two item pickups. Based on the v0.5.0 cave/generator branch. Review build; no release is implied.
