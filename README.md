# Bionic Commando HD

**v0.3.0 — painted characters, enemies and reactor**

Repository: https://github.com/kgrant191/bionic-commando-hd

A 4× Mesen/MesenCE graphics pack for the USA NES version of Bionic Commando.
This is a work-in-progress graphics remake covering the supplied opening and Area 1 recording.

## Install

1. Load your `Bionic Commando (USA).nes` ROM in Mesen or MesenCE.
2. Choose **Tools > HD Packs (NES) > Install HD Pack** and select
   `Bionic_Commando_HD_v0.3.0.zip`.
3. Confirm installation, enable HD packs in the NES video settings, and reload
   or reset the game when prompted.

For manual installation, place the contents of `pack/` together in
`HdPacks/Bionic Commando (USA)/`. If your ROM has another filename, the pack
directory must match its base name exactly.

## Included in this pass

- New title artwork and readable start prompt.
- Painted radio portraits for the operator, commander, and two intercepted
  enemy speakers. All four speakers retain their talking expressions; the final-room
  officer portrait is covered too.
- Painted world-map terrain with live routes, area numbers, selection and units.
- Sixteen Spencer paintings mapped to eighteen selected pose records covering standing, running, crouching,
  firing, hanging, swinging and the parachute entry, with full painted bodies.
- Eleven selected enemy poses covering rifle troops, crouching soldiers,
  bazooka troops, a grenade thrower and the large armored guard.
- Palette-specific material fallbacks and metal grapple links for other states.
- Painted fortress masonry, girders, barrels, cliffs, water, tower stucco
  and coping; an atmospheric sky replaces the flat exterior blue.
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
Unrecognized poses keep the previous material treatment; transitions and
unrecorded moves still need review. Some effects, equipment screens and the
Area Clear figure retain a smoothed baseline. Remaining architectural variants
and map vehicle shapes need further art passes.
The new title appears as a static composition; the original sliding logo and
small title character animation are not reproduced.

Only the supplied opening/Area 1 recording has been tested. Later areas,
unrecorded moves and alternate equipment or palette states need recordings
and validation. Shared tile patterns may affect later areas.

## Validation and source

See `validation/replay.json` for replay coverage and RAM parity results, and
`DEVELOPMENT.md` for the reproducible build and capture workflow.

The install ZIP contains only the pack and its install notes. ROMs, emulator
binaries, gameplay recordings and developer files are not included.

Tested core: MesenCE 2.2.1; HD-pack format 109.
Whole-file ROM SHA1: `D3A4BFD995D18C4A386971631759AECA3A7CFF8D`.

