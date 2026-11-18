# Area 3 v0.12.2 correction review

Non-grappleable outdoor wall insets now use dark recessed mesh instead of
granite. The exterior entrance has a complete metal frame and opaque dark
interior. The robot's compact burst, expanding blast and final fragments
reuse painted fire/smoke from the approved effects atlas.

## Delivered file

- `Bionic_Commando_HD_v0.12.2.zip`
- SHA256 `15e8f61c50bdc8ac638e662a21188097814f845eaeb94f0afc8c8307e20f4bc9`
- 47,039,460 bytes; 53 runtime files.
- All runtime files match a clean default rebuild byte for byte.

## Exact-ZIP playback

The unchanged MesenCE 2.2.1 core completed all 11,110 input frames of `3.mmo`
in one uninterrupted guarded run. The pack loaded by the emulator matches
the extracted ZIP byte for byte. All 187 RAM and 187 PPU checkpoints match
the original-game reference. No emulator crash occurred.

Every-frame auditing covered 3,175 graphics states
with zero unmapped states. A separate selection check requires all 70
recess patterns, all 16 doorway cells and all five explosion patterns to
select the new atlas. All 17 explosion states passed, spanning native
frames 9852–9867. The 281 previously approved robot body/exhaust states and
three-frame clamped-body pixel check remain valid.

## Visual review

The first full playback exposed square cutoffs in the final smoke phase.
That phase now gives each detached native fragment a complete soft-edged
puff. It needs no neighboring-sprite conditions or additional sprites.

Reviewed sampled screenshots across the full movie: equipment, snow/tree,
outdoor ascent, entrance approach and transition, factory, radio/control
room, boss, generator destruction, debrief and return to the map. Detailed
views covered the wall insets (2401), open entrance (5041), entry (4981),
compact burst (9854), expanded blast (9860) and final smoke (9867). The final
18-frame destruction sequence (9851–9868) was also reviewed as a contact
sheet. The screenshot callback shows the rendered scene one frame after
the corresponding native audit event.

The final run produced 453 valid PNG captures; the startup frame-one callback
produced one empty file before the first rendered image. Forty-four
inspected first-pass captures match the final playback byte for byte.
This is sampled visual review plus every-frame auditing, not a claim that
every frame was individually viewed.

All 194,319 preceding tile rules and 50 preceding PNGs remain unchanged.
The 103 new tile rules require Area 3. All 11,037 Area 3 neighboring-cell
references pass bounds checks. There are no new sprite additions, invalid
tile references or duplicate sprite additions. Earlier-area recordings were
not replayed; unrecorded routes and states are outside this review's scope.

The ZIP contains only the installable pack and notes, with no ROM, emulator,
movie, MP4 or Git bundle.
