# Bionic Commando HD

**v0.7.5 — Knife guard and active flare corrections**

Repository: https://github.com/kgrant191/bionic-commando-hd

A 4× Mesen/MesenCE graphics pack for the USA NES version of Bionic Commando.
This is a work-in-progress graphics remake covering the supplied opening, Area 1, Area 13 and Area 4 recordings.

## Install

1. Load your `Bionic Commando (USA).nes` ROM in Mesen or MesenCE.
2. Choose **Tools > HD Packs (NES) > Install HD Pack** and select
   `Bionic_Commando_HD_v0.7.5.zip`.
3. Confirm installation, enable HD packs in the NES video settings, and reload
   or reset the game when prompted.

For manual installation, place the contents of `pack/` together in
`HdPacks/Bionic Commando (USA)/`. If your ROM has another filename, the pack
directory must match its base name exactly.

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

See `validation/replay.json`, `validation/replay-feedback-v042.json` and `validation/replay-feedback-v050.json` for replay coverage and RAM parity results, and
`DEVELOPMENT.md` for the reproducible build and capture workflow.

The install ZIP contains only the pack and its install notes. ROMs, emulator
binaries, gameplay recordings and developer files are not included.

Tested core: MesenCE 2.2.1; HD-pack format 109.
Whole-file ROM SHA1: `D3A4BFD995D18C4A386971631759AECA3A7CFF8D`.


## Area 13 review pass

Adds Area 13 scenery, stone interiors, white guards and parachutes, neutral-area contacts, animated dialogue portraits and two item pickups. Based on the v0.5.0 cave/generator branch. Review build; no release is implied.
