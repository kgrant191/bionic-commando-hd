# Boss entrance eagle standard

Every generator/final-boss entrance should display an eagle to distinguish it
from radio rooms and ordinary doors. Preserve this marker as later areas are
added; capture any new pattern or palette variants rather than assigning the
generic grille to their boss entrance.

`boss-door-eagle-v0115.png` was generated with the built-in image tool: one
neutral fictional spread-wing eagle, with visible head, beak, feathered wings,
chest and short tail, embossed in worn gold/brass on a dark steel plaque.
The source prompt requested a front-facing painted industrial-game sprite,
readable at 64×32, with no text, radio antenna, flags, wreath or extra symbols.
The source has transparency outside its plaque. The builder crops its alpha
bounds and scales it into the existing 16×8-native-pixel eagle footprint.

The two detailed eagle CHR patterns are:
- `FBF478FDFBC2F2F50AFD85FEE6C3F3CD` (left)
- `DF2F5EBEDC414DBC10BFE17E64C1CDA0` (right)

The current pack contains these in palettes `0F21110B`, `0F261000`,
`0F271505`, `0F271606` and `0F2B1C0B`. New rules are placed before generic
painted-header rules and apply in gameplay across areas. The radio-arrow
patterns, shared one-pixel tiles beneath the emblem, side jambs and open
passage are not changed. No new nearby conditions are needed.
