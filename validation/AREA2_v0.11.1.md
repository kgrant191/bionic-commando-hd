# Area 2 v0.11.1 visual correction review

Scope: the supplied `2.mmo` and nine Area 2 screenshots. No earlier-area
recordings were replayed for this revision. This is a ZIP-only review build.

## Changes reviewed

- Replaced the outpost facade and railing with painted architectural artwork.
- Replaced both grenade blast phases shown by the user; retained native timing.
- Rebuilt cave door headers/jambs, drain outlets, supply crates and ledge mounts.
- Connected the large pipe assemblies, painted grilles and later narrow shaft
  fixture. The narrow fixture has separate rules for shared middle patterns.
- Replaced splash phases and separated neighboring water effects before mapping
  their cells. Corrected background water pairs previously classified as rock.
- Mapped red soldier recoil through its recorded flash palettes, preserving the
  red uniform. Restored Spencer's complete HD assembly for aqua damage palettes.
- Confirmed visible low spike tips and the existing AREA 02 CLEAR lettering.

## Final delivery playback

The exact extracted ZIP was installed in the MesenCE native playback runner.
All 12,044 inputs completed. All 202 RAM and 202 PPU checkpoints matched the
original run; no loader errors occurred. The 3,207 audited graphic states all
had a matching rule. The installed runtime files matched the extracted ZIP.
Rule coverage establishes mapping coverage, not visual quality.

Visual inspection used representative rendered frames plus dense sequences for
explosions (830–850), water (1180–1280), Spencer damage (2638–2690), red recoil
(2826–2920), later combat (5240–5300 and 5358–5392), and narrow shaft scrolling
(7680–7720). The final run captured 905 screenshots; not every captured frame
received individual visual inspection. Key review frames include 733, 843,
1201, 1453, 2644, 2907, 3151, 5257, 5509, 6811, 7693, 9133, 11053 and 11533.
Earlier candidate playbacks exposed door cropping, splash grouping and the
additional narrow pipe layout; those candidates were superseded.

The final structural check found no invalid tile references or duplicate sprite
additions, and every virtual sprite has a fallback. Rebuilding reproduced all
46 non-rule runtime files byte for byte and preserved every per-pattern/palette
rule sequence. Only independent palette-rule ordering differed in hires.txt;
this does not change match precedence. See the machine-readable reports.

This review covers the supplied recording, not every possible gameplay state.

## Delivered archive

- Filename: `Bionic_Commando_HD_v0.11.1.zip`
- Runtime files: 47
- Bytes: 45732921
- SHA256: `a80f8c2dbc20ebb1c573301e5dbe5e1d02bd3e2bd79b16b79ccea46c7ac3c9d9`
- Full playback output: `replay-area2/polish-release-final`
- Reports: `v0111-verification.json`, `v0111-package.json`,
  `v0111-reproducibility.json`, `v0111-build.json`.

The archive contains only runtime PNG/TXT files. No ROM, recording, emulator,
source atlas, MP4 or Git bundle is included.
