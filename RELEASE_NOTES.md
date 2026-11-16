# Bionic Commando HD v0.8.2 — Super Joe rear foot

The intro illustration extended into three cells absent from the original sprite layout, clipping the rear leg and boot. Attach those missing pieces to Super Joe's native head, including the recorded palette transitions. Preserve the existing art, size and position. No other artwork changes.

# Bionic Commando HD v0.8.1 — review corrections

Correct the initial boot/power-cycle title, intermittent story fragments, Area 1 cave frames, and the reported Area 5/15 artwork problems. Area 5 now has solid earth, mechanical ceiling objects, helicopter infantry, visible springs, consistent knife guards and a painted robot boss. The overhead encounter has revised scenery, proper overhead figures, new cover and bunker artwork. Both Area 15 interiors, dialogue fragments, the 1UP, barrier and colored radios are covered.

This is a review build, not a public release. Includes the v0.8.0 work and all approved v0.7.6 changes. No ROM or movie is bundled, and no gameplay state is changed.

# v0.8.0 — Intro story, Area 5 and Area 15

- Replace the story dossier, headquarters and sunset scenes with painted artwork, plus a complete Super Joe illustration and refreshed live text.
- Paint Area 5 factory walls, concrete huts, beams, chains, lava, shaft fixtures and reactor room.
- Add the blue acrobat's two main recorded poses and painted clipped-body fallbacks.
- Extend the town scenery, dialogue framing and NPC artwork to Area 15; paint its stone supply room.
- Paint the overhead interception's road, water, rock banks and soldiers; keep its character rules separate from side-view gameplay.
- Include the approved v0.7.6 fixes.

Review build. Original gameplay and story wording remain live. See `validation/INTRO_AREAS5_15_v0.8.0.md` for recording coverage and limits.

# v0.7.6 — Area 1 doors, crate rewards and grenade animation

- Replace contaminated exterior doorframe crops with a complete clean red steel frame.
- Review the other Area 1 entrances, including the communication room and boss entrance.
- Replace POW lettering and the green recovery flask with illustrated crate-reward sprites.
- Replace the orbiting POW star across recorded normal and flash palettes, retaining native timing.
- Cover the bazooka soldier's grenade wind-up and release poses with matching HD artwork.
- Add a compact grenade sprite and painted lower-body fallbacks for clipped red soldiers.
- Include all approved v0.7.5 corrections.

Review build; no ROM or gameplay changes. See `validation/AREA1_FIXES_v0.7.6.md`.

# v0.7.5 — Knife guard and active flare corrections

- Give the fast charging burgundy guard a heavier build and a knife, matching his original role.
- Keep one body scale across his three movement poses in Areas 4 and 13.
- Render the active flare as a lit red canister, separate from ordinary silver gunshots.
- Track the flare by its native object type and position through camera movement and simultaneous gunfire.
- Preserve the unlit flare pickup/equipment icon, XP bullet collectible and existing projectile palette fixes.
- Include the approved v0.7.3 town improvements and v0.7.4 gunshot corrections.

Review build; no ROM or game-state changes. See `validation/KNIFE_FLARE_v0.7.5.md` for regression coverage and limits.

# v0.7.4 — Projectile artwork and damage-palette fixes

- Replace the enlarged original enemy shot in Area 13 with dedicated HD artwork.
- Keep Spencer's projectile appearance consistent while his damage palette flashes in Area 4.
- Cover all six recorded gunshot palette variants, including red and white enemies.
- Preserve native projectile footprint, position, flight direction, speed and damage logic.
- Include all approved v0.7.3 town portrait, scenery, frame and doorway improvements.

Review build. See `validation/PROJECTILES_v0.7.4.md` for replay evidence and limits.

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
