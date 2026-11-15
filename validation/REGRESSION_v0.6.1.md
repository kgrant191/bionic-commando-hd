# Bionic Commando HD v0.6.1 regression

## Coverage

Five uploaded movie files represent four unique recordings. The unnumbered movie and `(1)` have identical SHA-256 hashes and inputs.

| Recording | Input frames | RAM/PPU checkpoints | Scope |
|---|---:|---:|---|
| Unnumbered / (1) | 40,442 | 339 | Opening, repeated Area 1 attempts, Game Over, radio rooms, cave, generator, Area Clear, map |
| (2) | 1,081 | 11 | Closed exterior door, Spencer layering, enemy combat |
| (3) | 6,842 | 59 | Cave, elevator, soldiers, armored guard, generator shutdown and results |
| (4) | 7,434 | 63 | Area 13, contacts, interiors, pickups, portraits, alarm and map |
| Total unique | 55,799 | 472 | About 15.5 minutes at 60 input frames/second |

All unique movies were replayed completely. The native PPU tile stream was audited on every emulated frame for matching tile/palette replacement rules. Rendered screenshots were inspected at 120-frame intervals across the recordings, with larger views of suspicious states. This is not visual inspection of every individual rendered frame.

## Findings fixed

1. **Wrong Game Over screen:** the title trigger matched the blank background palette shared by Game Over. It now requires an actual title-logo tile. Live Game Over lettering remains visible on black.
2. **Sky on blank transitions:** the unconditional exterior background appeared while the game disabled rendering. The sky now follows RAM `$00FF`, the game's mirror of its PPU mask. ROM stores at `$D7FD` and `$D805` write zero / `$1A` to both `$2001` and `$00FF`; no ROM or RAM writes were added by the pack.
3. **Original-shaped final death pose:** Spencer's horizontal defeated frame was outside the previous head-anchor set. Added a painted pose for that anchor and its body parts, including both directions.
4. **Old parachutes and supply case:** player, soldier and supply-drop patterns were separate. All three canopy patterns and the mirrored supply-case quarters now use painted art. Enemy canopies apply outside Area 13 as well.
5. **Rare missing electrical-effect palette:** `F1D94324FBFCC24A38B9E02387BC8075 / FF36150F` lacked a rule. It appeared in 36 counted tile instances in the opening recording, first at frame 23922. It now uses the existing painted electrical-effect crop.
6. **Area 13 green walking contact:** only the stationary contact head was covered. Added the separate walking head and three observed body configurations. Original fragments no longer overlay Spencer during the recorded overlap.

## Results

- All four unique movies reached their final input frame.
- 472 RAM checkpoint comparisons: zero mismatches.
- 472 PPU-memory checkpoint comparisons: zero mismatches.
- Zero unmatched tile/palette states in the completed revised audits.
- No HD pack loader or Lua script errors in completed verification runs.
- Closed-door foreground layering, portraits, cave fixtures, generator effects and Area Clear were inspected alongside the new fixes.
- The final supply-case and Area 13 walking-contact changes were followed by full additional replays of recordings (3) and (4). Opening/door reports retain the exact earlier installed-pack hashes; the final supply-case change is covered in (3), and the contact change is scoped to Area 13 and covered in (4).

The JSON reports preserve the actual tested pack hashes. TSV audit files contain key, palette, layer, selected rule index, first/last frame and instance count. Rule indices are specific to each tested pack and must not be interpreted against another build.

## Remaining limits / observations

- Thin scroll-edge slivers are also present in the original NES playback (for example, opening recording frame 17880). Existing eight-row top/bottom overscan remains; this revision does not patch native camera/nametable behavior or crop further into the HUD.
- A replacement-rule match proves coverage, not artistic correctness. Fonts, simple HUD symbols and some material fallbacks intentionally preserve the original design in smoothed form.
- Partial actor occlusion can use the established head-matched fallback pose until its full body signature returns.
- Unrecorded areas, equipment states and player weapon variants remain outside this regression. This is a review build, not a claim that every possible game state has been redrawn.

No gameplay, input, collision, level geometry, music or ROM changes.
