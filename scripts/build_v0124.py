"""A coherent snow-covered Area 3 cliff with shaded snow recesses."""
from pathlib import Path
import argparse, ctypes, json, shutil
import numpy as np
from PIL import Image
from build_v0123 import build as previous_build
from build_v0120 import OUT, indices
from build_v0111 import cell, fit

ROOT = Path(__file__).resolve().parents[1]


def build(dest, reuse=False):
    dest.mkdir(parents=True, exist_ok=True)
    if reuse:
        for p in dest.iterdir(): p.unlink()
        for p in (ROOT.parent/'output/v0123-extracted').iterdir(): shutil.copy2(p, dest/p.name)
    else:
        previous_build(dest)
    lines = (dest/'hires.txt').read_text().splitlines()
    names = [s[5:] for s in lines if s.startswith('<img>')]
    images = [Image.open(dest/n).convert('RGBA') for n in names]
    image_id = len(names); atlas = Image.new('RGBA', (1024, 1024))
    cells, rules, pairs, conditions = {}, [], set(), []
    oldrules = [s for s in lines if '<tile>' in s]
    old = {}
    for s in oldrules:
        a = s.split('<tile>')[1].split(',')
        old.setdefault((a[1], int(a[2], 16)), a)
    def oldcell(key, pal):
        a = old[key, pal]; x, y = map(int, a[3:5])
        return images[int(a[0])].crop((x, y, x+32, y+32))
    def emit(key, pal, im, guard=OUT):
        assert im.size == (32, 32)
        data = im.tobytes()
        if data not in cells:
            n = len(cells); xy = (n % 32 * 32, n // 32 * 32)
            cells[data] = xy; atlas.paste(im, xy)
        x, y = cells[data]
        rules.append(f'[{guard}]<tile>{image_id},{key},{pal:08X},{x},{y},1,N')
        pairs.add((key, pal))
    scaler = ctypes.CDLL(str(ROOT/'tools/scale.so'))
    scaler.scale4.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    def alpha(key):
        mask = np.uint8(indices(key) > 0)*255
        src = np.dstack([mask]*4).copy(); target = np.zeros((32, 32, 4), np.uint8)
        scaler.scale4(src.ctypes.data, target.ctypes.data, 8, 8)
        return Image.fromarray(target[:, :, 3])
    source = Image.open(ROOT/'art/area3-snowface-v0124.png').convert('RGBA')
    w, h = source.size
    wall = fit(source.crop((0, 0, w//2, h)), (32, 32))
    recess = fit(source.crop((w//2, 0, w, h)), (64, 64))
    ledge = cell(Image.open(ROOT/'art/area3-ice-ledge-v0124.png').convert('RGBA'), 0,
                 cols=1, rows=1, main_component=True)
    ledge = fit(ledge, (128, 64))
    layout = json.loads((ROOT/'capture/area3/vegetation-layout-v0123.json').read_text())['positions']
    catalog = json.loads((ROOT/'capture/area3/material-catalog.json').read_text())
    painted = {}
    counts = {'cliff': 0, 'recess': 0, 'ledge': 0, 'foreground': 0}
    for rec in catalog:
        if rec['layer'] != 0: continue
        key, pal, i = rec['key'], int(rec['palette'], 16), rec['index']
        if key == '0'*32: continue
        if pal == 0x1C201000 and i >= 71:
            x, y = layout[key]; im = recess.crop((x*32, y*32, x*32+32, y*32+32))
            im.putalpha(alpha(key)); kind = 'recess'
        elif pal in [0x1C271707, 0x1C201707, 0x1C302907]:
            # Indices 33–36 are horizontal cliff bands, not tree limbs.
            # They were included in the old bark range by mistake.
            if pal == 0x1C271707 and (9 <= i <= 32 or 37 <= i <= 40): continue
            im = wall.copy(); kind = 'cliff'
            if pal == 0x1C302907 and i in [1, 2, 3, 4]:
                x = 0 if i in [1, 2] else 32; y = 0 if i in [1, 3] else 32
                im.alpha_composite(ledge.crop((x, y, x+32, y+32)))
                # Retain the exact earlier platform contour and walkable lip.
                im.putalpha(oldcell(key, pal).getchannel('A')); kind = 'ledge'
            else:
                im.putalpha(alpha(key))
        else: continue
        painted[key, pal] = im; emit(key, pal, im); counts[kind] += 1
    # Native foreground lip fragments must use the same snow material as the
    # ledges they overlap; otherwise brown flakes remain visible while moving.
    aliases = {key for key, pal in old if pal == 0xFF30290F and (key, 0x1C302907) in painted}
    aliases |= {'0301000000000000B06E6D454D080800', '1824220200000000E69915746E6A4A88',
                '83CF79DFEF7BA6035C108620108418FC', '83D7FAFCF2E150085C2801010D122DF3'}
    # The native foreground snow is one pixel below the background tile.
    # Match its actual underlying ledge column instead of drawing bright
    # snow-shaped cutouts across the new blue ice face.
    ledgekeys = {r['index']: r['key'] for r in catalog if r['layer'] == 0
                 and r['palette'] == '1C302907' and r['index'] in [1, 2, 3, 4]}
    conditions.append('<condition>a3124LipY,positionCheckY,>=,1')
    for i, key in ledgekeys.items():
        conditions.append(f'<condition>a3124Ledge{i},tileNearby,0,-1,{key},1C302907,N')
    from PIL import ImageOps
    for key in sorted(aliases):
        top = key in {'83CF79DFEF7BA6035C108620108418FC', '83D7FAFCF2E150085C2801010D122DF3'}
        for i in ([1, 3] if top else [2, 4]):
            strip = Image.new('RGBA', (32, 64))
            strip.paste(wall, (0, 0)); strip.paste(wall, (0, 32))
            strip.alpha_composite(painted[ledgekeys[i], 0x1C302907], (0, 0))
            if top: strip.alpha_composite(painted[ledgekeys[i+1], 0x1C302907], (0, 32))
            material = strip.crop((0, 4, 32, 36))
            for hm in [False, True]:
                im = ImageOps.mirror(material) if hm else material.copy()
                im.putalpha(alpha(key))
                emit(key, 0xFF30290F, im, OUT+f'&a3124LipY&a3124Ledge{i}'
                     + ('&hmirror' if hm else '&!hmirror')+'&!vmirror')
        # Painted fallback at clipped boundaries where the matching native
        # background column is unavailable. Never show original green pixels.
        im = ledge.crop((0, 4 if top else 32, 32, 36 if top else 64))
        im.putalpha(alpha(key)); emit(key, 0xFF30290F, im)
        counts['foreground'] += 1
    # Keep the approved opaque doorway ahead of the new cliff fill. Its fill
    # key also occurs in the cliff, so the existing jamb guards remain vital.
    door_image = names.index('area3-surfaces-v0122.png')
    doors = [s for s in oldrules if s.split('<tile>')[1].split(',')[0] == str(door_image)
             and s.split('<tile>')[1].split(',')[2] == '1C201707']
    assert len(doors) == 16
    at = next(i for i, s in enumerate(lines) if '<tile>' in s)
    lines[at:at] = ['<img>area3-snowface-v0124.png'] + conditions + doors + rules
    lines[0] = '# Bionic Commando HD v0.12.4 - unified snowy cliff'
    (dest/'hires.txt').write_text('\n'.join(lines)+'\n')
    atlas.crop((0, 0, 1024, max(32, (len(cells)+31)//32*32))).save(dest/'area3-snowface-v0124.png')
    notes = (dest/'README.txt').read_text().replace('v0.12.3', 'v0.12.4')
    notes = notes.replace('Frost-tipped alpine moss and evergreen foliage replace the decorative wall mesh.\nVegetation stays distinct from the solid brown rock and snowy ledges.',
        'The outdoor cliff now has a consistent packed-snow finish and ice ledges.\nSoft blue snow recesses distinguish non-grappleable backing from solid terrain.')
    (dest/'README.txt').write_text(notes)
    report = {'version': '0.12.4', 'new_material_rules': len(rules), 'retained_door_priority_rules': len(doors),
              'art_cells': len(cells), 'materials': counts, 'new_conditions': len(conditions),
              'new_sprite_additions': 0, 'changed_pairs': [[k, f'{p:08X}'] for k,p in sorted(pairs)]}
    (ROOT/'validation/v0124-build.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'changed_pairs'}), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, default=ROOT/'pack')
    parser.add_argument('--reuse-approved', action='store_true')
    a = parser.parse_args(); build(a.output, a.reuse_approved)


if __name__ == '__main__': main()
