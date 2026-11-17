# v0.10.0 development handoff

Current branch: feature/weapons-area16-v0.10.0.
Base commit: d4efb47954ebe73e297767ee906996061deea010 (v0.9.8).
User reviews the install ZIP, then imports/pushes the source bundle with their
push-bundle.sh script. Continue on feature branches; main is not approved for merge.

`python3 scripts/build.py` is the canonical builder. It validates and copies
baselines/v098 and applies scripts/build_v0100.py. All old runtime assets remain
byte-identical. The new atlas is weapons-area16-v0100.png. Preserve the historical
builders for reference; the old v096→v097 chain did not reproduce the v097 hash in
this environment, so the verified v098 runtime is retained directly.

New generated sources are art/*v0100.png. The original transparent PNGs are kept;
the builder removes faint alpha noise before packing. Selected native CHR/palette
metadata and complete observed pair inventory are in capture/v0100. No ROM or
movie is committed. See validation/WEAPONS_AREA16_v0.10.0.md for evidence.

Equipment is $04CA (0 starter, 1 rocket launcher, 2 wide cannon); $0048 is not the
equipment selector. Area16 is $004D == $10. Overhead encounters use both $004C
values $13 and $14. Both positive and negative encounter guards must account for
both IDs to avoid side-view actor rules leaking into overhead scenes.

The large side-view rocket uses four mirrored quarters of CHR pattern
0000020E16183800000121110907077F. Its red/amber palettes must stay separate from
the green/blue POW orbit palettes that reuse that pattern. Keep the circular
footprint, native motion and hit timing. Wide-cannon projectile behavior is native.
