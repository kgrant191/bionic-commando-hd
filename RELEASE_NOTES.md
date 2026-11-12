# Bionic Commando HD v0.4.1 — review build

- Replace all eight communication-room doorway patterns with one aligned steel frame. The original visible-pixel matching had missed parts hidden behind Spencer in the source screenshot.
- Repair blue/cyan contamination in eleven repeated exterior texture patterns: platform rims, barrel tops, ladder edges and small cliff-edge fragments.
- Apply the texture repairs only to the contaminated pixels and their immediate fringe. Existing transparency, water, characters and unrelated tile artwork are unchanged.

Validation compares every tile rule with v0.4.0 and replays the complete supplied
Level 1 movie. See `validation/door-seams-v0.4.1.json` and `validation/replay.json`.
This is a test build, not a GitHub release. No ROM or gameplay changes.

---

# Bionic Commando HD v0.4.0 — review build

- Keep one enemy body scale across the painted sheet instead of stretching each pose to its weapon-dependent bounds.
- Give Spencer an exposed steel shoulder, elbow, forearm and hand for the grappling arm.
- Add two painted rotated swing poses; suppress their original boot and hand components too. Rotated heads no longer receive the metallic-chain fallback.
- Replace the lamp with a painted searchlight and limit water to eight recorded foam patterns.
- Extend painted wall/beam edge coverage, including alternate palettes at sky boundaries.
- Replace the equipment surround and starter handgun/radio icons; retain the game's moving selection cursor and item state.

The pistol remains the starter-weapon design. Different equipped weapons can have
separate artwork through native pattern or verified memory conditions. Player
machine-gun/bazooka variants are planned but not delivered in this checkpoint.
Later areas and unrecorded states remain untested. No ROM or gameplay changes.
See `validation/replay.json` and `validation/feedback-v0.4.0.json` for checks.
This is a test build, not a GitHub release.

---

# Bionic Commando HD v0.3.0 — review build

- Sixteen painted Spencer bodies mapped to 18 selected pose records: standing, running,
  crouching, firing, hanging, swinging and parachute entry.
- Painted enemies for 11 selected poses: rifle troops, crouching soldiers,
  bazooka troops, grenade throwing and the large armored guard.
- Painted reactor tubing, metal housings and amber core.
- Olive-brass machinery and tubular rails in the later underground section.
- Mesen sprite-limit removal to reduce missing strips in crowded combat.
- Reuse painted scenery during captured background-palette flashes instead
  of falling back to the earlier tile treatment.
- Retain the world map, radio expressions, scenery and overscan fix from v0.2.

Native sprite anchors preserve positions, flips and animation timing. Selected
poses use HD-only additional sprites; the ROM and gameplay are unchanged.
Other poses retain v0.2's material treatment. Effects, equipment UI, the Area
Clear figure, remaining architecture and later areas still need art passes.
Validation is recorded in `validation/replay.json`.

This is a test build, not a GitHub release.

---

# Bionic Commando HD v0.2.0 — review build

- Painted tactical terrain behind the live world-map routes, numbers and units.
- Eight portrait expressions for four radio speakers; live dialogue and the
  speakers' talking states remain driven by the original sprites.
- First sprite surface-detail pass: 648 palette-specific material mappings,
  selected painted Spencer/soldier heads and metallic grappling-arm links.
- Added 41 painted tower/environment keys and a textured flat-stucco material.
- Atmospheric exterior sky, with the existing eight-row top/bottom trim.
- Added 23 sprite keys found by denser sampling (every 15 frames).

Character silhouettes and movements remain the original NES animation.
Complete per-frame character redraws, remaining effects, reactor, equipment
screens, Area Clear figure and later areas are still future work.

No ROM or gameplay changes. This is a test build, not a GitHub release.
Validation is recorded in `validation/replay.json`.

---

# Bionic Commando HD v0.1.0

First review build for the opening screens and the supplied complete Area 1
playthrough.

- New title and field-radio interface.
- Painted fortress, underground, communication-room and final-room scenery.
- Consistent replacement of observed water animation phases and sky openings.
- Top and bottom eight-pixel overscan trim to hide the observed edge garbage.
- 4× tile replacements for 3,242 recorded/inspected pattern-and-palette keys.

This is a scenery baseline. Detailed characters, enemies, portraits, reactor,
effects, map, equipment UI and Area Clear artwork are still to come. Some
architecture remains a recolored baseline. Later areas are untested.

No ROM or gameplay patch is included. Validation details are recorded in
`validation/replay.json`.
