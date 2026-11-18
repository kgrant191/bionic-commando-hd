# Area 3 v0.12.0 review

Reviewed the complete supplied `3.mmo` (11,110 input frames), from equipment
selection through the outdoor approach, pipe works, radio room, generator,
clear screen and return to the map. This revision is scoped to Area 3;
earlier-area recordings were not replayed.

## Final delivered build

- ZIP: `Bionic_Commando_HD_v0.12.0.zip`
- SHA256: `79bf76feb9c41bbef54791281216b04c93da7d50659169cc4751d24b5037fc54`
- 46,907,729 bytes; 51 runtime files.
- The exact extracted ZIP was loaded for the final uninterrupted replay.
- A separate clean default build produced all 51 files byte for byte.

## Playback and mapping results

The unchanged MesenCE 2.2.1 core completed the movie in one attempt using
the guarded-screen harness. The harness protects renderer screen buffers;
it does not modify the ROM or gameplay RAM. Every-frame tile selection was
audited. All 3,047 observed graphics states had replacement mappings, with
zero uncovered states. Original-game RAM and PPU state matched at all 187
checkpoints. See `v0120-verification.json` and `v0120-input.json`.

All 185,431 previous tile rules and all 47 previous PNGs remain unchanged.
All 2,692 added rules require Area 3. Structural checks found no invalid
tiles, duplicate sprite additions, missing virtual fallbacks or unbounded
new neighbor references. Preserved Area 2 neighbor bounds also passed the
static check; this is not an earlier-area playback regression.

## Visual review

Mapping coverage alone does not prove that replacement artwork looks
finished. Contact sheets and full-resolution captures were inspected across
the full recording, with denser frame sequences for creature, guard and
fade transitions. The final replay produced 646 review screenshots; this
was sampled visual inspection plus every-frame automated auditing, not a
claim of individually inspecting every rendered frame.

Replaced the remaining original-looking outdoor cliff, snow and tree
materials; crawler legs, flying insect phases, plant mouths and seeds;
factory pipes, girders, mesh panels, platforms and spikes; radio-room knife
guards; communicator icon; and the Area 03 clear-screen characters.

Reviewed distinct guard strides, stable body sizes and native animation
timing. Green and red radio portraits retain their respective uniform
colors. No white dialogue character is present in this recording. Reviewed
the ordinary radio doorway separately from the eagle-marked generator door.

The final visual pass checked the repaired control-room elbow behind the
guards and continuous narrow factory-pipe joins. Key final captures include
the control room, frame 9361 (eagle doorway and pipes), 10081 (generator),
10369 (fade), 10561 (AREA 03 CLEAR), 10801 (bonus and recovered device) and
11041 (map return). Dense sequences covered plant-mouth/seed states,
crawler movement and the knife-guard walking poses.

The result covers states exercised by the supplied recording. Unrecorded
routes, equipment combinations and later areas remain outside this review.
The deliverable contains only the installable HD pack and its notes, with
no ROM, movie, video, emulator or Git bundle.
