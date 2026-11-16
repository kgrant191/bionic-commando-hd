# Intro and Areas 5 / 15 — v0.8.0 review

This build adds painted story scenes and live lettering, Super Joe's complete
three-palette illustration, Area 5 factory/shaft/reactor scenery and blue
acrobat poses, Area 15 town/room/chest artwork, and overhead battle scenery
and infantry. Existing approved v0.7.6 content remains included.

## Verification

MesenCE 2.2.1 core, HD pack format 109, USA ROM SHA1
`D3A4BFD995D18C4A386971631759AECA3A7CFF8D`.

| Recording | Input frames | RAM and PPU checkpoints |
| --- | ---: | ---: |
| intro.mmo | 4,752 | 41 |
| 5.mmo | 22,377 | 188 |
| 15.mmo | 7,236 | 62 |
| Original Area 1 | 40,442 | 339 |
| Area 1 door / hit follow-up | 1,081 | 11 |
| Cave / generator follow-up | 6,842 | 59 |
| Total | 82,730 | 700 |

Checkpoints cover frame 1, each 120th frame, and each recording's final frame.
Every RAM and PPU checkpoint matches its original-graphics replay. Reports are
`v080-intro.json`, `v080-area5.json`, `v080-area15.json`, `v080-area1.json`,
`v080-door.json`, and `v080-cave.json`. Each report records the tested pack's
hashes; final Area 5/15 refinements were replayed in those affected areas.
`v080-final-scope.json` verifies that those last refinements preserve all other
existing rule order, conditions, tile pixels and background images from the
full Area 1 regression build.

The validator checks atlas bounds, required images, HD loader errors, unique
sprite additions, virtual fallback definitions, replay completion, screenshot
dimensions, and byte-identical RAM/PPU checkpoints. The install ZIP contains
only referenced runtime images, hires.txt and installation notes.

## Visual review

Selected matching frames were inspected from all six replays. Main new-scene
checkpoints include intro 480/1200/1560/2280/3000/3360/4200/4752;
Area 5 1560/2280/3960/5880/6840/8760/11640/17400/19440/21360;
and Area 15 840/1080/1560/3000/3960/4920/5880. The preview uses actual
emulator captures, not generated scene mockups.

The compact blue pose and two main larger poses use the same uniform/helmet
identity. Clipped body parts keep painted fallbacks. Overhead character rules
are separate from side-view virtual sprites, preventing overlapping figures.
Story wording, dialogue timing, native movement, damage and collision remain
controlled by the game; no ROM patch is applied.

## Limits

Sampled visual review, not inspection of every rendered frame. Unrecorded
poses, later areas and equipment-dependent player weapon art remain outside
this pass. Some incidental effects continue to use the established smoothed
baseline. This is a review build, not a full-game release.
