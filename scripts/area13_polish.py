"""Town scenery and modular fixtures, retaining the live native tile layout."""
import numpy as np
from PIL import Image, ImageDraw

FRAME_KEYS = {
    'FCFDE5C6C5FC1068FC858E8FBDFC3058': (0, 0),
    '00FFFF00FF00000000FF00FFFF000000': (1, 0),
    '3FBFB931B13F041A3FA123A3AF3F0C16': (2, 0),
    '68686868686868685858585858585858': (0, 1),
    '1A1A1A1A1A1A1A1A1616161616161616': (2, 1),
    '6868FCFDE5C6C5FC5858FC858E8FBDFC': (0, 2),
    '000000FFFF00FF00000000FF00FFFF00': (1, 2),
    '1A1A3FBFB971B13F16163FA163E3AF3F': (2, 2),
}


def town_polish(root, keys, entries, indices, rule, guard, conditions):
    # A nine-slice code-native UI frame. Its segments follow the game's box
    # tiles, including boxes at non-grid screen offsets and changing heights.
    frame = Image.new('RGBA', (384, 384))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((24, 24, 359, 359), radius=30, fill=(8, 13, 17, 255))
    d.rounded_rectangle((32, 32, 351, 351), radius=24, fill=(133, 150, 154), width=4)
    d.rounded_rectangle((40, 40, 343, 343), radius=19, fill=(45, 61, 68))
    d.rounded_rectangle((52, 52, 331, 331), radius=12, fill=(20, 29, 35), outline=(71, 125, 134), width=4)
    d.rounded_rectangle((64, 64, 319, 319), radius=8, fill=(0, 0, 0), outline=(7, 12, 16), width=4)
    frame = frame.resize((96, 96), Image.Resampling.LANCZOS)
    sky_palette = {0x0F201C0C, 0x0F200F0C, 0x0F20160C, 0x0F20230C}
    for k, p in keys:
        if k in FRAME_KEYS and p in sky_palette:
            x, y = FRAME_KEYS[k]
            rule(k, p, frame.crop((x*32, y*32, x*32+32, y*32+32)), guard)

    # Only scenery patterns observed outside dialogue are made transparent.
    # The shared black tile, all live text and the frame retain their opacity.
    scene = entries(root, 2040)
    water = {e[3] for e in scene if e[0] == 0 and e[2] >= 208 and e[4] == 0x0F201C0C}
    sky = {e[3] for e in scene if e[0] == 0 and e[4] == 0x0F201C0C} - water
    sky.discard('0' * 32)
    forest = {e[3] for e in scene if e[0] == 0 and e[4] == 0x0F271707 and e[1] < 79 and 168 <= e[2] < 208}
    for k, p in keys:
        if (k in sky and p in sky_palette) or (k in forest and p == 0x0F271707):
            rule(k, p, Image.new('RGBA', (32, 32)), guard)
    distance = Image.open(root/'art/area13-distance-v073.png').convert('RGBA').resize(
        (1024, 960), Image.Resampling.LANCZOS)
    distance.save(root/'pack/area13-distance.png')
    # Follow the real palette-driven alarm. These are renderer palette grades
    # of the same scenery, never a clock or a guessed gameplay state.
    a = np.array(distance).astype(float)
    for name, color in [('alert', (190, 45, 28)), ('flash', (105, 90, 220))]:
        graded = a.copy()
        graded[:, :, :3] = a[:, :, :3]*.60 + np.array(color)*.40
        Image.fromarray(np.uint8(np.clip(graded, 0, 255))).save(root/f'pack/area13-distance-{name}.png')
    for color in ['0F', '16', '23']:
        conditions.append(f'<condition>a13Sky{color},ppuMemoryCheckConstant,3F0E,==,{color}')

    # Use the full native doorway metadata, including the header hidden by
    # Spencer in some captures. No screenshot-dependent partial frame crops.
    sheet = Image.open(root/'art/area13-fixtures-v073.png').convert('RGBA')
    cw = sheet.width//2
    door = sheet.crop((0, 0, cw, sheet.height)).resize((128, 128), Image.Resampling.LANCZOS)
    spikes = sheet.crop((cw, 0, sheet.width, sheet.height)).resize((64, 64), Image.Resampling.LANCZOS)
    replacements = {}
    for ly, x, y, k, p, h, v in entries(root, 2520):
        if ly or p != 0x0F201000 or k == '0'*32:
            continue
        if 32 <= x < 64 and 160 <= y < 192:
            # The lower jamb tile repeats vertically, so use one continuous
            # section; the upper jamb carries the joining cap.
            dx, dy = (x-32)*4, (y-160)*4
            replacements.setdefault((k, p), door.crop((dx, dy, dx+32, dy+32)))
        elif 160 <= x < 176 and 192 <= y < 208:
            dx, dy = (x-160)*4, (y-192)*4
            replacements[k, p] = spikes.crop((dx, dy, dx+32, dy+32))
    for (k, p), im in replacements.items():
        rule(k, p, im, guard)
    # The small barred façades use a separate pattern family from the large
    # town buildings and were absent from the original painting's reference.
    facade = Image.open(root/'art/area13-barred-facade-v073.png').convert('RGBA')
    facade = facade.crop((0, 0, facade.width//2, facade.height)).resize((128, 128), Image.Resampling.LANCZOS)
    for ly, x, y, k, p, h, v in entries(root, 1320):
        if ly == 0 and p == 0x0F201000 and 47 <= x < 79 and 160 <= y < 192:
            dx, dy = (x-47)*4, (y-160)*4
            # The upper rows share CHR with large buildings. Require the
            # small façade's own barred opening at the expected offset.
            name = f'a13BarredFacade{x}_{y}'
            conditions.append(f'<condition>{name},tileNearby,{55-x},{176-y},0000097740404040FFFFFFF7C0C0C0C0,0F201000,N')
            rule(k, p, facade.crop((dx, dy, dx+32, dy+32)), guard+'&'+name)
    return [
        f'[{guard}&screenEnabled&!a13Sky0F&!a13Sky16&!a13Sky23]<background>area13-distance.png,1,0,0,1',
        f'[{guard}&screenEnabled&a13Sky0F]<background>area13-distance.png,0.30,0,0,1',
        f'[{guard}&screenEnabled&a13Sky16]<background>area13-distance-alert.png,1,0,0,1',
        f'[{guard}&screenEnabled&a13Sky23]<background>area13-distance-flash.png,1,0,0,1',
    ]
