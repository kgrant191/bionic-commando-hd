# Bionic Commando HD v0.9.7

This patch starts from the exact v0.9.6 runtime ZIP. It preserves the
earlier Area 15, metallic ball, doorway and crimson/white boss corrections.

Changes:

- Painted copper rooftop railing and eagle emblem, aligned to native roof landmarks.
- Complete HD mappings for the recorded pink/white damage colors, including
  Spencer's swinging body, grapple and hand, and the airborne enemy.
- Generator hit illumination preserves black padding and recesses. The
  original `$0F` → `$16` palette signal still controls flash timing.
- Boss artwork and animation rules were unchanged in v0.9.7. The earlier
  interpretation of the rear mechanism as a claw was incorrect; v0.9.8
  corrects it to a fixed exhaust nozzle with an animated flame.

## Rebuild

Requires Python 3, Pillow and NumPy. Obtain `Bionic_Commando_HD_v0.9.6.zip`
from the previous test build, then run:

```sh
python3 scripts/apply_v097.py /path/to/Bionic_Commando_HD_v0.9.6.zip capture/v097 pack
```

The patch checks the baseline SHA256 before writing. The compact native-tile
captures cover all 90 damage tile/color combinations observed in the supplied
recording. No ROM or movie is included. The runtime ZIP contains only required
pack files; this development checkpoint preserves the patch inputs separately.

## Verification

The complete 1,940-frame `Bionic Commando (USA)(8).mmo` was replayed before and
after the patch, with original-ROM RAM and PPU parity checked every frame.
Compared 646 full-recording screenshots and separately captured every frame
of the opening 390-frame rooftop/swing sequence. Scope checks and results are
in `validation/v097-regression.json` and `validation/v097-dense.json`.

No altered gameplay state, new duplicate sprite additions, or image changes
outside the roof, damage sprites and generator flash regions were found in
the full recording. Unrecorded states remain untested.
