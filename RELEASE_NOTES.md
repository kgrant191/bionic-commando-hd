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
