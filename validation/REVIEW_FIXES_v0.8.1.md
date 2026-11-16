# v0.8.1 review verification

This revision addresses the seven reported groups of problems in the supplied intro, Area 5 and Area 15 recordings, plus the Area 1 cave-door feedback. It includes the unpushed v0.8.0 work and approved v0.7.6 baseline.

## Renderer changes

- The initial title uses the native boot/title state, not a single logo tile or its normal palette. The story top layer and sprite suppression cover transition palettes; the original dialogue remains live.
- Area 5 ground and its top edge are solid brown earth. Barrel cells fill their native footprint. The distant red wall is continuous behind the beams and lamps. Open doorframes have joined headers/jambs, and bounce fixtures show silver coils.
- Compact blue objects are mechanical, the blue airborne soldiers have their rotors and native flying/hovering poses, knife guards reuse the approved design, and the floating robot has dedicated artwork plus painted impact phases.
- The overhead encounter uses a quieter dirt/rock/water painting, overhead figures selected by their native pose, painted cover and a bunker entrance. Direct OAM component replacement avoids duplicated actors from mirrored anchor tiles. Native Spencer hair overlays no longer obscure the new head.
- Tall and low overhead cover variants are covered, and shared plain-road cells use an edge-continuous dirt material.
- Both Area 15 room states use the new masonry, doorway, barrier, spikes and pickups. The 1UP has red hair. Extra portrait mouth/helmet pieces are suppressed under the established talking portraits. The second weapon icon has complete art.
- Area 15's exterior shield insignia use fitted metal plaques; the distinct medical signs in Area 13 are unchanged.
- Radio colors share a complete icon while retaining colored cases. The recorded yellow pickup and pink menu radio were visually checked; additional palette combinations are declared for the same CHR family but were not individually played through.
- Area 1 radio/goal cave frames are rebuilt from complete native components; the distinct wing-emblem goal header is included. Shutters retain their native two-column footprint.

## Replay checks

MesenCE 2.2.1 core; 4× HD pack. No ROM/RAM/PPU writes or game logic modifications.

| Recording | Input frames | RAM + PPU checkpoints |
|---|---:|---:|
| Intro | 4,752 | 41 |
| Area 5 | 22,377 | 188 |
| Area 15 / truck encounter | 7,236 | 62 |
| Original Area 1 | 40,442 | 339 |
| Area 1 door/hit feedback | 1,081 | 11 |
| Area 1 cave/boss feedback | 6,842 | 59 |
| Total | 82,730 | 700 |

All checkpoints match the original recordings byte for byte. Runtime image references, tile coordinates, virtual additions and HD loader logs are checked by `scripts/validate.py`.

Fresh boot and the emulator's actual `PowerCycle()` path were each run for 600 frames. All 93 visible title samples per run, sampled every six frames, exactly match the HD title image. The intro was additionally captured every six frames. Its narration/dossier/headquarters upper scenery regions match their HD layers in 350 samples, with one expected black transition sample and no unexpected scenery pixels. Super Joe and live dialogue were visually reviewed in sampled frames.

The final small refinements were replayed through the cave, Area 15 and Area 5 recordings. `final-render-delta-v081.json` compares ordered rule guards and decoded tile pixels against the full regression build: only the documented cave goal frame, weapon icon, boss impact family, final overhead ground/cover and Area 15 insignia changed. Other tile renderings and every background image are identical.

## Visual scope and limitations

The review sheet contains actual emulator screenshots, not concept mockups. Additional samples cover the floor edge, barrel stacks, fly/hover poses, mechanical ceiling pieces, knife room, springs, boss damage states, both town interiors, equipment, portraits, cave doorways, title and story transitions. This is sampled visual inspection, not a claim that every rendered pixel of every gameplay frame was manually reviewed. Unrecorded areas, items with different CHR patterns and unseen actor poses still require their own recordings.

## Delivery

The install ZIP contains only files referenced by the pack plus its install README. ROMs, movies, source assets and validation captures are excluded. The source bundle includes this revision and v0.8.0 above approved commit `fe892d29dde3e472bda3c95823989ded3bffecd5`; it is intended for the existing local repository. This is a review build, not a published release.
