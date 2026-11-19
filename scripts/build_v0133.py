"""Repaint the approved Area 16 wheeled cannon for the Area 6 dockyard."""
import colorsys
import hashlib
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HEAD = "090E060606060606070E020202020202"
RED = "FF36150F"
BLUE = "FF30210F"
FLASH = "FF202A0F"
STAGE = "area6&!worldmap&!equipment&!title&!radio&!areaClear&!interception&!interception14"
ATLAS = "area6-blue-cannon-v0133.png"


def repaint(source, flash):
    result = source.copy()
    pixels = []
    for r, g, b, a in source.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        # The painted steel is crimson. Keep tires, barrel steel and bronze fittings.
        if a and (h < 0.055 or h > 0.90) and r - min(g, b) >= 10:
            hue = 0.598 if not flash else 0.57
            # Preserve the contrast between navy shadows and bright edge highlights.
            value = min(1, v * 1.07 + (0.16 if flash else 0.02))
            sat = min(0.9, s * (0.68 if flash else 1.07))
            r, g, b = [round(c * 255) for c in colorsys.hsv_to_rgb(hue, sat, value)]
        pixels.append((r, g, b, a))
    result.putdata(pixels)
    return result


def build(source, target):
    import shutil
    target.mkdir(parents=True, exist_ok=True)
    for f in source.iterdir():
        if f.is_file() and source != target:
            shutil.copy2(f, target / f.name)
    rows = (source / 'hires.txt').read_text().splitlines()
    assert ATLAS not in '\n'.join(rows), 'Input must be v0.13.2'
    sheets = [r[5:] for r in rows if r.startswith('<img>')]
    old_id = sheets.index('area16-identity-wheels-v0105.png')
    prior_id = sheets.index('area16-dialogue-cannon-v0104.png')
    old = Image.open(source / sheets[old_id]).convert('RGBA')
    anchors = [r[10:].split(',') for r in rows if r.startswith('<addition>' + HEAD + ',' + RED + ',')]
    assert len(anchors) == 16
    pose_keys = {a[4] for a in anchors}
    old_poses = [r for r in rows if f'<tile>{old_id},' in r and r.split('>')[1].split(',')[1] in pose_keys]
    native = {r.split('>')[1].split(',')[1] for r in rows if f'<tile>{prior_id},' in r and ',' + RED + ',' in r} - pose_keys
    assert len(native) == 9 and len(old_poses) == 48
    conditions = {r.split(',')[0][11:]: r.split(',')[1:] for r in rows if r.startswith('<condition>v0105Near')}
    cells = [Image.new('RGBA', (32, 32))]
    interned = {cells[0].tobytes(): 0}
    def offset(image):
        data = image.tobytes()
        if data not in interned:
            interned[data] = len(cells)
            cells.append(image)
        i = interned[data]
        return f'{(i % 16) * 32},{(i // 16) * 32}'
    additions, rules = [], []
    guards = {}
    for pal in (BLUE, FLASH):
        vkeys = {k: hashlib.md5(('area6-blue-cannon-v0133/' + pal + '/' + k).encode()).hexdigest().upper() for k in pose_keys}
        for src, _, x, y, key, _, ignore in anchors:
            additions.append(f'<addition>{src},{pal},{x},{y},{vkeys[key]},{pal},{ignore}')
        for r in old_poses:
            prev, fields = r.split('<tile>')
            _, key, _, x, y, bright, default = fields.split(',')
            x, y = int(x), int(y)
            cell = old.crop((x, y, x + 32, y + 32))
            guard = STAGE
            near = [g for g in prev[1:-1].split('&') if g.startswith('v0105Near')]
            if near:
                token = near[0]
                name = f'a633_{pal}_{token}'
                kind, dx, dy, chr_key, _, ignore = conditions[token]
                guards[name] = f'{kind},{dx},{dy},{chr_key},{pal},{ignore}'
                # Screen-space bounds protect the emulator's sprite-neighbor lookup at the border.
                # Vertical flips are absent on every cannon tile, but make the limit symmetric.
                if int(dy):
                    distance = abs(int(dy))
                    low, high = f'a633Ymin{distance}', f'a633Ymax{distance}'
                    guards[low] = f'positionCheckY,>=,{distance}'
                    guards[high] = f'positionCheckY,<,{240 - distance}'
                    guard += '&' + low + '&' + high
                guard += '&' + name
            xy = offset(repaint(cell, pal == FLASH))
            rules.append(f'[{guard}]<tile>{len(sheets)},{vkeys[key]},{pal},{xy},{bright},{default}')
        for key in sorted(native):
            rules.append(f'[{STAGE}]<tile>{len(sheets)},{key},{pal},0,0,1,N')
        for key in sorted(vkeys.values()):
            rules.append(f'<tile>{len(sheets)},{key},{pal},0,0,1,N')
    sheet = Image.new('RGBA', (16 * 32, ((len(cells) + 15) // 16) * 32))
    for i, cell in enumerate(cells):
        sheet.paste(cell, ((i % 16) * 32, (i // 16) * 32))
    sheet.save(target / ATLAS, optimize=True)
    first = next(i for i, r in enumerate(rows) if '<tile>' in r)
    rows[first:first] = (['# Area 6 blue wheeled cannon', '<img>' + ATLAS]
                         + ['<condition>' + name + ',' + spec for name, spec in guards.items()]
                         + additions + rules)
    rows[0] = '# Bionic Commando HD v0.13.3 - Area 6 blue wheeled cannon'
    (target / 'hires.txt').write_text('\n'.join(rows) + '\n')
    readme = (source / 'README.txt').read_text().replace('v0.13.2','v0.13.3',1)
    readme = readme.replace('NEW IN THIS BUILD\n','NEW IN THIS BUILD\nArea 6 uses the blue-armored version of the Area 16 wheeled cannon.\n\nPREVIOUS BUILDS\n',1)
    (target / 'README.txt').write_text(readme)


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('source', type=Path)
    cli.add_argument('target', type=Path)
    args = cli.parse_args()
    build(args.source, args.target)
