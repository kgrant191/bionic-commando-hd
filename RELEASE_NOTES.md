# v0.7.3 — Area 13 conversations and scenery

- Red and green town NPCs use side-facing portraits matching their standing outfits and the white-cap portrait style.
- Remove the duplicate older white NPC portrait caused by a mirrored native head tile.
- Replace chunky dialogue/portrait borders with a consistent metal frame.
- Add painted sky, clouds, snow mountains and distant trees, retaining native alarm colors.
- Repair the supply-room doorway header and side posts; align the spike bases while preserving alternating native heights.
- Paint the small barred town façades that still used enlarged native graphics.

Review build; no ROM or game-state changes. Existing communication-room portraits are preserved. See `validation/AREA13_v0.7.3.md`.

# v0.7.2 — Animation, portraits, HUD and water-edge fixes

- Stabilizes body proportions and head alignment across Area 4 shield-boss and red-rifle animations, plus the Area 13 red runner.
- Gives both white idle NPCs matching white-uniform, patrol-cap portraits with separate idle/talking expressions and distinct faces.
- Makes the XP bullet a bold upright white-and-green cartridge based on its original silhouette; room and enemy drops share it.
- Unifies player and enemy health indicators with a clean metal bezel and colored lens, retaining native counts and color states.
- Reformats the mission heading as AREA + live two-digit area number + CLEAR, including matching digits 0–9.
- Covers stale nametable scenery below the bottom water row on the first Area 1 descent, with a local water-neighbor condition.
- Adds 14 tile/palette pairs exposed by the water-glitch recording, including edge-of-screen scrolling states.

Review build; ROM and game state are unchanged. See validation/FEEDBACK_v0.7.2.md.

# v0.7.1 — Bullet and flare bomb correction

The Area 13 room drop is an XP bullet, matching the collectible dropped by enemies. All observed sprite-palette variants now use the same cartridge artwork. The flare bomb pickup and equipment icon use a compact unlit illumination canister. Energy Recovery remains separate. These corrections supersede the pill and handheld-flare interpretation in v0.7.0.

Reference: https://strategywiki.org/wiki/Bionic_Commando_(NES)/Items

# v0.7.0 — Area 4 review build

Adds the mountain gorge, cave materials, copper pipework, shaft ledges and vents. New sleeveless-guard walking poses and shield-guard mappings cover the recorded combat states. Includes flare and communicator inventory art, boss dialogue expressions and doorway trim and all v0.6.1 regression fixes.

Duplicate invisible sprite layers are combined so Area 13 mappings do not clip overlapping enemies in earlier areas.

No gameplay changes. Coverage and validation limits are recorded in validation/AREA4_v0.7.0.md.

Area 13 corrections: white, green and red NPCs keep their native uniform colors and distinct identities. The red runner has a dedicated three-pose cycle; armed and unarmed green contacts no longer share artwork. The red rifle guard is covered in Area 13 as well as Area 4, matching the shared native character. White idle NPCs have separate designs, and hit flashes retain white guard artwork. The pill is a capsule and the flare is a burning cartridge, including its equipment icon.

# v0.6.1 — Recording regression fixes

Game Over no longer triggers title artwork, and the sky is hidden during display-off transitions. Adds Spencer’s final death pose, player/enemy/supply parachutes, the Area 13 green contact’s walking cycle, and a missing electrical-effect palette variant.

Review build; no gameplay changes. Includes the unpushed v0.6.0 Area 13 work.

# Bionic Commando HD v0.6.0 — Area 13 review build

- Painted outpost buildings, medical signs, bronze shutters and rocky banks.
- Painted stone interiors, door surrounds and spikes.
- Eight white-guard pose mappings and a detailed parachute canopy.
- Neutral-area contact artwork and four dialogue portraits, with live mouth-state switching.
- Green supply and first-aid pickup artwork.
- Added recorded palette variants, including the alarm sequence.
- Carries forward the accepted v0.5.0 cave, generator and Area Clear improvements.

Validation: the complete 7,434-frame Area 13 recording is replayed in MesenCE 2.2.1. See validation/area13-replay.json for checkpoint parity and asset checks. The ROM is unchanged and is not distributed.

This is a review build, not a public release. Coverage is limited to the recorded actions; later areas still need recordings.
