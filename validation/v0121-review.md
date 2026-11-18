# Area 3 v0.12.1 correction review

The cross pendant replaces the incorrectly identified red radio in the Area 3
inventory. The isolated distant-mountain tile beside the tree is transparent
to the panorama. The deep sinking snow uses softer pale powder texture. The
boss reuses the approved Area 5 robot, fixed nozzle and both exhaust phases;
its art was not regenerated. Four recessed room details also reuse Area 5 art.

## Delivered file

- `Bionic_Commando_HD_v0.12.1.zip`
- SHA256 `ebe2ddba17eb21e259dfdf1ddc5e7a648b319ad2d3d31e59c7fc49faee5e93ec`
- 46,962,715 bytes; 52 runtime files.
- All files match a clean default rebuild byte for byte.

## Final playback

The exact extracted ZIP completed all 11,110 frames of `3.mmo` in one
uninterrupted guarded playback using the unchanged MesenCE 2.2.1 core.
All 187 RAM and 187 PPU checkpoints match the original-game reference.
Every-frame auditing covered 3,156 graphics states with zero unmapped states.
No emulator crash occurred. The final pack loaded by the emulator matches
the extracted ZIP byte for byte.

Mapping coverage alone previously missed old-looking mapped artwork. The
new boss-specific audit requires the 281 recorded boss graphics states to
select reused artwork or the explicitly guarded clipped-exhaust suppression.
It found zero old generic boss fallbacks. The normal and all three recorded
damage colors were checked: FF30150F, FF36060F, FF202A0F and FF30210F.

## Visual review

Reviewed the pendant in the equipment menu (991), the tree and sinking snow
(1441), the complete robot and nozzle (9440), the second exhaust phase (9755),
the boss at the right edge (9794–9796 and 9811), damage colors (9848–9851),
the generator/clear sequence and the recovered-device screen (10801).
The final run produced 529 screenshots across the movie, with denser boss
animation samples. Eight final screenshots match previously inspected final
artwork captures exactly. Frame 9795 was also inspected directly after the
last clipping correction. A pixel comparison of the left wall also passed
for all three clamped-body frames (9794–9796). This combines sampled visual review with
every-frame auditing; it does not claim each frame was individually viewed.

Reused exhaust conditions are split by mirror orientation before bounds are
applied, preserving valid lookups near the right edge. The final three-frame
clamped-sprite case uses positive boss-head checks across the screen. All
11,029 Area 3 neighboring-cell references pass static bounds verification.

All 188,123 preceding tile rules and 49 preceding PNGs remain unchanged.
New rules require Area 3. There are no new sprite additions, invalid tile
references or duplicate sprite additions. Earlier-area recordings were not
replayed for this task; unrecorded routes and states remain outside its scope.
The ZIP contains only the installable pack and notes, with no ROM, emulator,
movie, MP4 or Git bundle.
