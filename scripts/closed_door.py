"""Render the closed exterior door on the wall, behind painted actors.

The NES door is a sprite. Drawing it there puts it above the HD additions used
for Spencer, regardless of his original OAM order. Local sprite conditions
move the same live door state into background tiles without changing game RAM.
"""
from collections import defaultdict
from PIL import Image
import json

def make_closed_door(root):
    rows = [line.split(',') for line in
            (root/'capture/feedback-v042/00440.tiles').read_text().splitlines()]
    background = {(int(a[1]), int(a[2])): (a[3], int(a[4]))
                  for a in rows if a[0] == '0'}
    sprites = {(int(a[1]), int(a[2])): (a[3], int(a[4]))
               for a in rows if a[0] == '1' and int(a[4]) == 0xFF30150F}
    panel = Image.open(root/'art/closed-door-v4.2.png').convert('RGBA')
    panel = panel.resize((128, 96), Image.Resampling.LANCZOS)
    conditions, variants = [], defaultdict(list)
    mapping = []
    for row in range(4):
        y = 126 + row*8
        # Nearest visible sprite row also works when the door scrolls through
        # the screen edge; no off-screen central emblem trigger is required.
        sy = 133 if row == 0 else y-1
        left_key, palette = sprites[138, sy]
        for col in range(4):
            x = 138 + col*8
            sprite_key, _ = sprites[x, sy]
            key = background[x, y]
            name = f'closedDoor{row}_{col}'
            conditions.append(f'<condition>{name},spriteNearby,0,{sy-y},{sprite_key},{palette:08X},N')
            guard = name
            if col:
                side = name+'Left'
                conditions.append(f'<condition>{side},spriteNearby,{-col*8},{sy-y},{left_key},{palette:08X},N')
                guard += '&'+side
            # The door begins seven pixels into the background header row.
            overlay = panel.crop((col*32, (y-133)*4, col*32+32, (y-125)*4))
            variants[key].append((guard, overlay))
            mapping.append({'background_key': key[0], 'palette': f'{key[1]:08X}',
                            'cell': [col,row], 'guard': guard})
    hidden = set(sprites.values())
    (root/'validation/closed-door-mapping.json').write_text(json.dumps({
        'native_sprite_keys': [[k,f'{p:08X}'] for k,p in sorted(hidden)],
        'background_cells': mapping, 'render_layer': 'background',
        'native_panel_bounds': [138,133,170,157],
        'state_source': 'live door sprites; no memory writes'}, indent=2)+'\n')
    return conditions, variants, hidden
