# Bionic Commando HD v0.9.8

The Area 5 hover boss's rear assembly was incorrectly interpreted as a claw.
The original sprite uses a fixed exhaust nozzle and two flame states. This
patch replaces the moving claw and the separate, visibly cut-off fire with
one static crimson/ivory nozzle and a complete animated orange plume.

The two flame states follow the original tile changes. Both use the same
hardware layer. The patch retains the boss's crimson and white appearance
and existing damage illumination, with no gameplay or timing changes.
It also hides native exhaust fragments that the game clamps to the opposite
edge of the screen when the boss moves beyond the right edge.

## Rebuild

Requires Python 3, Pillow and NumPy. The runtime is rebuilt from the exact
v0.9.7 ZIP and the two compact native tile captures in `capture/v098`:

```sh
python3 scripts/apply_v098.py /path/to/Bionic_Commando_HD_v0.9.7.zip capture/v098 pack
```

Baseline SHA256:
`4c476b6758d2905391b0f465fbb43bb84f2ed8525b29683bba05bf9244e5ee8e`

Baseline file: `libfile_64f17ee1d3408191b0558a0e35fdac67`

The patch preserves all prior runtime images and rules. It adds one small
atlas and scoped replacements. Existing virtual sprite anchors are reused
to avoid duplicate sprites. Only the eleven known native exhaust patterns
may be replaced; nearby projectiles cannot become exhaust components.

`art/area5-exhaust-v098.png` contains the generated source layers. The build
uses the same hardware crop for both states, with separately cropped flame
layers. Atlas extraction, alignment and palette handling are reproducible.

## Validation

The complete 1,940-frame supplied movie is replayed against the original
ROM. `verify_v098.py` checks RAM/PPU parity, preservation of prior assets and
rules, valid atlas references, unique sprite additions, and screenshot-change
scope. Images are sampled every three frames throughout the recording.
Changes are confined to the rear exhaust and removal of its stray edge
fragments. Unrecorded states remain untested.

The animation preview uses 116 consecutive emulator frames at 60 fps,
aligned on the boss head and repeated three times. Both native flame phases
appear. The 185 fully opaque shared hardware pixels are checked in every
frame against the expected hardware colors, including the damage palettes.

The checkpoint is an incremental, reproducible patch, not a complete Git
repository or a Git bundle. It contains no ROM or movie. The installable ZIP
contains runtime files only. Use the recorded baseline above to rebuild.
