# Super Joe rear-foot correction

The original sprite layout has no cells at (144,113), (144,121) and (144,129). The existing HD illustration extends into those cells, which clipped the rear leg and boot. Three virtual sprite pieces now follow the unique native head through its five recorded palettes. No source artwork, scale, position, scene or gameplay logic was changed.

The complete 4,752-frame intro replay passes all 41 RAM/PPU checkpoints and pack-loader checks. An additional comparison covers 119 actual emulator screenshots, including 70 visible rear-leg samples during the scene and palette transitions. The complete artwork composites correctly in the three repaired cells; every pixel outside that region is identical to the earlier capture.

Ordered rules and decoded atlas pixels are identical for every existing tile/palette pair. The only additions are 15 guarded virtual tile/palette pairs (three cells across five palettes). Every background image and existing condition is unchanged. See `super-joe-v082.json` and `v082-intro-replay.json` for results.

This is a focused correction on top of v0.8.1. It does not claim that the other artwork issues reported for that build have been resolved.
